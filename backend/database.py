"""
Database management for the Kalshi Trading Bot
Handles all SQLite operations for storing trades, markets, and bot state
"""

import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH

class Database:
    """SQLite database wrapper for the bot"""
    
    def __init__(self, db_path=DATABASE_PATH):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_database(self):
        """Create all necessary tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Trades table - records all bot trades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                market_id TEXT NOT NULL,
                market_name TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                trade_size REAL NOT NULL,
                direction TEXT NOT NULL,
                entry_price REAL,
                exit_price REAL,
                pnl REAL,
                status TEXT NOT NULL,
                notes TEXT
            )
        ''')
        
        # Whale detections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whale_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                market_id TEXT NOT NULL,
                market_name TEXT NOT NULL,
                order_size REAL NOT NULL,
                direction TEXT NOT NULL,
                price REAL,
                traded BOOLEAN DEFAULT 0
            )
        ''')
        
        # Momentum detections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS momentum_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                market_id TEXT NOT NULL,
                market_name TEXT NOT NULL,
                price_change REAL NOT NULL,
                signal_level TEXT NOT NULL,
                direction TEXT NOT NULL,
                traded BOOLEAN DEFAULT 0
            )
        ''')
        
        # Market prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                market_id TEXT NOT NULL,
                market_name TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_trade(self, market_id, market_name, signal_type, trade_size, direction):
        """Log a new trade to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (
                timestamp, market_id, market_name, signal_type,
                trade_size, direction, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            market_id,
            market_name,
            signal_type,
            trade_size,
            direction,
            'open'
        ))
        
        conn.commit()
        trade_id = cursor.lastrowid
        conn.close()
        
        return trade_id
    
    def log_whale_detection(self, market_id, market_name, order_size, direction, price=None):
        """Log a detected whale bet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO whale_detections (
                timestamp, market_id, market_name, order_size, direction, price
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            market_id,
            market_name,
            order_size,
            direction,
            price
        ))
        
        conn.commit()
        conn.close()
    
    def log_momentum_detection(self, market_id, market_name, price_change, signal_level, direction):
        """Log a detected momentum signal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO momentum_detections (
                timestamp, market_id, market_name, price_change, signal_level, direction
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            market_id,
            market_name,
            price_change,
            signal_level,
            direction
        ))
        
        conn.commit()
        conn.close()
    
    def log_price(self, market_id, market_name, price):
        """Log market price for momentum calculation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_prices (
                timestamp, market_id, market_name, price
            ) VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            market_id,
            market_name,
            price
        ))
        
        conn.commit()
        conn.close()
    
    def get_trades(self, limit=100):
        """Get recent trades from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM trades
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return trades
    
    def get_bot_stats(self):
        """Get overall bot statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calculate P&L from all trades
        cursor.execute('SELECT SUM(pnl) as total_pnl FROM trades WHERE pnl IS NOT NULL')
        result = cursor.fetchone()
        total_pnl = result['total_pnl'] or 0.0
        
        # Count trades
        cursor.execute('SELECT COUNT(*) as trade_count FROM trades')
        result = cursor.fetchone()
        trade_count = result['trade_count'] or 0
        
        # Get today's P&L
        cursor.execute('''
            SELECT SUM(pnl) as daily_pnl FROM trades
            WHERE pnl IS NOT NULL AND date(timestamp) = date('now')
        ''')
        result = cursor.fetchone()
        daily_pnl = result['daily_pnl'] or 0.0
        
        conn.close()
        
        return {
            'total_pnl': total_pnl,
            'daily_pnl': daily_pnl,
            'trade_count': trade_count,
            'capital_remaining': 200.0 + total_pnl
        }
