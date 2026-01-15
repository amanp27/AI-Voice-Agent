# AI Voice Agent - System Architecture Documentation

## 📋 Executive Summary

This document outlines the architecture of our AI Voice Agent system - a real-time voice assistant application that enables natural conversations between users and an AI agent powered by OpenAI's Realtime API and LiveKit's infrastructure.

---

## 🏗️ System Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                       │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │          Next.js Frontend (Port 3000)                      │    │
│  │  - React UI Components                                     │    │
│  │  - LiveKit React SDK                                       │    │
│  │  - Real-time Chat Interface                                │    │
│  │  - Audio Visualizer                                        │    │
│  └────────────────────────────────────────────────────────────┘    │
│                              │                                     │
│                              │ HTTPS/WSS                           │
│                              ▼                                     │
└────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      API & ORCHESTRATION LAYER                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │        Next.js API Routes (/api/generate-token)            │     │
│  │  - User Authentication                                     │     │
│  │  - LiveKit Token Generation                                │     │
│  │  - Room Creation                                           │     │
│  └────────────────────────────────────────────────────────────┘     │
│                              │                                      │
│                              │                                      │
│                              ▼                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     REAL-TIME MEDIA LAYER                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │              LiveKit Cloud Infrastructure                  │     │
│  │  - WebRTC Signaling                                        │     │
│  │  - Media Routing (Audio Streams)                           │     │
│  │  - Data Channels (Text Messages)                           │     │
│  │  - Noise Cancellation (BVC)                                │     │
│  └────────────────────────────────────────────────────────────┘     │
│                              │                                      │
│                              │ WebRTC                               │
│                              ▼                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      AI AGENT PROCESSING LAYER                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │          Python Agent (agent.py - Port 42613)              │     │
│  │  ┌──────────────────────────────────────────────────┐      │     │
│  │  │  LiveKit Agents Framework                        │      │     │
│  │  │  - Session Management                            │      │     │
│  │  │  - Transcript Processing                         │      │     │
│  │  │  - Tool Orchestration                            │      │     │
│  │  └──────────────────────────────────────────────────┘      │     │
│  │                                                            │     │
│  │  ┌──────────────────────────────────────────────────┐      │     │
│  │  │  OpenAI Realtime Model (Voice: Sage)             │      │     │
│  │  │  - Voice-to-Voice Conversation                   │      │     │
│  │  │  - Natural Language Understanding                │      │     │
│  │  │  - Response Generation                           │      │     │
│  │  └──────────────────────────────────────────────────┘      │     │
│  │                                                            │     │
│  │  ┌──────────────────────────────────────────────────┐      │     │
│  │  │  Function Tools                                  │      │     │
│  │  │  - get_weather()                                 │      │     │
│  │  │  - search_web()                                  │      │     │
│  │  │  - send_email()                                  │      │     │
│  │  └──────────────────────────────────────────────────┘      │     │
│  └────────────────────────────────────────────────────────────┘     │
│                              │                                      │
│                              ▼                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      STORAGE & MEMORY LAYER                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────┐  ┌──────────────────────────────────┐      │
│  │  JSON File Storage  │  │       Mem0 Cloud API             │      │
│  │  (conversations/)   │  │  - User Memory Context           │      │
│  │  - Session Logs     │  │  - Conversation History          │      │
│  │  - Transcripts      │  │  - Personalization Data          │      │
│  └─────────────────────┘  └──────────────────────────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 System Flow Diagrams

### 1. **User Connection Flow**

When a user opens the application, here's what happens:

```
🧑 User                                                    🤖 AI Agent
  │
  │ Opens Application
  │──────────────────────────────────────────────────────────────▶
  │                                                               │
  │                        🎫 Request Access Token                │
  │──────────────────────────────────────────────────────────────▶│
  │                                                               │
  │                     ✅ Token + Room Created                   │
  │◀──────────────────────────────────────────────────────────────│
  │                                                               │
  │              🌐 Establish WebRTC Connection                   │
  │◀─────────────────────────────────────────────────────────────▶│
  │                    (via LiveKit Cloud)                        │
  │                                                               │
  │                                                         📚 Load User Memory
  │                                                               │
  │                     👋 "Hello! How can I help?"               │
  │◀──────────────────────────────────────────────────────────────│
  │
  ✅ Connected & Ready
```

**Key Steps:**
1. User clicks "Connect to Voice Agent"
2. Next.js generates unique JWT token + room
3. WebRTC connection established through LiveKit
4. Agent loads user's previous conversation history from Mem0
5. Agent greets user with personalized context

---

### 2. **Voice Conversation Flow**

Real-time voice interaction between user and AI:

```
🧑 User                     🎙️ Processing                    🤖 AI Agent
  │                                                              │
  │  "What's the weather                                         │
  │   in London?"                                                │
  ├──────────────▶                                               │
  │               │                                              │
  │               │ 🔊 Audio Captured                            │
  │               │ 🔇 Noise Cancelled                           │
  │               ├─────────────────────────────────────────────▶│
  │               │                                              │
  │               │                              🧠 Understand Intent
  │               │                              🔧 Call get_weather("London")
  │               │                              💬 Generate Response
  │               │                                              │
  │               │         🗣️ Voice Response                    │
  │               │◀─────────────────────────────────────────────│
  │  🔊 Hears     │                                              │
  │  "It's 15°C   │                                              │
  │   and cloudy" │                                              │
  │◀──────────────│                                              │
  │                                                              │
  │  💬 Transcript appears in chat                               │
  │  "What's the weather in London?"                             │
  │  "It's currently 15°C and cloudy in London."                 │
```

**Key Features:**
- Sub-500ms latency
- Automatic noise cancellation
- Real-time transcription
- Tool execution (weather, search, email)
- Visual feedback (listening/thinking/speaking states)

---

### 3. **Multi-Modal Interaction Flow**

Users can interact via voice OR text - both work seamlessly:

```
       🧑 User Interface                    🤖 Backend Processing
       
┌──────────────────────────┐
│  🎤 Voice Input          │───────────▶  Voice → Text → AI → Voice Response
│  "Send email to..."      │
└──────────────────────────┘
                                            
┌──────────────────────────┐
│  ⌨️  Text Input           │───────────▶  Text → AI → Voice/Text Response  
│  "xyz@gmail.com"         │
└──────────────────────────┘

┌──────────────────────────┐
│  💬 Unified Chat Display │◀────────── All messages appear here
│  • User messages (blue)  │            regardless of input method
│  • Agent responses (gray)│
└──────────────────────────┘
```

**Example Conversation:**
```
User (voice):  "Can you send an email for me?"
Agent (voice): "Of course! What's the recipient's email?"
User (text):   xyz@gmail.com
Agent (voice): "Got it. What's the subject?"
User (voice):  "Meeting reminder"
Agent (voice): "And the message?"
User (text):   Don't forget our 3pm meeting today
Agent (voice): "Email sent successfully to xyz@gmail.com!"
```

---

### 4. **Memory & Personalization Flow**

How the system remembers and learns from conversations:

```
        📅 Session 1                                    📅 Session 2
        
🧑 "My name is John"                          🧑 Opens app
    │                                              │
    ▼                                              ▼
🤖 "Nice to meet you, John!"          🤖 "Welcome back, John!"
    │                                              ▲
    │                                              │
    ▼                                              │
💾 Saved to Mem0                          📚 Loaded from Mem0
   • User: name = "John"                    • Previous context
   • Conversation context                   • Name, preferences
   • Preferences                            • Past conversations
```

**Storage Strategy:**

```
Every Conversation
       │
       ├──────────────────────┬──────────────────────┐
       ▼                      ▼                      ▼
   
📝 Real-time              💾 Session Backup       🧠 Long-term Memory
   Transcript                (JSON Files)            (Mem0 Cloud)
       │                         │                      │
       │                         │                      │
   Live chat UI          conversations/          User context
   updates               YYYYMMDD_HHMMSS.json    & preferences
                         • Full transcript        • Survives restarts
                         • Timestamps             • Cross-device
                         • User/Agent msgs        • Personalization
```

**What Gets Stored:**
- ✅ User name and preferences
- ✅ Previous conversation topics
- ✅ Tool usage patterns
- ✅ Context for future interactions
- ❌ Sensitive data (encrypted if needed)

---

### 5. **Tool Execution Flow**

When AI needs external information:

```
🧑 "What's the weather?"
    │
    ▼
🤖 Understands intent
    │
    ├─── Needs external data ───┐
    │                            │
    ▼                            ▼
                          🔧 get_weather("current_location")
                                 │
                                 ▼
                          🌐 API Call to wttr.in
                                 │
                                 ▼
                          ✅ "15°C, Cloudy"
                                 │
                                 ▼
🤖 "It's currently 15°C and cloudy"
    │
    ▼
🧑 Hears response
```

**Available Tools:**
```
┌─────────────────────┐
│  🌤️  get_weather()  │ → wttr.in API
│  📧 send_email()    │ → Gmail SMTP
│  🔍 search_web()    │ → DuckDuckGo
└─────────────────────┘
```

**Tool Execution Timeline:**
```
0ms ──────▶ User asks question
100ms ─────▶ AI detects tool needed
200ms ─────▶ Tool function called
1-3s ──────▶ External API responds
1.5-3.5s ──▶ AI formulates answer
2-4s ──────▶ User hears response
```

---

## 🛠️ Technology Stack

### **Frontend**
- **Framework**: Next.js 14 (React 18)
- **UI Library**: Tailwind CSS
- **Real-time SDK**: LiveKit React Components
- **Audio Visualization**: BarVisualizer
- **Language**: TypeScript

### **Backend**
- **Agent Runtime**: Python 3.13
- **Framework**: LiveKit Agents SDK 1.3.10
- **AI Model**: OpenAI Realtime API (Voice: Sage)
- **Plugins**:
  - `livekit-plugins-openai`
  - `livekit-plugins-noise-cancellation`

### **Infrastructure**
- **Media Server**: LiveKit Cloud (India Region)
- **Protocol**: WebRTC
- **Signaling**: WSS (WebSocket Secure)
- **Authentication**: JWT Tokens

### **Storage & Memory**
- **Session Storage**: JSON Files (Local)
- **User Memory**: Mem0 Cloud API
- **Conversation Logs**: File System

### **External APIs**
- **Weather**: wttr.in API
- **Web Search**: DuckDuckGo Search
- **Email**: Gmail SMTP

---

## 📊 Component Breakdown

### **1. Frontend Components**

```typescript
VoiceAssistantPage (Main)
├── ConnectionStatus
│   └── Displays: Connected/Disconnected/Connecting
├── ChatMessages
│   └── Displays: User & Agent messages with timestamps
├── VoiceVisualizer
│   ├── State Indicator (Listening/Thinking/Speaking)
│   └── Audio Bars (BarVisualizer)
├── InputArea
│   ├── Text Input Field
│   ├── Send Button
│   └── Disconnect Button
└── DataChannelListener
    └── Receives messages from agent
```

### **2. Backend Components**

```python
agent.py
├── Assistant (Agent Class)
│   ├── LLM: OpenAI Realtime Model
│   ├── Tools: [get_weather, search_web, send_email]
│   └── Instructions: AGENT_INSTRUCTION
├── Session Manager (my_agent)
│   ├── Connection Handler
│   ├── Transcript Listeners
│   │   ├── @session.on("user_transcript")
│   │   └── @session.on("agent_transcript")
│   ├── Data Channel Handler
│   │   └── @room.on("data_received")
│   └── Shutdown Hook
│       └── Saves to Mem0 on disconnect
└── Storage Functions
    ├── append_message() → JSON files
    └── save_to_mem0() → Cloud storage
```

### **3. API Routes**

```
/api/generate-token
├── Input: userID (query param)
├── Process:
│   ├── Create LiveKit Room (UUID)
│   ├── Generate Access Token (JWT)
│   └── Set Permissions (publish/subscribe)
└── Output: { roomName, token }
```

---

## 🔐 Security & Authentication

### **Token-Based Access**
```
User Request → API generates JWT Token
              ↓
JWT includes:
- User Identity
- Room Name
- Permissions (publish, subscribe, data)
- Expiration Time
              ↓
LiveKit validates token on connection
```

### **Data Privacy**
- Each user has isolated conversation storage
- Mem0 uses user_id for memory segregation
- No cross-user data leakage

### **Environment Variables** (Secured)
```
LIVEKIT_URL
LIVEKIT_API_KEY
LIVEKIT_API_SECRET
OPENAI_API_KEY
MEM0_API_KEY
GMAIL_USER
GMAIL_APP_PASSWORD
```

---

## 📝 Key Features

### ✅ **Real-Time Voice Conversations**
- Low-latency voice-to-voice communication
- Natural language understanding
- Context-aware responses

### ✅ **Multi-Modal Interaction**
- Voice input (microphone)
- Text input (keyboard)
- Both displayed in unified chat interface

### ✅ **Tool Integration**
- **Weather**: Get current weather for any city
- **Web Search**: Search DuckDuckGo for information
- **Email**: Send emails via Gmail SMTP

### ✅ **Memory & Personalization**
- Stores user context in Mem0
- Loads previous conversation history
- Personalizes responses based on past interactions

### ✅ **Conversation Storage**
- Real-time transcript capture
- JSON file storage (session-based)
- Mem0 cloud backup

### ✅ **Audio Processing**
- Noise cancellation (BVC algorithm)
- Audio visualization
- State indicators (listening/thinking/speaking)

---

## 📈 Scalability Considerations

### **Current Capacity**
- **Concurrent Users**: 5-10 users
- **Storage**: Local file system
- **Region**: India (LiveKit Cloud)

### **Production Recommendations**

#### 1. **Database Migration**
```
Current: JSON Files
         ↓
Recommended: PostgreSQL / MongoDB
- Handles concurrent writes
- Better query performance
- Reliable backups
```

#### 2. **Session ID Enhancement**
```python
# Current (collision risk)
session_id = datetime.now().strftime('%Y%m%d_%H%M%S')

# Recommended
import uuid
session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
```

#### 3. **Load Balancing**
```
User Traffic
     │
     ▼
Load Balancer
     │
     ├──→ Agent Instance 1
     ├──→ Agent Instance 2
     └──→ Agent Instance 3
```

#### 4. **Monitoring & Logging**
- **Application**: Sentry for error tracking
- **Infrastructure**: CloudWatch/Datadog
- **Metrics**: Track latency, errors, active sessions

---

## 🚀 Deployment Architecture

### **Development Environment**
```
┌──────────────────┐
│  Developer PC    │
│                  │
│  Port 3000: UI   │
│  Port 42613: Ag  │
└──────────────────┘
```

### **Production Environment** (Recommended)
```
┌────────────────────────────────────────┐
│           Cloud Provider               │
│  (AWS / GCP / Azure)                   │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────┐  ┌───────────────┐  │
│  │  Frontend    │  │  Backend      │  │
│  │  (Vercel)    │  │  (AWS EC2)    │  │
│  │  Next.js     │  │  Python Agent │  │
│  └──────────────┘  └───────────────┘  │
│                                        │
│  ┌──────────────┐  ┌───────────────┐  │
│  │  Database    │  │  Storage      │  │
│  │  (RDS)       │  │  (S3)         │  │
│  └──────────────┘  └───────────────┘  │
│                                        │
└────────────────────────────────────────┘
         │
         ▼
┌────────────────────┐
│  LiveKit Cloud     │
│  (Media Server)    │
└────────────────────┘
```

---

## 📊 Performance Metrics

### **Response Times**
- Voice latency: ~200-500ms
- Text message: ~100-200ms
- Tool execution: 1-3 seconds (weather/search/email)

### **Audio Quality**
- Sample rate: 24kHz
- Codec: Opus
- Noise cancellation: BVC algorithm

### **Storage**
- Average session: 50-100 messages
- File size: ~5-10 KB per session
- Mem0 storage: Unlimited (cloud)

---

## 🐛 Known Limitations

1. **Session Collision**: Multiple users in same second share session ID
2. **File Storage**: Not suitable for high concurrency
3. **No User Auth**: Anyone can connect with any userID
4. **Single Region**: Limited to India region (LiveKit)
5. **Memory Management**: No automatic cleanup of old sessions

---

## 🔮 Future Enhancements

### **Phase 1** (Short-term)
- [ ] Implement proper user authentication
- [ ] Migrate to PostgreSQL database
- [ ] Add rate limiting
- [ ] Unique session IDs with UUID

### **Phase 2** (Medium-term)
- [ ] Multi-region deployment
- [ ] Load balancing
- [ ] Real-time monitoring dashboard
- [ ] Conversation analytics

### **Phase 3** (Long-term)
- [ ] Multi-language support
- [ ] Advanced tool integrations (Calendar, CRM)
- [ ] Voice customization
- [ ] Mobile app (React Native)

---

## 📚 File Structure

```
project/
├── frontend/ (Next.js)
│   ├── app/
│   │   ├── api/
│   │   │   └── generate-token/
│   │   │       └── route.ts
│   │   └── page.tsx
│   ├── .env.local
│   ├── next.config.js
│   └── package.json
│
├── backend/ (Python)
│   ├── agent.py
│   ├── tools.py
│   ├── prompts.py
│   ├── .env
│   ├── requirements.txt
│   └── conversations/
│       └── YYYYMMDD_HHMMSS.json
│
└── documentation/
    └── architecture.md (this file)
```

---

## 📞 Support & Maintenance

### **Logs Location**
- Frontend: Browser Console
- Backend: Terminal output + LiveKit Cloud dashboard
- Conversations: `conversations/` directory

### **Monitoring**
- Check LiveKit dashboard for active sessions
- Monitor JSON file growth in `conversations/`
- Review Mem0 dashboard for memory usage

### **Troubleshooting**
- Connection issues → Check LiveKit credentials
- Transcription not working → Verify OpenAI API key
- Memory not loading → Check Mem0 API key
- Tools failing → Verify external API access

---

## ✅ Conclusion

This AI Voice Agent system provides a robust foundation for real-time voice interactions with AI. The architecture is modular, allowing for easy enhancements and scaling as requirements grow.

**Current Status**: ✅ Development Ready  
**Production Ready**: ⚠️ Requires enhancements (see Future Enhancements)

---

**Document Version**: 1.0  
**Last Updated**: January 13, 2026  
**Maintained By**: Aman Prajapati [AI Developer]