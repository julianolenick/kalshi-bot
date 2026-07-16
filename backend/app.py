"""
Kalshi Trading Bot - Main Application
Flask web server that runs the bot and serves the dashboard
"""

from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import FLASK_HOST, FLASK_PORT, DEBUG, MARKET_CHECK_INTERVAL
from kalshi_api import KalshiAPI
from detector import SignalDetector
from trader import TradeExecutor
from risk_manager import RiskManager
from database import Database

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend')

# Initialize bot components
api = KalshiAPI()
detector = SignalDetector()
trader = TradeExecutor()
risk_manager = RiskManager()
db = Database()

# Bot state
bot_state = {
    'running': False,
    'last_check': None,
    'markets_monitored': 0,
    'signals_detected': 0,
    'trades_executed': 0
}

# ========================
# API ENDPOINTS
# ========================

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current bot status and metrics"""
    stats = db.get_bot_stats()
    risk_metrics = risk_manager.get_risk_metrics()
    
    return jsonify({
        'bot_running': bot_state['running'],
        'last_check': bot_state['last_check'],
        'markets_monitored': bot_state['markets_monitored'],
        'signals_detected': bot_state['signals_detected'],
        'trades_executed': stats['trade_count'],
        'total_pnl': stats['total_pnl'],
        'daily_pnl': stats['daily_pnl'],
        'available_capital': stats['capital_remaining'],
        'risk_metrics': risk_metrics
    })

@app.route('/api/trades')
def get_trades():
    """Get recent trades"""
    limit = request.args.get('limit', 50, type=int)
    trades = db.get_trades(limit)
    return jsonify(trades)

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    bot_state['running'] = True
    return jsonify({'success': True, 'message': 'Bot started'})

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    bot_state['running'] = False
    return jsonify({'success': True, 'message': 'Bot stopped'})

@app.route('/api/bot/config')
def get_config():
    """Get current bot configuration"""
    from config import (
        STARTING_CAPITAL, MAX_TRADE_SIZE, DAILY_LOSS_LIMIT,
        WHALE_THRESHOLD, MOMENTUM_WINDOW, MOMENTUM_THRESHOLDS
    )
    
    return jsonify({
        'starting_capital': STARTING_CAPITAL,
        'max_trade_size': MAX_TRADE_SIZE,
        'daily_loss_limit': DAILY_LOSS_LIMIT,
        'whale_threshold': WHALE_THRESHOLD,
        'momentum_window': MOMENTUM_WINDOW,
        'momentum_thresholds': MOMENTUM_THRESHOLDS
    })

# ========================
# BOT MONITORING LOOP
# ========================

def monitor_markets():
    """
    Main bot loop - runs periodically to check markets for signals
    This is the heart of the trading bot
    """
    
    if not bot_state['running']:
        return
    
    try:
        # Get all active markets
        markets = api.get_markets()
        
        if not markets:
            print("No markets available")
            return
        
        bot_state['markets_monitored'] = len(markets)
        bot_state['last_check'] = datetime.now().isoformat()
        
        # Check each market for signals
        for market in markets:
            market_id = market.get('id')
            market_name = market.get('name')
            current_price = market.get('price')
            
            if not market_id or current_price is None:
                continue
            
            # Log price for momentum calculation
            db.log_price(market_id, market_name, current_price)
            
            # Get order book to detect whales
            order_book = api.get_order_book(market_id)
            whale_signal = detector.detect_whale_bet(
                {'id': market_id, 'name': market_name},
                order_book
            )
            
            # Get price history for momentum detection
            # In production, would retrieve from database
            # For now, we'll create a minimal history
            price_history = [
                {'price': current_price, 'timestamp': datetime.now()}
            ]
            
            momentum_signal = detector.detect_momentum(
                market_id,
                market_name,
                current_price,
                price_history
            )
            
            # Evaluate combined signals
            trade_signal = detector.evaluate_trade_signal(
                whale_signal,
                momentum_signal
            )
            
            # Execute trade if signals warrant it
            if trade_signal.get('should_trade'):
                bot_state['signals_detected'] += 1
                trade_result = trader.execute_trade(
                    market_id,
                    market_name,
                    trade_signal,
                    current_price
                )
                
                if trade_result.get('success'):
                    bot_state['trades_executed'] += 1
                    print(f"Trade executed: {trade_result['message']}")
    
    except Exception as e:
        print(f"Error in market monitoring: {e}")

# ========================
# SCHEDULER SETUP
# ========================

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=monitor_markets,
    trigger="interval",
    seconds=MARKET_CHECK_INTERVAL,
    id='market_monitor',
    name='Monitor markets for signals',
    replace_existing=True
)

if __name__ == '__main__':
    print("Starting Kalshi Trading Bot...")
    print(f"Dashboard available at http://{FLASK_HOST}:{FLASK_PORT}")
    
    # Start the scheduler
    scheduler.start()
    
    # Start Flask server
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=DEBUG)
