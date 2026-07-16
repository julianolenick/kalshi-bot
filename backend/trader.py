"""
Trade Execution Engine
Executes trades based on detected signals while respecting risk limits
"""

from datetime import datetime
from kalshi_api import KalshiAPI
from risk_manager import RiskManager
from database import Database

class TradeExecutor:
    """Executes trades on the Kalshi platform"""
    
    def __init__(self):
        """Initialize trade executor"""
        self.api = KalshiAPI()
        self.risk_manager = RiskManager()
        self.db = Database()
    
    def execute_trade(self, market_id, market_name, trade_signal, current_price):
        """
        Execute a trade based on detected signals
        
        Args:
            market_id: The market to trade
            market_name: Human-readable market name
            trade_signal: Result from detector.evaluate_trade_signal()
            current_price: Current market price
        
        Returns:
            {'success': bool, 'order_id': string, 'message': string}
        """
        
        if not trade_signal.get('should_trade'):
            return {'success': False, 'message': 'No trade signal'}
        
        trade_size = trade_signal.get('trade_size')
        direction = trade_signal.get('direction')
        signal_type = trade_signal.get('signal_type')
        
        # Check if we can trade
        risk_check = self.risk_manager.can_trade(trade_size)
        if not risk_check['can_trade']:
            return {
                'success': False,
                'message': f"Risk check failed: {risk_check['reason']}"
            }
        
        # Determine order price (slightly better than market to increase chance of fill)
        # For 'yes' bets: place bid slightly below current price
        # For 'no' bets: place ask slightly above current price
        if direction == 'yes':
            order_price = max(current_price - 0.01, 0.01)  # Don't go below 0.01
        else:
            order_price = min(current_price + 0.01, 0.99)  # Don't go above 0.99
        
        # Log to database first (so we have record even if API call fails)
        trade_id = self.db.log_trade(
            market_id,
            market_name,
            signal_type,
            trade_size,
            direction
        )
        
        # Execute order on Kalshi
        try:
            order_result = self.api.place_order(
                market_id=market_id,
                side=direction,
                price=order_price,
                size=trade_size,
                order_type='limit'
            )
            
            if order_result and 'order_id' in order_result:
                return {
                    'success': True,
                    'order_id': order_result['order_id'],
                    'trade_id': trade_id,
                    'message': f'Order placed: {trade_size} {direction} @ {order_price}',
                    'signal_type': signal_type,
                    'confidence': trade_signal.get('confidence')
                }
            else:
                return {
                    'success': False,
                    'trade_id': trade_id,
                    'message': 'Failed to place order on Kalshi API'
                }
        
        except Exception as e:
            return {
                'success': False,
                'trade_id': trade_id,
                'message': f'Trade execution error: {str(e)}'
            }
    
    def cancel_trade(self, order_id):
        """
        Cancel an open trade
        
        Args:
            order_id: The order to cancel
        
        Returns:
            {'success': bool, 'message': string}
        """
        try:
            result = self.api.cancel_order(order_id)
            if result:
                return {'success': True, 'message': 'Order cancelled'}
            else:
                return {'success': False, 'message': 'Failed to cancel order'}
        except Exception as e:
            return {'success': False, 'message': f'Cancel error: {str(e)}'}
