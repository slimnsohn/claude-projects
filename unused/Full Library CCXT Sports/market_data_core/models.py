"""
Unified data models for sports betting market data
Provides consistent data structures across all providers.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class MarketType(Enum):
    """Types of betting markets"""
    MONEYLINE = "moneyline"  # Head-to-head winner
    SPREAD = "spread"        # Point spread
    TOTAL = "total"          # Over/under
    PROP = "prop"            # Player/team props
    FUTURES = "futures"      # Season-long bets


class QuoteSide(Enum):
    """Side of a betting quote"""
    HOME = "home"
    AWAY = "away"
    OVER = "over"
    UNDER = "under"
    YES = "yes"
    NO = "no"


class Sport(Enum):
    """Supported sports"""
    NFL = "nfl"
    MLB = "mlb"
    NBA = "nba"
    NHL = "nhl"
    NCAAF = "ncaaf"  # College Football
    NCAAB = "ncaab"  # College Basketball


@dataclass
class Team:
    """Represents a sports team with multiple name variations"""
    name: str                              # Primary name (e.g., "Kansas City Chiefs")
    city: str                              # City (e.g., "Kansas City")
    nickname: str                          # Team nickname (e.g., "Chiefs")
    abbreviations: List[str] = field(default_factory=list)  # ["KC", "KAN"]
    alternative_names: List[str] = field(default_factory=list)  # Alternative spellings
    sport: Optional[Sport] = None
    conference: Optional[str] = None       # AFC/NFC for NFL, etc.
    division: Optional[str] = None         # Division name
    
    def __post_init__(self):
        """Ensure consistent data after initialization"""
        if not self.abbreviations:
            self.abbreviations = []
        if not self.alternative_names:
            self.alternative_names = []
        
        # Add common variations to alternative names if not already present
        variations = [
            self.name,
            f"{self.city} {self.nickname}",
            self.nickname
        ]
        for variation in variations:
            if variation and variation not in self.alternative_names:
                self.alternative_names.append(variation)
    
    def matches(self, search_name: str, min_confidence: float = 0.8) -> float:
        """
        Check if this team matches a search name and return confidence score
        
        Args:
            search_name: Name to match against
            min_confidence: Minimum confidence threshold
            
        Returns:
            Confidence score (0.0 to 1.0), 0.0 if below threshold
        """
        search_name = search_name.strip().upper()
        
        # Exact matches
        exact_matches = [
            self.name.upper(),
            self.nickname.upper(),
            f"{self.city} {self.nickname}".upper()
        ] + [name.upper() for name in self.abbreviations + self.alternative_names]
        
        if search_name in exact_matches:
            return 1.0
        
        # Fuzzy matching using simple substring and similarity
        from difflib import SequenceMatcher
        
        best_score = 0.0
        for candidate in exact_matches:
            if candidate in search_name or search_name in candidate:
                score = 0.9  # High score for substring match
            else:
                score = SequenceMatcher(None, search_name, candidate).ratio()
            
            best_score = max(best_score, score)
        
        return best_score if best_score >= min_confidence else 0.0


@dataclass
class Game:
    """Represents a sports game/event"""
    game_id: str                          # Unique identifier
    home_team: Team                       # Home team
    away_team: Team                       # Away team
    sport: Sport                          # Sport type
    game_date: datetime                   # When game occurs
    season: Optional[str] = None          # Season identifier (e.g., "2024")
    week: Optional[int] = None            # Week number (for NFL)
    venue: Optional[str] = None           # Stadium/arena name
    status: Optional[str] = None          # Game status (scheduled, live, final)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional game info
    
    def __post_init__(self):
        """Ensure consistent data after initialization"""
        if not self.metadata:
            self.metadata = {}
    
    def get_matchup_string(self) -> str:
        """Get standardized matchup string"""
        return f"{self.away_team.abbreviations[0] if self.away_team.abbreviations else self.away_team.nickname} @ {self.home_team.abbreviations[0] if self.home_team.abbreviations else self.home_team.nickname}"


@dataclass
class Market:
    """Represents a betting market for a game"""
    market_id: str                        # Unique identifier
    game: Game                            # Associated game
    market_type: MarketType               # Type of market
    name: str                             # Market name/description
    spread_line: Optional[float] = None   # Point spread (if applicable)
    total_line: Optional[float] = None    # Total points line (if applicable)
    is_active: bool = True                # Whether market is accepting bets
    close_time: Optional[datetime] = None # When market closes
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure consistent data after initialization"""
        if not self.metadata:
            self.metadata = {}


@dataclass
class Quote:
    """Represents a betting quote/odds for a specific outcome"""
    quote_id: str                         # Unique identifier
    market: Market                        # Associated market
    side: QuoteSide                       # Which side of bet
    provider: str                         # Data provider name
    bookmaker: Optional[str] = None       # Specific bookmaker (for aggregated data)
    
    # Odds in multiple formats
    american_odds: Optional[int] = None   # American odds (-110, +150)
    decimal_odds: Optional[float] = None  # Decimal odds (1.91, 2.50)
    implied_probability: Optional[float] = None  # 0.0 to 1.0
    
    # Market depth (if available)
    price: Optional[float] = None         # Actual price/cost to bet
    size: Optional[float] = None          # Available liquidity
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = None
    is_valid: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate derived values and ensure consistency"""
        if not self.metadata:
            self.metadata = {}
        
        # Calculate missing odds formats
        if self.american_odds is not None and self.decimal_odds is None:
            self.decimal_odds = self._american_to_decimal(self.american_odds)
        elif self.decimal_odds is not None and self.american_odds is None:
            self.american_odds = self._decimal_to_american(self.decimal_odds)
        
        # Calculate implied probability
        if self.decimal_odds is not None and self.implied_probability is None:
            self.implied_probability = 1.0 / self.decimal_odds
        elif self.american_odds is not None and self.implied_probability is None:
            self.implied_probability = self._american_to_probability(self.american_odds)
    
    @staticmethod
    def _american_to_decimal(american_odds: int) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    @staticmethod
    def _decimal_to_american(decimal_odds: float) -> int:
        """Convert decimal odds to American odds"""
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))
    
    @staticmethod
    def _american_to_probability(american_odds: int) -> float:
        """Convert American odds to implied probability"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)


@dataclass
class Category:
    """Represents a category/grouping of markets"""
    category_id: str                      # Unique identifier
    name: str                             # Category name
    sport: Sport                          # Associated sport
    description: Optional[str] = None     # Category description
    parent_category: Optional['Category'] = None  # Parent category (for hierarchical)
    subcategories: List['Category'] = field(default_factory=list)
    markets: List[Market] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure consistent data after initialization"""
        if not self.subcategories:
            self.subcategories = []
        if not self.markets:
            self.markets = []
        if not self.metadata:
            self.metadata = {}


# Utility classes for provider responses

@dataclass
class ProviderResponse:
    """Generic response wrapper for provider API calls"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    provider: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure consistent data after initialization"""
        if not self.metadata:
            self.metadata = {}


@dataclass
class GameAlignment:
    """Represents alignment between same game from different providers"""
    alignment_id: str
    games: Dict[str, Game]               # Provider name -> Game
    confidence: float                     # Alignment confidence (0.0 to 1.0)
    aligned_at: datetime = field(default_factory=datetime.utcnow)
    alignment_criteria: List[str] = field(default_factory=list)  # What matched
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure consistent data after initialization"""
        if not self.alignment_criteria:
            self.alignment_criteria = []
        if not self.metadata:
            self.metadata = {}
    
    def get_primary_game(self) -> Game:
        """Get the primary game (first provider or highest confidence)"""
        if not self.games:
            raise ValueError("No games in alignment")
        return next(iter(self.games.values()))


@dataclass
class ArbitrageOpportunity:
    """Represents a potential arbitrage opportunity between providers"""
    opportunity_id: str
    game_alignment: GameAlignment
    market_type: MarketType
    quotes: Dict[str, Quote]             # Provider/bookmaker -> Quote
    total_probability: float             # Sum of implied probabilities
    profit_margin: float                 # Potential profit percentage
    stakes: Dict[str, float]             # Recommended stake per provider
    detected_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure consistent data after initialization"""
        if not self.metadata:
            self.metadata = {}
    
    def is_profitable(self, min_margin: float = 0.01) -> bool:
        """Check if opportunity is profitable above minimum margin"""
        return self.profit_margin > min_margin and self.total_probability < 1.0