from agno.agent import Agent
from agno.tools import tool
import requests
import os
from typing import List, Dict
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

from agno.models.anthropic import Claude
LLM = Claude(id="claude-sonnet-4-0")

class StockPick(BaseModel):
    symbol: str
    name: str
    rationale: str
    confidence: int = Field(ge=1, le=100)

class Top3(BaseModel):
    picks: List[StockPick]


@tool(
    name="finance_api_search",                
    description="Get current market data including trending stocks and market indices",  
)
def finance_api_search(query: str) -> Dict:
    """Get current market data including trending individual stocks."""
    url = "https://api.dataforseo.com/v3/serp/google/finance_markets/live/advanced"

    payload="[{\"location_code\":2124, \"language_code\":\"en\", \"market_type\":\"indexes/americas\"}]"
    
    finance_api_base64 = os.getenv('FINANCE_API_BASE64')
    if not finance_api_base64:
        raise ValueError('FINANCE_API_BASE64 environment variable is not set')

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
        
        return {"status": "error", "message": "No data found in API response"}
        
    except Exception as e:
        return {"status": "error", "message": f"API call failed: {str(e)}"}

@tool(
    name="twilio_call_user",                
    description="call using twillion api",  
)
def twilio_call_user(user_phone: str, top3: Dict) -> str:
    account_sid = os.environ['account_sid']
    auth_token = os.environ['auth_token']
    TWILLIO_PHONE_NUMBER = os.environ['TWILLIO_PHONE_NUMBER']
    client = Client(account_sid, auth_token)

    call = client.calls.create(
    url="http://demo.twilio.com/docs/voice.xml",
    to="6473236920", # my phone number
    from_=TWILLIO_PHONE_NUMBER
    )

    return call.sid

agent = Agent(
    model=LLM,
    tools=[finance_api_search, twilio_call_user],
    output_schema=Top3,     # forces JSON with picks/confidence/rationale
    markdown=True
)

user_question = "Recommend me 5 stocks to buy today"

agent.print_response(f"""User asked: {user_question}

Call finance_api_search to get current trending stocks data.
The function returns a structured response with a 'trending_stocks' array containing individual stock information.
Each stock has: symbol, name, price, price_change, percentage_change, and trend.

Analyze the trending stocks and select the number of stocks the user requested with:
- Positive trend ('up')
- Good percentage gains
- Well-known companies
- Strong recent performance

You MUST return your response as valid JSON in this exact format:
{{
  "picks": [
    {{"symbol": "STOCK_SYMBOL", "rationale": "reason for recommendation", "confidence": score}},
    {{"symbol": "STOCK_SYMBOL", "rationale": "reason for recommendation", "confidence": score}}
    // ... return exactly the number of stocks the user requested
  ]
}}

If you cannot find enough good stock picks, return as many as you can find, or return:
{{
  "picks": []
}}

Do not return any text outside of this JSON structure.""", stream=True)
