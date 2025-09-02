"""
Phase 1 Validation Tests
Tests basic project structure, imports, configuration, and utilities.
"""

import sys
import os
import unittest
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestPhase1ProjectStructure(unittest.TestCase):
    """Test project structure and import paths"""
    
    def test_project_directories_exist(self):
        """Test that all required directories exist"""
        required_dirs = [
            'market_data_core',
            'market_data_kalshi', 
            'market_data_odds',
            'config',
            'tests/test_core',
            'tests/test_kalshi',
            'tests/test_odds',
            'tests/test_integration',
            'exploration'
        ]
        
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            self.assertTrue(full_path.exists(), f"Directory {dir_path} should exist")
            if 'test' not in dir_path and dir_path not in ['exploration', 'config']:
                init_file = full_path / '__init__.py'
                self.assertTrue(init_file.exists(), f"{dir_path}/__init__.py should exist")
    
    def test_core_imports(self):
        """Test that core module imports work correctly"""
        try:
            # Test individual imports
            from market_data_core.exceptions import MarketDataError, AuthenticationError
            from market_data_core.utils import ConfigLoader, RateLimiter
            from market_data_core.models import Team, Game, Market, Quote
            from market_data_core.base_client import BaseMarketDataClient
            
            # Test package import
            import market_data_core
            
            self.assertIsNotNone(MarketDataError)
            self.assertIsNotNone(ConfigLoader)
            self.assertIsNotNone(Team)
            self.assertIsNotNone(BaseMarketDataClient)
            
        except ImportError as e:
            self.fail(f"Core imports failed: {e}")
    
    def test_provider_imports(self):
        """Test that provider package imports work"""
        try:
            import market_data_kalshi
            import market_data_odds
            
            # These should not fail even if implementations don't exist yet
            self.assertIsNotNone(market_data_kalshi)
            self.assertIsNotNone(market_data_odds)
            
        except ImportError as e:
            self.fail(f"Provider imports failed: {e}")


class TestConfigurationManagement(unittest.TestCase):
    """Test configuration loading and validation"""
    
    def setUp(self):
        """Set up test configuration"""
        self.config_dir = project_root / 'config'
        self.test_config_path = self.config_dir / 'test_secrets.json'
        
        # Create test configuration
        test_config = {
            "kalshi": {
                "api_key": "test_kalshi_key",
                "private_key": "test_private_key",
                "base_url": "https://test.kalshi.com"
            },
            "odds_api": {
                "api_key": "test_odds_key",
                "base_url": "https://test.odds-api.com"
            },
            "rate_limits": {
                "kalshi_requests_per_minute": 60,
                "odds_api_requests_per_minute": 500
            }
        }
        
        import json
        with open(self.test_config_path, 'w') as f:
            json.dump(test_config, f)
    
    def tearDown(self):
        """Clean up test files"""
        if self.test_config_path.exists():
            self.test_config_path.unlink()
    
    def test_config_loader_initialization(self):
        """Test ConfigLoader can be initialized"""
        from market_data_core.utils import ConfigLoader
        
        loader = ConfigLoader(str(self.test_config_path))
        self.assertIsNotNone(loader)
    
    def test_config_loading(self):
        """Test configuration loading and validation"""
        from market_data_core.utils import ConfigLoader
        
        loader = ConfigLoader(str(self.test_config_path))
        
        kalshi_config = loader.get_kalshi_config()
        self.assertEqual(kalshi_config['api_key'], 'test_kalshi_key')
        self.assertEqual(kalshi_config['base_url'], 'https://test.kalshi.com')
        
        odds_config = loader.get_odds_api_config()
        self.assertEqual(odds_config['api_key'], 'test_odds_key')
        self.assertEqual(odds_config['base_url'], 'https://test.odds-api.com')
        
        rate_limits = loader.get_rate_limits()
        self.assertEqual(rate_limits['kalshi_requests_per_minute'], 60)
    
    def test_config_validation_missing_file(self):
        """Test error handling for missing config file"""
        from market_data_core.utils import ConfigLoader
        
        with self.assertRaises(FileNotFoundError):
            ConfigLoader('nonexistent_config.json')
    
    def test_config_validation_missing_sections(self):
        """Test validation of required config sections"""
        from market_data_core.utils import ConfigLoader
        
        # Create incomplete config
        incomplete_config = {"kalshi": {"api_key": "test"}}
        
        incomplete_path = self.config_dir / 'incomplete_test.json'
        import json
        with open(incomplete_path, 'w') as f:
            json.dump(incomplete_config, f)
        
        try:
            with self.assertRaises(ValueError):
                ConfigLoader(str(incomplete_path))
        finally:
            if incomplete_path.exists():
                incomplete_path.unlink()


class TestUtilities(unittest.TestCase):
    """Test utility functions"""
    
    def test_rate_limiter(self):
        """Test rate limiting functionality"""
        from market_data_core.utils import RateLimiter
        import time
        
        # Create rate limiter allowing 2 requests per 2 seconds
        limiter = RateLimiter(max_requests=2, time_window=2)
        
        # First two requests should proceed immediately
        self.assertTrue(limiter.can_proceed())
        limiter.wait_if_needed()
        
        self.assertTrue(limiter.can_proceed())
        limiter.wait_if_needed()
        
        # Third request should be rate limited
        self.assertFalse(limiter.can_proceed())
    
    def test_exponential_backoff(self):
        """Test exponential backoff utility"""
        from market_data_core.utils import ExponentialBackoff
        
        backoff = ExponentialBackoff(base_delay=0.1, max_delay=1.0, backoff_factor=2.0)
        
        # Test retry logic
        self.assertTrue(backoff.should_retry())
        
        # Test delay calculation
        delay1 = backoff.get_delay()
        self.assertAlmostEqual(delay1, 0.1, places=2)
        
        delay2 = backoff.get_delay()
        self.assertAlmostEqual(delay2, 0.2, places=2)
        
        # Test reset
        backoff.reset()
        self.assertEqual(backoff.attempt, 0)
    
    def test_timestamp_parsing(self):
        """Test timestamp parsing utility"""
        from market_data_core.utils import parse_timestamp
        
        # Test various timestamp formats
        test_cases = [
            ('2024-12-25T15:30:00Z', datetime(2024, 12, 25, 15, 30, 0)),
            ('2024-12-25T15:30:00', datetime(2024, 12, 25, 15, 30, 0)),
            ('2024-12-25 15:30:00', datetime(2024, 12, 25, 15, 30, 0)),
            ('2024-12-25', datetime(2024, 12, 25, 0, 0, 0)),
            ('invalid', None),
            ('', None)
        ]
        
        for timestamp_str, expected in test_cases:
            result = parse_timestamp(timestamp_str)
            self.assertEqual(result, expected, f"Failed for {timestamp_str}")
    
    def test_odds_utilities(self):
        """Test odds calculation utilities"""
        from market_data_core.utils import calculate_implied_probability, american_to_decimal_odds
        
        # Test American odds to probability
        prob_positive = calculate_implied_probability(150)  # +150 odds
        self.assertAlmostEqual(prob_positive, 0.4, places=2)
        
        prob_negative = calculate_implied_probability(-150)  # -150 odds
        self.assertAlmostEqual(prob_negative, 0.6, places=2)
        
        # Test American to decimal conversion
        decimal_positive = american_to_decimal_odds(150)
        self.assertAlmostEqual(decimal_positive, 2.5, places=2)
        
        decimal_negative = american_to_decimal_odds(-150)
        self.assertAlmostEqual(decimal_negative, 1.67, places=2)


class TestExceptions(unittest.TestCase):
    """Test custom exception classes"""
    
    def test_base_exception(self):
        """Test base MarketDataError"""
        from market_data_core.exceptions import MarketDataError
        
        error = MarketDataError("Test error", provider="test_provider", 
                               error_code="TEST001", details={"key": "value"})
        
        self.assertEqual(str(error), "Test error | Provider: test_provider | Code: TEST001")
        self.assertEqual(error.provider, "test_provider")
        self.assertEqual(error.error_code, "TEST001")
        self.assertEqual(error.details["key"], "value")
    
    def test_specific_exceptions(self):
        """Test specific exception types"""
        from market_data_core.exceptions import (
            AuthenticationError, RateLimitError, DataNotFoundError,
            KalshiError, OddsAPIError
        )
        
        # Test authentication error
        auth_error = AuthenticationError("Auth failed")
        self.assertIn("Auth failed", str(auth_error))
        
        # Test rate limit error
        rate_error = RateLimitError("Rate limited", retry_after=60)
        self.assertEqual(rate_error.retry_after, 60)
        
        # Test data not found
        not_found_error = DataNotFoundError("No data", requested_data="team_stats")
        self.assertEqual(not_found_error.requested_data, "team_stats")
        
        # Test provider-specific errors
        kalshi_error = KalshiError("Kalshi error")
        self.assertEqual(kalshi_error.provider, "kalshi")
        
        odds_error = OddsAPIError("Odds API error")
        self.assertEqual(odds_error.provider, "odds_api")


class TestDataModels(unittest.TestCase):
    """Test core data models"""
    
    def test_team_model(self):
        """Test Team model functionality"""
        from market_data_core.models import Team, Sport
        
        team = Team(
            name="Kansas City Chiefs",
            city="Kansas City", 
            nickname="Chiefs",
            abbreviations=["KC", "KAN"],
            sport=Sport.NFL
        )
        
        self.assertEqual(team.name, "Kansas City Chiefs")
        self.assertEqual(team.city, "Kansas City")
        self.assertIn("KC", team.abbreviations)
        
        # Test team matching
        self.assertGreater(team.matches("Kansas City Chiefs"), 0.9)
        self.assertGreater(team.matches("Chiefs"), 0.9)
        self.assertGreater(team.matches("KC"), 0.9)
        self.assertLess(team.matches("Broncos"), 0.8)
    
    def test_game_model(self):
        """Test Game model functionality"""
        from market_data_core.models import Team, Game, Sport
        
        home_team = Team("Denver Broncos", "Denver", "Broncos", ["DEN"])
        away_team = Team("Kansas City Chiefs", "Kansas City", "Chiefs", ["KC"])
        
        game = Game(
            game_id="nfl_2024_week1_kc_den",
            home_team=home_team,
            away_team=away_team,
            sport=Sport.NFL,
            game_date=datetime(2024, 9, 8, 20, 0, 0),
            week=1
        )
        
        self.assertEqual(game.sport, Sport.NFL)
        self.assertEqual(game.week, 1)
        
        matchup = game.get_matchup_string()
        self.assertIn("KC", matchup)
        self.assertIn("DEN", matchup)
        self.assertIn("@", matchup)
    
    def test_quote_model(self):
        """Test Quote model with odds calculations"""
        from market_data_core.models import Quote, Market, Game, Team, Sport, MarketType, QuoteSide
        
        # Create basic game and market for quote
        home_team = Team("Test Home", "Test", "Home", ["TH"])
        away_team = Team("Test Away", "Test", "Away", ["TA"])
        game = Game("test_game", home_team, away_team, Sport.NFL, datetime.now())
        market = Market("test_market", game, MarketType.MONEYLINE, "Test Market")
        
        quote = Quote(
            quote_id="test_quote",
            market=market,
            side=QuoteSide.HOME,
            provider="test_provider",
            american_odds=150
        )
        
        # Test automatic calculations
        self.assertAlmostEqual(quote.decimal_odds, 2.5, places=2)
        self.assertAlmostEqual(quote.implied_probability, 0.4, places=2)
        
        # Test with decimal odds input
        quote2 = Quote(
            quote_id="test_quote2",
            market=market,
            side=QuoteSide.AWAY,
            provider="test_provider",
            decimal_odds=1.67
        )
        
        self.assertEqual(quote2.american_odds, -149)  # Should be close to -150


def run_phase1_validation():
    """Run all Phase 1 validation tests"""
    print("=== PHASE 1 VALIDATION TESTS ===")
    print("Testing project structure, imports, configuration, and utilities...")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestPhase1ProjectStructure,
        TestConfigurationManagement,
        TestUtilities,
        TestExceptions,
        TestDataModels
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\nPHASE 1 VALIDATION SUCCESSFUL!")
        print("Project structure, imports, configuration, and utilities are working correctly.")
        return True
    else:
        print("\nX PHASE 1 VALIDATION FAILED!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        return False


if __name__ == "__main__":
    # Set up import paths
    sys.path.insert(0, str(project_root / 'market-data-core'))
    
    # Add import paths for market data modules
    sys.path.insert(0, str(project_root))
    
    # Run validation
    success = run_phase1_validation()
    sys.exit(0 if success else 1)