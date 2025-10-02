from dotenv import load_dotenv
# from elevenlabs.client import ElevenLabs
# from elevenlabs.play import play
import os
load_dotenv()
# elevenlabs = ElevenLabs(
#   api_key=os.getenv("ELEVEN_LABS_API"),
# )
# audio = elevenlabs.text_to_speech.convert(
#     text="The first move is what sets everything in motion.",
#     voice_id="JBFqnCBsd6RMkjVDRZzb",
#     model_id="eleven_multilingual_v2",
#     output_format="mp3_44100_128",
# )
# play(b"".join(list(audio)))


from agno.agent import Agent
from agno.tools.eleven_labs import ElevenLabsTools

# Create an Agent with the ElevenLabs tool
agent = Agent(tools=[
    ElevenLabsTools(
        api_key=os.getenv("ELEVEN_LABS_API"),
        voice_id="JBFqnCBsd6RMkjVDRZzb", 
        model_id="eleven_multilingual_v2", 
        target_directory="audio_generations"
    )
], name="ElevenLabs Agent")

agent.print_response("Generate a audio summary of the big bang theory", markdown=True)