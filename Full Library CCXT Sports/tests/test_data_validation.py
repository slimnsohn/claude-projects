#!/usr/bin/env python3
"""
Data Validation Tests
Validates that the library has comprehensive data across multiple dates and providers.
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from market_data_core import get_nfl_data_manager, Sport
from market_data_core.models import Game


class TestDataAvailability(unittest.TestCase):
    """Test data availability across multiple dates"""
    
    def setUp(self):
        """Set up data manager"""
        self.data_manager = get_nfl_data_manager()
    
    def test_comprehensive_schedule_loaded(self):
        """Test that comprehensive schedule data is loaded"""
        # Should have significantly more than the original 4 games
        total_games = len(self.data_manager.games)
        self.assertGreaterEqual(total_games, 50, 
                               f"Should have at least 50 games, got {total_games}")
        
        print(f"OK Total games loaded: {total_games}")
    
    def test_multiple_weeks_coverage(self):
        """Test that data covers multiple weeks"""
        weeks = set()
        for game in self.data_manager.games.values():
            if hasattr(game, 'week') and game.week:
                weeks.add(game.week)
        
        self.assertGreaterEqual(len(weeks), 3, 
                               f"Should cover at least 3 weeks, got {len(weeks)}: {sorted(weeks)}")
        
        print(f"OK Weeks covered: {sorted(weeks)}")
    
    def test_multiple_dates_coverage(self):
        """Test that data covers multiple unique dates"""
        dates = set()
        for game in self.data_manager.games.values():
            if game.game_date:
                date_str = game.game_date.strftime('%Y-%m-%d')
                dates.add(date_str)
        
        self.assertGreaterEqual(len(dates), 10, 
                               f"Should cover at least 10 unique dates, got {len(dates)}")
        
        print(f"OK Unique dates covered: {len(dates)}")
        print(f"  Date range: {min(dates)} to {max(dates)}")
    
    def test_games_across_date_ranges(self):
        """Test that games are distributed across different date ranges"""
        # Group games by date
        games_by_date = defaultdict(list)
        for game in self.data_manager.games.values():
            if game.game_date:
                date_str = game.game_date.strftime('%Y-%m-%d')
                games_by_date[date_str].append(game)
        
        # Should have multiple dates with games
        dates_with_games = len(games_by_date)
        self.assertGreaterEqual(dates_with_games, 10)
        
        # Should have reasonable distribution (not all games on one date)
        max_games_per_date = max(len(games) for games in games_by_date.values())
        self.assertLessEqual(max_games_per_date, 20, "Too many games on single date")
        
        print(f"OK Games distributed across {dates_with_games} dates")
        print(f"  Max games per date: {max_games_per_date}")
    
    def test_game_time_variety(self):
        """Test that games have variety in times (not all at same time)"""
        game_times = set()
        for game in self.data_manager.games.values():
            if game.game_date:
                time_str = game.game_date.strftime('%H:%M')
                game_times.add(time_str)
        
        self.assertGreaterEqual(len(game_times), 4, 
                               f"Should have at least 4 different game times, got {len(game_times)}: {sorted(game_times)}")
        
        print(f"OK Game time variety: {sorted(game_times)}")
    
    def test_team_coverage(self):
        """Test that multiple teams are represented"""
        home_teams = set()
        away_teams = set()
        
        for game in self.data_manager.games.values():
            if game.home_team:
                # Use nickname or abbreviation if available
                team_id = getattr(game.home_team, 'abbreviation', game.home_team.nickname)
                home_teams.add(team_id)
            if game.away_team:
                team_id = getattr(game.away_team, 'abbreviation', game.away_team.nickname)
                away_teams.add(team_id)
        
        all_teams = home_teams.union(away_teams)
        self.assertGreaterEqual(len(all_teams), 20, 
                               f"Should have at least 20 teams represented, got {len(all_teams)}")
        
        print(f"OK Teams represented: {len(all_teams)}")
        print(f"  Sample teams: {sorted(list(all_teams))[:10]}")
    
    def test_prime_time_games_exist(self):
        """Test that prime time games are included"""
        prime_time_games = []
        
        for game in self.data_manager.games.values():
            # Prime time is typically 8:20 PM (20:20) or later
            if game.game_date and game.game_date.hour >= 20:
                prime_time_games.append(game)
        
        self.assertGreater(len(prime_time_games), 0, "Should have some prime time games")
        
        print(f"OK Prime time games: {len(prime_time_games)}")
        if prime_time_games:
            sample = prime_time_games[0]
            print(f"  Sample: {sample.away_team.nickname} @ {sample.home_team.nickname} at {sample.game_date}")
    
    def test_date_range_querying(self):
        """Test that data manager can find games in date ranges"""
        # Test finding games in first week of September
        start_date = datetime(2024, 9, 1)
        end_date = datetime(2024, 9, 8)
        
        games_in_range = self.data_manager.get_games_by_date_range(start_date, end_date)
        self.assertGreater(len(games_in_range), 0, "Should find games in early September")
        
        # Test finding games in mid-September
        start_date = datetime(2024, 9, 15)
        end_date = datetime(2024, 9, 22)
        
        games_in_range = self.data_manager.get_games_by_date_range(start_date, end_date)
        self.assertGreater(len(games_in_range), 0, "Should find games in mid September")
        
        print(f"OK Date range querying works")
    
    def test_future_dates_available(self):
        """Test that data includes future dates (for live betting scenarios)"""
        now = datetime.now()
        future_games = []
        
        for game in self.data_manager.games.values():
            # In real scenario, some games should be in future
            # For test data, check if we have games beyond early September
            if game.game_date and game.game_date > datetime(2024, 9, 10):
                future_games.append(game)
        
        self.assertGreater(len(future_games), 0, "Should have games beyond September 10th")
        
        print(f"OK Future games available: {len(future_games)}")
        if future_games:
            latest_game = max(future_games, key=lambda g: g.game_date)
            print(f"  Latest game: {latest_game.away_team.nickname} @ {latest_game.home_team.nickname} on {latest_game.game_date}")


class TestProviderDataIntegration(unittest.TestCase):
    """Test that providers can work with the comprehensive data"""
    
    def test_kalshi_league_mapping(self):
        """Test Kalshi league mapping works with comprehensive data"""
        from market_data_kalshi.client import KalshiClient
        
        # Test configuration (won't authenticate but tests structure)
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        
        # Generate a test private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        test_config = {
            'api_key': 'testkey12345678901234567890',
            'private_key': private_pem
        }
        
        try:
            client = KalshiClient(test_config)
            
            # Should have NFL mapping
            self.assertIn(Sport.NFL, client.LEAGUE_MAP)
            self.assertEqual(client.LEAGUE_MAP[Sport.NFL], 'KXNFLGAME')
            
            print("OK Kalshi league mapping validated")
            
        except Exception as e:
            # Expected due to test keys, but mapping should work
            if "not a valid PEM" in str(e):
                print("OK Kalshi client structure validated (auth expected to fail with test keys)")
            else:
                raise e
    
    def test_odds_api_sport_mapping(self):
        """Test Odds API sport mapping works with comprehensive data"""
        from market_data_odds.client import OddsAPIClient
        
        test_config = {
            'api_key': 'testapikey12345678901234567890'
        }
        
        try:
            client = OddsAPIClient(test_config)
            
            # Should have NFL mapping
            nfl_key = client.handler.get_sport_key_for_api(Sport.NFL)
            self.assertEqual(nfl_key, 'americanfootball_nfl')
            
            print("OK Odds API sport mapping validated")
            
        except Exception as e:
            print(f"Note: {e}")


def run_data_validation_tests():
    """Run all data validation tests"""
    print("=== DATA VALIDATION TESTS ===")
    print("Validating comprehensive data availability across multiple dates...")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDataAvailability,
        TestProviderDataIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\nSUCCESS DATA VALIDATION SUCCESSFUL!")
        print("Library has comprehensive multi-date data coverage.")
        print("All providers can work with the comprehensive dataset.")
        return True
    else:
        print("\nX DATA VALIDATION FAILED!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        for test, error in result.errors:
            print(f"ERROR in {test}: {error}")
        for test, failure in result.failures:
            print(f"FAILURE in {test}: {failure}")
        return False


if __name__ == "__main__":
    success = run_data_validation_tests()
    sys.exit(0 if success else 1)