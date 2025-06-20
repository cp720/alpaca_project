import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.backends.backend_pdf import PdfPages
from dotenv import load_dotenv

# Load API credentials from environment variables
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets/")

# Initialize Alpaca API (for fetching historical data)
api = tradeapi.REST(API_KEY, API_SECRET, base_url=BASE_URL, api_version='v2')

# Set up parameters
symbols = ['AMD', 'PLTR', 'TQQQ', 'CAVA', 'AMZN', 'GOOGL', 'WMT', 'SPY']

all_trade_records = []

pdf_pages = PdfPages('trading_report.pdf')

fig, ax = plt.subplots(figsize=(12, 6))

for symbol in symbols:

    start_date = '2022-12-01'
    end_date = '2024-09-25'
    holding_period = 35

    # Initial capital for backtesting
    initial_cash = 100000  # $100,000
    cash = initial_cash
    position = 0  # Number of shares held
    entry_price = 0
    holding_days = 0

    # Fetch historical data
    data = api.get_bars(symbol, '1Day', start=start_date, end=end_date).df

    # Compute indicators
    data['MA50'] = data['close'].rolling(window=50).mean()
    data['MA200'] = data['close'].rolling(window=200).mean()
    data['10d_low'] = data['close'].rolling(window=10).min()
    data['10d_high'] = data['close'].rolling(window=10).max()

    # Drop rows with NaN values (from rolling calculations)
    data.dropna(inplace=True)

    # Initialize columns for backtesting
    data['position'] = 0  # 1 for holding the stock, 0 for not holding
    data['cash'] = cash
    data['portfolio_value'] = cash
    data['holding_days'] = 0
    data['symbol'] = symbol

    # Add these lists before the backtesting loop
    buy_dates = []
    sell_dates = []
    trade_records = []

    for idx in range(len(data)):
        current_price = data['close'].iloc[idx]
        MA50 = data['MA50'].iloc[idx]
        MA200 = data['MA200'].iloc[idx]
        ten_day_low = data['10d_low'].iloc[idx]
        ten_day_high = data['10d_high'].iloc[idx]

        # Check if currently holding the position
        if position == 0:
            # Buy conditions
            if (current_price <= ten_day_low) and (current_price >= MA50) and (current_price >= MA200):
                # Calculate quantity to buy (10% of cash balance)
                quantity_to_buy = int((cash * 0.3) / current_price)
                if quantity_to_buy > 0:
                    position = quantity_to_buy
                    entry_price = current_price
                    cash -= position * current_price  # Update cash balance
                    holding_days = 0
                    print(f"Buying {position} shares at ${current_price:.2f} on {data.index[idx].date()}")
                    buy_dates.append(data.index[idx])  # Add this line
                    trade_records.append({
                        'Date': data.index[idx].date(),
                        'Action': 'Buy',
                        'Price': current_price,
                        'Quantity': position,
                        'Total': position * current_price,
                        'MA50': MA50,
                        'MA200': MA200,
                        'Ten_Day_Low': ten_day_low,
                        'Ten_Day_High': ten_day_high,
                        'Symbol': symbol  # Add the symbol to the trade record
                    })
        else:
            # Increment holding days
            holding_days += 1
            # Sell conditions
            if (current_price >= ten_day_high) or (current_price < MA50) or (holding_days > holding_period):
                cash += position * current_price  # Update cash balance
                print(f"Selling {position} shares at ${current_price:.2f} on {data.index[idx].date()}")
                
                sell_dates.append(data.index[idx])  # Add this line
                trade_records.append({
                    'Date': data.index[idx].date(),
                    'Action': 'Sell',
                    'Price': current_price,
                    'Quantity': position,
                    'Total': position * current_price,
                    'MA50': MA50,
                    'MA200': MA200,
                    'Ten_Day_Low': ten_day_low,
                    'Ten_Day_High': ten_day_high,
                    'Symbol': symbol  # Add the symbol to the trade record
                })
                position = 0
                holding_days = 0

        # Update position and cash in DataFrame
        data['position'].iloc[idx] = position
        data['cash'].iloc[idx] = cash
        # Calculate portfolio value
        data['portfolio_value'].iloc[idx] = cash + position * current_price
        data['holding_days'].iloc[idx] = holding_days

    all_trade_records.extend(trade_records)

    # Plot the portfolio value for the current symbol
    ax.plot(data.index, data['portfolio_value'], label=f'{symbol} Portfolio Value')
    ax.scatter(buy_dates, data.loc[buy_dates, 'portfolio_value'], color='green', marker='^', label=f'{symbol} Buy', alpha=0.7)
    ax.scatter(sell_dates, data.loc[sell_dates, 'portfolio_value'], color='red', marker='v', label=f'{symbol} Sell', alpha=0.7)


# Create a DataFrame from all trade records
trade_df = pd.DataFrame(all_trade_records)

# Round numeric columns to 2 decimal places for better readability
numeric_columns = ['Price', 'Total', 'MA50', 'MA200', 'Ten_Day_Low', 'Ten_Day_High']
trade_df[numeric_columns] = trade_df[numeric_columns].round(2)

#finalize graph
ax.set_title('Portfolio Value Over Time')
ax.set_xlabel('Date')
ax.set_ylabel('Portfolio Value ($)')
ax.legend()
ax.grid(True)

# Save the graph to the PDF
pdf_pages.savefig(fig)

# Create a new figure for the table
fig, ax = plt.subplots(figsize=(16, 4))
ax.axis('tight')
ax.axis('off')
table = ax.table(cellText=trade_df.values, colLabels=trade_df.columns, cellLoc='center', loc='center')

# Adjust table style
table.auto_set_font_size(False)
table.set_fontsize(7)  # Reduced font size to fit more columns
table.scale(1.2, 1.2)

# Save the table to the PDF
pdf_pages.savefig(fig, bbox_inches='tight')

# Close the PDF file
pdf_pages.close()

print("Trading report saved as 'trading_report.pdf'")

# Display the graph (optional, if you want to see it immediately)
plt.show()

# Print the trade records table (optional, for console output)
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Don't wrap to multiple lines
print(trade_df.to_string(index=False))

# Calculate performance metrics
total_return = (data['portfolio_value'].iloc[-1] - initial_cash) / initial_cash * 100
print(f"\nTotal Return: {total_return:.2f}%")
