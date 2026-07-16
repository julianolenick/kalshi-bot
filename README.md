# Kalshi Trading Bot 🤖

An automated trading bot for the Kalshi prediction market platform that detects whale bets and momentum shifts to execute trades automatically.

## Features

- **Whale Detection**: Tracks large orders (>$5,000) across all markets
- **Momentum Analysis**: Market-specific momentum thresholds for 20+ sports and crypto markets
- **Automated Trading**: Executes trades based on whale activity and/or momentum signals
- **Risk Management**: $5 max per trade, $50 daily loss limit, $200 starting capital
- **Web Dashboard**: Real-time monitoring of bot activity and portfolio
- **24/7 Operation**: Continuously monitors markets

## Quick Start

1. Clone the repo:
```bash
git clone https://github.com/julianolenick/kalshi-bot.git
cd kalshi-bot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment:
```bash
cp .env.example .env
# Edit .env with your Kalshi API key and secret
```

5. Run the bot:
```bash
python backend/app.py
```

6. Open dashboard: `http://localhost:5000`

## Trading Logic

- **Whale bet alone** → $2.50 trade (50% position)
- **Momentum alone** → $2.50 trade (50% position)
- **Both signals** → $5.00 trade (full position)

## Configuration

Edit `backend/config.py` to customize momentum thresholds, trade sizes, and risk limits.

## License

MIT
