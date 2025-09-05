from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from config.constants import BetType, Provider

@dataclass
class Odds:
    """Normalized odds representation"""
    provider: Provider
    bet_type: BetType
    timestamp: datetime
    
    # Moneyline odds (American format)
    home_ml: Optional[int] = None
    away_ml: Optional[int] = None
    
    # Spread
    spread_line: Optional[float] = None  # Points (positive means home is favored)
    home_spread_odds: Optional[int] = None
    away_spread_odds: Optional[int] = None
    
    # Total (Over/Under)
    total_line: Optional[float] = None  # Total points
    over_odds: Optional[int] = None
    under_odds: Optional[int] = None
    
    # Additional metadata
    volume: Optional[float] = None
    liquidity: Optional[float] = None
    bookmaker: Optional[str] = None
    
    def to_american_odds(self, decimal_odds: float) -> int:
        """Convert decimal odds to American format"""
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))
    
    def to_decimal_odds(self, american_odds: int) -> float:
        """Convert American odds to decimal format"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def to_implied_probability(self, american_odds: int) -> float:
        """Convert American odds to implied probability (0-1)"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def get_moneyline_favorite(self) -> Optional[str]:
        """Determine which team is favored in moneyline"""
        if self.home_ml is None or self.away_ml is None:
            return None
        
        # Lower odds (more negative or less positive) means favorite
        if abs(self.home_ml) > abs(self.away_ml):
            return "away" if self.away_ml < 0 or (self.away_ml > 0 and self.home_ml > self.away_ml) else "home"
        else:
            return "home" if self.home_ml < 0 or (self.home_ml > 0 and self.away_ml > self.home_ml) else "away"
    
    def get_spread_favorite(self) -> Optional[str]:
        """Determine which team is favored in spread"""
        if self.spread_line is None:
            return None
        
        # Positive spread means home team is favored by that many points
        return "home" if self.spread_line > 0 else "away"
    
    def calculate_payout(self, bet_amount: float, american_odds: int) -> float:
        """Calculate payout for a given bet amount and odds"""
        if american_odds > 0:
            return bet_amount * (american_odds / 100)
        else:
            return bet_amount * (100 / abs(american_odds))
    
    def __str__(self):
        """String representation of odds"""
        parts = [f"{self.provider.value} ({self.bet_type.value})"]
        
        if self.bet_type == BetType.MONEYLINE:
            if self.home_ml and self.away_ml:
                parts.append(f"ML: {self.home_ml:+d}/{self.away_ml:+d}")
        
        elif self.bet_type == BetType.SPREAD:
            if self.spread_line and self.home_spread_odds and self.away_spread_odds:
                parts.append(f"Spread: {self.spread_line:+.1f} ({self.home_spread_odds:+d}/{self.away_spread_odds:+d})")
        
        elif self.bet_type == BetType.TOTAL:
            if self.total_line and self.over_odds and self.under_odds:
                parts.append(f"Total: {self.total_line} (O/U: {self.over_odds:+d}/{self.under_odds:+d})")
        
        return " - ".join(parts)