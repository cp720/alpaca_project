# strategies/base_strategy.py
import pandas as pd  # For Timedelta and da
# strategies/base_strategy.py
from lumibot.strategies.strategy import Strategy
import logging

class BaseStrategy(Strategy):
    def initialize(self, **kwargs):
        """Initialize common parameters for all strategies."""
        self.symbols = kwargs.get('symbols', [])
        self.cash_allocation = kwargs.get('cash_allocation', 0.1)
        self.logger = self.setup_logger()
        # Any additional common initialization

    def setup_logger(self):
        """Set up logging for the strategy."""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        # Configure logging handlers if needed
        return logger

    def on_trading_iteration(self):
        """Define the core logic of the strategy."""
        raise NotImplementedError("Subclasses should implement this method.")

    def calculate_position_size(self, price, symbol, allocation=None):
        if allocation is None:
            allocation = self.cash_allocation
        cash = self.get_cash()
        # Adjust allocation based on the number of symbols
        adjusted_allocation = allocation / len(self.symbols)
        position_size = int((cash * adjusted_allocation) / price)
        return position_size

    # Add any other general utility methods needed by all strategies



