from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from config.constants import Sport, Provider

@dataclass
class Game:
    """Normalized game representation"""
    game_id: str  # Unique identifier
    sport: Sport
    home_team: str
    away_team: str
    start_time: datetime
    venue: Optional[str] = None
    
    # Store provider-specific IDs for reference
    provider_ids: Dict[Provider, str] = field(default_factory=dict)
    
    # Odds for this game
    odds: Dict[str, 'Odds'] = field(default_factory=dict)
    
    # Game status
    status: Optional[str] = None  # scheduled, live, finished, postponed
    
    # Additional metadata
    season: Optional[str] = None
    week: Optional[int] = None
    
    def __hash__(self):
        """Hash based on teams and start time for deduplication"""
        return hash(f"{self.home_team}_{self.away_team}_{self.start_time.date()}")
    
    def __eq__(self, other):
        """Equality check for game matching"""
        if not isinstance(other, Game):
            return False
        return (self.home_team == other.home_team and 
                self.away_team == other.away_team and 
                self.start_time.date() == other.start_time.date())
    
    def __str__(self):
        """String representation"""
        return f"{self.away_team} @ {self.home_team} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"
    
    def add_provider_id(self, provider: Provider, provider_id: str):
        """Add a provider-specific ID"""
        self.provider_ids[provider] = provider_id
    
    def add_odds(self, odds_key: str, odds: 'Odds'):
        """Add odds for this game"""
        self.odds[odds_key] = odds
    
    def get_odds_by_provider(self, provider: Provider) -> List['Odds']:
        """Get all odds from a specific provider"""
        return [odds for key, odds in self.odds.items() if provider.value in key]
    
    def is_today(self) -> bool:
        """Check if game is today"""
        return self.start_time.date() == datetime.now().date()
    
    def time_until_start(self) -> Optional[str]:
        """Get human-readable time until start"""
        # Handle timezone-aware vs naive datetime comparison
        now = datetime.now()
        if self.start_time.tzinfo is not None:
            # If start_time is timezone-aware, make now timezone-aware too
            from datetime import timezone
            now = datetime.now(timezone.utc)
        
        if self.start_time < now:
            return "Started"
        
        delta = self.start_time - now
        hours = delta.total_seconds() // 3600
        minutes = (delta.total_seconds() % 3600) // 60
        
        if hours >= 24:
            days = hours // 24
            return f"{int(days)} day{'s' if days != 1 else ''}"
        elif hours >= 1:
            return f"{int(hours)}h {int(minutes)}m"
        else:
            return f"{int(minutes)}m"