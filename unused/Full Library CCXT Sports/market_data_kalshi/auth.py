"""
Kalshi Authentication
Implements RSA-PSS authentication for Kalshi API
"""

import base64
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature

from market_data_core.exceptions import AuthenticationError
from market_data_core.utils import setup_logging


class KalshiAuthenticator:
    """Handles RSA-PSS authentication for Kalshi API"""
    
    def __init__(self, api_key: str, private_key_content: str):
        """
        Initialize authenticator
        
        Args:
            api_key: Kalshi API key ID
            private_key_content: RSA private key in PEM format
        """
        self.api_key = api_key
        self.logger = setup_logging("kalshi_auth")
        
        try:
            # Load the private key
            self.private_key = serialization.load_pem_private_key(
                private_key_content.encode('utf-8'),
                password=None  # Assuming no password for simplicity
            )
            
            if not isinstance(self.private_key, rsa.RSAPrivateKey):
                raise AuthenticationError("Private key must be RSA")
                
        except Exception as e:
            raise AuthenticationError(f"Failed to load private key: {e}")
        
        # Token management
        self.access_token = None
        self.token_expires_at = None
        self.token_refresh_buffer = 60  # Refresh 60 seconds before expiry
    
    @classmethod
    def from_config(cls, config: Dict) -> 'KalshiAuthenticator':
        """Create authenticator from configuration"""
        api_key = config.get('api_key')
        private_key = config.get('private_key')
        
        if not api_key:
            raise AuthenticationError("Missing API key in configuration")
        if not private_key:
            raise AuthenticationError("Missing private key in configuration")
        
        return cls(api_key, private_key)
    
    def create_signature(self, method: str, path: str, body: str = "") -> str:
        """
        Create RSA-PSS signature for request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            body: Request body (empty for GET requests)
            
        Returns:
            Base64-encoded signature
        """
        try:
            # Create the message to sign
            timestamp = str(int(time.time()))
            message = f"{timestamp}{method.upper()}{path}{body}"
            
            # Sign the message using RSA-PSS
            signature = self.private_key.sign(
                message.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Encode signature as base64
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            
            return signature_b64
            
        except Exception as e:
            raise AuthenticationError(f"Failed to create signature: {e}")
    
    def get_auth_headers(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """
        Get authentication headers for request
        
        Args:
            method: HTTP method
            path: Request path  
            body: Request body
            
        Returns:
            Dict of authentication headers
        """
        timestamp = str(int(time.time()))
        signature = self.create_signature(method, path, body)
        
        headers = {
            'KALSHI-ACCESS-KEY': self.api_key,
            'KALSHI-ACCESS-SIGNATURE': signature,
            'KALSHI-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
        
        # Add access token if available
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        return headers
    
    def is_token_valid(self) -> bool:
        """Check if current access token is valid"""
        if not self.access_token or not self.token_expires_at:
            return False
        
        # Check if token expires soon (within refresh buffer)
        now = datetime.utcnow()
        expires_soon = now >= (self.token_expires_at - timedelta(seconds=self.token_refresh_buffer))
        
        return not expires_soon
    
    def set_access_token(self, token: str, expires_at: Optional[datetime] = None):
        """
        Set access token
        
        Args:
            token: Access token
            expires_at: Token expiration time (defaults to 30 minutes from now)
        """
        self.access_token = token
        if expires_at is None:
            # Default to 30 minutes expiry as per Kalshi docs
            self.token_expires_at = datetime.utcnow() + timedelta(minutes=30)
        else:
            self.token_expires_at = expires_at
        
        self.logger.info(f"Access token set, expires at {self.token_expires_at}")
    
    def clear_access_token(self):
        """Clear access token"""
        self.access_token = None
        self.token_expires_at = None
        self.logger.info("Access token cleared")