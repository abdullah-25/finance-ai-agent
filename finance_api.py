import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.dataforseo.com/v3/serp/google/finance_markets/live/advanced"

payload="[{\"location_code\":2124, \"language_code\":\"en\", \"market_type\":\"indexes/americas\"}]"
# Get the base64 encoded credentials from environment variables
finance_api_base64 = os.getenv('FINANCE_API_BASE64')
if not finance_api_base64:
    raise ValueError('FINANCE_API_BASE64 environment variable is not set')

headers = {
    'Authorization': f'Basic {finance_api_base64}',
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

response_json = response.json()
if "result" in response_json:
    print(response_json["result"])
else:
    print(response_json)

