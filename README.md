This repository contains a minimal example of algorithmic trading strategies built with
[Alpaca](https://alpaca.markets/) and the `lumibot` framework. The `main.py` script launches
trading strategies that rely on credentials provided through environment variables.

## Prerequisites
- Python 3.8+
- An Alpaca brokerage account
- Dependencies listed in [`requirements.txt`](requirements.txt)

Install the requirements with:

```bash
pip install -r requirements.txt
```
## Configuration

Create a `.env` file in the project root with your Alpaca API credentials:

```bash
ALPACA_API_KEY=your_key
ALPACA_API_SECRET=your_secret
# Optional: override the default paper trading URL
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

`python-dotenv` loads these values when `main.py` runs.

## Usage

Run the ten day low strategy:

```bash
python main.py --strategy ten_day_low
```

Logs and settings files are saved under the `logs/` directory.

## Directory Layout

```
.
├── main.py               # Entrypoint for running strategies
├── strategies/           # Base strategy classes
├── ten_day_low_strategy.py   # E strategy script
├── utils/                # Helper utilities
├── requirements.txt      # Python dependencies
└── logs/                 # Generated log files
```

## Disclaimer

This code is provided for educational purposes only. 

