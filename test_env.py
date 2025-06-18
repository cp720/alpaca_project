import os
from dotenv import load_dotenv

load_dotenv()

ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_API_SECRET = os.getenv('ALPACA_API_SECRET')

if not ALPACA_API_KEY or not ALPACA_API_SECRET:
    print("Error: API credentials not found.")
else:
    print("API credentials loaded successfully.")