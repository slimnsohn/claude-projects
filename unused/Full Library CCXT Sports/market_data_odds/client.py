"""
Odds API Market Data Client
Implements The Odds API integration with unified interface.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
from pathlib import Path

# Handle both import and direct execution
if __name__ == "__main__":
    # Running as script - add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Use absolute imports for direct execution
    from market_data_core.base_client import BaseMarketDataClient
    from market_data_core.models import ProviderResponse, Sport, Game, Market, Quote, Category
    from market_data_core.exceptions import MarketDataError, AuthenticationError
    from market_data_core.utils import RateLimiter
    from market_data_core import get_team_matcher
    from market_data_odds.auth import OddsAPIAuthenticator
    from market_data_odds.handler import OddsAPIResponseHandler
else:
    # Running as import - use relative imports
    from market_data_core.base_client import BaseMarketDataClient
    from market_data_core.models import ProviderResponse, Sport, Game, Market, Quote, Category
    from market_data_core.exceptions import MarketDataError, AuthenticationError
    from market_data_core.utils import RateLimiter
    from market_data_core import get_team_matcher
    from .auth import OddsAPIAuthenticator
    from .handler import OddsAPIResponseHandler


class OddsAPIClient(BaseMarketDataClient):
    """Odds API client implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Odds API client"""
        super().__init__("odds_api", config)
        
        # Initialize authenticator
        try:
            self.auth = OddsAPIAuthenticator.from_config(config)
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Odds API authentication: {e}")
        
        # API configuration
        self.base_url = config.get('base_url', 'https://api.the-odds-api.com/v4')
        
        # Rate limiting (500 requests per minute as per config)
        rate_limit_config = config.get('rate_limits', {})
        max_requests = rate_limit_config.get('odds_api_requests_per_minute', 500)
        self.rate_limiter = RateLimiter(max_requests, 60)
        
        # Response handler for data transformation
        self.handler = OddsAPIResponseHandler()
        
        # Team matcher for team name resolution
        self.team_matcher = get_team_matcher(Sport.NFL)  # Default to NFL, can be extended
        
        # Request configuration
        self.timeout_config = config.get('timeouts', {})
        self.default_timeout = self.timeout_config.get('default_timeout', 30)
        
        # Default parameters for Odds API requests
        self.default_params = {
            'regions': 'us',  # US region
            'oddsFormat': 'american',  # American odds format
            'dateFormat': 'iso'  # ISO date format
        }
    
    async def authenticate(self) -> bool:
        """Test authentication with Odds API"""
        try:
            await self.rate_limiter.async_wait_if_needed()
            
            # Test authentication by fetching available sports
            url = f"{self.base_url}/sports"
            params = self.auth.get_auth_params()
            headers = self.auth.get_auth_headers()
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.default_timeout)) as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._authenticated = True
                        self.logger.info(f"Successfully authenticated with Odds API - {len(data)} sports available")
                        return True
                    elif response.status == 401:
                        error_text = await response.text()
                        self.logger.error(f"Authentication failed: Invalid API key")
                        return False
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Authentication error {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Authentication exception: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check authentication status"""
        return self._authenticated
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Odds API"""
        if not self._authenticated:
            if not await self.authenticate():
                raise AuthenticationError("Failed to authenticate with Odds API")
        
        await self.rate_limiter.async_wait_if_needed()
        
        # Prepare request
        url = f"{self.base_url}{endpoint}"
        request_params = self.auth.get_auth_params()
        request_params.update(self.default_params)
        
        if params:
            request_params.update(params)
        
        headers = self.auth.get_auth_headers()
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.default_timeout)) as session:
                async with session.get(url, params=request_params, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        # Re-authenticate and retry once
                        self._authenticated = False
                        if await self.authenticate():
                            request_params.update(self.auth.get_auth_params())
                            async with session.get(url, params=request_params, headers=headers) as retry_response:
                                if retry_response.status == 200:
                                    return await retry_response.json()
                                else:
                                    error_text = await retry_response.text()
                                    raise MarketDataError(f"Request failed after retry: {error_text}")
                        else:
                            raise AuthenticationError("Re-authentication failed")
                    elif response.status == 429:
                        # Rate limit exceeded
                        self.logger.warning("Rate limit exceeded, will be handled by rate limiter")
                        raise MarketDataError("Rate limit exceeded")
                    else:
                        error_text = await response.text()
                        raise MarketDataError(f"API request failed {response.status}: {error_text}")
                        
        except aiohttp.ClientError as e:
            raise MarketDataError(f"Network error: {e}")
    
    async def get_sports(self) -> ProviderResponse:
        """Get available sports from Odds API"""
        try:
            data = await self._make_request("/sports")
            
            # Extract supported sports that we can handle
            supported_sports = []
            for sport_data in data:
                sport_key = sport_data.get('key')
                if sport_key:
                    sport = self.handler.get_sport_from_api_key(sport_key)
                    if sport:
                        supported_sports.append(sport)
            
            return ProviderResponse(
                success=True,
                data=supported_sports,
                provider=self.provider_name,
                metadata={
                    'total_api_sports': len(data),
                    'supported_sports': len(supported_sports)
                }
            )
            
        except Exception as e:
            return self._create_error_response(e, "get_sports")
    
    async def get_categories(self, sport: Sport) -> ProviderResponse:
        """Get categories for a sport"""
        try:
            sport_key = self.handler.get_sport_key_for_api(sport)
            if not sport_key:
                return ProviderResponse(
                    success=False,
                    error=f"Sport {sport} not supported by Odds API",
                    provider=self.provider_name
                )
            
            # Create categories for this sport
            categories = await self.handler.create_categories_for_sport(sport)
            
            return ProviderResponse(
                success=True,
                data=categories,
                provider=self.provider_name
            )
            
        except Exception as e:
            return self._create_error_response(e, "get_categories")
    
    async def get_games(self, sport: Sport, date_from: Optional[datetime] = None,
                       date_to: Optional[datetime] = None) -> ProviderResponse:
        """Get games for a sport"""
        try:
            sport_key = self.handler.get_sport_key_for_api(sport)
            if not sport_key:
                return ProviderResponse(
                    success=False,
                    error=f"Sport {sport} not supported by Odds API",
                    provider=self.provider_name
                )
            
            # Prepare request parameters
            params = {
                'markets': 'h2h',  # Get moneyline markets
            }
            
            # Add date filters if provided
            if date_from:
                params['commenceTimeFrom'] = date_from.isoformat()
            if date_to:
                params['commenceTimeTo'] = date_to.isoformat()
            
            # Fetch odds data
            endpoint = f"/sports/{sport_key}/odds"
            odds_data = await self._make_request(endpoint, params)
            
            if not odds_data:
                return ProviderResponse(
                    success=True,
                    data=[],
                    provider=self.provider_name,
                    metadata={'message': f'No games found for {sport.value}'}
                )
            
            # Convert odds data to games using appropriate team matcher
            team_matcher = self._get_team_matcher_for_sport(sport)
            games = await self.handler.odds_data_to_games(odds_data, sport, team_matcher)
            
            return ProviderResponse(
                success=True,
                data=games,
                provider=self.provider_name,
                metadata={
                    'odds_entries': len(odds_data),
                    'games_created': len(games),
                    'sport_key': sport_key
                }
            )
            
        except Exception as e:
            return self._create_error_response(e, "get_games")
    
    async def get_markets(self, game: Game) -> ProviderResponse:
        """Get markets for a specific game"""
        try:
            # Extract markets from game metadata (bookmakers data)
            markets = await self.handler.create_markets_from_bookmakers(game)
            
            return ProviderResponse(
                success=True,
                data=markets,
                provider=self.provider_name,
                metadata={'markets_created': len(markets)}
            )
            
        except Exception as e:
            return self._create_error_response(e, "get_markets")
    
    async def get_quotes(self, market: Market) -> ProviderResponse:
        """Get quotes for a market"""
        try:
            # Extract outcomes from market metadata
            raw_market_data = market.metadata.get('raw_market_data', {})
            outcomes = raw_market_data.get('outcomes', [])
            
            if not outcomes:
                return ProviderResponse(
                    success=True,
                    data=[],
                    provider=self.provider_name,
                    metadata={'message': 'No outcomes available for market'}
                )
            
            # Create quotes from outcomes
            quotes = await self.handler.create_quotes_from_outcomes(market, outcomes)
            
            return ProviderResponse(
                success=True,
                data=quotes,
                provider=self.provider_name,
                metadata={'quotes_created': len(quotes)}
            )
            
        except Exception as e:
            return self._create_error_response(e, "get_quotes")
    
    def _get_team_matcher_for_sport(self, sport: Sport):
        """Get appropriate team matcher for sport"""
        # For now, we'll use NFL team matcher for all sports
        # This could be extended to support sport-specific matchers
        if sport == Sport.NFL:
            return get_team_matcher(Sport.NFL)
        else:
            # For other sports, create a basic matcher or extend the system
            return get_team_matcher(Sport.NFL)  # Placeholder
    
    async def get_available_bookmakers(self, sport: Sport) -> ProviderResponse:
        """Get available bookmakers for a sport (Odds API specific method)"""
        try:
            sport_key = self.handler.get_sport_key_for_api(sport)
            if not sport_key:
                return ProviderResponse(
                    success=False,
                    error=f"Sport {sport} not supported by Odds API",
                    provider=self.provider_name
                )
            
            # Fetch odds data to see available bookmakers
            endpoint = f"/sports/{sport_key}/odds"
            params = {'markets': 'h2h'}
            
            odds_data = await self._make_request(endpoint, params)
            
            # Extract unique bookmakers
            bookmakers = set()
            for game_data in odds_data:
                for bookmaker_data in game_data.get('bookmakers', []):
                    bookmakers.add(bookmaker_data.get('key'))
            
            return ProviderResponse(
                success=True,
                data=list(bookmakers),
                provider=self.provider_name,
                metadata={'sport_key': sport_key, 'games_checked': len(odds_data)}
            )
            
        except Exception as e:
            return self._create_error_response(e, "get_available_bookmakers")
    
    async def get_usage_info(self) -> ProviderResponse:
        """Get API usage information (Odds API specific method)"""
        try:
            # The Odds API returns usage info in response headers
            # We'll make a small request to check usage
            endpoint = "/sports"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.default_timeout)) as session:
                params = self.auth.get_auth_params()
                headers = self.auth.get_auth_headers()
                
                async with session.get(f"{self.base_url}{endpoint}", params=params, headers=headers) as response:
                    usage_info = {}
                    
                    # Extract usage from headers
                    if 'x-requests-remaining' in response.headers:
                        usage_info['requests_remaining'] = response.headers['x-requests-remaining']
                    if 'x-requests-used' in response.headers:
                        usage_info['requests_used'] = response.headers['x-requests-used']
                    if 'x-ratelimit-remaining' in response.headers:
                        usage_info['rate_limit_remaining'] = response.headers['x-ratelimit-remaining']
                    
                    return ProviderResponse(
                        success=True,
                        data=usage_info,
                        provider=self.provider_name,
                        metadata={'timestamp': datetime.utcnow().isoformat()}
                    )
                    
        except Exception as e:
            return self._create_error_response(e, "get_usage_info")


# Allow running as script for testing
if __name__ == "__main__":
    # Import configuration after path is set
    from config.config import get_odds_api_config
    
    async def test_client():
        """Test the Odds API client"""
        print("=== Testing Odds API Client ===")
        
        # Get configuration
        config = get_odds_api_config()
        if not config.get('api_key'):
            print("ERROR: No Odds API configuration found")
            return
        
        print(f"API Key: {config['api_key'][:8]}...")
        
        # Test client
        try:
            client = OddsAPIClient(config)
            print("OK: Client created successfully")
            
            # Test authentication
            auth_result = await client.authenticate()
            print(f"Authentication: {'OK' if auth_result else 'ERROR'}")
            
            if auth_result:
                # Test getting sports
                sports_response = await client.get_sports()
                if sports_response.success:
                    print(f"OK: Sports: {len(sports_response.data)} available")
                    print(f"  {[s.name for s in sports_response.data]}")
                else:
                    print(f"ERROR: Sports error: {sports_response.error}")
                
                # Test getting NFL games
                games_response = await client.get_games(Sport.NFL)
                if games_response.success:
                    print(f"OK: NFL Games: {len(games_response.data)} available")
                    if games_response.data:
                        sample = games_response.data[0]
                        print(f"  Sample: {sample.away_team.nickname} @ {sample.home_team.nickname}")
                else:
                    print(f"ERROR: Games error: {games_response.error}")
            
        except Exception as e:
            print(f"ERROR: Client test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("Odds API Client Test")
    print("=" * 30)
    asyncio.run(test_client())