"""
Odds API Integration Tests
Tests the Odds API client, authentication, and handler integration.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from market_data_odds import OddsAPIClient, OddsAPIAuthenticator, OddsAPIResponseHandler
from market_data_core import Sport, Team
from market_data_core.exceptions import AuthenticationError


class TestOddsAPIAuthentication(unittest.TestCase):
    """Test Odds API authentication functionality"""
    
    def test_authenticator_initialization(self):
        """Test authenticator can be initialized with API key"""
        auth = OddsAPIAuthenticator("testapikey12345678901234567890")
        self.assertEqual(auth.api_key, "testapikey12345678901234567890")
        self.assertTrue(auth.is_valid())
    
    def test_invalid_api_key(self):
        """Test error handling for invalid API key"""
        with self.assertRaises(AuthenticationError):
            OddsAPIAuthenticator("")
        
        # Short key should be detected as invalid
        auth = OddsAPIAuthenticator("short")
        self.assertFalse(auth.is_valid())
    
    def test_auth_params(self):
        """Test authentication parameters"""
        auth = OddsAPIAuthenticator("testapikey12345678901234567890")
        params = auth.get_auth_params()
        
        self.assertIn('apiKey', params)
        self.assertEqual(params['apiKey'], 'testapikey12345678901234567890')
    
    def test_auth_headers(self):
        """Test authentication headers"""
        auth = OddsAPIAuthenticator("testapikey12345678901234567890")
        headers = auth.get_auth_headers()
        
        self.assertIn('Content-Type', headers)
        self.assertEqual(headers['Content-Type'], 'application/json')
    
    def test_from_config(self):
        """Test creating authenticator from config"""
        config = {'api_key': 'configtestkey12345678901234567890'}
        auth = OddsAPIAuthenticator.from_config(config)
        
        self.assertEqual(auth.api_key, 'configtestkey12345678901234567890')
    
    def test_test_url(self):
        """Test generating test URL"""
        auth = OddsAPIAuthenticator("testapikey12345678901234567890")
        url = auth.get_test_url()
        
        self.assertIn('api.the-odds-api.com', url)
        self.assertIn('testapikey12345678901234567890', url)


class TestOddsAPIResponseHandler(unittest.TestCase):
    """Test Odds API response handler functionality"""
    
    def setUp(self):
        """Set up test handler"""
        self.handler = OddsAPIResponseHandler()
    
    def test_handler_initialization(self):
        """Test handler initializes correctly"""
        self.assertIsNotNone(self.handler.SPORT_MAP)
        self.assertIsNotNone(self.handler.REVERSE_SPORT_MAP)
        self.assertIsNotNone(self.handler.MARKET_TYPE_MAP)
        
        # Check sport mappings
        self.assertIn(Sport.NFL, self.handler.SPORT_MAP)
        self.assertEqual(self.handler.SPORT_MAP[Sport.NFL], 'americanfootball_nfl')
        
        # Check reverse mapping
        self.assertEqual(self.handler.get_sport_from_api_key('americanfootball_nfl'), Sport.NFL)
        self.assertEqual(self.handler.get_sport_key_for_api(Sport.NFL), 'americanfootball_nfl')
    
    def test_game_date_parsing(self):
        """Test game date parsing"""
        # Test valid ISO format
        date_str = "2024-09-05T20:20:00Z"
        parsed_date = self.handler._parse_game_date(date_str)
        
        self.assertIsNotNone(parsed_date)
        self.assertIsInstance(parsed_date, datetime)
    
    def test_game_status_determination(self):
        """Test game status determination"""
        # Test future game
        future_game = {
            'commence_time': '2030-09-05T20:20:00Z'  # Far future
        }
        status = self.handler._determine_game_status(future_game)
        self.assertEqual(status, 'scheduled')
        
        # Test past game
        past_game = {
            'commence_time': '2020-09-05T20:20:00Z'  # Far past
        }
        status = self.handler._determine_game_status(past_game)
        self.assertEqual(status, 'final')
    
    def test_american_odds_conversion(self):
        """Test American odds conversion utilities"""
        # Test positive odds
        decimal = self.handler._american_to_decimal(150)
        self.assertEqual(decimal, 2.5)
        
        probability = self.handler._american_to_probability(150)
        self.assertAlmostEqual(probability, 0.4, places=1)
        
        # Test negative odds
        decimal = self.handler._american_to_decimal(-150)
        self.assertAlmostEqual(decimal, 1.667, places=2)
        
        probability = self.handler._american_to_probability(-150)
        self.assertEqual(probability, 0.6)
    
    def test_market_type_mapping(self):
        """Test market type mapping"""
        from market_data_core.models import MarketType
        
        self.assertEqual(self.handler.MARKET_TYPE_MAP['h2h'], MarketType.MONEYLINE)
        self.assertEqual(self.handler.MARKET_TYPE_MAP['spreads'], MarketType.SPREAD)
        self.assertEqual(self.handler.MARKET_TYPE_MAP['totals'], MarketType.TOTAL)
    
    async def test_create_categories(self):
        """Test creating categories for sport"""
        categories = await self.handler.create_categories_for_sport(Sport.NFL)
        
        self.assertEqual(len(categories), 1)
        category = categories[0]
        
        self.assertEqual(category.sport, Sport.NFL)
        self.assertIn('NFL', category.name)
        self.assertEqual(category.metadata['sport_key'], 'americanfootball_nfl')


class TestOddsAPIClient(unittest.TestCase):
    """Test Odds API client functionality"""
    
    def setUp(self):
        """Set up test client configuration"""
        self.test_config = {
            'api_key': 'testapikey12345678901234567890',
            'base_url': 'https://api.the-odds-api.com/v4'
        }
    
    def test_client_initialization(self):
        """Test client can be initialized"""
        client = OddsAPIClient(self.test_config)
        
        self.assertEqual(client.provider_name, "odds_api")
        self.assertIsNotNone(client.auth)
        self.assertIsNotNone(client.handler)
        self.assertIsNotNone(client.rate_limiter)
        self.assertIsNotNone(client.team_matcher)
    
    def test_supported_sports(self):
        """Test supported sports mapping"""
        client = OddsAPIClient(self.test_config)
        
        # Check handler has sport mappings
        self.assertIn(Sport.NFL, client.handler.SPORT_MAP)
        self.assertIn(Sport.MLB, client.handler.SPORT_MAP)
        self.assertIn(Sport.NBA, client.handler.SPORT_MAP)
        self.assertIn(Sport.NHL, client.handler.SPORT_MAP)
    
    def test_authentication_status(self):
        """Test authentication status checking"""
        client = OddsAPIClient(self.test_config)
        
        # Initially not authenticated
        self.assertFalse(client.is_authenticated())
        
        # Mock authentication
        client._authenticated = True
        self.assertTrue(client.is_authenticated())
    
    def test_invalid_config_authentication(self):
        """Test error handling for invalid authentication config"""
        invalid_config = {'api_key': ''}
        
        with self.assertRaises(AuthenticationError):
            OddsAPIClient(invalid_config)
    
    def test_rate_limiter_configuration(self):
        """Test rate limiter is configured correctly"""
        client = OddsAPIClient(self.test_config)
        
        # Default should be 500 requests per minute
        self.assertEqual(client.rate_limiter.max_requests, 500)
        self.assertEqual(client.rate_limiter.time_window, 60)
    
    def test_default_params(self):
        """Test default API parameters"""
        client = OddsAPIClient(self.test_config)
        
        expected_params = {
            'regions': 'us',
            'oddsFormat': 'american',
            'dateFormat': 'iso'
        }
        
        for key, value in expected_params.items():
            self.assertEqual(client.default_params[key], value)
    
    @patch('aiohttp.ClientSession')
    async def test_get_sports_mock(self, mock_session):
        """Test get_sports method with mock"""
        # Mock response data
        mock_sports_data = [
            {'key': 'americanfootball_nfl', 'title': 'NFL'},
            {'key': 'baseball_mlb', 'title': 'MLB'},
            {'key': 'unsupported_sport', 'title': 'Unsupported'}
        ]
        
        # Setup mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_sports_data)
        
        mock_session_instance = AsyncMock()
        mock_session_instance.get = AsyncMock()
        mock_session_instance.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session_instance.get.return_value.__aexit__ = AsyncMock(return_value=None)
        
        mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Test
        client = OddsAPIClient(self.test_config)
        client._authenticated = True  # Mock authentication
        
        response = await client.get_sports()
        
        # Verify
        self.assertTrue(response.success)
        self.assertIsInstance(response.data, list)
        # Should only include supported sports (NFL, MLB)
        self.assertEqual(len(response.data), 2)
        self.assertIn(Sport.NFL, response.data)
        self.assertIn(Sport.MLB, response.data)
    
    async def test_get_categories(self):
        """Test get_categories method"""
        client = OddsAPIClient(self.test_config)
        
        # Test supported sport
        response = await client.get_categories(Sport.NFL)
        self.assertTrue(response.success)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        
        # Test unsupported sport
        # Create a mock sport that's not in the mapping
        from market_data_core.models import Sport
        unsupported_sport = Sport.MLB  # Use MLB but pretend it's unsupported
        
        # Temporarily remove from handler mapping
        original_mapping = client.handler.SPORT_MAP.copy()
        del client.handler.SPORT_MAP[Sport.MLB]
        
        try:
            response = await client.get_categories(Sport.MLB)
            self.assertFalse(response.success)
            self.assertIn("not supported", response.error)
        finally:
            # Restore mapping
            client.handler.SPORT_MAP.update(original_mapping)
    
    def test_team_matcher_for_sport(self):
        """Test team matcher selection for different sports"""
        client = OddsAPIClient(self.test_config)
        
        # Test NFL
        nfl_matcher = client._get_team_matcher_for_sport(Sport.NFL)
        self.assertIsNotNone(nfl_matcher)
        
        # Test other sports (should fallback to NFL for now)
        mlb_matcher = client._get_team_matcher_for_sport(Sport.MLB)
        self.assertIsNotNone(mlb_matcher)


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios between authentication, handler, and client"""
    
    def test_full_workflow_mock(self):
        """Test the full workflow with mocked components"""
        config = {'api_key': 'testapikey12345678901234567890'}
        
        # Initialize components
        auth = OddsAPIAuthenticator.from_config(config)
        handler = OddsAPIResponseHandler()
        client = OddsAPIClient(config)
        
        # Test authentication
        self.assertTrue(auth.is_valid())
        auth_params = auth.get_auth_params()
        self.assertIn('apiKey', auth_params)
        
        # Test handler
        sport_key = handler.get_sport_key_for_api(Sport.NFL)
        self.assertEqual(sport_key, 'americanfootball_nfl')
        
        sport = handler.get_sport_from_api_key('americanfootball_nfl')
        self.assertEqual(sport, Sport.NFL)
        
        # Test client configuration
        self.assertEqual(client.provider_name, "odds_api")
        self.assertIsNotNone(client.auth)
        self.assertIsNotNone(client.handler)
    
    def test_error_handling(self):
        """Test error handling across components"""
        # Test auth errors
        with self.assertRaises(AuthenticationError):
            OddsAPIAuthenticator("")
        
        # Test client with bad config
        with self.assertRaises(AuthenticationError):
            OddsAPIClient({'api_key': ''})
        
        # Test handler with invalid data
        handler = OddsAPIResponseHandler()
        
        # Invalid sport key should return None
        sport = handler.get_sport_from_api_key('invalid_sport')
        self.assertIsNone(sport)
        
        # Invalid sport should return None
        sport_key = handler.get_sport_key_for_api("INVALID_SPORT")
        self.assertIsNone(sport_key)


def run_odds_api_integration_tests():
    """Run all Odds API integration tests"""
    print("=== ODDS API INTEGRATION TESTS ===")
    print("Testing Odds API authentication, client, and handler integration...")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestOddsAPIAuthentication,
        TestOddsAPIResponseHandler,
        TestOddsAPIClient,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\nODDS API INTEGRATION SUCCESSFUL!")
        print("Odds API authentication, client, and handler integration are working correctly.")
        print("Phase 4 implementation is complete and ready for live API testing.")
        return True
    else:
        print("\nX ODDS API INTEGRATION FAILED!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        for test, error in result.errors:
            print(f"ERROR in {test}: {error}")
        for test, failure in result.failures:
            print(f"FAILURE in {test}: {failure}")
        return False


if __name__ == "__main__":
    # Run integration tests
    success = run_odds_api_integration_tests()
    sys.exit(0 if success else 1)