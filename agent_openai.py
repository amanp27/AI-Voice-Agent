from dotenv import load_dotenv
import logging
import json
import os
from datetime import datetime
import asyncio

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import openai, noise_cancellation
from mem0 import AsyncMemoryClient

from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import get_weather, search_web, send_email

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STORAGE_DIR = "conversations"

def ensure_storage_dir():
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)

def append_message(session_id, role, content, msg_type="text"):
    try:
        ensure_storage_dir()
        filename = f"{STORAGE_DIR}/{session_id}.json"
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
        else:
            data = {
                "session_id": session_id,
                "start_time": datetime.now().isoformat(),
                "messages": []
            }
        
        data["messages"].append({
            "role": role,
            "content": content,
            "type": msg_type
        })
        data["end_time"] = datetime.now().isoformat()
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Saved {role} message")
    except Exception as e:
        logger.error(f"❌ Save error: {e}")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=openai.realtime.RealtimeModel(
                voice="sage",
                temperature=0.8
            ),
            tools=[get_weather, search_web, send_email]
        )

server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    logger.info(f"🚀 Session started: {session_id}")
    
    await ctx.connect()
    
    # Get user ID from participant
    user_id = "guest"
    for p in ctx.room.remote_participants.values():
        user_id = p.identity
        break
    
    logger.info(f"👤 User: {user_id}")
    
    # Initialize Mem0 for this user
    mem0 = AsyncMemoryClient(api_key=os.getenv("MEM0_API_KEY"))
    
    # Load user's memory
    memory_context = ""
    try:
        results = await mem0.get_all(user_id=user_id)
        if results:
            memories = [result["memory"] for result in results[:5]]  # Last 5 memories
            memory_context = "\n\nUser context:\n" + "\n".join(memories)
            logger.info(f"📚 Loaded {len(memories)} memories for {user_id}")
    except Exception as e:
        logger.warning(f"⚠️ Could not load memories: {e}")
    
    # Track conversation for Mem0
    conversation_messages = []
    last_user_msg = ""
    
    # Handle text input from user
    @ctx.room.on("data_received")
    def on_data(data: rtc.DataPacket):
        nonlocal last_user_msg
        try:
            msg = data.data.decode('utf-8')
            logger.info(f"📝 User text: {msg}")
            
            last_user_msg = msg
            conversation_messages.append({"role": "user", "content": msg})
            append_message(session_id, "user", msg, "text")
            
            # Echo to UI
            asyncio.create_task(
                ctx.room.local_participant.publish_data(
                    f"USER:{msg}".encode('utf-8')
                )
            )
        except Exception as e:
            logger.error(f"Data error: {e}")
    
    session = AgentSession()
    
    # Capture transcripts
    @session.on("user_transcript")
    def on_user_transcript(transcript):
        nonlocal last_user_msg
        logger.info(f"🎤 User said: {transcript}")
        
        last_user_msg = transcript
        conversation_messages.append({"role": "user", "content": transcript})
        append_message(session_id, "user", transcript, "speech")
        
        # Send to UI
        asyncio.create_task(
            ctx.room.local_participant.publish_data(
                f"USER:{transcript}".encode('utf-8')
            )
        )
    
    @session.on("agent_transcript")
    def on_agent_transcript(transcript):
        logger.info(f"🤖 Agent said: {transcript}")
        
        conversation_messages.append({"role": "assistant", "content": transcript})
        append_message(session_id, "assistant", transcript, "speech")
        
        # Send to UI
        asyncio.create_task(
            ctx.room.local_participant.publish_data(
                f"AGENT:{transcript}".encode('utf-8')
            )
        )
    
    # Shutdown hook to save to Mem0
    async def save_to_mem0():
        if conversation_messages:
            try:
                logger.info(f"💾 Saving {len(conversation_messages)} messages to Mem0 for {user_id}")
                await mem0.add(conversation_messages, user_id=user_id)
                logger.info("✅ Saved to Mem0")
            except Exception as e:
                logger.error(f"❌ Mem0 save error: {e}")
    
    ctx.add_shutdown_callback(save_to_mem0)
    
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony() 
                    if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP 
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )
    
    logger.info("✅ Session ready")
    
    # Add memory context to greeting
    greeting = SESSION_INSTRUCTION + memory_context
    await session.generate_reply(instructions=greeting)

if __name__ == "__main__":
    agents.cli.run_app(server)