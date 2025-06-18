import alpaca_trade_api as tradeapi
import pandas as pd
from alpaca.trading.client import TradingClient
from datetime import datetime, timedelta
from utils.trading_utils import calculate_position_size
import os
import time 
from dotenv import load_dotenv

api_key =  os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_API_SECRET')
base_url = 'https://paper-api.alpaca.markets' # paper trading endpoint

api = tradeapi.REST(api_key, api_secret, base_url, api_version= 'v2')

client = TradingClient(api_key, api_secret, paper=True)

# get acount information
account = client.get_account()
