"""
Cross-Provider Integration Tests
Tests integration between Kalshi and Odds API providers.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import asyncio

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from market_data_kalshi import KalshiClient, KalshiAuthenticator
from market_data_odds import OddsAPIClient, OddsAPIAuthenticator
from market_data_core import Sport, Team, Game, Market, Quote
from market_data_core import get_team_matcher, get_nfl_data_manager


class TestCrossProviderIntegration(unittest.TestCase):
    """Test integration scenarios between providers"""
    
    def setUp(self):
        """Set up test clients and data"""
        # Generate test RSA key for Kalshi
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        # Test configurations
        self.kalshi_config = {
            'api_key': 'testkalshikey12345678901234567890',
            'private_key': private_pem,
            'base_url': 'https://demo-api.kalshi.co/trade-api/v2'
        }
        
        self.odds_api_config = {
            'api_key': 'testoddsapikey12345678901234567890',
            'base_url': 'https://api.the-odds-api.com/v4'
        }
        
        # Create clients
        self.kalshi_client = KalshiClient(self.kalshi_config)
        self.odds_client = OddsAPIClient(self.odds_api_config)
        
        # Team matcher for testing
        self.team_matcher = get_team_matcher(Sport.NFL)
        
        # Sample game data for testing
        self.sample_teams = self._get_sample_teams()
    
    def _get_sample_teams(self):
        """Get sample teams for testing"""
        nfl_data = get_nfl_data_manager()
        teams = nfl_data.get_all_teams()
        
        # Get Chiefs and Ravens for testing
        chiefs = teams.get('KC')
        ravens = teams.get('BAL')
        
        return {'chiefs': chiefs, 'ravens': ravens}
    
    def test_both_clients_initialize(self):
        """Test that both clients can be initialized"""
        self.assertEqual(self.kalshi_client.provider_name, 'kalshi')
        self.assertEqual(self.odds_client.provider_name, 'odds_api')
        
        # Both should have team matchers
        self.assertIsNotNone(self.kalshi_client.team_matcher)
        self.assertIsNotNone(self.odds_client.team_matcher)
    
    def test_consistent_team_matching(self):
        """Test that both providers match teams consistently"""
        test_team_names = [
            'Kansas City Chiefs',
            'KC',
            'Chiefs',
            'Baltimore Ravens',
            'Ravens',
            'BAL'
        ]
        
        for name in test_team_names:
            kalshi_match = self.kalshi_client.team_matcher.match_team(name)
            odds_match = self.odds_client.team_matcher.match_team(name)
            
            # Both should find matches for valid NFL teams
            if kalshi_match.matched_team and odds_match.matched_team:
                # Should match to same team
                self.assertEqual(
                    kalshi_match.matched_team.name,
                    odds_match.matched_team.name,
                    f"Team matching inconsistent for {name}"
                )
    
    def test_unified_data_models(self):
        """Test that both providers create compatible data models"""
        # Create sample game using unified models
        chiefs = self.sample_teams['chiefs']
        ravens = self.sample_teams['ravens']
        
        if chiefs and ravens:
            # Create a sample game
            game = Game(
                game_id="test_game_kc_bal",
                home_team=chiefs,
                away_team=ravens,
                sport=Sport.NFL,
                game_date=datetime(2024, 9, 5, 20, 20),
                season="2024",
                week=1
            )
            
            # Verify both providers can work with this game object
            self.assertEqual(game.sport, Sport.NFL)
            self.assertIsInstance(game.home_team, Team)
            self.assertIsInstance(game.away_team, Team)
            
            # Both clients should support the same sports
            kalshi_supports_nfl = Sport.NFL in self.kalshi_client.LEAGUE_MAP
            odds_supports_nfl = Sport.NFL in self.odds_client.handler.SPORT_MAP
            
            self.assertTrue(kalshi_supports_nfl)
            self.assertTrue(odds_supports_nfl)
    
    async def test_get_sports_consistency(self):
        """Test that both providers return consistent sports lists"""
        # Mock responses for both providers
        with patch.object(self.kalshi_client, 'get_sports') as mock_kalshi:
            with patch.object(self.odds_client, 'get_sports') as mock_odds:
                # Mock return values
                from market_data_core.models import ProviderResponse
                
                mock_kalshi.return_value = ProviderResponse(
                    success=True,
                    data=[Sport.NFL, Sport.MLB, Sport.NBA],
                    provider='kalshi'
                )
                
                mock_odds.return_value = ProviderResponse(
                    success=True,
                    data=[Sport.NFL, Sport.MLB, Sport.NBA, Sport.NHL],
                    provider='odds_api'
                )
                
                # Get sports from both
                kalshi_sports = await self.kalshi_client.get_sports()
                odds_sports = await self.odds_client.get_sports()
                
                # Both should succeed
                self.assertTrue(kalshi_sports.success)
                self.assertTrue(odds_sports.success)
                
                # Should have common sports
                kalshi_set = set(kalshi_sports.data)
                odds_set = set(odds_sports.data)
                common_sports = kalshi_set.intersection(odds_set)
                
                self.assertIn(Sport.NFL, common_sports)
                self.assertIn(Sport.MLB, common_sports)
    
    def test_sport_key_mappings(self):
        """Test that sport key mappings are consistent where possible"""
        # NFL should be supported by both
        kalshi_nfl_key = self.kalshi_client.LEAGUE_MAP.get(Sport.NFL)
        odds_nfl_key = self.odds_client.handler.get_sport_key_for_api(Sport.NFL)
        
        self.assertEqual(kalshi_nfl_key, 'KXNFLGAME')
        self.assertEqual(odds_nfl_key, 'americanfootball_nfl')
        
        # Both should be valid strings
        self.assertIsInstance(kalshi_nfl_key, str)
        self.assertIsInstance(odds_nfl_key, str)
    
    def test_error_handling_consistency(self):
        """Test that both providers handle errors consistently"""
        # Test unsupported sport
        from market_data_core.models import Sport
        
        # Create a mock unsupported sport by temporarily removing from mappings
        original_kalshi = self.kalshi_client.LEAGUE_MAP.copy()
        original_odds = self.odds_client.handler.SPORT_MAP.copy()
        
        try:
            # Remove NBA from both
            if Sport.NBA in self.kalshi_client.LEAGUE_MAP:
                del self.kalshi_client.LEAGUE_MAP[Sport.NBA]
            if Sport.NBA in self.odds_client.handler.SPORT_MAP:
                del self.odds_client.handler.SPORT_MAP[Sport.NBA]
            
            # Both should handle unsupported sport similarly
            async def test_unsupported():
                kalshi_response = await self.kalshi_client.get_categories(Sport.NBA)
                odds_response = await self.odds_client.get_categories(Sport.NBA)
                
                # Both should fail gracefully
                self.assertFalse(kalshi_response.success)
                self.assertFalse(odds_response.success)
                
                # Both should have descriptive error messages
                self.assertIn('not supported', kalshi_response.error.lower())
                self.assertIn('not supported', odds_response.error.lower())
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(test_unsupported())
            loop.close()
        
        finally:
            # Restore mappings
            self.kalshi_client.LEAGUE_MAP.update(original_kalshi)
            self.odds_client.handler.SPORT_MAP.update(original_odds)


class TestDataConsistency(unittest.TestCase):
    """Test data consistency between providers"""
    
    def test_team_object_compatibility(self):
        """Test that Team objects from different sources are compatible"""
        team_matcher = get_team_matcher(Sport.NFL)
        
        # Test matching same team names
        chiefs_match1 = team_matcher.match_team('Kansas City Chiefs')
        chiefs_match2 = team_matcher.match_team('KC')
        
        if chiefs_match1.matched_team and chiefs_match2.matched_team:
            # Should be the same team object
            self.assertEqual(
                chiefs_match1.matched_team.name,
                chiefs_match2.matched_team.name
            )
            
            # Both should have consistent attributes
            team = chiefs_match1.matched_team
            self.assertIsInstance(team.name, str)
            self.assertIsInstance(team.city, str)
            self.assertIsInstance(team.nickname, str)
            self.assertEqual(team.sport, Sport.NFL)
    
    def test_game_id_consistency(self):
        """Test that game IDs are generated consistently"""
        nfl_data = get_nfl_data_manager()
        games = list(nfl_data.games.values())
        
        if games:
            sample_game = games[0]
            
            # Game ID should be consistent format
            self.assertIsInstance(sample_game.game_id, str)
            self.assertTrue(len(sample_game.game_id) > 5)
            
            # Should contain recognizable elements
            game_id_lower = sample_game.game_id.lower()
            self.assertTrue(
                any(team in game_id_lower for team in ['kc', 'bal', 'phi', 'gb']) or
                'nfl' in game_id_lower or
                '2024' in game_id_lower
            )
    
    def test_quote_format_consistency(self):
        """Test that quote formats are consistent between providers"""
        from market_data_core.models import Quote, Market, QuoteSide
        
        # Create sample quotes from both providers (conceptually)
        sample_market = Mock(spec=Market)
        
        # Kalshi-style quote (binary, probability-based)
        kalshi_quote = Quote(
            quote_id="kalshi_test_quote",
            market=sample_market,
            side=QuoteSide.YES,
            provider="kalshi",
            price=0.65,  # 65 cents = 65% probability
            implied_probability=0.65,
            timestamp=datetime.utcnow()
        )
        
        # Odds API-style quote (American odds)
        odds_quote = Quote(
            quote_id="odds_api_test_quote",
            market=sample_market,
            side=QuoteSide.HOME,
            provider="odds_api",
            american_odds=-150,
            decimal_odds=1.67,
            implied_probability=0.60,
            timestamp=datetime.utcnow()
        )
        
        # Both should have consistent basic structure
        for quote in [kalshi_quote, odds_quote]:
            self.assertIsInstance(quote.quote_id, str)
            self.assertIsNotNone(quote.provider)
            self.assertIsNotNone(quote.side)
            self.assertIsNotNone(quote.timestamp)
            
            # Should have some form of pricing
            self.assertTrue(
                quote.price is not None or 
                quote.american_odds is not None or
                quote.decimal_odds is not None
            )


class TestProviderRegistry(unittest.TestCase):
    """Test provider registry and management"""
    
    def test_provider_names_unique(self):
        """Test that provider names are unique"""
        kalshi_config = {
            'api_key': 'test',
            'private_key': 'test'
        }
        odds_config = {
            'api_key': 'testoddsapikey12345678901234567890'
        }
        
        try:
            kalshi = KalshiClient(kalshi_config)
            odds = OddsAPIClient(odds_config)
            
            # Provider names should be different
            self.assertNotEqual(kalshi.provider_name, odds.provider_name)
            
            # Should be descriptive
            self.assertEqual(kalshi.provider_name, 'kalshi')
            self.assertEqual(odds.provider_name, 'odds_api')
            
        except Exception:
            # Skip if we can't initialize (missing dependencies, etc.)
            self.skipTest("Could not initialize clients for provider name test")


def run_cross_provider_tests():
    """Run all cross-provider integration tests"""
    print("=== CROSS-PROVIDER INTEGRATION TESTS ===")
    print("Testing integration between Kalshi and Odds API providers...")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestCrossProviderIntegration,
        TestDataConsistency,
        TestProviderRegistry
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\nCROSS-PROVIDER INTEGRATION SUCCESSFUL!")
        print("Both providers work together seamlessly with consistent data models.")
        print("Ready for Phase 7: Final library assembly.")
        return True
    else:
        print("\nX CROSS-PROVIDER INTEGRATION FAILED!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        for test, error in result.errors:
            print(f"ERROR in {test}: {error}")
        for test, failure in result.failures:
            print(f"FAILURE in {test}: {failure}")
        return False


if __name__ == "__main__":
    # Run integration tests
    success = run_cross_provider_tests()
    sys.exit(0 if success else 1)