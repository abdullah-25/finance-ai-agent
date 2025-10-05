# Quibittron System Design Document

## Executive Summary

I built Quibittron as an AI-powered stock analysis and recommendation system that combines real-time financial data, natural language processing, and voice communication to provide intelligent stock picks. My system analyzes market data, generates personalized recommendations, converts them to speech, and delivers them via phone calls for approval workflows.

## Architecture Overview

### System Architecture
I designed the system to follow a **microservices-inspired architecture** with three main components:

1. **Backend AI Engine** - Python-based workflow orchestration
2. **Web Interface** - React/TypeScript frontend with Express.js backend
3. **Communication Layer** - Twilio voice integration with ElevenLabs TTS

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend AI    │    │   External      │
│   (React/TS)    │◄──►│   (Python)      │◄──►│   APIs          │
│   - Chat UI     │    │   - Workflow    │    │   - Finance     │
│   - Express.js  │    │   - Claude AI   │    │   - Twilio      │
└─────────────────┘    └─────────────────┘    │   - ElevenLabs  │
                                               └─────────────────┘
```

### Data Flow
1. **User Input**: Users submit queries via my web chat interface
2. **AI Processing**: My Python workflow processes queries using Claude AI
3. **Data Retrieval**: I fetch live market data from DataForSEO API
4. **Analysis**: My AI analyzes data and generates top 3 stock recommendations
5. **Speech Generation**: I convert recommendations to audio via ElevenLabs
6. **Voice Delivery**: I deliver audio via Twilio phone call for approval
7. **Response**: My system returns the final result to the user interface

## Technology Stack

### Backend AI Engine (Python)
- **Framework**: Agno (AI workflow orchestration)
- **AI Model**: Anthropic Claude Sonnet 4.0
- **Database**: SQLite (workflow state management)
- **Key Libraries**:
  - `Flask` + `Flask-CORS` - REST API endpoints
  - `anthropic` - Claude AI integration
  - `requests` - HTTP client for external APIs
  - `python-dotenv` - Environment variable management

### Frontend (React/TypeScript)
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter (lightweight React router)
- **State Management**: TanStack Query (React Query)
- **UI Components**: Radix UI primitives with custom styling
- **Styling**: Tailwind CSS with custom design system
- **Build Tool**: Vite
- **Backend**: Express.js server (dual-purpose serving)

### External Service Integration
- **Finance Data**: DataForSEO Google Finance API
- **Text-to-Speech**: ElevenLabs API
- **Voice Calls**: Twilio Voice API
- **Authentication**: Environment-based API key management

### Infrastructure
- **Development**: Local development with ngrok tunneling
- **File Storage**: Local filesystem for audio files and call results
- **Session Management**: File-based storage for workflow state

## Core Components

### 1. AI Workflow Engine (`backend/main.py`)
**Purpose**: I designed this to orchestrate the entire stock analysis and recommendation process

**Key Features I Implemented**:
- **Multi-step Workflow**: I created an 8-step process from user input to final approval
- **Agent-based Architecture**: I built specialized AI agents for different tasks
  - API Agent: I use this for financial data retrieval and analysis
  - Summary Agent: I implemented this for content summarization
  - TTS Agent: I designed this for audio generation
  - Phone Agent: I built this for voice call management
  - Approval Agent: I created this for decision processing

**My Workflow Steps**:
1. I collect user input
2. I prepare API queries
3. I retrieve financial data
4. I summarize content
5. I prepare TTS input
6. I generate audio
7. I execute phone calls
8. I process approval responses

### 2. Web Interface (`frontend/`)
**Purpose**: I built this to provide a user-friendly chat interface for stock queries

**My Architecture**:
- **Client-side**: I created a React SPA with chat UI components
- **Server-side**: I implemented Express.js API proxy and static file serving
- **Communication**: I use RESTful API with JSON payloads

**Key Features I Built**:
- I designed a minimal, clean chat interface
- I implemented real-time message streaming
- I created responsive design for mobile/desktop
- I added dark/light mode support

### 3. Communication Services (`backend/server.py`)
**Purpose**: I built this to handle voice communications and external API integrations

**Services I Implemented**:
- **Twilio Integration**: I handle phone call initiation and DTMF collection
- **Audio Serving**: I serve MP3 files for voice calls  
- **Webhook Handling**: I process ElevenLabs and Twilio callbacks
- **File Management**: I manage audio file storage and cleanup

## API Endpoints

### My Backend Python API
- `GET /my-api/agent` - I execute the complete AI workflow here
- `POST /api/chat` - I handle chat interface requests (workflow execution)

### My Twilio Voice Webhooks
- `POST /voice` - I handle initial calls with TTS playback
- `POST /gather` - I collect DTMF input
- `GET /audio/<filename>` - I serve audio files

### My Frontend Express API
- I proxy endpoints to the Python backend
- I serve static files for the React application

## Data Models

### Workflow State
```python
StepInput/StepOutput: Content and metadata for workflow steps
Session: Workflow execution state in SQLite
```

### Financial Data
```python
Stock Information:
- symbol: Stock ticker
- name: Company name
- price: Current price
- price_change: Absolute change
- percentage_change: Percentage change
- trend: Price trend direction
```

### Call Management
```json
Call Result:
{
  "request_id": "uuid",
  "digit": "user_input",
  "timestamp": "unix_time",
  "created_at": "formatted_date"
}
```

## Security Considerations

### API Key Management
- Environment variables for all external service credentials
- Base64 encoded credentials for DataForSEO API
- No hardcoded secrets in source code

### Data Privacy
- Local file storage for temporary audio files
- Automatic cleanup of call result files
- No persistent user data storage

### Communication Security
- HTTPS endpoints for all external webhooks
- Secure phone number handling
- Input validation on all API endpoints

## Performance & Scalability

### Current Limitations I'm Aware Of
- **Single-threaded workflow execution** in my current implementation
- **File-based storage** I'm using isn't suitable for high concurrency
- **Synchronous API calls** throughout my workflow
- **Local audio file storage** I implemented

### Scalability Improvements I Plan
- I plan to migrate from SQLite to PostgreSQL
- I want to implement async workflow processing with message queues
- I'll move to cloud storage for audio files (S3/GCS)
- I'm considering horizontal scaling with container orchestration
- I plan to add Redis for session and cache management

## Deployment Architecture

### My Development Environment
- I run a local Python Flask server on port 3000
- I use a local React dev server with Vite
- I use ngrok tunneling for Twilio webhooks
- I manage API credentials through environment files

### My Production Considerations
- **Web Server**: I plan to use Nginx proxy with SSL termination
- **Application**: I'll use Gunicorn WSGI server for my Python backend
- **Process Management**: I'm considering PM2 or systemd for service management
- **Monitoring**: I need to implement application logs and health check endpoints

## Future Enhancements

### Technical Improvements I Want to Make
1. **Async Processing**: I need to convert my workflow to async/await pattern
2. **Database Migration**: I plan to move to PostgreSQL with proper schema
3. **Caching Layer**: I want to add Redis for API response caching
4. **Error Handling**: I need comprehensive retry logic and error recovery
5. **Testing**: I should build unit and integration test suites

### Feature Extensions I'm Considering
1. **Multi-language Support**: I'd like to add internationalization for TTS and UI
2. **User Accounts**: I want to implement persistent user preferences and history
3. **Advanced Analytics**: I'm planning portfolio tracking and performance analysis
4. **Mobile App**: I'm considering native iOS/Android applications
5. **Real-time Updates**: I want to add WebSocket integration for live data feeds

## Conclusion

I built Quibittron to demonstrate a sophisticated integration of AI, financial APIs, and communication technologies. My current architecture provides a solid foundation for an AI-powered stock recommendation system, with clear pathways for scaling and feature enhancement. The modular design I chose allows for independent development and deployment of system components while maintaining clean separation of concerns.
