# main.py

import argparse
import os
from lumibot.brokers import Alpaca
from lumibot.traders import Trader
from strategies.ten_day_low_strategy import TenDayLowStrategy
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Run trading strategies.')
    parser.add_argument('--strategy', type=str, required=True, help='The strategy to run.')
    args = parser.parse_args()

    # Broker credentials
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
    ALPACA_API_SECRET = os.getenv('ALPACA_API_SECRET')
    ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')

    if not ALPACA_API_KEY or not ALPACA_API_SECRET:
        raise ValueError('Alpaca API credentials not found. Please set them in a .env file or as environment variables.')

    # Initialize the Alpaca broker
    alpaca_creds = {
        "API_KEY": ALPACA_API_KEY,
        "API_SECRET": ALPACA_API_SECRET,
        "BASE_URL": ALPACA_BASE_URL,
        "PAPER": True
    }
    broker = Alpaca(alpaca_creds)

    # Initialize the strategy based on the argument
    if args.strategy.lower() == 'ten_day_low':
        # Specify the list of symbols you want the strategy to trade
        symbols = ["TQQQ"]  # Adjust the symbols as needed

        strategy = TenDayLowStrategy(
            name='TenDayLowStrategy',
            broker=broker,
            parameters={
                "symbols": symbols,
                "cash_allocation": 0.5,  # Adjust as desired (e.g., 50% of your cash)
                "lookback_period": 10,
                "holding_period": 10
            }
        )
    else:
        raise ValueError(f"Unknown strategy specified: {args.strategy}")

    # Create a trader and add the strategy
    trader = Trader()
    trader.add_strategy(strategy)

    # Run the trader
    trader.run_all()

if __name__ == '__main__':
    main()
