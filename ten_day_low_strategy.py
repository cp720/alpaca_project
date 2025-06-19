# ten_day_low_strategy.py
from lumibot.traders import Strategy
from datetime import datetime, timedelta
from utils.trading_utils import calculate_position_size
import pandas as pd

class TenDayLowStrategy(Strategy):
    def initialize(self):
        self.symbols = self.parameters["symbols"]
        self.cash_allocation = self.parameters["cash_allocation"]
        self.lookback = self.parameters["lookback_period"]
        self.holding_period = self.parameters["holding_period"]

    def on_trading_iteration(self):
        for symbol in self.symbols:
            self._evaluate_and_trade(symbol)

    def _evaluate_and_trade(self, symbol):
        data = self.broker.get_historical_data(
            symbol,
            timeframe="1Day",
            start=self.now - timedelta(days=365),
            end=self.now
        ).df

        data["MA50"] = data["close"].rolling(50).mean()
        data["MA200"] = data["close"].rolling(200).mean()
        data["10d_low"]= data["close"].rolling(self.lookback).min()
        data["10d_high"]=data["close"].rolling(self.lookback).max()

        price = data["close"].iloc[-1]
        ma50 = data["MA50"].iloc[-1]
        ma200 = data["MA200"].iloc[-1]
        low10 = data["10d_low"].iloc[-1]
        high10 = data["10d_high"].iloc[-1]

        position = self.broker.get_position(symbol)
        qty = position.qty if position else 0

        # Buy
        if not position and price <= low10 and price >= ma50 and price >= ma200:
            qty_to_buy = calculate_position_size(price, self.cash_allocation, self.broker.cash)
            if qty_to_buy > 0:
                self.buy(symbol, qty_to_buy)

        # Sell
        elif position:
            days_held = (self.now - position.entry_time).days
            if price >= high10 or price < ma50 or days_held > self.holding_period:
                self.close_position(symbol)
