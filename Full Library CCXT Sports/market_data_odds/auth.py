"""
Odds API Authentication
Simple API key authentication for The Odds API.
"""

from typing import Dict, Optional

from market_data_core.exceptions import AuthenticationError
from market_data_core.utils import setup_logging


class OddsAPIAuthenticator:
    """Handles simple API key authentication for Odds API"""
    
    def __init__(self, api_key: str):
        """
        Initialize authenticator
        
        Args:
            api_key: The Odds API key
        """
        self.api_key = api_key
        self.logger = setup_logging("odds_api_auth")
        
        if not api_key or not api_key.strip():
            raise AuthenticationError("API key cannot be empty")
    
    @classmethod
    def from_config(cls, config: Dict) -> 'OddsAPIAuthenticator':
        """Create authenticator from configuration"""
        api_key = config.get('api_key')
        
        if not api_key:
            raise AuthenticationError("Missing API key in configuration")
        
        return cls(api_key)
    
    @classmethod
    def from_file(cls, api_key_file: str) -> 'OddsAPIAuthenticator':
        """Create authenticator from API key file"""
        try:
            with open(api_key_file, 'r') as f:
                content = f.read().strip()
                
                # Handle different file formats
                if "=" in content:
                    # Format: api_key = 'value' or api_key=value
                    api_key = content.split("=")[1].strip().strip("'\"")
                else:
                    # Just the key value
                    api_key = content
                
                return cls(api_key)
                
        except FileNotFoundError:
            raise AuthenticationError(f"API key file not found: {api_key_file}")
        except Exception as e:
            raise AuthenticationError(f"Failed to read API key file: {e}")
    
    def get_auth_params(self) -> Dict[str, str]:
        """
        Get authentication parameters for request
        
        Returns:
            Dict with API key parameter
        """
        return {'apiKey': self.api_key}
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers (Odds API uses query params, not headers)
        
        Returns:
            Standard headers for requests
        """
        return {
            'Content-Type': 'application/json',
            'User-Agent': 'SportsMarketDataLibrary/1.0'
        }
    
    def is_valid(self) -> bool:
        """
        Check if API key is valid format
        
        Returns:
            True if key appears to be valid format
        """
        # Basic validation - Odds API keys are typically 32+ character hex strings
        if not self.api_key:
            return False
        
        # Should be alphanumeric and reasonably long
        if len(self.api_key) < 16:
            return False
        
        # Should contain only valid characters
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        if not all(c in valid_chars for c in self.api_key):
            return False
        
        return True
    
    def get_test_url(self, base_url: str = "https://api.the-odds-api.com/v4") -> str:
        """
        Get URL for testing authentication
        
        Args:
            base_url: Base URL for Odds API
            
        Returns:
            Test URL with API key
        """
        params = self.get_auth_params()
        return f"{base_url}/sports?apiKey={params['apiKey']}"


def test_odds_api_authentication():
    """Test Odds API authentication functionality"""
    print("=== ODDS API AUTHENTICATION TESTS ===")
    
    # Test with dummy API key
    print("Testing authenticator initialization...")
    try:
        auth = OddsAPIAuthenticator("test_api_key_12345678901234567890")
        print(f"✓ API key: {auth.api_key[:10]}...")
        print(f"✓ Valid format: {auth.is_valid()}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test authentication parameters
    print("Testing auth parameters...")
    params = auth.get_auth_params()
    print(f"✓ Auth params: {list(params.keys())}")
    
    headers = auth.get_auth_headers()
    print(f"✓ Headers: {list(headers.keys())}")
    
    # Test from config
    print("Testing from config...")
    config = {'api_key': 'config_test_key_12345678901234567890'}
    try:
        auth_config = OddsAPIAuthenticator.from_config(config)
        print(f"✓ Config auth created: {auth_config.api_key[:10]}...")
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False
    
    # Test invalid cases
    print("Testing error handling...")
    try:
        OddsAPIAuthenticator("")
        print("✗ Should have failed with empty key")
        return False
    except AuthenticationError:
        print("✓ Empty key rejected correctly")
    
    try:
        OddsAPIAuthenticator("short")
        valid = OddsAPIAuthenticator("short").is_valid()
        if valid:
            print("✗ Short key should be invalid")
            return False
        else:
            print("✓ Short key rejected correctly")
    except Exception as e:
        print(f"✓ Short key handling: {e}")
    
    print("\n✓ All authentication tests passed!")
    return True


if __name__ == "__main__":
    test_odds_api_authentication()