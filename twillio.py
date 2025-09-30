# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Set environment variables for your credentials
# Read more at http://twil.io/secure

account_sid = os.environ['account_sid']
auth_token = os.environ['auth_token']
TWILLIO_PHONE_NUMBER = os.environ['TWILLIO_PHONE_NUMBER']
client = Client(account_sid, auth_token)

call = client.calls.create(
  url="http://demo.twilio.com/docs/voice.xml",
  to="6473236920",
  from_=TWILLIO_PHONE_NUMBER
)

print(call.sid)