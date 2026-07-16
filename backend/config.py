"""
Configuration file for the Kalshi Trading Bot
Adjust these settings to customize bot behavior
"""

import os
from dotenv import load_dotenv

load_dotenv()

# =======================
# API Configuration
# =======================
KALSHI_API_KEY = os.getenv('KALSHI_API_KEY')
KALSHI_API_SECRET = os.getenv('KALSHI_API_SECRET')
KALSHI_BASE_URL = 'https://api.kalshi.com/v1'

# =======================
# Trading Configuration
# =======================

# Risk Management
STARTING_CAPITAL = 200.0  # Initial bankroll in dollars
MAX_TRADE_SIZE = 5.0  # Maximum bet per trade
MIN_TRADE_SIZE = 2.5  # Minimum bet per trade (50% position)
DAILY_LOSS_LIMIT = 50.0  # Stop trading if daily loss exceeds this

# Whale Detection
WHALE_THRESHOLD = 5000.0  # Orders larger than this are whales (in dollars)

# Momentum Detection Thresholds (% change in 5 minutes)
MOMENTUM_THRESHOLDS = {
    'nfl_live': 12.0,
    'nba_live': 10.0,
    'mlb_live': 8.0,
    'nhl_live': 10.0,
    'soccer_live': 8.0,
    'tennis_live': 12.0,
    'ncaa_basketball': 11.0,
    'ncaa_football': 13.0,
    'crypto_btc': 5.0,
    'crypto_eth': 5.0,
    'default': 10.0
}

MOMENTUM_LEVELS = {
    'nfl_live': {'base': 8.0, 'strong': 12.0, 'extreme': 18.0},
    'nba_live': {'base': 6.0, 'strong': 10.0, 'extreme': 15.0},
    'mlb_live': {'base': 5.0, 'strong': 8.0, 'extreme': 12.0},
    'nhl_live': {'base': 6.0, 'strong': 10.0, 'extreme': 15.0},
    'soccer_live': {'base': 5.0, 'strong': 8.0, 'extreme': 12.0},
    'tennis_live': {'base': 8.0, 'strong': 12.0, 'extreme': 18.0},
    'ncaa_basketball': {'base': 7.0, 'strong': 11.0, 'extreme': 16.0},
    'ncaa_football': {'base': 8.0, 'strong': 13.0, 'extreme': 18.0},
    'crypto_btc': {'base': 3.0, 'strong': 5.0, 'extreme': 8.0},
    'crypto_eth': {'base': 3.0, 'strong': 5.0, 'extreme': 8.0},
    'default': {'base': 7.0, 'strong': 10.0, 'extreme': 15.0}
}

# Market monitoring interval (in seconds)
MARKET_CHECK_INTERVAL = 5

# Price history window for momentum calculation (in minutes)
MOMENTUM_WINDOW = 5

# =======================
# Server Configuration
# =======================
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
DEBUG = os.getenv('DEBUG', 'True') == 'True'
BOT_ENVIRONMENT = os.getenv('BOT_ENVIRONMENT', 'development')

# =======================
# Database
# =======================
DATABASE_PATH = 'kalshi_bot.db'
