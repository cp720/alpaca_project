from lumibot.brokers import Alpaca
from lumibot.traders import Trader
from ten_day_low_strategy import TenDayLowStrategy
import os, argparse
from dotenv import load_dotenv

def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", required=True)
    args = parser.parse_args()

    broker = Alpaca({
        "API_KEY":   os.getenv("ALPACA_API_KEY"),
        "API_SECRET":os.getenv("ALPACA_API_SECRET"),
        "BASE_URL":  os.getenv("ALPACA_BASE_URL"),
        "PAPER":     True
    })

    if args.strategy.lower() == "ten_day_low":
        strat = TenDayLowStrategy(
            name="TenDayLow",
            broker=broker,
            parameters={
                "symbols": ["TQQQ", "SPY", "GOOGL"],
                "cash_allocation": 0.1,
                "lookback_period": 10,
                "holding_period": 10
            }
        )
    else:
        raise ValueError("Unknown strategy")

    trader = Trader()
    trader.add_strategy(strat)
    trader.run_all()

if __name__ == "__main__":
    main()
