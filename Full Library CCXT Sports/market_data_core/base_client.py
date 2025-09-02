"""
Abstract base client for market data providers
Defines the standard interface that all providers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Union
from datetime import datetime

from .models import (
    Team, Game, Market, Quote, Category, Sport, MarketType, 
    ProviderResponse, GameAlignment, ArbitrageOpportunity
)
from .exceptions import MarketDataError
from .utils import setup_logging


class BaseMarketDataClient(ABC):
    """Abstract base class for all market data providers"""
    
    def __init__(self, provider_name: str, config: Dict[str, Any]):
        """
        Initialize base client
        
        Args:
            provider_name: Name of the provider (e.g., "kalshi", "odds_api")
            config: Provider-specific configuration
        """
        self.provider_name = provider_name
        self.config = config
        self.logger = setup_logging(f"market_data.{provider_name}")
        self._authenticated = False
    
    # Authentication methods
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the provider
        
        Returns:
            True if authentication successful, False otherwise
            
        Raises:
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if client is currently authenticated"""
        pass
    
    # Core data retrieval methods
    
    @abstractmethod
    async def get_sports(self) -> ProviderResponse:
        """
        Get list of available sports from provider
        
        Returns:
            ProviderResponse containing list of Sport objects
        """
        pass
    
    @abstractmethod
    async def get_categories(self, sport: Sport) -> ProviderResponse:
        """
        Get categories/leagues for a sport
        
        Args:
            sport: Sport to get categories for
            
        Returns:
            ProviderResponse containing list of Category objects
        """
        pass
    
    @abstractmethod
    async def get_games(self, sport: Sport, date_from: Optional[datetime] = None, 
                       date_to: Optional[datetime] = None) -> ProviderResponse:
        """
        Get games for a sport within date range
        
        Args:
            sport: Sport to get games for
            date_from: Start date (optional)
            date_to: End date (optional)
            
        Returns:
            ProviderResponse containing list of Game objects
        """
        pass
    
    @abstractmethod
    async def get_markets(self, game: Game) -> ProviderResponse:
        """
        Get available markets for a game
        
        Args:
            game: Game to get markets for
            
        Returns:
            ProviderResponse containing list of Market objects
        """
        pass
    
    @abstractmethod
    async def get_quotes(self, market: Market) -> ProviderResponse:
        """
        Get current quotes/odds for a market
        
        Args:
            market: Market to get quotes for
            
        Returns:
            ProviderResponse containing list of Quote objects
        """
        pass
    
    # Convenience methods with default implementations
    
    async def get_game_quotes(self, game: Game, 
                             market_types: Optional[List[MarketType]] = None) -> ProviderResponse:
        """
        Get all quotes for a game, optionally filtered by market types
        
        Args:
            game: Game to get quotes for
            market_types: Optional list of market types to filter by
            
        Returns:
            ProviderResponse containing dict of {market_type: [Quote]}
        """
        try:
            # Get markets for game
            markets_response = await self.get_markets(game)
            if not markets_response.success:
                return markets_response
            
            markets = markets_response.data
            if market_types:
                markets = [m for m in markets if m.market_type in market_types]
            
            # Get quotes for each market
            all_quotes = {}
            for market in markets:
                quotes_response = await self.get_quotes(market)
                if quotes_response.success and quotes_response.data:
                    all_quotes[market.market_type] = quotes_response.data
            
            return ProviderResponse(
                success=True,
                data=all_quotes,
                provider=self.provider_name
            )
            
        except Exception as e:
            self.logger.error(f"Error getting game quotes: {e}")
            return ProviderResponse(
                success=False,
                error=str(e),
                provider=self.provider_name
            )
    
    async def find_team(self, search_name: str, sport: Sport) -> Optional[Team]:
        """
        Find a team by name within a sport
        
        Args:
            search_name: Name to search for
            sport: Sport to search within
            
        Returns:
            Team object if found, None otherwise
        """
        try:
            # This is a basic implementation - providers should override with better logic
            games_response = await self.get_games(sport)
            if not games_response.success or not games_response.data:
                return None
            
            # Extract unique teams from games
            teams = set()
            for game in games_response.data:
                teams.add(game.home_team)
                teams.add(game.away_team)
            
            # Find best match
            best_match = None
            best_confidence = 0.0
            
            for team in teams:
                confidence = team.matches(search_name)
                if confidence > best_confidence:
                    best_match = team
                    best_confidence = confidence
            
            return best_match if best_confidence > 0.8 else None
            
        except Exception as e:
            self.logger.error(f"Error finding team {search_name}: {e}")
            return None
    
    async def find_game(self, home_team: Union[str, Team], away_team: Union[str, Team], 
                       sport: Sport, game_date: Optional[datetime] = None) -> Optional[Game]:
        """
        Find a specific game by teams and optional date
        
        Args:
            home_team: Home team (name or Team object)
            away_team: Away team (name or Team object)
            sport: Sport
            game_date: Optional game date for filtering
            
        Returns:
            Game object if found, None otherwise
        """
        try:
            # Convert team names to Team objects if needed
            if isinstance(home_team, str):
                home_team = await self.find_team(home_team, sport)
                if not home_team:
                    return None
            
            if isinstance(away_team, str):
                away_team = await self.find_team(away_team, sport)
                if not away_team:
                    return None
            
            # Get games and find match
            games_response = await self.get_games(sport, game_date)
            if not games_response.success or not games_response.data:
                return None
            
            for game in games_response.data:
                # Check team matches (handle both home/away arrangements)
                home_match = (game.home_team.matches(home_team.name) > 0.8 or 
                             game.home_team.matches(away_team.name) > 0.8)
                away_match = (game.away_team.matches(home_team.name) > 0.8 or 
                             game.away_team.matches(away_team.name) > 0.8)
                
                if home_match and away_match:
                    return game
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding game {home_team} vs {away_team}: {e}")
            return None
    
    # Health and status methods
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform basic health check on provider
        
        Returns:
            Dict containing health status information
        """
        try:
            start_time = datetime.utcnow()
            
            # Try to authenticate
            auth_success = await self.authenticate() if not self.is_authenticated() else True
            
            # Try to get sports list
            sports_response = await self.get_sports()
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                'provider': self.provider_name,
                'status': 'healthy' if auth_success and sports_response.success else 'unhealthy',
                'authenticated': auth_success,
                'api_accessible': sports_response.success,
                'response_time_seconds': response_time,
                'timestamp': end_time.isoformat(),
                'rate_limit_remaining': getattr(sports_response, 'rate_limit_remaining', None)
            }
            
        except Exception as e:
            return {
                'provider': self.provider_name,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    # Rate limiting and error handling
    
    def _handle_rate_limit(self, response_data: Dict[str, Any]) -> None:
        """Handle rate limit information from provider response"""
        if 'rate_limit_remaining' in response_data:
            remaining = response_data['rate_limit_remaining']
            if remaining is not None and remaining < 10:
                self.logger.warning(f"Rate limit low: {remaining} requests remaining")
    
    def _create_error_response(self, error: Exception, 
                              context: Optional[str] = None) -> ProviderResponse:
        """Create standardized error response"""
        error_msg = f"{context}: {error}" if context else str(error)
        
        return ProviderResponse(
            success=False,
            error=error_msg,
            provider=self.provider_name,
            metadata={'exception_type': type(error).__name__}
        )