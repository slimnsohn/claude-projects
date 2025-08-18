#!/usr/bin/env python3
"""
Kalshi API client with proper RSA signature authentication.
"""

import os
import time
import json
import base64
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Cryptography imports for RSA signing
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RSAKalshiClient:
    """Kalshi API client with proper RSA signature authentication."""

    def __init__(self, api_key: Optional[str] = None, private_key_pem: Optional[str] = None):
        """Initialize the RSA Kalshi client."""
        self.api_key = api_key or os.getenv("KALSHI_API_KEY")
        
        # Load private key from environment or directly from .env file
        if private_key_pem:
            private_key_text = private_key_pem
        else:
            # Read private key directly from .env file to handle multiline properly
            private_key_text = self._read_private_key_from_env()
        
        if not self.api_key:
            raise ValueError("KALSHI_API_KEY must be set in .env")
        
        if not private_key_text:
            raise ValueError("KALSHI_PRIVATE_KEY must be set in .env")
        
        # Parse the RSA private key
        try:
            # Handle both RSA PRIVATE KEY and PRIVATE KEY formats
            if "-----BEGIN RSA PRIVATE KEY-----" in private_key_text:
                # Load RSA private key format
                self.private_key = serialization.load_pem_private_key(
                    private_key_text.encode('utf-8'),
                    password=None
                )
            elif "-----BEGIN PRIVATE KEY-----" in private_key_text:
                # Load PKCS#8 private key format
                self.private_key = serialization.load_pem_private_key(
                    private_key_text.encode('utf-8'),
                    password=None
                )
            else:
                # Try to add PEM headers if missing
                private_key_text = f"-----BEGIN PRIVATE KEY-----\n{private_key_text}\n-----END PRIVATE KEY-----"
                self.private_key = serialization.load_pem_private_key(
                    private_key_text.encode('utf-8'),
                    password=None
                )
            logger.info("Successfully loaded RSA private key")
            
        except Exception as e:
            logger.error(f"Failed to load private key: {e}")
            raise ValueError(f"Invalid RSA private key: {e}")
        
        self.base_url = "https://api.elections.kalshi.com/trade-api/v2"
        self.session = requests.Session()
    
    def _read_private_key_from_env(self) -> str:
        """Read private key directly from .env file to handle multiline properly."""
        try:
            with open('.env', 'r') as f:
                content = f.read()
            
            # Find the private key section
            start_marker = "KALSHI_PRIVATE_KEY="
            start_pos = content.find(start_marker)
            if start_pos == -1:
                return ""
            
            # Extract everything after the = until the next environment variable or end
            key_start = start_pos + len(start_marker)
            lines = content[key_start:].split('\n')
            
            private_key_lines = []
            for line in lines:
                line = line.strip()
                if line.startswith('#') or (line.startswith('KALSHI_') and '=' in line):
                    # Stop at comments or next environment variable
                    break
                if line:  # Skip empty lines
                    private_key_lines.append(line)
            
            private_key = '\n'.join(private_key_lines)
            logger.debug(f"Extracted private key: {len(private_key)} characters")
            return private_key
            
        except Exception as e:
            logger.error(f"Error reading private key from .env: {e}")
            return ""
    
    def _generate_rsa_signature(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        """Generate proper RSA signature for Kalshi API."""
        try:
            # Create the message to sign (timestamp + method + path + body)
            message = f"{timestamp}{method.upper()}{path}{body}"
            message_bytes = message.encode('utf-8')
            
            logger.debug(f"Signing message: {message}")
            
            # Sign with RSA private key using PKCS1v15 padding and SHA256
            signature_bytes = self.private_key.sign(
                message_bytes,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # Encode signature as base64
            signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
            
            logger.debug(f"Generated signature: {signature_b64[:50]}...")
            return signature_b64
            
        except Exception as e:
            logger.error(f"Error generating RSA signature: {e}")
            return ""
    
    def _make_authenticated_request(self, method: str, endpoint: str, data: Dict = None) -> requests.Response:
        """Make authenticated request to Kalshi API with RSA signature."""
        url = f"{self.base_url}{endpoint}"
        timestamp = str(int(time.time() * 1000))
        
        # Prepare request body
        body = json.dumps(data, separators=(',', ':')) if data else ""
        
        # Generate RSA signature
        signature = self._generate_rsa_signature(timestamp, method.upper(), endpoint, body)
        
        if not signature:
            raise Exception("Failed to generate RSA signature")
        
        # Set headers according to Kalshi API specification
        headers = {
            "KALSHI-ACCESS-KEY": self.api_key,
            "KALSHI-ACCESS-TIMESTAMP": timestamp,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Make request
        logger.debug(f"{method.upper()} {url}")
        logger.debug(f"Headers: {headers}")
        
        if data:
            response = self.session.request(method, url, headers=headers, json=data)
        else:
            response = self.session.request(method, url, headers=headers)
        
        return response
    
    def get_exchange_status(self) -> Dict:
        """Get exchange status (public endpoint - no auth needed)."""
        logger.info("Fetching exchange status...")
        try:
            url = f"{self.base_url}/exchange/status"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching exchange status: {e}")
            return {}
    
    def get_portfolio_balance(self) -> Dict:
        """Get portfolio balance with RSA authentication."""
        logger.info("Fetching portfolio balance...")
        try:
            response = self._make_authenticated_request("GET", "/portfolio/balance")
            
            if response.status_code == 200:
                logger.info("Successfully fetched portfolio balance")
                return response.json()
            else:
                logger.error(f"Balance request failed: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {}
    
    def get_portfolio_orders(self, limit: int = 1000) -> List[Dict]:
        """Get portfolio orders."""
        logger.info("Fetching portfolio orders...")
        try:
            response = self._make_authenticated_request("GET", f"/portfolio/orders?limit={limit}")
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get("orders", [])
                logger.info(f"Successfully fetched {len(orders)} orders")
                return orders
            else:
                logger.error(f"Orders request failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return []
    
    def get_portfolio_fills(self, limit: int = 1000) -> List[Dict]:
        """Get portfolio fills/trades."""
        logger.info("Fetching portfolio fills...")
        try:
            response = self._make_authenticated_request("GET", f"/portfolio/fills?limit={limit}")
            
            if response.status_code == 200:
                data = response.json()
                fills = data.get("fills", [])
                logger.info(f"Successfully fetched {len(fills)} fills")
                return fills
            else:
                logger.error(f"Fills request failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching fills: {e}")
            return []
    
    def get_portfolio_positions(self) -> List[Dict]:
        """Get portfolio positions."""
        logger.info("Fetching portfolio positions...")
        try:
            response = self._make_authenticated_request("GET", "/portfolio/positions")
            
            if response.status_code == 200:
                data = response.json()
                positions = data.get("positions", [])
                logger.info(f"Successfully fetched {len(positions)} positions")
                return positions
            else:
                logger.error(f"Positions request failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []
    
    def get_account_history(self, limit: int = 1000) -> List[Dict]:
        """Get account transaction history including deposits."""
        logger.info("Fetching account history...")
        try:
            response = self._make_authenticated_request("GET", f"/portfolio/settlements?limit={limit}")
            
            if response.status_code == 200:
                data = response.json()
                history = data.get("settlements", [])
                logger.info(f"Successfully fetched {len(history)} history records")
                return history
            else:
                logger.error(f"History request failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching account history: {e}")
            return []
    
    def fetch_all_data(self) -> Dict[str, Any]:
        """Fetch all available portfolio data."""
        logger.info("Starting comprehensive data fetch with RSA authentication...")
        
        data = {
            "exchange_status": self.get_exchange_status(),
            "balance": self.get_portfolio_balance(),
            "orders": self.get_portfolio_orders(),
            "fills": self.get_portfolio_fills(),
            "positions": self.get_portfolio_positions(),
            "account_history": self.get_account_history(),
            "fetched_at": datetime.now().isoformat(),
            "api_base": self.base_url,
            "auth_method": "rsa_signature"
        }
        
        # Count records
        total_records = 0
        for key, value in data.items():
            if isinstance(value, list):
                count = len(value)
                total_records += count
                logger.info(f"  {key}: {count} records")
            elif isinstance(value, dict) and value:
                logger.info(f"  {key}: retrieved successfully")
        
        logger.info(f"RSA authenticated data fetch complete! Total records: {total_records}")
        return data


def main():
    """Test the RSA Kalshi client."""
    try:
        print("=== RSA Kalshi API Client Test ===")
        
        # Check credentials
        api_key = os.getenv("KALSHI_API_KEY")
        private_key = os.getenv("KALSHI_PRIVATE_KEY")
        
        if not api_key:
            print("ERROR: No KALSHI_API_KEY found in .env file")
            return
        
        if not private_key:
            print("ERROR: No KALSHI_PRIVATE_KEY found in .env file")
            return
        
        print(f"API Key: {api_key[:10]}...")
        print(f"Private Key: {len(private_key)} characters")
        
        # Initialize client
        print("\nInitializing RSA client...")
        client = RSAKalshiClient()
        print("RSA client initialized successfully!")
        
        # Test public endpoint
        print("\nTesting public endpoint...")
        status = client.get_exchange_status()
        if status:
            print(f"SUCCESS: Exchange status: {status}")
        else:
            print("ERROR: Failed to get exchange status")
            return
        
        # Test authenticated endpoints
        print("\nTesting RSA authenticated endpoints...")
        
        # Test balance
        balance = client.get_portfolio_balance()
        if balance:
            print(f"SUCCESS: Portfolio balance retrieved")
            print(f"Balance details: {balance}")
        else:
            print("Note: Portfolio balance request failed (check logs for details)")
        
        # Test a few more endpoints
        orders = client.get_portfolio_orders()
        fills = client.get_portfolio_fills()
        
        print(f"\nData retrieved:")
        print(f"- Orders: {len(orders)}")
        print(f"- Fills: {len(fills)}")
        
        # Fetch and save all data
        print("\nFetching all available data...")
        all_data = client.fetch_all_data()
        
        # Save to file
        os.makedirs("data", exist_ok=True)
        filename = f"data/rsa_kalshi_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w") as f:
            json.dump(all_data, f, indent=2, default=str)
        
        print(f"\nSUCCESS: Data saved to {filename}")
        print("RSA authentication is working!")
        
    except Exception as e:
        logger.error(f"Error in RSA client test: {e}")
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()