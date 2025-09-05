"""
Kalshi API Client for MLB Market Data
Development version for testing and validation
"""

import requests
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import time
import hmac
import hashlib
import base64
from urllib.parse import urlencode

class KalshiClient:
    def __init__(self, credentials_file: str):
        """Initialize Kalshi client with API credentials"""
        self.base_url = "https://trading-api.kalshi.com/trade-api/v2"
        self.credentials = self._load_credentials(credentials_file)
        self.session_token = None
        
    def _load_credentials(self, creds_file: str) -> Dict:
        """Load Kalshi credentials from file"""
        try:
            credentials = {}
            with open(creds_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        credentials[key] = value
            
            # Extract private key from multi-line format
            if 'KALSHI_PRIVATE_KEY' in credentials:
                # The private key is already properly formatted in the file
                pass
                
            return credentials
            
        except FileNotFoundError:
            raise ValueError(f"Credentials file not found: {creds_file}")
    
    def authenticate(self) -> bool:
        """Authenticate with Kalshi API using API key method"""
        try:
            # Try email/password authentication first
            if 'KALSHI_EMAIL' in self.credentials and 'KALSHI_PASSWORD' in self.credentials:
                return self._authenticate_email_password()
            
            # Fall back to API key if available
            elif 'KALSHI_API_KEY' in self.credentials:
                return self._authenticate_api_key()
            
            else:
                print("No valid authentication method found")
                return False
                
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def _authenticate_email_password(self) -> bool:
        """Authenticate using email/password"""
        url = f"{self.base_url}/login"
        
        payload = {
            "email": self.credentials['KALSHI_EMAIL'],
            "password": self.credentials['KALSHI_PASSWORD']
        }
        
        try:
            print("Authenticating with Kalshi using email/password...")
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            auth_data = response.json()
            self.session_token = auth_data.get('token')
            
            if self.session_token:
                print("Successfully authenticated with Kalshi")
                return True
            else:
                print("No token received from Kalshi")
                return False
                
        except Exception as e:
            print(f"Email/password authentication failed: {e}")
            return False
    
    def _authenticate_api_key(self) -> bool:
        """Authenticate using API key (if supported)"""
        # For now, assume API key can be used directly in headers
        # This might need adjustment based on Kalshi's actual API key implementation
        print("Using API key authentication")
        self.session_token = self.credentials['KALSHI_API_KEY']
        return True
    
    def get_mlb_markets(self) -> Dict:
        """Fetch MLB-related markets from Kalshi"""
        if not self.session_token:
            if not self.authenticate():
                return {'success': False, 'error': 'Authentication failed'}
        
        url = f"{self.base_url}/markets"
        
        headers = {
            'Authorization': f'Bearer {self.session_token}',
            'Content-Type': 'application/json'
        }
        
        # Search for MLB-related markets
        params = {
            'limit': 100,
            'cursor': '',
            'event_ticker': '',  # Will search for baseball/MLB events
            'series_ticker': '',
            'status': 'open'  # Only get active markets
        }
        
        try:
            print("Fetching Kalshi MLB markets...")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Filter for MLB/baseball related markets
            all_markets = data.get('markets', [])
            mlb_markets = []
            
            for market in all_markets:
                market_title = market.get('title', '').lower()
                market_ticker = market.get('ticker', '').lower()
                
                # Look for baseball/MLB keywords
                if any(keyword in market_title or keyword in market_ticker 
                       for keyword in ['mlb', 'baseball', 'world series', 'yankees', 'dodgers', 
                                       'red sox', 'mets', 'giants', 'braves', 'astros', 'cubs']):
                    mlb_markets.append(market)
            
            print(f"Found {len(mlb_markets)} MLB-related markets out of {len(all_markets)} total markets")
            
            return {
                'success': True,
                'data': mlb_markets,
                'total_markets': len(all_markets),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'source': 'kalshi_api'
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Kalshi markets: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def normalize_kalshi_data(self, raw_data: Dict) -> List[Dict]:
        """Convert Kalshi API response to normalized schema"""
        if not raw_data.get('success'):
            return []
        
        normalized_games = []
        
        for market in raw_data.get('data', []):
            try:
                # Extract basic market info
                market_id = market.get('ticker')
                title = market.get('title', '')
                
                # Try to extract team information from title
                # This is challenging as Kalshi markets may not follow standard formats
                teams = self._extract_teams_from_title(title)
                if not teams:
                    print(f"Could not extract teams from market: {title}")
                    continue
                
                home_team, away_team = teams
                
                # Get market pricing
                yes_price = market.get('yes_price', 0) / 100.0  # Convert cents to percentage
                no_price = market.get('no_price', 0) / 100.0
                
                # Convert Kalshi prices to odds
                home_odds = self._kalshi_price_to_odds(yes_price)
                away_odds = self._kalshi_price_to_odds(no_price)
                
                # Extract game date/time if available
                event_date = market.get('close_time', market.get('expire_time'))
                game_date = event_date[:10] if event_date else None
                
                normalized_game = {
                    "game_id": f"kalshi_{market_id}",
                    "game_date": game_date,
                    "game_time": event_date,
                    "sport": "MLB",
                    "home_team": self._standardize_team_name(home_team),
                    "away_team": self._standardize_team_name(away_team),
                    "source": "kalshi",
                    "home_odds": home_odds,
                    "away_odds": away_odds,
                    "metadata": {
                        "last_updated": raw_data.get('timestamp'),
                        "bookmaker": "kalshi",
                        "market_type": "prediction_market",
                        "raw_data": market,
                        "kalshi_yes_price": yes_price,
                        "kalshi_no_price": no_price
                    }
                }
                
                normalized_games.append(normalized_game)
                
            except Exception as e:
                print(f"Error normalizing Kalshi market: {e}")
                continue
        
        print(f"Successfully normalized {len(normalized_games)} games from Kalshi")
        return normalized_games
    
    def _extract_teams_from_title(self, title: str) -> Optional[tuple]:
        """Extract team names from Kalshi market title"""
        # Common patterns in Kalshi MLB markets
        patterns = [
            # "Will the Yankees beat the Red Sox?"
            r'Will the (.+?) beat the (.+?)\?',
            # "Yankees vs Red Sox winner"
            r'(.+?) vs (.+?) winner',
            # "Yankees to win against Red Sox"
            r'(.+?) to win against (.+?)[\.\?]',
        ]
        
        import re
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                team1 = match.group(1).strip()
                team2 = match.group(2).strip()
                # Assume first team is away, second is home (may need adjustment)
                return (team2, team1)  # (home, away)
        
        return None
    
    def _kalshi_price_to_odds(self, price: float, fee: float = 0.03) -> Dict:
        """Convert Kalshi percentage price to odds object with fee adjustment"""
        if price <= 0 or price >= 1:
            price = 0.5  # Default to 50% if invalid
        
        # Adjust for Kalshi's fee structure
        adjusted_price = price * (1 - fee)
        
        # Convert to American odds
        if adjusted_price >= 0.5:
            american_odds = int(-100 * adjusted_price / (1 - adjusted_price))
        else:
            american_odds = int(100 * (1 - adjusted_price) / adjusted_price)
        
        # Calculate decimal odds and implied probability
        decimal_odds = self._american_to_decimal(american_odds)
        implied_prob = self._decimal_to_probability(decimal_odds)
        
        return {
            "american": american_odds,
            "decimal": decimal_odds,
            "implied_probability": implied_prob
        }
    
    def _american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def _decimal_to_probability(self, decimal_odds: float) -> float:
        """Convert decimal odds to implied probability"""
        return 1 / decimal_odds
    
    def _standardize_team_name(self, team_name: str) -> str:
        """Standardize team names for consistent matching"""
        # Simple team name mappings - same as Pinnacle client
        team_mappings = {
            "Los Angeles Angels": "LAA", "Angels": "LAA",
            "Houston Astros": "HOU", "Astros": "HOU",
            "Oakland Athletics": "OAK", "Athletics": "OAK", "A's": "OAK",
            "Toronto Blue Jays": "TOR", "Blue Jays": "TOR", "Jays": "TOR",
            "Atlanta Braves": "ATL", "Braves": "ATL",
            "Milwaukee Brewers": "MIL", "Brewers": "MIL",
            "St. Louis Cardinals": "STL", "Cardinals": "STL",
            "Chicago Cubs": "CHC", "Cubs": "CHC",
            "Arizona Diamondbacks": "ARI", "Diamondbacks": "ARI", "D-backs": "ARI",
            "Colorado Rockies": "COL", "Rockies": "COL",
            "Los Angeles Dodgers": "LAD", "Dodgers": "LAD",
            "San Diego Padres": "SD", "Padres": "SD",
            "San Francisco Giants": "SF", "Giants": "SF",
            "Miami Marlins": "MIA", "Marlins": "MIA",
            "New York Mets": "NYM", "Mets": "NYM",
            "Philadelphia Phillies": "PHI", "Phillies": "PHI",
            "Pittsburgh Pirates": "PIT", "Pirates": "PIT",
            "Washington Nationals": "WSH", "Nationals": "WSH",
            "Chicago White Sox": "CWS", "White Sox": "CWS",
            "Cleveland Guardians": "CLE", "Guardians": "CLE",
            "Detroit Tigers": "DET", "Tigers": "DET",
            "Kansas City Royals": "KC", "Royals": "KC",
            "Minnesota Twins": "MIN", "Twins": "MIN",
            "New York Yankees": "NYY", "Yankees": "NYY",
            "Baltimore Orioles": "BAL", "Orioles": "BAL",
            "Boston Red Sox": "BOS", "Red Sox": "BOS",
            "Tampa Bay Rays": "TB", "Rays": "TB",
            "Texas Rangers": "TEX", "Rangers": "TEX",
            "Seattle Mariners": "SEA", "Mariners": "SEA"
        }
        
        return team_mappings.get(team_name, team_name)

# Test function for development
def test_kalshi_client():
    """Test the Kalshi client functionality"""
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        
        # Test authentication
        if not client.authenticate():
            print("Authentication failed - cannot proceed with market fetch")
            return []
        
        # Fetch MLB markets
        raw_data = client.get_mlb_markets()
        print("\n=== RAW KALSHI DATA SAMPLE ===")
        if raw_data.get('success') and raw_data.get('data'):
            sample_market = raw_data['data'][0] if raw_data['data'] else {}
            print(json.dumps(sample_market, indent=2)[:500] + "...")
        else:
            print(f"No data: {raw_data}")
        
        # Normalize the data
        normalized_games = client.normalize_kalshi_data(raw_data)
        print(f"\n=== NORMALIZED KALSHI GAMES: {len(normalized_games)} ===")
        
        if normalized_games:
            print(json.dumps(normalized_games[0], indent=2))
        
        return normalized_games
        
    except Exception as e:
        print(f"Test failed: {e}")
        return []

if __name__ == "__main__":
    test_kalshi_client()