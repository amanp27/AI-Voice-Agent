from dotenv import load_dotenv
import logging
import os
import asyncio

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import google, noise_cancellation
from mem0 import AsyncMemoryClient

from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import get_weather, search_web, send_email

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Puck",
                temperature=0.8
            ),
            tools=[get_weather, search_web, send_email]
        )

server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    await ctx.connect()
    
    # Get user ID
    user_id = "guest"
    for p in ctx.room.remote_participants.values():
        user_id = p.identity
        break
    
    logger.info(f"👤 User: {user_id}")
    
    # Initialize Mem0
    mem0 = AsyncMemoryClient(api_key=os.getenv("MEM0_API_KEY"))
    
    # Load user memory
    memory_context = ""
    try:
        results = await mem0.get_all(user_id=user_id)
        if results:
            memories = [result["memory"] for result in results[:5]]
            memory_context = "\n\nUser context:\n" + "\n".join(memories)
            logger.info(f"📚 Loaded {len(memories)} memories")
    except Exception as e:
        logger.warning(f"⚠️ Memory load failed: {e}")
    
    # Track conversation
    conversation_messages = []
    
    # Handle text messages
    @ctx.room.on("data_received")
    def on_data(data: rtc.DataPacket):
        try:
            msg = data.data.decode('utf-8')
            logger.info(f"📝 Text: {msg}")
            conversation_messages.append({"role": "user", "content": msg})
            
            asyncio.create_task(
                ctx.room.local_participant.publish_data(f"USER:{msg}".encode('utf-8'))
            )
        except Exception as e:
            logger.error(f"Error: {e}")
    
    session = AgentSession()
    
    # Capture transcripts
    @session.on("user_transcript")
    def on_user_transcript(transcript):
        logger.info(f"🎤 User: {transcript}")
        conversation_messages.append({"role": "user", "content": transcript})
        
        asyncio.create_task(
            ctx.room.local_participant.publish_data(f"USER:{transcript}".encode('utf-8'))
        )
    
    @session.on("agent_transcript")
    def on_agent_transcript(transcript):
        logger.info(f"🤖 Agent: {transcript}")
        conversation_messages.append({"role": "assistant", "content": transcript})
        
        asyncio.create_task(
            ctx.room.local_participant.publish_data(f"AGENT:{transcript}".encode('utf-8'))
        )
    
    # Save to Mem0 on disconnect
    async def save_to_mem0():
        if conversation_messages:
            try:
                logger.info(f"💾 Saving to Mem0")
                await mem0.add(conversation_messages, user_id=user_id)
                logger.info("✅ Saved")
            except Exception as e:
                logger.error(f"❌ Save failed: {e}")
    
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
    
    logger.info("✅ Ready")
    
    greeting = SESSION_INSTRUCTION + memory_context
    await session.generate_reply(instructions=greeting)

if __name__ == "__main__":
    agents.cli.run_app(server)