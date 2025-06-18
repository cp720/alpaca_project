import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient
from datetime import datetime, timedelta
from utils.trading_utils import calculate_position_size
import pandas as pd
import os
import time 
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_API_SECRET')

BASE_URL = "https://paper-api.alpaca.markets/"

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, base_url=BASE_URL, api_version='v2')
# Initialize Alpaca client
client = TradingClient(API_KEY, API_SECRET, paper=True)

# get acount information
account = client.get_account()
# get cash balance
cash_balance = float(account.cash)

print(f"Available cash: ${cash_balance:.2f}")

# Set up parameters
symbols = ['TQQQ', 'SPY', 'GOOGL']

try:
   while True:  # Infinite loop to keep the program running
      
      #get dates
      end_date = "2024-09-27"
      start_date = "2024-01-01"

      for symbol in symbols:

         holding_period = 10
         holding_days = 0
         entry_price = 0

         # Fetch data
         data = api.get_bars(symbol, '1Day', start=start_date, end=end_date).df
         data['MA50'] = data['close'].rolling(window=50).mean()
         data['MA200'] = data['close'].rolling(window=200).mean()
         data['10d_low'] = data['close'].rolling(window=10).min()
         data['10d_high'] = data['close'].rolling(window=10).max()

         current_price = data['close'].iloc[-1]
         MA50 = data['MA50'].iloc[-1]
         MA200 = data['MA200'].iloc[-1]
         ten_day_low = data['10d_low'].iloc[-1]
         ten_day_high = data['10d_high'].iloc[-1]

         # First get all the positions into a dataframe indexed by symbol
         my_positions = api.list_positions()
         #print( my_positions)
         my_positions_df = pd.DataFrame([position._raw for position in my_positions])
         my_positions_df.set_index('symbol', inplace=True)
         #print(my_positions_df.head(10))
         # Then check if a particular stock is in the index
         if symbol in my_positions_df.index:
               position_exists = True
               qty = float(my_positions_df.at[symbol, 'qty'])
               #print(qty)
         else:
               position_exists = False
               qty = 0

         if not position_exists or qty == 0:
               print("Buy conditions apply")
               if (current_price <= ten_day_low) and (current_price >= MA50) and (current_price >= MA200):
                  quantity_to_buy = calculate_position_size(current_price, 0.1, cash_balance)
                  print(f"Quantity to Buy: ${quantity_to_buy:.2f}")
                  if quantity_to_buy > 0: #if there is enough cash to buy
                     try:
                           order = client.submit_order(
                              symbol = symbol,
                              qty = quantity_to_buy,
                              side = 'buy',
                              type = 'market',
                              time_in_force = 'gtc'
                           )
                           print(f"Buy order placed for {quantity_to_buy} shares of {symbol}")
                           holding_days = 0
                           entry_price = current_price

                     except Exception as e:
                           print(f"Error placing buy order: {e}")
         else:
               #increment holding days
               holding_days = holding_days + 1
               # Sell condition
               if (current_price >= ten_day_high) or (current_price < MA50) or (holding_days > holding_period):
                  try:
                     order = client.close_position(symbol)
                     print(f"Sell order placed to close entire position of {symbol}")
                     holding_days = 0
                  except Exception as e:
                     print(f"Error closing position: {e}")
               print(symbol + " position exists - Sell conditions apply")

         print("Successful Run")

      # Sleep for a specified duration (e.g., 60 seconds) before the next iteration
      time.sleep(36000)  # Adjust the sleep duration as needed
except KeyboardInterrupt:
    print("\nProgram terminated by user")
