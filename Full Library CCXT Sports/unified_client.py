"""
Unified Sports Market Data Client
Provides a single interface to multiple market data providers (Kalshi, Odds API, etc.)
"""

import asyncio
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from market_data_core.models import (
    Sport, Game, Market, Quote, Category, ProviderResponse
)
from market_data_core.exceptions import MarketDataError, AuthenticationError
from market_data_core.utils import setup_logging
from market_data_kalshi import KalshiClient
from market_data_odds import OddsAPIClient


class ProviderType(Enum):
    """Available market data providers"""
    KALSHI = "kalshi"
    ODDS_API = "odds_api"


@dataclass
class ProviderConfig:
    """Configuration for a market data provider"""
    provider_type: ProviderType
    config: Dict[str, Any]
    enabled: bool = True
    priority: int = 1  # Lower number = higher priority


class ArbitrageOpportunity:
    """Represents a potential arbitrage opportunity between providers"""
    
    def __init__(self, game: Game, opportunities: List[Dict]):
        self.game = game
        self.opportunities = opportunities
        self.total_edge = sum(opp.get('edge', 0) for opp in opportunities)
        self.providers_involved = set(opp.get('provider') for opp in opportunities)
    
    def __str__(self):
        return f"Arbitrage: {self.game.away_team.nickname} @ {self.game.home_team.nickname} - Edge: {self.total_edge:.2%}"


class UnifiedMarketDataClient:
    """Unified client for accessing multiple market data providers"""
    
    def __init__(self, provider_configs: List[ProviderConfig]):
        """
        Initialize unified client
        
        Args:
            provider_configs: List of provider configurations
        """
        self.logger = setup_logging("unified_client")
        self.providers = {}
        self.provider_configs = {pc.provider_type: pc for pc in provider_configs}
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured providers"""
        for provider_type, config in self.provider_configs.items():
            if not config.enabled:
                continue
                
            try:
                if provider_type == ProviderType.KALSHI:
                    client = KalshiClient(config.config)
                elif provider_type == ProviderType.ODDS_API:
                    client = OddsAPIClient(config.config)
                else:
                    self.logger.warning(f"Unknown provider type: {provider_type}")
                    continue
                
                self.providers[provider_type] = {
                    'client': client,
                    'priority': config.priority,
                    'enabled': config.enabled
                }
                
                self.logger.info(f"Initialized provider: {provider_type.value}")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize provider {provider_type.value}: {e}")
    
    def get_enabled_providers(self) -> List[ProviderType]:
        """Get list of enabled providers"""
        return [
            provider_type for provider_type, info in self.providers.items()
            if info['enabled']
        ]
    
    async def authenticate_all(self) -> Dict[ProviderType, bool]:
        """Authenticate with all providers"""
        results = {}
        
        for provider_type, info in self.providers.items():
            if not info['enabled']:
                results[provider_type] = False
                continue
                
            try:
                client = info['client']
                success = await client.authenticate()
                results[provider_type] = success
                
                if success:
                    self.logger.info(f"Authentication successful: {provider_type.value}")
                else:
                    self.logger.warning(f"Authentication failed: {provider_type.value}")
                    
            except Exception as e:
                self.logger.error(f"Authentication error for {provider_type.value}: {e}")
                results[provider_type] = False
        
        return results
    
    async def get_sports(self, provider_filter: Optional[List[ProviderType]] = None) -> Dict[ProviderType, ProviderResponse]:
        """Get available sports from all or filtered providers"""
        providers_to_query = provider_filter or list(self.providers.keys())
        results = {}
        
        tasks = []
        for provider_type in providers_to_query:
            if provider_type in self.providers and self.providers[provider_type]['enabled']:
                client = self.providers[provider_type]['client']
                tasks.append((provider_type, client.get_sports()))
        
        # Execute all requests concurrently
        if tasks:
            responses = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
            
            for (provider_type, _), response in zip(tasks, responses):
                if isinstance(response, Exception):
                    results[provider_type] = ProviderResponse(
                        success=False,
                        error=str(response),
                        provider=provider_type.value
                    )
                else:
                    results[provider_type] = response
        
        return results
    
    async def get_games(self, sport: Sport, 
                       date_from: Optional[datetime] = None,
                       date_to: Optional[datetime] = None,
                       provider_filter: Optional[List[ProviderType]] = None) -> Dict[ProviderType, ProviderResponse]:
        """Get games from all or filtered providers"""
        providers_to_query = provider_filter or list(self.providers.keys())
        results = {}
        
        tasks = []
        for provider_type in providers_to_query:
            if provider_type in self.providers and self.providers[provider_type]['enabled']:
                client = self.providers[provider_type]['client']
                tasks.append((provider_type, client.get_games(sport, date_from, date_to)))
        
        # Execute all requests concurrently
        if tasks:
            responses = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
            
            for (provider_type, _), response in zip(tasks, responses):
                if isinstance(response, Exception):
                    results[provider_type] = ProviderResponse(
                        success=False,
                        error=str(response),
                        provider=provider_type.value
                    )
                else:
                    results[provider_type] = response
        
        return results
    
    async def get_unified_games(self, sport: Sport,
                               date_from: Optional[datetime] = None,
                               date_to: Optional[datetime] = None) -> List[Game]:
        """Get unified list of games from all providers, with cross-provider matching"""
        all_results = await self.get_games(sport, date_from, date_to)
        
        # Collect all games from successful responses
        all_games = []
        for provider_type, response in all_results.items():
            if response.success and response.data:
                for game in response.data:
                    # Tag each game with its source provider
                    game.metadata = game.metadata or {}
                    game.metadata['source_provider'] = provider_type.value
                    all_games.append(game)
        
        # Remove duplicates based on team matching and date proximity
        unified_games = self._deduplicate_games(all_games)
        
        self.logger.info(f"Unified {len(all_games)} games from {len(all_results)} providers into {len(unified_games)} unique games")
        
        return unified_games
    
    def _deduplicate_games(self, games: List[Game]) -> List[Game]:
        """Remove duplicate games based on teams and date proximity"""
        unique_games = []
        
        for game in games:
            is_duplicate = False
            
            for existing_game in unique_games:
                # Check if same teams
                same_teams = (
                    self._teams_match(game.home_team, existing_game.home_team) and
                    self._teams_match(game.away_team, existing_game.away_team)
                ) or (
                    self._teams_match(game.home_team, existing_game.away_team) and
                    self._teams_match(game.away_team, existing_game.home_team)
                )
                
                # Check if dates are close (within 6 hours)
                if same_teams and abs((game.game_date - existing_game.game_date).total_seconds()) < 21600:
                    is_duplicate = True
                    
                    # Merge metadata from duplicate
                    existing_game.metadata = existing_game.metadata or {}
                    game_metadata = game.metadata or {}
                    
                    # Add provider sources
                    existing_sources = existing_game.metadata.get('source_providers', [])
                    if isinstance(existing_sources, str):
                        existing_sources = [existing_sources]
                    
                    new_source = game_metadata.get('source_provider')
                    if new_source and new_source not in existing_sources:
                        existing_sources.append(new_source)
                    
                    existing_game.metadata['source_providers'] = existing_sources
                    break
            
            if not is_duplicate:
                unique_games.append(game)
        
        return unique_games
    
    def _teams_match(self, team1, team2) -> bool:
        """Check if two teams are the same"""
        if not team1 or not team2:
            return False
        
        # Exact match
        if team1 == team2:
            return True
        
        # Name-based matching
        return (team1.name.lower() == team2.name.lower() or
                team1.nickname.lower() == team2.nickname.lower())
    
    async def find_arbitrage_opportunities(self, sport: Sport, 
                                         min_edge: float = 0.02,
                                         date_from: Optional[datetime] = None,
                                         date_to: Optional[datetime] = None) -> List[ArbitrageOpportunity]:
        """Find arbitrage opportunities between providers"""
        # Get games from all providers
        unified_games = await self.get_unified_games(sport, date_from, date_to)
        
        arbitrage_opportunities = []
        
        for game in unified_games:
            # Get markets from all providers for this game
            provider_markets = await self._get_markets_for_game_all_providers(game)
            
            # Analyze for arbitrage opportunities
            opportunities = self._analyze_arbitrage_for_game(game, provider_markets, min_edge)
            
            if opportunities:
                arb_opp = ArbitrageOpportunity(game, opportunities)
                if arb_opp.total_edge >= min_edge:
                    arbitrage_opportunities.append(arb_opp)
        
        # Sort by edge (highest first)
        arbitrage_opportunities.sort(key=lambda x: x.total_edge, reverse=True)
        
        return arbitrage_opportunities
    
    async def _get_markets_for_game_all_providers(self, game: Game) -> Dict[ProviderType, List[Market]]:
        """Get markets for a game from all providers"""
        results = {}
        
        tasks = []
        for provider_type, info in self.providers.items():
            if not info['enabled']:
                continue
                
            client = info['client']
            tasks.append((provider_type, client.get_markets(game)))
        
        if tasks:
            responses = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
            
            for (provider_type, _), response in zip(tasks, responses):
                if isinstance(response, Exception):
                    results[provider_type] = []
                elif response.success:
                    results[provider_type] = response.data or []
                else:
                    results[provider_type] = []
        
        return results
    
    def _analyze_arbitrage_for_game(self, game: Game, 
                                   provider_markets: Dict[ProviderType, List[Market]], 
                                   min_edge: float) -> List[Dict]:
        """Analyze arbitrage opportunities for a single game"""
        opportunities = []
        
        # This is a simplified arbitrage analysis
        # In practice, this would be much more sophisticated
        
        # For now, just return empty list - arbitrage analysis is complex
        # and would require matching quotes across different market types
        # and calculating optimal bet sizing
        
        return opportunities
    
    async def get_best_quotes(self, sport: Sport, market_type: str = "moneyline") -> Dict[str, Dict]:
        """Get best quotes for each game across all providers"""
        unified_games = await self.get_unified_games(sport)
        best_quotes = {}
        
        for game in unified_games:
            game_key = f"{game.away_team.nickname}_at_{game.home_team.nickname}"
            
            # Get markets from all providers
            provider_markets = await self._get_markets_for_game_all_providers(game)
            
            # Find best quotes for this game
            game_best = await self._find_best_quotes_for_game(game, provider_markets, market_type)
            
            if game_best:
                best_quotes[game_key] = {
                    'game': game,
                    'best_quotes': game_best
                }
        
        return best_quotes
    
    async def _find_best_quotes_for_game(self, game: Game, 
                                       provider_markets: Dict[ProviderType, List[Market]], 
                                       market_type: str) -> Dict:
        """Find best quotes for a specific game"""
        best_quotes = {}
        
        # This would implement quote comparison logic
        # For now, return empty dict
        
        return best_quotes
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers"""
        health_status = {
            'overall_status': 'healthy',
            'providers': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        for provider_type, info in self.providers.items():
            if not info['enabled']:
                health_status['providers'][provider_type.value] = {
                    'status': 'disabled',
                    'authenticated': False
                }
                continue
            
            try:
                client = info['client']
                
                # Check if client is authenticated
                is_authenticated = client.is_authenticated()
                
                # Try a simple operation (get sports)
                sports_response = await client.get_sports()
                
                status = 'healthy' if sports_response.success else 'unhealthy'
                
                health_status['providers'][provider_type.value] = {
                    'status': status,
                    'authenticated': is_authenticated,
                    'last_response': sports_response.success,
                    'error': None if sports_response.success else sports_response.error
                }
                
            except Exception as e:
                health_status['providers'][provider_type.value] = {
                    'status': 'error',
                    'authenticated': False,
                    'error': str(e)
                }
        
        # Determine overall status
        provider_statuses = [p['status'] for p in health_status['providers'].values()]
        if any(status == 'healthy' for status in provider_statuses):
            health_status['overall_status'] = 'healthy'
        elif any(status == 'unhealthy' for status in provider_statuses):
            health_status['overall_status'] = 'degraded'
        else:
            health_status['overall_status'] = 'unhealthy'
        
        return health_status


# Convenience function to create unified client
def create_unified_client(kalshi_config: Optional[Dict] = None,
                         odds_api_config: Optional[Dict] = None) -> UnifiedMarketDataClient:
    """
    Create unified client with standard configuration
    
    Args:
        kalshi_config: Kalshi API configuration
        odds_api_config: Odds API configuration
        
    Returns:
        Configured UnifiedMarketDataClient
    """
    provider_configs = []
    
    if kalshi_config:
        provider_configs.append(ProviderConfig(
            provider_type=ProviderType.KALSHI,
            config=kalshi_config,
            priority=1
        ))
    
    if odds_api_config:
        provider_configs.append(ProviderConfig(
            provider_type=ProviderType.ODDS_API,
            config=odds_api_config,
            priority=2
        ))
    
    return UnifiedMarketDataClient(provider_configs)


# Example usage
async def example_usage():
    """Example of how to use the unified client"""
    
    # Create client with both providers
    unified_client = create_unified_client(
        kalshi_config={
            'api_key': 'your_kalshi_key',
            'private_key': 'your_private_key',
            'base_url': 'https://demo-api.kalshi.co/trade-api/v2'
        },
        odds_api_config={
            'api_key': 'your_odds_api_key',
            'base_url': 'https://api.the-odds-api.com/v4'
        }
    )
    
    # Authenticate with all providers
    print("Authenticating with providers...")
    auth_results = await unified_client.authenticate_all()
    print(f"Authentication results: {auth_results}")
    
    # Check health
    print("\nChecking provider health...")
    health = await unified_client.health_check()
    print(f"Health status: {health['overall_status']}")
    
    # Get NFL games from all providers
    print("\nGetting NFL games...")
    unified_games = await unified_client.get_unified_games(Sport.NFL)
    print(f"Found {len(unified_games)} unique NFL games")
    
    # Show sample games
    for game in unified_games[:3]:
        sources = game.metadata.get('source_providers', ['unknown'])
        print(f"  {game.away_team.nickname} @ {game.home_team.nickname} - Sources: {sources}")
    
    # Look for arbitrage opportunities
    print("\nLooking for arbitrage opportunities...")
    arbitrage_ops = await unified_client.find_arbitrage_opportunities(Sport.NFL, min_edge=0.01)
    
    if arbitrage_ops:
        print(f"Found {len(arbitrage_ops)} arbitrage opportunities:")
        for opp in arbitrage_ops[:3]:
            print(f"  {opp}")
    else:
        print("No arbitrage opportunities found")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())