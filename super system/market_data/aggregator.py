from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict
import logging

from config.constants import Sport, BetType, Provider
from models import Game, Odds
from .base import DataProvider

class MarketDataAggregator:
    """Central aggregator for all market data sources"""
    
    def __init__(self, providers: Optional[List[Provider]] = None):
        self.providers = providers or [Provider.ODDS_API, Provider.KALSHI, Provider.POLYMARKET]
        self.clients = {}
        self.logger = self._setup_logger()
        
        # Initialize clients as they become available
        self._initialize_available_clients()
    
    def _setup_logger(self):
        """Setup logger for aggregator"""
        logger = logging.getLogger("market_data_aggregator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_available_clients(self):
        """Initialize clients that are available"""
        for provider in self.providers:
            try:
                if provider == Provider.ODDS_API:
                    # Import only when needed
                    from .odds_api.production.client import OddsAPIClient
                    self.clients[provider] = OddsAPIClient()
                    self.logger.info(f"Initialized {provider.value} client")
                    
                elif provider == Provider.KALSHI:
                    from .kalshi.production.client import KalshiClient
                    self.clients[provider] = KalshiClient()
                    self.logger.info(f"Initialized {provider.value} client")
                    
                elif provider == Provider.POLYMARKET:
                    from .polymarket.production.client import PolymarketClient
                    self.clients[provider] = PolymarketClient()
                    self.logger.info(f"Initialized {provider.value} client")
                    
            except ImportError as e:
                self.logger.warning(f"Could not initialize {provider.value} client: {e}")
            except Exception as e:
                self.logger.error(f"Error initializing {provider.value} client: {e}")
    
    def add_client(self, provider: Provider, client: DataProvider):
        """Manually add a client"""
        self.clients[provider] = client
        self.logger.info(f"Manually added {provider.value} client")
    
    def get_all_games(self, sport: Sport, date: Optional[datetime] = None) -> List[Game]:
        """
        Fetch and aggregate games from all providers
        Returns deduplicated list of games with odds from all sources
        """
        if not self.clients:
            self.logger.warning("No clients available")
            return []
        
        self.logger.info(f"Aggregating {sport.value} games from {len(self.clients)} providers")
        
        # Use a dictionary to deduplicate games by their hash
        all_games = {}
        
        for provider, client in self.clients.items():
            try:
                self.logger.info(f"Fetching from {provider.value}")
                provider_games = client.get_games(sport.value, date)
                self.logger.info(f"Retrieved {len(provider_games)} games from {provider.value}")
                
                for game in provider_games:
                    # Use game hash for deduplication
                    game_key = hash(game)
                    
                    if game_key in all_games:
                        # Merge with existing game
                        existing_game = all_games[game_key]
                        
                        # Merge provider IDs
                        for p, pid in game.provider_ids.items():
                            existing_game.add_provider_id(p, pid)
                        
                        # Merge odds
                        for odds_key, odds in game.odds.items():
                            existing_game.add_odds(odds_key, odds)
                        
                        # Update metadata if missing
                        if not existing_game.venue and game.venue:
                            existing_game.venue = game.venue
                        if not existing_game.status and game.status:
                            existing_game.status = game.status
                            
                        self.logger.debug(f"Merged game: {game}")
                    else:
                        all_games[game_key] = game
                        self.logger.debug(f"Added new game: {game}")
                        
            except Exception as e:
                self.logger.error(f"Error fetching from {provider.value}: {e}")
                continue
        
        games_list = list(all_games.values())
        self.logger.info(f"Aggregated {len(games_list)} unique games")
        
        # Sort by start time
        games_list.sort(key=lambda x: x.start_time)
        
        return games_list
    
    def get_best_odds(self, game: Game, bet_type: BetType) -> Dict[str, Odds]:
        """Find best odds across all providers for a specific bet type"""
        best_odds = {
            'home': None,
            'away': None, 
            'over': None,
            'under': None,
            'home_spread': None,
            'away_spread': None
        }
        
        self.logger.debug(f"Finding best {bet_type.value} odds for {game}")
        
        for odds_key, odds in game.odds.items():
            if odds.bet_type != bet_type:
                continue
            
            if bet_type == BetType.MONEYLINE:
                # Better moneyline = higher positive odds or less negative odds
                if odds.home_ml is not None:
                    if (best_odds['home'] is None or 
                        self._is_better_odds(odds.home_ml, best_odds['home'].home_ml)):
                        best_odds['home'] = odds
                
                if odds.away_ml is not None:
                    if (best_odds['away'] is None or 
                        self._is_better_odds(odds.away_ml, best_odds['away'].away_ml)):
                        best_odds['away'] = odds
                        
            elif bet_type == BetType.TOTAL:
                if odds.over_odds is not None:
                    if (best_odds['over'] is None or 
                        self._is_better_odds(odds.over_odds, best_odds['over'].over_odds)):
                        best_odds['over'] = odds
                
                if odds.under_odds is not None:
                    if (best_odds['under'] is None or 
                        self._is_better_odds(odds.under_odds, best_odds['under'].under_odds)):
                        best_odds['under'] = odds
                        
            elif bet_type == BetType.SPREAD:
                if odds.home_spread_odds is not None:
                    if (best_odds['home_spread'] is None or 
                        self._is_better_odds(odds.home_spread_odds, best_odds['home_spread'].home_spread_odds)):
                        best_odds['home_spread'] = odds
                
                if odds.away_spread_odds is not None:
                    if (best_odds['away_spread'] is None or 
                        self._is_better_odds(odds.away_spread_odds, best_odds['away_spread'].away_spread_odds)):
                        best_odds['away_spread'] = odds
        
        # Filter out None values
        return {k: v for k, v in best_odds.items() if v is not None}
    
    def _is_better_odds(self, new_odds: int, current_best: int) -> bool:
        """
        Determine if new_odds is better than current_best for betting
        Better odds = higher potential payout
        """
        if current_best is None:
            return True
        
        # For positive odds, higher is better
        if new_odds > 0 and current_best > 0:
            return new_odds > current_best
        # For negative odds, closer to 0 is better (less negative)
        elif new_odds < 0 and current_best < 0:
            return new_odds > current_best  # -110 is better than -120
        # Positive odds are generally better than negative odds
        elif new_odds > 0 and current_best < 0:
            return True
        elif new_odds < 0 and current_best > 0:
            return False
        
        return False
    
    def find_arbitrage_opportunities(self, game: Game, bet_type: BetType) -> Optional[Dict]:
        """
        Find potential arbitrage opportunities for a game
        Returns dictionary with arbitrage details if found, None otherwise
        """
        best_odds = self.get_best_odds(game, bet_type)
        
        if bet_type == BetType.MONEYLINE:
            if 'home' not in best_odds or 'away' not in best_odds:
                return None
            
            home_odds = best_odds['home'].home_ml
            away_odds = best_odds['away'].away_ml
            
            # Convert to implied probabilities
            home_prob = self._american_to_probability(home_odds)
            away_prob = self._american_to_probability(away_odds)
            
            total_prob = home_prob + away_prob
            
            if total_prob < 1.0:  # Arbitrage opportunity
                return {
                    'type': 'arbitrage',
                    'bet_type': bet_type,
                    'total_probability': total_prob,
                    'profit_margin': 1.0 - total_prob,
                    'home_bet': {
                        'odds': home_odds,
                        'provider': best_odds['home'].provider,
                        'stake_percentage': home_prob / total_prob
                    },
                    'away_bet': {
                        'odds': away_odds,
                        'provider': best_odds['away'].provider,
                        'stake_percentage': away_prob / total_prob
                    }
                }
        
        return None
    
    def _american_to_probability(self, american_odds: int) -> float:
        """Convert American odds to implied probability"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def get_provider_status(self) -> Dict[Provider, str]:
        """Get status of all configured providers"""
        status = {}
        for provider in self.providers:
            if provider in self.clients:
                status[provider] = "active"
            else:
                status[provider] = "unavailable"
        return status
    
    def refresh_all_clients(self):
        """Refresh/reinitialize all clients"""
        self.clients.clear()
        self._initialize_available_clients()
    
    def get_games_by_provider(self, sport: Sport, provider: Provider, date: Optional[datetime] = None) -> List[Game]:
        """Get games from a specific provider only"""
        if provider not in self.clients:
            self.logger.error(f"Provider {provider.value} not available")
            return []
        
        try:
            return self.clients[provider].get_games(sport.value, date)
        except Exception as e:
            self.logger.error(f"Error fetching from {provider.value}: {e}")
            return []