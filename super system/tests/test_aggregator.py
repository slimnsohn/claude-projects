#!/usr/bin/env python3
"""
Tests for the market data aggregator
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from market_data.aggregator import MarketDataAggregator
from market_data.base import DataProvider
from models import Game, Odds
from config.constants import Sport, Provider, BetType

class MockDataProvider(DataProvider):
    """Mock data provider for testing"""
    
    def __init__(self, provider_name: str, games_data: list = None):
        super().__init__(provider_name)
        self.games_data = games_data or []
    
    def fetch_games(self, sport: str, date=None):
        return self.games_data
    
    def parse_games(self, raw_data):
        return raw_data
    
    def normalize_games(self, parsed_data):
        # Return pre-built Game objects
        return parsed_data

class TestMarketDataAggregator:
    """Test cases for MarketDataAggregator"""
    
    def create_sample_game(self, game_id: str, provider: Provider, home_team: str = "KC", away_team: str = "BUF"):
        """Create a sample game for testing"""
        game = Game(
            game_id=game_id,
            sport=Sport.NFL,
            home_team=home_team,
            away_team=away_team,
            start_time=datetime.now() + timedelta(days=1)
        )
        game.add_provider_id(provider, game_id)
        return game
    
    def create_sample_odds(self, provider: Provider, bet_type: BetType, **kwargs):
        """Create sample odds for testing"""
        return Odds(
            provider=provider,
            bet_type=bet_type,
            timestamp=datetime.now(),
            **kwargs
        )
    
    def test_aggregator_initialization(self):
        """Test aggregator initialization"""
        # Test with default providers
        aggregator = MarketDataAggregator()
        assert len(aggregator.providers) == 3
        assert Provider.ODDS_API in aggregator.providers
        assert Provider.KALSHI in aggregator.providers
        assert Provider.POLYMARKET in aggregator.providers
        
        # Test with custom providers
        custom_providers = [Provider.ODDS_API]
        aggregator = MarketDataAggregator(providers=custom_providers)
        assert len(aggregator.providers) == 1
        assert Provider.ODDS_API in aggregator.providers
    
    def test_manual_client_addition(self):
        """Test manually adding clients"""
        aggregator = MarketDataAggregator(providers=[])
        
        # Create mock client
        mock_client = MockDataProvider("test_provider")
        
        # Add client
        aggregator.add_client(Provider.ODDS_API, mock_client)
        
        assert Provider.ODDS_API in aggregator.clients
        assert aggregator.clients[Provider.ODDS_API] == mock_client
    
    def test_game_deduplication(self):
        """Test that identical games from different providers are deduplicated"""
        aggregator = MarketDataAggregator(providers=[])
        
        # Create identical games from different providers
        game1 = self.create_sample_game("odds_123", Provider.ODDS_API)
        game2 = self.create_sample_game("kalshi_456", Provider.KALSHI, "KC", "BUF")  # Same teams/time
        
        # Add different odds to each game
        odds1 = self.create_sample_odds(Provider.ODDS_API, BetType.MONEYLINE, home_ml=-110, away_ml=100)
        odds2 = self.create_sample_odds(Provider.KALSHI, BetType.MONEYLINE, home_ml=-105, away_ml=95)
        
        game1.add_odds("odds_api_ml", odds1)
        game2.add_odds("kalshi_ml", odds2)
        
        # Create mock clients
        odds_client = MockDataProvider("odds_api", [game1])
        kalshi_client = MockDataProvider("kalshi", [game2])
        
        aggregator.add_client(Provider.ODDS_API, odds_client)
        aggregator.add_client(Provider.KALSHI, kalshi_client)
        
        # Get all games
        games = aggregator.get_all_games(Sport.NFL)
        
        # Should have only 1 game (deduplicated)
        assert len(games) == 1
        
        # Should have provider IDs from both providers
        merged_game = games[0]
        assert len(merged_game.provider_ids) == 2
        assert Provider.ODDS_API in merged_game.provider_ids
        assert Provider.KALSHI in merged_game.provider_ids
        
        # Should have odds from both providers
        assert len(merged_game.odds) == 2
        assert "odds_api_ml" in merged_game.odds
        assert "kalshi_ml" in merged_game.odds
    
    def test_best_odds_selection(self):
        """Test best odds selection logic"""
        aggregator = MarketDataAggregator(providers=[])
        
        # Create game with multiple odds
        game = self.create_sample_game("test_game", Provider.ODDS_API)
        
        # Add moneyline odds from different providers
        odds1 = self.create_sample_odds(Provider.ODDS_API, BetType.MONEYLINE, home_ml=-110, away_ml=100)
        odds2 = self.create_sample_odds(Provider.KALSHI, BetType.MONEYLINE, home_ml=-105, away_ml=105)  # Better odds
        
        game.add_odds("odds_api_ml", odds1)
        game.add_odds("kalshi_ml", odds2)
        
        # Get best odds
        best_odds = aggregator.get_best_odds(game, BetType.MONEYLINE)
        
        # Should select better odds for each side
        assert "home" in best_odds
        assert "away" in best_odds
        
        # Kalshi has better home odds (-105 vs -110)
        assert best_odds["home"].provider == Provider.KALSHI
        assert best_odds["home"].home_ml == -105
        
        # Kalshi also has better away odds (+105 vs +100)
        assert best_odds["away"].provider == Provider.KALSHI
        assert best_odds["away"].away_ml == 105
    
    def test_arbitrage_detection(self):
        """Test arbitrage opportunity detection"""
        aggregator = MarketDataAggregator(providers=[])
        
        # Create game
        game = self.create_sample_game("arb_game", Provider.ODDS_API)
        
        # Create odds that allow arbitrage
        # Home: +120 (implied prob: 45.45%)
        # Away: +130 (implied prob: 43.48%)
        # Total: 88.93% < 100% = arbitrage opportunity
        odds1 = self.create_sample_odds(Provider.ODDS_API, BetType.MONEYLINE, home_ml=120, away_ml=100)
        odds2 = self.create_sample_odds(Provider.KALSHI, BetType.MONEYLINE, home_ml=100, away_ml=130)
        
        game.add_odds("odds_api_ml", odds1)
        game.add_odds("kalshi_ml", odds2)
        
        # Find arbitrage
        arb = aggregator.find_arbitrage_opportunities(game, BetType.MONEYLINE)
        
        assert arb is not None
        assert arb["type"] == "arbitrage"
        assert arb["total_probability"] < 1.0
        assert arb["profit_margin"] > 0.0
        
        # Check bet distribution
        assert "home_bet" in arb
        assert "away_bet" in arb
        
        # Should recommend better odds for each side
        assert arb["home_bet"]["odds"] == 120  # Better home odds from odds_api
        assert arb["away_bet"]["odds"] == 130  # Better away odds from kalshi
    
    def test_no_arbitrage_normal_odds(self):
        """Test that normal odds don't show arbitrage opportunities"""
        aggregator = MarketDataAggregator(providers=[])
        
        # Create game with normal odds (no arbitrage)
        game = self.create_sample_game("normal_game", Provider.ODDS_API)
        
        # Normal odds that don't allow arbitrage
        odds = self.create_sample_odds(Provider.ODDS_API, BetType.MONEYLINE, home_ml=-110, away_ml=-110)
        game.add_odds("normal_odds", odds)
        
        # Should not find arbitrage
        arb = aggregator.find_arbitrage_opportunities(game, BetType.MONEYLINE)
        assert arb is None
    
    def test_provider_status(self):
        """Test provider status reporting"""
        aggregator = MarketDataAggregator(providers=[Provider.ODDS_API, Provider.KALSHI])
        
        # Add only one client
        mock_client = MockDataProvider("odds_api")
        aggregator.add_client(Provider.ODDS_API, mock_client)
        
        status = aggregator.get_provider_status()
        
        assert status[Provider.ODDS_API] == "active"
        assert status[Provider.KALSHI] == "unavailable"
    
    def test_single_provider_fetch(self):
        """Test fetching from a single provider"""
        aggregator = MarketDataAggregator(providers=[])
        
        # Create game data
        game = self.create_sample_game("single_game", Provider.ODDS_API)
        
        # Create mock client
        mock_client = MockDataProvider("odds_api", [game])
        aggregator.add_client(Provider.ODDS_API, mock_client)
        
        # Fetch from specific provider
        games = aggregator.get_games_by_provider(Sport.NFL, Provider.ODDS_API)
        
        assert len(games) == 1
        assert games[0] == game
    
    def test_empty_results(self):
        """Test handling of empty results from providers"""
        aggregator = MarketDataAggregator(providers=[])
        
        # Add client that returns no games
        empty_client = MockDataProvider("empty", [])
        aggregator.add_client(Provider.ODDS_API, empty_client)
        
        games = aggregator.get_all_games(Sport.NFL)
        assert len(games) == 0
    
    def test_client_error_handling(self):
        """Test error handling when clients fail"""
        aggregator = MarketDataAggregator(providers=[])
        
        # Create a client that raises an exception
        def failing_get_games(*args, **kwargs):
            raise Exception("API Error")
        
        mock_client = MockDataProvider("failing")
        mock_client.get_games = failing_get_games
        
        aggregator.add_client(Provider.ODDS_API, mock_client)
        
        # Should handle the error gracefully and return empty list
        games = aggregator.get_all_games(Sport.NFL)
        assert len(games) == 0

def run_tests():
    """Run all tests manually"""
    print("Running aggregator tests...")
    
    test_instance = TestMarketDataAggregator()
    
    # Get all test methods
    test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
    
    for method_name in test_methods:
        try:
            method = getattr(test_instance, method_name)
            method()
            print(f"  ✅ {method_name}")
        except Exception as e:
            print(f"  ❌ {method_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ Aggregator tests completed!")

if __name__ == "__main__":
    run_tests()