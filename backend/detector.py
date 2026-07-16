"""
Whale and Momentum Detection Engine
Analyzes market data to identify trading signals
"""

from datetime import datetime, timedelta
from config import WHALE_THRESHOLD, MOMENTUM_THRESHOLDS, MOMENTUM_LEVELS, MOMENTUM_WINDOW
from database import Database

class SignalDetector:
    """Detects whale bets and momentum shifts in market data"""
    
    def __init__(self):
        """Initialize detector with database connection"""
        self.db = Database()
        self.whale_threshold = WHALE_THRESHOLD
        self.momentum_thresholds = MOMENTUM_THRESHOLDS
        self.momentum_levels = MOMENTUM_LEVELS
    
    def detect_whale_bet(self, market_data, order_book):
        """
        Detect if a whale bet just occurred
        A whale bet is an order larger than our threshold
        
        Args:
            market_data: Market info (id, name, etc)
            order_book: Current order book with recent orders
        
        Returns:
            {'whale_detected': bool, 'direction': 'yes'/'no', 'size': $}
        """
        if not order_book or 'recent_orders' not in order_book:
            return {'whale_detected': False}
        
        recent_orders = order_book.get('recent_orders', [])
        
        # Check if any recent orders exceed whale threshold
        for order in recent_orders:
            order_size = order.get('size', 0)
            
            if order_size >= self.whale_threshold:
                direction = order.get('side', 'yes')  # 'yes' or 'no'
                price = order.get('price')
                
                # Log the whale detection
                self.db.log_whale_detection(
                    market_data['id'],
                    market_data['name'],
                    order_size,
                    direction,
                    price
                )
                
                return {
                    'whale_detected': True,
                    'direction': direction,
                    'size': order_size,
                    'price': price
                }
        
        return {'whale_detected': False}
    
    def detect_momentum(self, market_id, market_name, current_price, price_history):
        """
        Detect momentum shifts based on price movement
        Checks if price moved significantly in the last 5 minutes
        
        Args:
            market_id: Market identifier
            market_name: Human-readable market name
            current_price: Current market price (0.0 to 1.0)
            price_history: List of recent prices with timestamps
        
        Returns:
            {'momentum_detected': bool, 'signal_level': 'base'/'strong'/'extreme',
             'direction': 'up'/'down', 'price_change': %}
        """
        if not price_history or len(price_history) < 2:
            return {'momentum_detected': False}
        
        # Get price from MOMENTUM_WINDOW minutes ago
        now = datetime.now()
        window_start = now - timedelta(minutes=MOMENTUM_WINDOW)
        
        # Find oldest price in window
        oldest_price = None
        for price_point in price_history:
            if price_point['timestamp'] >= window_start:
                oldest_price = price_point['price']
                break
        
        if oldest_price is None:
            oldest_price = price_history[-1]['price']
        
        # Calculate percentage change
        price_change = ((current_price - oldest_price) / oldest_price) * 100
        direction = 'up' if price_change > 0 else 'down'
        abs_change = abs(price_change)
        
        # Get market-specific threshold
        market_key = market_name.lower().replace(' ', '_')
        threshold = self.momentum_thresholds.get(market_key, 
                                                self.momentum_thresholds['default'])
        levels = self.momentum_levels.get(market_key,
                                         self.momentum_levels['default'])
        
        # Determine signal level
        signal_level = None
        if abs_change >= levels['extreme']:
            signal_level = 'extreme'
        elif abs_change >= levels['strong']:
            signal_level = 'strong'
        elif abs_change >= levels['base']:
            signal_level = 'base'
        
        if signal_level:
            # Log the momentum detection
            self.db.log_momentum_detection(
                market_id,
                market_name,
                abs_change,
                signal_level,
                direction
            )
            
            return {
                'momentum_detected': True,
                'signal_level': signal_level,
                'direction': direction,
                'price_change': price_change
            }
        
        return {'momentum_detected': False}
    
    def evaluate_trade_signal(self, whale_signal, momentum_signal):
        """
        Combine whale and momentum signals to decide if/how to trade
        
        Trading Logic:
        - Whale alone: $2.50 (50% position)
        - Momentum alone: $2.50 (50% position)  
        - Both: $5.00 (full position)
        
        Args:
            whale_signal: Result from detect_whale_bet()
            momentum_signal: Result from detect_momentum()
        
        Returns:
            {'should_trade': bool, 'trade_size': $, 'signal_type': string,
             'confidence': 'low'/'medium'/'high'}
        """
        whale_detected = whale_signal.get('whale_detected', False)
        momentum_detected = momentum_signal.get('momentum_detected', False)
        
        if not whale_detected and not momentum_detected:
            return {'should_trade': False}
        
        # Determine trade size and type based on signals
        if whale_detected and momentum_detected:
            # Both signals: maximum confidence
            trade_size = 5.0
            signal_type = 'whale_and_momentum'
            confidence = 'high'
            # Use whale direction as it's the primary signal
            direction = whale_signal.get('direction', 'yes')
        
        elif whale_detected:
            # Whale alone
            trade_size = 2.5
            signal_type = 'whale_only'
            confidence = 'medium'
            direction = whale_signal.get('direction', 'yes')
        
        else:  # momentum_detected
            # Momentum alone
            trade_size = 2.5
            signal_type = 'momentum_only'
            confidence = 'medium'
            # Trade in the direction of momentum
            direction = 'yes' if momentum_signal.get('direction') == 'up' else 'no'
        
        return {
            'should_trade': True,
            'trade_size': trade_size,
            'signal_type': signal_type,
            'direction': direction,
            'confidence': confidence,
            'whale_signal': whale_signal if whale_detected else None,
            'momentum_signal': momentum_signal if momentum_detected else None
        }
