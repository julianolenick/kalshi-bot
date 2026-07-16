"""
Kalshi API Integration
Handles all communication with the Kalshi prediction market API
"""

import requests
import json
from datetime import datetime
from config import KALSHI_API_KEY, KALSHI_API_SECRET, KALSHI_BASE_URL

class KalshiAPI:
    """Wrapper for Kalshi API calls"""
    
    def __init__(self):
        """Initialize API client with credentials"""
        self.api_key = KALSHI_API_KEY
        self.api_secret = KALSHI_API_SECRET
        self.base_url = KALSHI_BASE_URL
        self.session = requests.Session()
        
        # Set up auth headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method, endpoint, data=None):
        """Make authenticated request to Kalshi API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = self.session.get(url)
            elif method == 'POST':
                response = self.session.post(url, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return None
    
    def get_markets(self):
        """
        Get all active prediction markets
        Returns list of market data with current prices
        """
        return self._make_request('GET', '/markets')
    
    def get_market(self, market_id):
        """
        Get details for a specific market
        
        Args:
            market_id: The market ID from Kalshi
        
        Returns:
            Market data including current prices and order book
        """
        return self._make_request('GET', f'/markets/{market_id}')
    
    def get_order_book(self, market_id):
        """
        Get current order book for a market
        Shows bids, asks, and recent orders
        
        Args:
            market_id: The market ID
        
        Returns:
            Order book data with whale bets visible
        """
        return self._make_request('GET', f'/markets/{market_id}/order-book')
    
    def place_order(self, market_id, side, price, size, order_type='limit'):
        """
        Place a trade order on a market
        
        Args:
            market_id: The market to trade
            side: 'yes' or 'no'
            price: Price from 0.01 to 0.99
            size: Amount in dollars
            order_type: 'limit' or 'market'
        
        Returns:
            Order confirmation with order_id
        """
        data = {
            'market_id': market_id,
            'side': side,
            'price': price,
            'size': size,
            'type': order_type
        }
        
        return self._make_request('POST', '/orders', data)
    
    def cancel_order(self, order_id):
        """
        Cancel an open order
        
        Args:
            order_id: The order to cancel
        
        Returns:
            Cancellation confirmation
        """
        return self._make_request('DELETE', f'/orders/{order_id}')
    
    def get_portfolio(self):
        """
        Get your current portfolio
        Shows cash balance, open positions, and P&L
        
        Returns:
            Portfolio data
        """
        return self._make_request('GET', '/portfolio')
    
    def get_balance(self):
        """
        Get current cash balance
        
        Returns:
            Cash balance in dollars
        """
        portfolio = self.get_portfolio()
        if portfolio and 'balance' in portfolio:
            return portfolio['balance']
        return None
    
    def get_trades(self, limit=100):
        """
        Get recent trades from your account
        
        Args:
            limit: Maximum number of trades to return
        
        Returns:
            List of recent trades
        """
        return self._make_request('GET', f'/orders?limit={limit}')
