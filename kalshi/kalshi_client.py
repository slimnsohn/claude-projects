#!/usr/bin/env python3
"""
Kalshi API Client for fetching trading data and transactions.
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import requests
import kalshi

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KalshiClient:
    """Client for interacting with Kalshi API to fetch trading data."""
    
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the Kalshi client with credentials."""
        self.email = email or os.getenv('KALSHI_EMAIL')
        self.password = password or os.getenv('KALSHI_PASSWORD')
        self.api_key = api_key or os.getenv('KALSHI_API_KEY')
        
        # Setup API configuration
        self.configuration = kalshi.Configuration(
            host="https://trading-api.kalshi.com/v1"
        )
        
        # Initialize API clients
        self.api_client = None
        self.auth_api = None
        self.user_api = None
        self.portfolio_api = None
        
        self._setup_clients()
        
    def _setup_clients(self):
        """Setup the various API clients."""
        try:
            self.api_client = kalshi.ApiClient(self.configuration)
            self.auth_api = kalshi.AuthApi(self.api_client)
            self.user_api = kalshi.UserApi(self.api_client)
            self.portfolio_api = kalshi.PortfolioApi(self.api_client)
            logger.info("Kalshi API clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize API clients: {e}")
            raise
    
    def authenticate(self) -> bool:
        """Authenticate with Kalshi API using email/password or API key."""
        try:
            if self.email and self.password:
                # Login with email/password
                login_request = kalshi.LoginRequest(
                    email=self.email,
                    password=self.password
                )
                response = self.auth_api.login(login_request)
                logger.info("Successfully authenticated with email/password")
                return True
                
            elif self.api_key:
                # Use API key authentication
                self.configuration.api_key['cookie'] = self.api_key
                logger.info("API key configured for authentication")
                return True
                
            else:
                logger.error("No valid credentials provided. Please set KALSHI_EMAIL/KALSHI_PASSWORD or KALSHI_API_KEY")
                return False
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def get_user_orders(self, limit: int = 1000, cursor: Optional[str] = None) -> List[Dict]:
        """Fetch all user orders."""
        try:
            logger.info("Fetching user orders...")
            response = self.user_api.user_orders_get(limit=limit, cursor=cursor)
            orders = response.orders if hasattr(response, 'orders') else []
            logger.info(f"Retrieved {len(orders)} orders")
            return [order.to_dict() for order in orders]
        except Exception as e:
            logger.error(f"Failed to fetch orders: {e}")
            return []
    
    def get_user_fills(self, limit: int = 1000, cursor: Optional[str] = None) -> List[Dict]:
        """Fetch all user fills/trades."""
        try:
            logger.info("Fetching user fills...")
            response = self.user_api.user_trades_get(limit=limit, cursor=cursor)
            fills = response.trades if hasattr(response, 'trades') else []
            logger.info(f"Retrieved {len(fills)} fills")
            return [fill.to_dict() for fill in fills]
        except Exception as e:
            logger.error(f"Failed to fetch fills: {e}")
            return []
    
    def get_user_positions(self) -> List[Dict]:
        """Fetch all user market positions."""
        try:
            logger.info("Fetching user positions...")
            response = self.user_api.user_get_market_positions()
            positions = response.market_positions if hasattr(response, 'market_positions') else []
            logger.info(f"Retrieved {len(positions)} positions")
            return [pos.to_dict() for pos in positions]
        except Exception as e:
            logger.error(f"Failed to fetch positions: {e}")
            return []
    
    def get_account_history(self, limit: int = 1000, cursor: Optional[str] = None) -> List[Dict]:
        """Fetch account transaction history."""
        try:
            logger.info("Fetching account history...")
            response = self.user_api.user_get_account_history(limit=limit, cursor=cursor)
            history = response.history if hasattr(response, 'history') else []
            logger.info(f"Retrieved {len(history)} account history entries")
            return [entry.to_dict() for entry in history]
        except Exception as e:
            logger.error(f"Failed to fetch account history: {e}")
            return []
    
    def fetch_all_data(self) -> Dict[str, List[Dict]]:
        """Fetch all trading data (orders, fills, positions, history)."""
        logger.info("Starting complete data fetch...")
        
        data = {
            'orders': self.get_user_orders(),
            'fills': self.get_user_fills(),
            'positions': self.get_user_positions(),
            'account_history': self.get_account_history(),
            'fetched_at': datetime.now().isoformat()
        }
        
        total_records = sum(len(data[key]) for key in data if key != 'fetched_at')
        logger.info(f"Data fetch complete. Total records: {total_records}")
        
        return data


def main():
    """Main function for testing the client."""
    try:
        # Initialize client
        client = KalshiClient()
        
        # Authenticate
        if not client.authenticate():
            logger.error("Authentication failed. Please check your credentials.")
            return
        
        # Fetch all data
        all_data = client.fetch_all_data()
        
        # Save to file
        os.makedirs('data', exist_ok=True)
        filename = f"data/kalshi_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(all_data, f, indent=2, default=str)
        
        logger.info(f"Data saved to {filename}")
        
        # Print summary
        print("\n=== Data Fetch Summary ===")
        print(f"Orders: {len(all_data['orders'])}")
        print(f"Fills/Trades: {len(all_data['fills'])}")
        print(f"Positions: {len(all_data['positions'])}")
        print(f"Account History: {len(all_data['account_history'])}")
        print(f"Saved to: {filename}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    main()