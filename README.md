# Quibittron - AI Stock Recommendation System

An intelligent stock recommendation system that uses AI to analyze market data, generate audio summaries via ElevenLabs TTS, and makes phone calls through Twilio to get approval from a senior manager.

## Architecture Overview

### Backend (Python Flask)
- **Framework**: Flask with CORS support
- **AI Agent Framework**: Agno with Claude Sonnet 4.0
- **APIs Integrated**:
  - DataForSEO Google Finance API for market data
  - ElevenLabs for text-to-speech conversion
  - Twilio for phone calls and DTMF input collection
- **Database**: SQLite for workflow session management

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter
- **UI Components**: Radix UI with Tailwind CSS
- **Build Tool**: Vite
- **Server**: Express.js for development

## System Workflow

1. **User Input**: User asks for stock recommendations via chat interface
2. **API Analysis**: System calls Google Finance API to get market data
3. **AI Processing**: Claude analyzes data and picks top 3 performing stocks
4. **Text Summarization**: AI creates a concise summary of recommendations
5. **Audio Generation**: ElevenLabs converts summary to speech
6. **Phone Call**: Twilio calls senior manager to play audio and collect approval (1=yes, any other=no)
7. **Final Response**: System returns approval status to user

## Project Structure

```
quibittron/
├── backend/                 # Python Flask backend
│   ├── main.py             # Core workflow and agents
│   ├── server.py           # Flask server with Twilio webhooks
│   ├── requirements.txt    # Python dependencies
│   └── senior_manager.json # Manager contact info
├── frontend/               # React TypeScript frontend
│   ├── client/            # React app source
│   │   ├── src/
│   │   │   ├── App.tsx    # Main app component
│   │   │   ├── pages/ChatPage.tsx  # Chat interface
│   │   │   └── components/ # UI components
│   │   └── index.html     # HTML entry point
│   ├── server/            # Express development server
│   └── package.json       # Node.js dependencies
└── README.md              # This file
```

## Prerequisites

- Python 3.8+
- Node.js 18+
- ngrok account (for webhook tunneling)
- API Keys:
  - DataForSEO (Google Finance API)
  - ElevenLabs (Text-to-Speech)
  - Twilio (Phone calls)
  - Anthropic Claude API

## Environment Variables

Create a `.env` file in the backend directory with:

```env
# DataForSEO API
FINANCE_API_BASE64=your_dataforseo_base64_credentials

# ElevenLabs API
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Twilio API
account_sid=your_twilio_account_sid
auth_token=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key

# Ngrok webhook URL (update after starting ngrok)
BASE_URL=https://your-ngrok-subdomain.ngrok-free.app
```

## Local Setup with ngrok

### Step 1: Install Dependencies

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend Setup
```bash
cd frontend
npm install
```

### Step 2: Install and Setup ngrok

1. **Install ngrok**:
   ```bash
   # macOS with Homebrew
   brew install ngrok/ngrok/ngrok
   
   # Or download from https://ngrok.com/download
   ```

2. **Authenticate ngrok**:
   ```bash
   ngrok config add-authtoken YOUR_NGROK_AUTH_TOKEN
   ```

### Step 3: Start ngrok Tunnel

```bash
# Start ngrok tunnel for backend (port 3000)
ngrok http 3000
```

**Important**: Copy the HTTPS URL from ngrok output (e.g., `https://abc123.ngrok-free.app`) and update the `BASE_URL` in your `.env` file.

### Step 4: Update Senior Manager Contact

Edit `backend/senior_manager.json` with the phone number for approval calls:
```json
{
  "phone": "+1234567890"
}
```

### Step 5: Start the Applications

#### Terminal 1 - Backend Server
```bash
cd backend
python server.py
```
The backend will start on `http://localhost:3000`

#### Terminal 2 - Frontend Development Server
```bash
cd frontend
npm run dev
```
The frontend will start on `http://localhost:3000` (Express server)

#### Terminal 3 - Keep ngrok Running
Keep the ngrok tunnel active to receive Twilio webhooks.

### Step 6: Test the Application

1. **Open Browser**: Navigate to `http://localhost:3000`
2. **Send Message**: Ask "Which stocks should I buy today?"
3. **Watch Workflow**:
   - AI fetches market data
   - Generates top 3 stock recommendations
   - Creates audio summary
   - Calls senior manager for approval
   - Returns final decision

## API Endpoints

### Backend Endpoints
- `GET /my-api/agent` - Run workflow directly
- `POST /api/chat` - Chat interface endpoint
- `POST /voice` - Twilio voice webhook
- `POST /gather` - Twilio DTMF input handler
- `GET /audio/<filename>` - Serve generated audio files

### Frontend Routes
- `/` - Main chat interface

## Key Components

### Backend Components
- **Workflow Engine**: Multi-step AI agent pipeline
- **API Integration**: Google Finance data fetching
- **Audio Generation**: ElevenLabs TTS integration
- **Phone System**: Twilio call management with DTMF collection
- **Webhook Handlers**: TwiML response generation

### Frontend Components
- **ChatPage**: Main chat interface
- **ChatInput**: Message input with send functionality
- **ChatMessage**: Message display component
- **LoadingDots**: Loading indicator

## Troubleshooting

### ngrok Issues
- Ensure ngrok is authenticated and running
- Update `BASE_URL` in `.env` when ngrok URL changes
- Verify webhook URLs in Twilio console match ngrok URL

### API Connection Issues
- Check all API keys are valid and properly set
- Verify backend is running on port 3000
- Ensure frontend is pointing to correct backend URL

### Twilio Call Issues
- Verify phone number format (E.164: +1234567890)
- Check Twilio account balance
- Ensure webhook URLs are publicly accessible via ngrok

### Audio Generation Issues
- Check ElevenLabs API key and quota
- Verify `audio_generations/` directory is writable
- Ensure sufficient disk space for audio files

## Production Deployment Notes

1. **Security**: Add proper authentication and API rate limiting
2. **Scaling**: Consider using Redis for session storage
3. **Monitoring**: Implement logging and error tracking
4. **SSL**: Use proper SSL certificates instead of ngrok
5. **Database**: Migrate to PostgreSQL for production
6. **Environment**: Use environment-specific configuration files

## License

This project is licensed under the MIT License.