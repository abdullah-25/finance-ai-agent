from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()
    

client = ElevenLabs(
    api_key=os.environ['ELEVEN_LABS_API']
)

response = client.conversational_ai.agents.create(
    name="My conversational agent",
    conversation_config={
        "agent": {
            "prompt": {
                "prompt": "You are a helpful assistant that can answer questions and help with tasks.",
            }
        }
    }
)