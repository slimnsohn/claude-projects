"""
Kalshi Integration Tests
Tests the Kalshi client, authentication, and handler integration.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from market_data_kalshi import KalshiClient, KalshiAuthenticator, KalshiResponseHandler
from market_data_core import Sport
from market_data_core.exceptions import AuthenticationError


class TestKalshiAuthentication(unittest.TestCase):
    """Test Kalshi authentication functionality"""
    
    def test_authenticator_initialization(self):
        """Test authenticator can be initialized with test keys"""
        # Generate test RSA key pair
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        
        # Generate test private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        # Test authenticator initialization
        auth = KalshiAuthenticator("test_api_key", private_pem)
        self.assertEqual(auth.api_key, "test_api_key")
        self.assertIsNotNone(auth.private_key)
    
    def test_signature_creation(self):
        """Test RSA-PSS signature creation"""
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        
        # Generate test private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        auth = KalshiAuthenticator("test_api_key", private_pem)
        
        # Test signature creation
        signature = auth.create_signature("GET", "/markets", "")
        self.assertIsInstance(signature, str)
        self.assertGreater(len(signature), 100)  # Should be base64 encoded signature
    
    def test_auth_headers(self):
        """Test authentication headers generation"""
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        
        # Generate test private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        auth = KalshiAuthenticator("test_api_key", private_pem)
        
        headers = auth.get_auth_headers("GET", "/markets", "")
        
        # Check required headers
        self.assertIn('KALSHI-ACCESS-KEY', headers)
        self.assertIn('KALSHI-ACCESS-SIGNATURE', headers)
        self.assertIn('KALSHI-ACCESS-TIMESTAMP', headers)
        self.assertIn('Content-Type', headers)
        
        self.assertEqual(headers['KALSHI-ACCESS-KEY'], 'test_api_key')
        self.assertEqual(headers['Content-Type'], 'application/json')
    
    def test_token_management(self):
        """Test access token management"""
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        
        # Generate test private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        auth = KalshiAuthenticator("test_api_key", private_pem)
        
        # Initially no token
        self.assertFalse(auth.is_token_valid())
        self.assertIsNone(auth.access_token)
        
        # Set token
        auth.set_access_token("test_token_123")
        self.assertTrue(auth.is_token_valid())
        self.assertEqual(auth.access_token, "test_token_123")
        
        # Clear token
        auth.clear_access_token()
        self.assertFalse(auth.is_token_valid())
        self.assertIsNone(auth.access_token)
    
    def test_invalid_private_key(self):
        """Test error handling for invalid private key"""
        with self.assertRaises(AuthenticationError):
            KalshiAuthenticator("test_api_key", "invalid_private_key")
    
    def test_from_config(self):
        """Test creating authenticator from config"""
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        
        # Generate test private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        config = {
            'api_key': 'test_config_key',
            'private_key': private_pem
        }
        
        auth = KalshiAuthenticator.from_config(config)
        self.assertEqual(auth.api_key, 'test_config_key')


class TestKalshiResponseHandler(unittest.TestCase):
    """Test Kalshi response handler functionality"""
    
    def setUp(self):
        """Set up test handler"""
        self.handler = KalshiResponseHandler()
    
    def test_handler_initialization(self):
        """Test handler initializes correctly"""
        self.assertIsNotNone(self.handler.market_type_patterns)
        self.assertIn('MONEYLINE', [mt.name for mt in self.handler.market_type_patterns.keys()])
    
    def test_parse_nfl_ticker(self):
        """Test parsing NFL ticker format"""
        ticker = "KXNFLGAME-KC-BAL-24W1-WIN"
        game_info = self.handler._parse_game_from_ticker(ticker, Sport.NFL)
        
        self.assertIsNotNone(game_info)
        self.assertEqual(game_info['team1'], 'KC')
        self.assertEqual(game_info['team2'], 'BAL') 
        self.assertEqual(game_info['season'], '2024')
        self.assertEqual(game_info['week'], 1)
        self.assertEqual(game_info['sport'], Sport.NFL)
    
    def test_parse_mlb_ticker(self):
        """Test parsing MLB ticker format"""
        ticker = "KXMLBGAME-LAD-SD-24-WIN"
        game_info = self.handler._parse_game_from_ticker(ticker, Sport.MLB)
        
        self.assertIsNotNone(game_info)
        self.assertEqual(game_info['team1'], 'LAD')
        self.assertEqual(game_info['team2'], 'SD')
        self.assertEqual(game_info['season'], '2024')
        self.assertEqual(game_info['sport'], Sport.MLB)
    
    def test_parse_invalid_ticker(self):
        """Test parsing invalid ticker"""
        result = self.handler._parse_game_from_ticker("INVALID-TICKER", Sport.NFL)
        self.assertIsNone(result)
    
    def test_determine_market_type(self):
        """Test market type determination"""
        # Test moneyline market
        ticker = "KXNFLGAME-KC-BAL-24W1-WIN"
        market_type = self.handler._determine_market_type(ticker)
        self.assertEqual(market_type.name, 'MONEYLINE')
    
    def test_determine_game_status(self):
        """Test game status determination from market data"""
        # Test open markets
        markets = [{'status': 'open'}, {'status': 'open'}]
        status = self.handler._determine_game_status(markets)
        self.assertEqual(status, 'scheduled')
        
        # Test closed markets
        markets = [{'status': 'closed'}, {'status': 'closed'}]
        status = self.handler._determine_game_status(markets)
        self.assertEqual(status, 'live')
        
        # Test settled markets
        markets = [{'status': 'settled'}, {'status': 'resolved'}]
        status = self.handler._determine_game_status(markets)
        self.assertEqual(status, 'final')


class TestKalshiClient(unittest.TestCase):
    """Test Kalshi client functionality"""
    
    def setUp(self):
        """Set up test client configuration"""
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        
        # Generate test private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        self.test_config = {
            'api_key': 'test_api_key',
            'private_key': private_pem,
            'base_url': 'https://demo-api.kalshi.co/trade-api/v2',
            'demo_base_url': 'https://demo-api.kalshi.co/trade-api/v2'
        }
    
    def test_client_initialization(self):
        """Test client can be initialized"""
        client = KalshiClient(self.test_config)
        
        self.assertEqual(client.provider_name, "kalshi")
        self.assertIsNotNone(client.auth)
        self.assertIsNotNone(client.handler)
        self.assertIsNotNone(client.rate_limiter)
        self.assertIsNotNone(client.team_matcher)
    
    def test_supported_sports(self):
        """Test supported sports mapping"""
        client = KalshiClient(self.test_config)
        
        # Check league mappings
        self.assertIn(Sport.NFL, client.LEAGUE_MAP)
        self.assertIn(Sport.MLB, client.LEAGUE_MAP)
        self.assertIn(Sport.NBA, client.LEAGUE_MAP)
        self.assertIn(Sport.NHL, client.LEAGUE_MAP)
        
        self.assertEqual(client.LEAGUE_MAP[Sport.NFL], 'KXNFLGAME')
        self.assertEqual(client.LEAGUE_MAP[Sport.MLB], 'KXMLBGAME')
    
    def test_authentication_status(self):
        """Test authentication status checking"""
        client = KalshiClient(self.test_config)
        
        # Initially not authenticated
        self.assertFalse(client.is_authenticated())
        
        # Mock authentication
        client._authenticated = True
        client.auth.set_access_token("mock_token")
        
        self.assertTrue(client.is_authenticated())
    
    def test_invalid_config_authentication(self):
        """Test error handling for invalid authentication config"""
        invalid_config = {'api_key': 'test', 'private_key': 'invalid'}
        
        with self.assertRaises(AuthenticationError):
            KalshiClient(invalid_config)
    
    @patch('aiohttp.ClientSession')
    async def test_get_sports(self, mock_session):
        """Test get_sports method"""
        client = KalshiClient(self.test_config)
        
        response = await client.get_sports()
        
        self.assertTrue(response.success)
        self.assertIsInstance(response.data, list)
        self.assertIn(Sport.NFL, response.data)
        self.assertIn(Sport.MLB, response.data)


def run_kalshi_integration_tests():
    """Run all Kalshi integration tests"""
    print("=== KALSHI INTEGRATION TESTS ===")
    print("Testing Kalshi authentication, client, and handler integration...")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestKalshiAuthentication,
        TestKalshiResponseHandler,
        TestKalshiClient
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\nKALSHI INTEGRATION SUCCESSFUL!")
        print("Kalshi authentication, client, and handler integration are working correctly.")
        print("Phase 3 implementation is complete and ready for live API testing.")
        return True
    else:
        print("\nX KALSHI INTEGRATION FAILED!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        for test, error in result.errors:
            print(f"ERROR in {test}: {error}")
        for test, failure in result.failures:
            print(f"FAILURE in {test}: {failure}")
        return False


if __name__ == "__main__":
    # Run integration tests
    success = run_kalshi_integration_tests()
    sys.exit(0 if success else 1)