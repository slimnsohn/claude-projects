"""
Kalshi Market Data Client
Implements Kalshi prediction market API integration with unified interface.
Uses public API endpoints (no authentication required for market data).
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from market_data_core.base_client import BaseMarketDataClient
from market_data_core.models import ProviderResponse, Sport, Game, Market, Quote, Category
from market_data_core.exceptions import MarketDataError, AuthenticationError
from market_data_core.utils import RateLimiter
from market_data_core import get_team_matcher

from .handler import KalshiResponseHandler


class KalshiClient(BaseMarketDataClient):
    """Kalshi market data client implementation"""
    
    # Kalshi league/sport mappings
    LEAGUE_MAP = {
        Sport.NFL: 'KXNFLGAME',
        Sport.MLB: 'KXMLBGAME', 
        Sport.NBA: 'KXNBAGAME',
        Sport.NHL: 'KXNHLGAME',
    }
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Kalshi client (public API, no authentication required)"""
        super().__init__("kalshi", config)
        
        # API configuration - use public endpoints
        self.production_url = 'https://api.elections.kalshi.com/trade-api/v2'
        self.demo_url = 'https://demo-api.kalshi.co/trade-api/v2' 
        self.base_url = self.production_url  # Start with production
        
        # Rate limiting (60 requests per minute)
        rate_limit_config = config.get('rate_limits', {})
        max_requests = rate_limit_config.get('kalshi_requests_per_minute', 60)
        self.rate_limiter = RateLimiter(max_requests, 60)
        
        # Response handler for data transformation
        self.handler = KalshiResponseHandler()
        
        # Team matcher for NFL team matching
        self.team_matcher = get_team_matcher(Sport.NFL)
        
        # Default timeout
        self.timeout_config = config.get('timeouts', {})
        self.default_timeout = self.timeout_config.get('default_timeout', 30)
        
        # Mark as authenticated since we use public endpoints
        self._authenticated = True
    
    async def authenticate(self) -> bool:
        """Test connection to public API (no authentication required)"""
        try:
            await self.rate_limiter.async_wait_if_needed()
            
            # Test both endpoints like the working client
            endpoints_to_try = [
                (self.production_url, "production"),
                (self.demo_url, "demo")
            ]
            
            for base_url, source_name in endpoints_to_try:
                try:
                    # Test with a simple markets request
                    url = f"{base_url}/markets"
                    params = {'limit': 1}  # Just test with one market
                    
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.default_timeout)) as session:
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                self.base_url = base_url  # Use the working endpoint
                                self._authenticated = True
                                self.logger.info(f"Successfully connected to Kalshi {source_name} API")
                                return True
                            else:
                                self.logger.warning(f"Kalshi {source_name} API returned {response.status}")
                                
                except Exception as e:
                    self.logger.warning(f"Error testing {source_name} endpoint: {e}")
                    continue
            
            self.logger.error("Failed to connect to any Kalshi endpoint")
            return False
            
        except Exception as e:
            self.logger.error(f"Connection test exception: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check authentication status"""
        return self._authenticated
    
    async def _make_request(self, method: str, path: str, params: Optional[Dict] = None) -> Dict:
        """Make public API request to Kalshi"""
        if not self.is_authenticated():
            if not await self.authenticate():
                raise MarketDataError("Failed to connect to Kalshi API")
        
        await self.rate_limiter.async_wait_if_needed()
        
        # Prepare public API request (no auth headers needed)
        url = f"{self.base_url}{path}"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.default_timeout)) as session:
                async with session.request(method, url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise MarketDataError(f"Kalshi API request failed {response.status}: {error_text}")
                        
        except aiohttp.ClientError as e:
            raise MarketDataError(f"Network error: {e}")
    
    async def _fetch_all_markets(self, series_ticker: str) -> List[Dict]:
        """Fetch all markets for a series ticker with pagination (like working client)"""
        try:
            all_markets = []
            cursor = None
            page = 1
            
            self.logger.info(f"Fetching markets for {series_ticker}...")
            
            while True:
                params = {
                    'series_ticker': series_ticker,
                    'limit': 200
                }
                if cursor:
                    params['cursor'] = cursor
                
                data = await self._make_request("GET", "/markets", params)
                markets = data.get('markets', [])
                all_markets.extend(markets)
                
                self.logger.debug(f"Page {page}: {len(markets)} markets (total: {len(all_markets)})")
                
                # Check for more pages
                cursor = data.get('cursor')
                if not cursor or len(markets) == 0:
                    break
                
                page += 1
            
            self.logger.info(f"Found {len(all_markets)} total markets for {series_ticker}")
            return all_markets
            
        except Exception as e:
            self.logger.error(f"Error fetching markets for {series_ticker}: {e}")
            return []
    
    async def get_sports(self) -> ProviderResponse:
        """Get available sports from Kalshi"""
        try:
            # Return supported sports based on our league map
            supported_sports = list(self.LEAGUE_MAP.keys())
            
            return ProviderResponse(
                success=True,
                data=supported_sports,
                provider=self.provider_name,
                metadata={'note': 'Supported sports based on Kalshi series tickers'}
            )
            
        except Exception as e:
            return self._create_error_response(e, "get_sports")
    
    async def get_categories(self, sport: Sport) -> ProviderResponse:
        """Get categories for a sport (Kalshi doesn't have traditional categories)"""
        try:
            if sport not in self.LEAGUE_MAP:
                return ProviderResponse(
                    success=False,
                    error=f"Sport {sport} not supported by Kalshi",
                    provider=self.provider_name
                )
            
            # Kalshi doesn't have categories like traditional sportsbooks
            # Each sport is essentially one category
            categories = [
                Category(
                    category_id=self.LEAGUE_MAP[sport],
                    name=f"{sport.value.upper()} Games",
                    sport=sport,
                    description=f"Prediction markets for {sport.value.upper()} games",
                    metadata={'series_ticker': self.LEAGUE_MAP[sport]}
                )
            ]
            
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
            if sport not in self.LEAGUE_MAP:
                return ProviderResponse(
                    success=False,
                    error=f"Sport {sport} not supported by Kalshi",
                    provider=self.provider_name
                )
            
            series_ticker = self.LEAGUE_MAP[sport]
            
            # Fetch markets for this sport
            markets_data = await self._fetch_all_markets(series_ticker)
            
            if not markets_data:
                return ProviderResponse(
                    success=True,
                    data=[],
                    provider=self.provider_name,
                    metadata={'message': f'No active markets found for {sport.value}'}
                )
            
            # Convert markets to games
            games = await self.handler.markets_to_games(markets_data, sport, self.team_matcher)
            
            # Filter by date range if provided
            if date_from or date_to:
                filtered_games = []
                for game in games:
                    if date_from and game.game_date < date_from:
                        continue
                    if date_to and game.game_date > date_to:
                        continue
                    filtered_games.append(game)
                games = filtered_games
            
            return ProviderResponse(
                success=True,
                data=games,
                provider=self.provider_name,
                metadata={'markets_count': len(markets_data), 'games_count': len(games)}
            )
            
        except Exception as e:
            return self._create_error_response(e, "get_games")
    
    async def get_markets(self, game: Game) -> ProviderResponse:
        """Get markets for a specific game"""
        try:
            # Use game metadata to find associated markets
            game_markets = []
            
            if 'kalshi_markets' in game.metadata:
                # Game already has associated Kalshi market data
                market_data = game.metadata['kalshi_markets']
                markets = await self.handler.create_markets_from_data(market_data, game)
                game_markets.extend(markets)
            else:
                # Search for markets by team names
                series_ticker = self.LEAGUE_MAP.get(game.sport)
                if series_ticker:
                    all_markets = await self._fetch_all_markets(series_ticker)
                    # Filter markets for this specific game
                    for market_data in all_markets:
                        if self.handler.is_market_for_game(market_data, game):
                            market = await self.handler.create_market_from_data(market_data, game)
                            if market:
                                game_markets.append(market)
            
            return ProviderResponse(
                success=True,
                data=game_markets,
                provider=self.provider_name
            )
            
        except Exception as e:
            return self._create_error_response(e, "get_markets")
    
    async def get_quotes(self, market: Market) -> ProviderResponse:
        """Get quotes for a market"""
        try:
            market_ticker = market.metadata.get('kalshi_ticker')
            if not market_ticker:
                return ProviderResponse(
                    success=False,
                    error="Market missing Kalshi ticker",
                    provider=self.provider_name
                )
            
            # Get orderbook/market data for quotes
            market_data = await self._make_request("GET", f"/markets/{market_ticker}")
            
            if not market_data:
                return ProviderResponse(
                    success=False,
                    error=f"No market data found for ticker {market_ticker}",
                    provider=self.provider_name
                )
            
            # Convert market data to quotes
            quotes = await self.handler.create_quotes_from_market(market_data, market)
            
            return ProviderResponse(
                success=True,
                data=quotes,
                provider=self.provider_name
            )
            
        except Exception as e:
            return self._create_error_response(e, "get_quotes")
    
    async def _fetch_all_markets(self, series_ticker: str) -> List[Dict]:
        """Fetch all markets for a series ticker with pagination"""
        try:
            all_markets = []
            cursor = None
            page = 1
            max_pages = 100  # Safety limit
            
            while page <= max_pages:
                params = {
                    'series_ticker': series_ticker,
                    'status': 'open',  # Only get open markets
                    'limit': 1000  # Max limit
                }
                
                if cursor:
                    params['cursor'] = cursor
                
                data = await self._make_request("GET", "/markets", params)
                
                markets = data.get('markets', [])
                if not markets:
                    break
                
                all_markets.extend(markets)
                
                # Check for next page
                cursor = data.get('cursor')
                if not cursor:
                    break
                
                page += 1
            
            self.logger.info(f"Fetched {len(all_markets)} markets for {series_ticker}")
            return all_markets
            
        except Exception as e:
            self.logger.error(f"Error fetching markets for {series_ticker}: {e}")
            return []