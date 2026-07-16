"""
Risk Management Module
Enforces trading limits and prevents excessive losses
"""

from datetime import datetime, date
from config import MAX_TRADE_SIZE, DAILY_LOSS_LIMIT, STARTING_CAPITAL
from database import Database

class RiskManager:
    """Manages trading risk and enforces limits"""
    
    def __init__(self):
        """Initialize risk manager"""
        self.db = Database()
        self.max_trade_size = MAX_TRADE_SIZE
        self.daily_loss_limit = DAILY_LOSS_LIMIT
        self.starting_capital = STARTING_CAPITAL
    
    def can_trade(self, proposed_trade_size):
        """
        Check if we can execute a trade
        Validates:
        - Trade size doesn't exceed max
        - Daily loss limit not exceeded
        - We have sufficient capital
        
        Args:
            proposed_trade_size: Amount we want to bet in dollars
        
        Returns:
            {'can_trade': bool, 'reason': string, 'available_capital': $}
        """
        
        # Check trade size
        if proposed_trade_size > self.max_trade_size:
            return {
                'can_trade': False,
                'reason': f'Trade size ${proposed_trade_size} exceeds maximum ${self.max_trade_size}',
                'available_capital': 0
            }
        
        # Get current stats
        stats = self.db.get_bot_stats()
        daily_pnl = stats['daily_pnl']
        capital_available = stats['capital_remaining']
        
        # Check daily loss limit
        if daily_pnl < -self.daily_loss_limit:
            return {
                'can_trade': False,
                'reason': f'Daily loss limit exceeded (${daily_pnl} vs ${-self.daily_loss_limit})',
                'available_capital': capital_available
            }
        
        # Check available capital
        if capital_available <= 0:
            return {
                'can_trade': False,
                'reason': 'No capital available for trading',
                'available_capital': capital_available
            }
        
        # All checks passed
        return {
            'can_trade': True,
            'reason': 'Trade approved',
            'available_capital': capital_available
        }
    
    def get_daily_pnl(self):
        """
        Calculate today's profit/loss
        
        Returns:
            P&L in dollars for today
        """
        stats = self.db.get_bot_stats()
        return stats['daily_pnl']
    
    def get_total_pnl(self):
        """
        Calculate total profit/loss since starting
        
        Returns:
            Total P&L in dollars
        """
        stats = self.db.get_bot_stats()
        return stats['total_pnl']
    
    def get_available_capital(self):
        """
        Get current available trading capital
        
        Returns:
            Capital available in dollars
        """
        stats = self.db.get_bot_stats()
        return stats['capital_remaining']
    
    def get_risk_metrics(self):
        """
        Get overall risk metrics for dashboard
        
        Returns:
            Dictionary with risk-related metrics
        """
        stats = self.db.get_bot_stats()
        daily_pnl = stats['daily_pnl']
        total_pnl = stats['total_pnl']
        capital = stats['capital_remaining']
        
        # Calculate loss remaining before daily limit
        loss_remaining = -self.daily_loss_limit - daily_pnl
        loss_percentage = (loss_remaining / self.daily_loss_limit) * 100 if self.daily_loss_limit > 0 else 0
        
        # Calculate capital percentage remaining
        capital_percentage = (capital / self.starting_capital) * 100
        
        return {
            'daily_pnl': daily_pnl,
            'total_pnl': total_pnl,
            'available_capital': capital,
            'capital_percentage': capital_percentage,
            'daily_loss_limit': self.daily_loss_limit,
            'loss_remaining': loss_remaining,
            'loss_percentage': loss_percentage,
            'max_trade_size': self.max_trade_size,
            'trades_executed': stats['trade_count']
        }
