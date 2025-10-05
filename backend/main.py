import os
import requests
import time
from dotenv import load_dotenv
import elevenlabs

from agno.agent import Agent
from agno.tools import tool
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.workflow.types import StepInput, StepOutput
from agno.workflow.workflow import Workflow
from server import call_and_collect

load_dotenv(override=True)


def read_manager_phone_from_json(json_path: str = "senior_manager.json") -> str:
    """Get manager phone number - currently hardcoded"""
    return "+16473236920"


def get_user_input(step_input: StepInput) -> StepOutput:
    """Step 1: Get user input via API parameters"""
    user_query = input('how can I help you today? \n')
    return StepOutput(content=user_query)


def prepare_api_input(step_input: StepInput) -> StepOutput:
    """Step 2: Prepare input for API agent"""
    user_query = step_input.previous_step_content
    
    prompt = f"""
    You are a precise market analyst. Call the tool `custom_api_function` exactly once with this query:
    "{user_query}"

       After the call, do the following:

       1) Parse the API response and build a list of candidates with fields:
            - symbol (ticker)
            - name
            - last_price (if available)
            - change_percent (preferred: changePercent, percent_change, pct_change; 
            otherwise compute as (last_price - previous_close) / previous_close * 100 if those fields exist)

       2) Definition of positive performance:
            - change_percent > 0.

       3) Pick the TOP 3 by highest change_percent.
            - Tie-breakers in order: higher volume, then higher market cap, then alphabetical by symbol.
            - Only use symbols that actually appear in the API response. Do not invent anything.

       4) Output format:
            
                I have found { '{' }COUNT{ '}' } stocks with the most potential:
                    1 - <NAME_1> (<SYMBOL_1>)
                    2 - <NAME_2> (<SYMBOL_2>)
                    3 - <NAME_3> (<SYMBOL_3>)

      Rules:
    
        - If fewer than 3 positive stocks exist, set COUNT accordingly and list only that many lines.
        - Round change_percent to one decimal place when shown.
        - Be concise. No JSON. No code fences. No extra commentary beyond the table and the final line.
    """

    return StepOutput(content=prompt)
    

@tool
def custom_api_function(query: str = "") -> str:
    """Call Google finance market API via DataForSEO"""
    url = "https://api.dataforseo.com/v3/serp/google/finance_markets/live/advanced"
    payload = '[{"location_code":2124, "language_code":"en", "market_type":"indexes/americas"}]'
    finance_api_base64 = os.getenv('FINANCE_API_BASE64')

    headers = {
        'Authorization': f'Basic {finance_api_base64}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response_json = response.json()
        
        # Navigate to the correct data structure
        if "tasks" in response_json:
            task_result = response_json["tasks"][0].get("result", [])
            if len(task_result) > 0:
                first_result = task_result[0]
                items = first_result.get('items', [])
                
                # Extract individual stocks from the 'interested' section
                trending_stocks = []
                for item in items:
                    if item.get('type') == 'google_finance_interested':
                        for stock_item in item.get('items', []):
                            if stock_item.get('type') == 'google_finance_market_instrument_element':
                                stock_info = {
                                    'symbol': stock_item.get('ticker'),
                                    'name': stock_item.get('displayed_name'),
                                    'price': stock_item.get('price'),
                                    'price_change': stock_item.get('price_delta'),
                                    'percentage_change': stock_item.get('percentage_delta'),
                                    'trend': stock_item.get('trend')
                                }
                                trending_stocks.append(stock_info)
                
                return {
                    "status": "success",
                    "timestamp": first_result.get('datetime', ''),
                    "trending_stocks": trending_stocks,
                    "total_stocks_found": len(trending_stocks)
                }
        
        return {"status": "error", "message": "No data found"}
    except Exception as e:
        return f"API call failed: {str(e)}"


def summarize_tts_input(step_input: StepInput) -> StepOutput:
    """Step 3.1: Prepare summarized input for ElevenLabs TTS tool"""
    api_results = step_input.previous_step_content
    
    prompt = f"""
    Call summarizer_agent exactly once to summarize text below:
    
    "{api_results.strip()}"
    
    After summarizing text, return that summary ONLY.
    """
    
    return StepOutput(content=prompt.strip())
    
       
def prepare_tts_input(step_input: StepInput) -> StepOutput:
    """Step 4: Prepare input for ElevenLabs TTS tool"""
    summary_results = step_input.previous_step_content
    
    prompt = f"""
    Use the custom_elevenlabs_tts tool to convert this text to audio:
    
    "{summary_results}"
    
    After generating the audio, return ONLY the file path to the generated audio file, nothing else.
    """
    
    return StepOutput(content=prompt.strip())
    

@tool
def custom_elevenlabs_tts(text: str = "") -> str:
    """Generate audio using ElevenLabs client directly"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    # Clean text for TTS (remove markdown formatting)
    clean_text = text.replace("**", "").replace("|", "").replace("\n", " ").strip()
    
    try:
        from elevenlabs import ElevenLabs
        client = ElevenLabs(api_key=api_key)
        
        audio_generator = client.text_to_speech.convert(
            text=clean_text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        # Create filename with timestamp
        timestamp = int(time.time())
        filename = f"audio_generations/tts_{timestamp}.mp3"
        
        # Save audio file
        os.makedirs("audio_generations", exist_ok=True)
        
        with open(filename, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)
        
        # Return absolute path
        abs_path = os.path.abspath(filename)
        return abs_path
        
    except Exception as e:
        return f"Error: Failed to generate audio: {str(e)}"
        

def prepare_phone_input(step_input: StepInput) -> StepOutput:
    """Step 6: Prepare input for phone agent using TTS result as the message"""
    phone_number = read_manager_phone_from_json("senior_manager.json") 
    if not phone_number:
        phone_number = "+16473236920"

    tts_result = step_input.previous_step_content

    prompt = f"""
    Make a phone call to {phone_number} using the twilio_function.

    Use these parameters:
    - phone_number: {phone_number}
    - message: {tts_result}

    The message comes from the ElevenLabs TTS result.
    """

    return StepOutput(content=prompt.strip())


@tool
def twilio_function(message: str = "") -> str:
    """Make a phone call using Twilio API and collect user input"""
    receiver_number = read_manager_phone_from_json("senior_manager.json")
    if not receiver_number:
        receiver_number = "+16473236920"

    try:
        digit = call_and_collect(
            receiver_number,  
            message,
            timeout_sec=45
        )
        return f"User pressed: {digit}"
    except Exception as e:
        return f"Phone call failed: {str(e)}"
        

def handle_approval_step(step_input: StepInput) -> StepOutput:
    """Step 8: Handle approval response and return final result"""
    twilio_result = step_input.previous_step_content
    
    if "1" in twilio_result:
        final_message = "Even the senior manager thinks this is a great idea!"
    else:
        final_message = "Sorry, I can't help them today"
    
    return StepOutput(content=final_message)

# Define agents
api_agent = Agent(
    name="API Agent",
    model=Claude(id="claude-sonnet-4-0"),
    tools=[custom_api_function],
    role="Fetch data from external APIs based on user queries",
)

summarizer_agent = Agent(
    name="Summary Agent",
    model=Claude(id="claude-sonnet-4-0"),
    role="Summarize information into 1 or two sentences",
)

tts_agent = Agent(
    name="TTS Agent", 
    model=Claude(id="claude-sonnet-4-0"),
    tools=[custom_elevenlabs_tts],
    role="You are an AI agent that can generate audio using the ElevenLabs API.",
    instructions=[
        "When the user asks you to generate audio, use the 'custom_elevenlabs_tts' tool to convert text to audio.",
        "After generating audio successfully, return ONLY the full path to the generated audio file.",
        "The audio should be short and concise for phone calls.",
        "Do not include any other text in your response - only the file path."
    ]
)

phone_agent = Agent(
    name="Phone Agent",
    model=Claude(id="claude-sonnet-4-0"),
    tools=[twilio_function],
    role="Make phone calls and handle user responses",
)

approval_agent = Agent(
    name="Approval Agent",
    model=Claude(id="claude-sonnet-4-0"),
    role="Handle approval logic and return final results",
)


# Create workflow (available for import)
approval_workflow = Workflow(
    name="AI stocks picker Workflow",
    description="Get user input, call API, create speech, make phone call, and handle approval",
    db=SqliteDb(
        session_table="approval_workflow_session",
        db_file="tmp/approval_workflow.db",
    ),
    steps=[
        get_user_input,      # Step 1: Get CLI input from user
        prepare_api_input,   # Step 2: Prepare API input
        api_agent,           # Step 3: Call API using custom tool
        summarizer_agent,    # step 3.1: Summarize text
        prepare_tts_input,   # Step 4: Prepare TTS input
        tts_agent,           # Step 5: Convert to speech
        prepare_phone_input, # Step 6: Prepare phone input
        phone_agent,         # Step 7: Make phone call
        handle_approval_step # Step 8: Handle approval and return result
    ],
)

if __name__ == "__main__":
    result = approval_workflow.run()
    print("\n=== Workflow Result ===")
    print(result)
