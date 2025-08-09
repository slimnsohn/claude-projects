#!/usr/bin/env python3
"""
Kalshi API Client for fetching trading data and transactions.
Uses the working v1 API with session-based authentication.
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class KalshiClient:
    """Client for interacting with Kalshi API to fetch trading data."""

    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """Initialize the Kalshi client with credentials."""
        self.email = email or os.getenv("KALSHI_EMAIL")
        self.password = password or os.getenv("KALSHI_PASSWORD")
        self.base_url = "https://api.elections.kalshi.com/v1"
        self.session = requests.Session()
        self.authenticated = False

        if not self.email or not self.password:
            raise ValueError("KALSHI_EMAIL and KALSHI_PASSWORD must be set in .env")

    def authenticate(self) -> bool:
        """Authenticate with Kalshi using email/password and session cookies."""
        logger.info("🔐 Starting session authentication...")

        login_data = {"email": self.email, "password": self.password}

        try:
            response = self.session.post(
                f"{self.base_url}/login",
                json=login_data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=10,
            )

            logger.info(f"Login response: {response.status_code}")

            if response.status_code == 200:
                # Test authentication by trying to access a protected endpoint
                test_response = self.session.get(f"{self.base_url}/me", timeout=10)

                if test_response.status_code == 200:
                    self.authenticated = True
                    logger.info("✅ Session authentication successful!")
                    return True
                else:
                    logger.error(f"❌ Auth test failed: {test_response.status_code}")
                    return False
            else:
                logger.error(
                    f"❌ Login failed: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False

    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Make authenticated request using session."""
        if not self.authenticated:
            logger.error("❌ Not authenticated! Call authenticate() first.")
            return None

        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.request(method, url, timeout=30, **kwargs)

            logger.info(f"{method} {endpoint}: {response.status_code}")

            if response.status_code == 200:
                if response.text:
                    try:
                        return response.json()
                    except:
                        return response.text
                else:
                    return {"status": "success", "empty_response": True}
            else:
                logger.error(
                    f"Request failed {endpoint}: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"Request error {endpoint}: {e}")
            return None

    def get_user_info(self):
        """Get user profile information."""
        logger.info("Fetching user info...")
        return self._make_request("GET", "/me")

    def get_user_orders(
        self, limit: int = 1000, cursor: Optional[str] = None
    ) -> List[Dict]:
        """Fetch all user orders."""
        logger.info("Fetching portfolio orders...")
        response = self._make_request(
            "GET", "/portfolio/orders", params={"limit": limit}
        )
        if isinstance(response, dict) and "orders" in response:
            return response["orders"]
        return response if isinstance(response, list) else []

    def get_user_fills(
        self, limit: int = 1000, cursor: Optional[str] = None
    ) -> List[Dict]:
        """Fetch all user fills/trades."""
        logger.info("Fetching portfolio fills...")
        response = self._make_request(
            "GET", "/portfolio/fills", params={"limit": limit}
        )
        if isinstance(response, dict) and "fills" in response:
            return response["fills"]
        return response if isinstance(response, list) else []

    def get_user_positions(self) -> List[Dict]:
        """Fetch all user market positions."""
        logger.info("Fetching portfolio positions...")
        response = self._make_request("GET", "/portfolio/positions")
        if isinstance(response, dict) and "positions" in response:
            return response["positions"]
        return response if isinstance(response, list) else []

    def get_account_history(
        self, limit: int = 1000, cursor: Optional[str] = None
    ) -> List[Dict]:
        """Fetch account transaction history."""
        logger.info("Fetching portfolio settlements...")
        response = self._make_request(
            "GET", "/portfolio/settlements", params={"limit": limit}
        )
        if isinstance(response, dict) and "settlements" in response:
            return response["settlements"]
        return response if isinstance(response, list) else []

    def get_portfolio_balance(self):
        """Get portfolio balance."""
        logger.info("Fetching portfolio balance...")
        return self._make_request("GET", "/portfolio/balance")

    def fetch_all_data(self) -> Dict[str, Any]:
        """Fetch all trading data (orders, fills, positions, history)."""
        logger.info("🚀 Starting comprehensive data fetch...")

        if not self.authenticated:
            logger.error("❌ Must authenticate first!")
            return None

        data = {
            "user_info": self.get_user_info(),
            "balance": self.get_portfolio_balance(),
            "orders": self.get_user_orders(),
            "fills": self.get_user_fills(),
            "positions": self.get_user_positions(),
            "account_history": self.get_account_history(),
            "fetched_at": datetime.now().isoformat(),
            "api_base": self.base_url,
        }

        # Count records
        record_counts = {}
        total_records = 0

        for key, value in data.items():
            if isinstance(value, list):
                count = len(value)
                record_counts[key] = count
                total_records += count
                logger.info(f"  📊 {key}: {count} records")
            elif isinstance(value, dict) and value and not value.get("empty_response"):
                record_counts[key] = 1
                logger.info(f"  📊 {key}: retrieved")
            else:
                record_counts[key] = 0

        logger.info(f"✅ Data fetch complete! Total records: {total_records}")
        return data


def main():
    """Main function for testing the client."""
    try:
        # Initialize client
        client = KalshiClient()

        # Authenticate
        if not client.authenticate():
            logger.error("❌ Authentication failed. Please check your credentials.")
            return

        # Fetch all data
        all_data = client.fetch_all_data()

        if not all_data:
            logger.error("❌ Failed to fetch data!")
            return

        # Save to file
        os.makedirs("data", exist_ok=True)
        filename = f"data/kalshi_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, "w") as f:
            json.dump(all_data, f, indent=2, default=str)

        logger.info(f"💾 Data saved to {filename}")

        # Print summary
        print("\n" + "=" * 60)
        print("🎉 KALSHI DATA SUCCESSFULLY RETRIEVED!")
        print("=" * 60)

        user_info = all_data.get("user_info", {})
        balance = all_data.get("balance", {})
        orders = all_data.get("orders", [])
        fills = all_data.get("fills", [])
        positions = all_data.get("positions", [])
        account_history = all_data.get("account_history", [])

        if user_info and isinstance(user_info, dict):
            print(f"User: {user_info.get('email', 'N/A')}")

        if balance and isinstance(balance, dict):
            print(f"Balance: {balance}")

        print(f"\n📊 Portfolio Summary:")
        print(f"  Orders: {len(orders) if isinstance(orders, list) else 'N/A'}")
        print(f"  Fills/Trades: {len(fills) if isinstance(fills, list) else 'N/A'}")
        print(
            f"  Positions: {len(positions) if isinstance(positions, list) else 'N/A'}"
        )
        print(
            f"  Account History: {len(account_history) if isinstance(account_history, list) else 'N/A'}"
        )

        print(f"\n💾 Full data saved to: {filename}")
        print("✅ Your Kalshi data retrieval is working!")

    except Exception as e:
        logger.error(f"❌ Error in main: {e}")


if __name__ == "__main__":
    main()
