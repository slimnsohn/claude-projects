"""
Updated Kalshi API Client - Uses new endpoints and handles current market reality
Development version for testing and validation
"""

import requests
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.timestamp_utils import simplify_timestamp, simplify_date, parse_game_time_safe, format_display_time
from config.sports_config import get_sport_config, get_available_sports, SPORTS_CONFIG
import time

class KalshiClientUpdated:
    def __init__(self, credentials_file: str):
        """Initialize Kalshi client with new API endpoints"""
        # Try production endpoint first since demo may not have MLB markets
        self.production_url = "https://api.elections.kalshi.com/trade-api/v2"
        self.demo_url = "https://demo-api.kalshi.co/trade-api/v2"
        self.base_url = self.production_url  # Start with production
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
            return credentials
        except FileNotFoundError:
            raise ValueError(f"Credentials file not found: {creds_file}")
    
    def get_all_markets(self) -> Dict:
        """Fetch all available markets from Kalshi"""
        # Try both production and demo endpoints
        endpoints_to_try = [
            (self.production_url, "production"),
            (self.demo_url, "demo")
        ]
        
        for base_url, source_name in endpoints_to_try:
            url = f"{base_url}/markets"
            
            try:
                print(f"Fetching Kalshi markets from {source_name} API...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                markets = data.get('markets', [])
                
                print(f"Successfully fetched {len(markets)} markets from Kalshi {source_name}")
                
                # If we found markets, use this endpoint
                if len(markets) > 0:
                    self.base_url = base_url  # Update to working endpoint
                    return {
                        'success': True,
                        'data': markets,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'source': f'kalshi_{source_name}_api'
                    }
                    
            except requests.exceptions.RequestException as e:
                print(f"Error fetching from {source_name} API: {e}")
                continue
        
        # If both failed
        return {
            'success': False,
            'error': "Failed to fetch from both production and demo APIs",
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_sport_patterns_from_config(self) -> Dict:
        """Get sport search patterns from sports configuration"""
        sport_patterns = {}
        
        for sport_key, config in SPORTS_CONFIG.items():
            sport_patterns[sport_key] = {
                'keywords': config.kalshi_keywords,
                'tickers': config.kalshi_tickers
            }
        
        return sport_patterns
    
    
    def search_sports_markets(self, sport_type: str = 'all') -> Dict:
        """Search for sports markets using efficient series_ticker method"""
        print(f"Fetching Kalshi markets for {sport_type} sports...")
        
        sports_markets = []
        
        if sport_type == 'all':
            # Get all sports markets using series_ticker for each sport
            sport_patterns = self._get_sport_patterns_from_config()
            
            for sport, patterns in sport_patterns.items():
                for ticker_pattern in patterns['tickers']:
                    sport_markets = self._get_markets_by_series_ticker(ticker_pattern)
                    for market in sport_markets:
                        market['detected_sport'] = sport
                        sports_markets.append(market)
        else:
            # Get markets for specific sport using series_ticker
            sport_patterns = self._get_sport_patterns_from_config()
            
            if sport_type in sport_patterns:
                sport_config = sport_patterns[sport_type]
                
                for ticker_pattern in sport_config['tickers']:
                    sport_markets = self._get_markets_by_series_ticker(ticker_pattern)
                    for market in sport_markets:
                        market['detected_sport'] = sport_type
                        sports_markets.append(market)
            else:
                # Fallback to old method for unknown sports
                return self._search_sports_markets_fallback(sport_type)
        
        print(f"Found {len(sports_markets)} {sport_type} sports markets")
        
        # Group by sport for summary
        sport_counts = {}
        for market in sports_markets:
            sport = market.get('detected_sport', 'unknown')
            sport_counts[sport] = sport_counts.get(sport, 0) + 1
        
        if sport_counts:
            print("Sport breakdown:")
            for sport, count in sorted(sport_counts.items()):
                print(f"  {sport}: {count} markets")
        
        return {
            'success': True,
            'data': sports_markets,
            'total_found': len(sports_markets),
            'sport_breakdown': sport_counts,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'kalshi_sports_search'
        }
    
    def _get_markets_by_series_ticker(self, series_ticker: str) -> List[Dict]:
        """Get all markets for a specific series ticker (e.g., KXNFLGAME)"""
        try:
            url = f"{self.base_url}/markets"
            params = {'series_ticker': series_ticker}
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            markets = data.get('markets', [])
            
            return markets
            
        except Exception as e:
            print(f"Error fetching markets for series {series_ticker}: {e}")
            return []
    
    def _search_sports_markets_fallback(self, sport_type: str) -> Dict:
        """Fallback method using old search approach"""
        print(f"Using fallback search for {sport_type}...")
        
        # Get all markets using pagination
        all_markets = self._get_all_markets_paginated()
        
        if not all_markets.get('success'):
            return all_markets
        
        all_markets_data = all_markets.get('data', [])
        print(f"Searching through {len(all_markets_data)} total markets...")
        
        sports_markets = []
        sport_patterns = self._get_sport_patterns_from_config()
        
        # Search for markets
        for market in all_markets_data:
            title = market.get('title', '').lower()
            ticker = market.get('ticker', '').lower()
            
            # Check if this market matches the requested sport
            market_sport = None
            for sport, patterns in sport_patterns.items():
                if sport != sport_type:
                    continue
                    
                # Check ticker patterns first (most reliable)
                if any(pattern in ticker for pattern in patterns['tickers']):
                    market_sport = sport
                    break
                    
                # Check keywords in title
                if any(keyword in title for keyword in patterns['keywords']):
                    market_sport = sport
                    break
            
            # Add to results if matches requested sport
            if market_sport:
                market['detected_sport'] = market_sport
                sports_markets.append(market)
        
        return {
            'success': True,
            'data': sports_markets,
            'total_found': len(sports_markets),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'kalshi_fallback_search'
        }
    
    def _get_all_markets_paginated(self) -> Dict:
        """Get all markets using pagination"""
        all_markets = []
        cursor = None
        page = 1
        
        while True:
            try:
                url = f"{self.base_url}/markets"
                params = {'limit': 1000}
                if cursor:
                    params['cursor'] = cursor
                
                response = requests.get(url, params=params, timeout=60)
                response.raise_for_status()
                
                data = response.json()
                markets = data.get('markets', [])
                new_cursor = data.get('cursor', '')
                
                all_markets.extend(markets)
                
                if not new_cursor or new_cursor == cursor or len(markets) == 0:
                    break
                    
                cursor = new_cursor
                page += 1
                
                if page > 25:  # Safety limit
                    break
                    
            except Exception as e:
                print(f"Pagination error on page {page}: {e}")
                break
        
        return {
            'success': True,
            'data': all_markets,
            'total_pages': page,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'kalshi_paginated_api'
        }
    
    def get_easy_data_view(self, sport_type: str = 'all', limit: int = 20) -> Dict:
        """Easy-to-read view of Kalshi sports markets data"""
        print(f"Fetching easy data view for {sport_type} sports...")
        
        # Get sports markets
        markets_data = self.search_sports_markets(sport_type)
        
        if not markets_data.get('success'):
            return markets_data
        
        markets = markets_data.get('data', [])
        easy_view = []
        
        for market in markets[:limit]:
            ticker = market.get('ticker')
            title = market.get('title', '')
            sport = market.get('detected_sport', 'unknown')
            status = market.get('status', 'unknown')
            
            # Get pricing
            yes_bid = market.get('yes_bid', 0)
            no_bid = market.get('no_bid', 0)
            
            yes_pct = f"{yes_bid}%" if yes_bid else "N/A"
            no_pct = f"{no_bid}%" if no_bid else "N/A"
            
            close_time = market.get('close_time', '')
            easy_view.append({
                'ticker': ticker,
                'title': title,
                'sport': sport.upper(),
                'pricing': f"{yes_pct} / {no_pct}",
                'status': status,
                'close_time': simplify_timestamp(close_time) if close_time else 'N/A',
                'close_time_display': format_display_time(close_time) if close_time else 'N/A'
            })
        
        return {
            'success': True,
            'data': easy_view,
            'total_found': len(markets),
            'showing': len(easy_view),
            'sport_breakdown': markets_data.get('sport_counts', {}),
            'timestamp': markets_data.get('timestamp')
        }
    
    def normalize_kalshi_data(self, raw_data: Dict, min_time_buffer_minutes: int = 15) -> List[Dict]:
        """Convert Kalshi API response to normalized schema for all sports, filtering out live games"""
        if not raw_data.get('success'):
            return []
        
        normalized_games = []
        live_games_filtered = 0
        
        for market in raw_data.get('data', []):
            try:
                # Extract basic market info
                market_id = market.get('ticker')
                title = market.get('title', '')
                sport = market.get('detected_sport', 'unknown')
                
                # Extract team info from title
                teams = self._extract_teams_from_title(title, sport)
                if not teams:
                    print(f"Could not extract teams from market: {title}")
                    continue
                
                home_team, away_team = teams
                
                # Get market pricing - use yes_bid/no_bid (real format) or fallback to yes_price/no_price
                yes_bid = market.get('yes_bid', 0)
                no_bid = market.get('no_bid', 0)
                
                # Convert from cents to percentage
                yes_price = yes_bid / 100.0 if yes_bid else 0.5  
                no_price = no_bid / 100.0 if no_bid else 0.5
                
                # Fallback to yes_price/no_price if bids not available
                if yes_bid == 0 and no_bid == 0:
                    yes_price = market.get('yes_price', 5000) / 10000.0
                    no_price = market.get('no_price', 5000) / 10000.0
                
                # Determine which team the "YES" market refers to
                yes_team = market.get('yes_sub_title', '').strip()
                
                # Convert Kalshi prices to odds and assign correctly
                if yes_team and yes_team.lower() in home_team.lower():
                    # YES market is for home team
                    home_odds = self._kalshi_price_to_odds(yes_price, yes_bid)
                    away_odds = self._kalshi_price_to_odds(no_price, no_bid)
                elif yes_team and yes_team.lower() in away_team.lower():
                    # YES market is for away team
                    home_odds = self._kalshi_price_to_odds(no_price, no_bid)
                    away_odds = self._kalshi_price_to_odds(yes_price, yes_bid)
                else:
                    # Fallback: assume YES is for away team (common pattern)
                    home_odds = self._kalshi_price_to_odds(no_price, no_bid)
                    away_odds = self._kalshi_price_to_odds(yes_price, yes_bid)
                
                # Extract game date from ticker (e.g., KXMLBGAME-25AUG21HOUBAL-HOU)
                game_date, game_time_estimate = self._extract_date_from_ticker(market_id)
                
                # IMPORTANT: Kalshi market close_time is NOT the game time!
                # Market close_time is when the market closes (often weeks after the game)
                # We need to use the actual game time extracted from the ticker for filtering
                event_date = market.get('close_time', market.get('expire_time'))
                
                # For live game filtering, use the game time from ticker, not market close time
                if game_date and game_time_estimate:
                    # Use the actual game date/time from ticker for filtering
                    filter_time = f"{game_date}T{game_time_estimate}:00Z"
                else:
                    # Fall back to market close time only if we can't extract game time
                    filter_time = event_date
                
                # Skip games that have already started or are starting soon
                if not self._is_future_game(filter_time, min_time_buffer_minutes):
                    live_games_filtered += 1
                    continue
                
                # Use extracted date from ticker, estimated time for display
                if game_date and game_time_estimate:
                    display_time = f"{game_date} {game_time_estimate}"
                else:
                    display_time = format_display_time(event_date) if event_date else "Unknown"
                
                normalized_game = {
                    "game_id": f"kalshi_{market_id}",
                    "game_date": game_date,
                    "game_time": game_time_estimate or "Unknown",
                    "game_time_display": display_time,
                    "sport": sport.upper(),
                    "home_team": self._standardize_team_name(home_team, sport),
                    "away_team": self._standardize_team_name(away_team, sport),
                    "source": "kalshi",
                    "home_odds": home_odds,
                    "away_odds": away_odds,
                    "metadata": {
                        "last_updated": raw_data.get('timestamp'),
                        "bookmaker": "kalshi",
                        "market_type": "prediction_market",
                        "raw_data": market,
                        "kalshi_yes_price": yes_price,
                        "kalshi_no_price": no_price,
                        "original_title": title,
                        "original_close_time": event_date,
                        "ticker_parsed_date": game_date
                    }
                }
                
                normalized_games.append(normalized_game)
                
            except Exception as e:
                print(f"Error normalizing Kalshi market {market.get('ticker', 'unknown')}: {e}")
                continue
        
        if live_games_filtered > 0:
            print(f"Filtered out {live_games_filtered} live/starting games from Kalshi")
        print(f"Successfully normalized {len(normalized_games)} future games from Kalshi")
        return normalized_games
    
    def _extract_date_from_ticker(self, ticker: str) -> tuple:
        """Extract game date from Kalshi ticker format: KXMLBGAME-25AUG21HOUBAL-HOU"""
        if not ticker or '-' not in ticker:
            return None, None
        
        try:
            parts = ticker.split('-')
            if len(parts) < 2:
                return None, None
            
            # Extract date part: look for pattern like 25AUG21
            # Format appears to be: [GAME_ID][MONTH][DAY] not [DAY][MONTH][YEAR]
            # So 25AUG21 = Game 25, August 21st
            
            # Find the month abbreviation in the string
            month_map = {
                'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
                'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
                'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
            }
            
            month_str = None
            month = None
            for month_abbr, month_num in month_map.items():
                if month_abbr in parts[1]:
                    month_str = month_abbr
                    month = month_num
                    break
            
            if not month_str:
                return None, None
            
            # Extract day: everything after the month abbreviation
            month_pos = parts[1].find(month_str)
            day_part = parts[1][month_pos + 3:]  # After month abbreviation
            
            # Extract just the digits for the day
            day = ""
            for char in day_part:
                if char.isdigit():
                    day += char
                else:
                    break
            
            if not day or len(day) > 2:
                return None, None
            
            day = day.zfill(2)  # Pad with zero if needed
            
            # Use current year (2025)
            full_year = "2025"
            game_date = f"{full_year}-{month}-{day}"
            
            # Validate the date
            from datetime import datetime
            datetime.strptime(game_date, '%Y-%m-%d')
            
            # Estimate game time (most games are in evening)
            # This is a rough estimate - real time would need different logic
            estimated_time = "19:00"  # 7 PM default
            
            return game_date, estimated_time
            
        except Exception as e:
            print(f"Error parsing ticker date '{ticker}': {e}")
            return None, None
    
    def _is_future_game(self, game_time_str: str, min_buffer_minutes: int = 15) -> bool:
        """Check if game is in the future with minimum buffer using safe parsing"""
        return parse_game_time_safe(game_time_str, min_buffer_minutes)
    
    def _extract_teams_from_title(self, title: str, sport: str = 'unknown') -> Optional[tuple]:
        """Extract team names from Kalshi market title for any sport"""
        import re
        
        # Pattern for "X at Y Winner?" format (most common for Kalshi)
        at_winner_pattern = r'(.+?) at (.+?) Winner\?'
        match = re.search(at_winner_pattern, title, re.IGNORECASE)
        if match:
            away_team = match.group(1).strip()
            home_team = match.group(2).strip()
            return (home_team, away_team)  # (home, away)
        
        # Pattern for "X vs Y Winner?" format
        vs_winner_pattern = r'(.+?) vs (.+?) Winner\?'
        match = re.search(vs_winner_pattern, title, re.IGNORECASE)
        if match:
            team1 = match.group(1).strip()
            team2 = match.group(2).strip()
            return (team2, team1)  # Assume second is home
        
        # Pattern for "Will X beat Y" format
        beat_pattern = r'Will (.+?) beat (.+?)(?: on| \?|$)'
        match = re.search(beat_pattern, title, re.IGNORECASE)
        if match:
            team1 = match.group(1).strip()
            team2 = match.group(2).strip()
            return (team2, team1)  # (home, away) - team being beaten is home
        
        # Pattern for "X vs Y" format  
        vs_pattern = r'(.+?) vs (.+?)(?: |$|\?)'
        match = re.search(vs_pattern, title, re.IGNORECASE)
        if match:
            team1 = match.group(1).strip()
            team2 = match.group(2).strip()
            return (team2, team1)  # Assume second team is home
            
        # Pattern for "X at Y" format
        at_pattern = r'(.+?) at (.+?)(?: |$|\?)'
        match = re.search(at_pattern, title, re.IGNORECASE)
        if match:
            away_team = match.group(1).strip()
            home_team = match.group(2).strip()
            return (home_team, away_team)  # (home, away)
        
        return None
    
    def _kalshi_price_to_odds(self, price: float, kalshi_cents: int = 0, fee: float = 0.03) -> Dict:
        """Convert Kalshi percentage price to odds object"""
        if price <= 0 or price >= 1:
            price = 0.5
        
        # For demonstration, let's not apply fees since these are mock markets
        adjusted_price = price  # price * (1 - fee) for real markets
        
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
            "implied_probability": implied_prob,
            "kalshi_cents": kalshi_cents
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
    
    def _standardize_team_name(self, team_name: str, sport: str = 'unknown') -> str:
        """Standardize team names for consistent matching across all sports"""
        team_name = team_name.strip()
        
        # MLB team mappings
        mlb_mappings = {
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
            "Minnesota Twins": "MIN", "Twins": "MIN", "Minnesota": "MIN",
            "New York Yankees": "NYY", "Yankees": "NYY",
            "Baltimore Orioles": "BAL", "Orioles": "BAL",
            "Boston Red Sox": "BOS", "Red Sox": "BOS",
            "Tampa Bay Rays": "TB", "Rays": "TB",
            "Texas Rangers": "TEX", "Rangers": "TEX",
            "Seattle Mariners": "SEA", "Mariners": "SEA"
        }
        
        # NFL team mappings
        nfl_mappings = {
            "Arizona Cardinals": "ARI", "Cardinals": "ARI",
            "Atlanta Falcons": "ATL", "Falcons": "ATL",
            "Baltimore Ravens": "BAL", "Ravens": "BAL",
            "Buffalo Bills": "BUF", "Bills": "BUF",
            "Carolina Panthers": "CAR", "Panthers": "CAR",
            "Chicago Bears": "CHI", "Bears": "CHI",
            "Cincinnati Bengals": "CIN", "Bengals": "CIN",
            "Cleveland Browns": "CLE", "Browns": "CLE",
            "Dallas Cowboys": "DAL", "Cowboys": "DAL",
            "Denver Broncos": "DEN", "Broncos": "DEN",
            "Detroit Lions": "DET", "Lions": "DET",
            "Green Bay Packers": "GB", "Packers": "GB",
            "Houston Texans": "HOU", "Texans": "HOU",
            "Indianapolis Colts": "IND", "Colts": "IND",
            "Jacksonville Jaguars": "JAX", "Jaguars": "JAX",
            "Kansas City Chiefs": "KC", "Chiefs": "KC",
            "Las Vegas Raiders": "LV", "Raiders": "LV",
            "Los Angeles Chargers": "LAC", "Chargers": "LAC",
            "Los Angeles Rams": "LAR", "Rams": "LAR",
            "Miami Dolphins": "MIA", "Dolphins": "MIA",
            "Minnesota Vikings": "MIN", "Vikings": "MIN",
            "New England Patriots": "NE", "Patriots": "NE",
            "New Orleans Saints": "NO", "Saints": "NO",
            "New York Giants": "NYG", "Giants": "NYG",
            "New York Jets": "NYJ", "Jets": "NYJ",
            "Philadelphia Eagles": "PHI", "Eagles": "PHI",
            "Pittsburgh Steelers": "PIT", "Steelers": "PIT",
            "San Francisco 49ers": "SF", "49ers": "SF", "Niners": "SF",
            "Seattle Seahawks": "SEA", "Seahawks": "SEA",
            "Tampa Bay Buccaneers": "TB", "Buccaneers": "TB", "Bucs": "TB",
            "Tennessee Titans": "TEN", "Titans": "TEN",
            "Washington Commanders": "WAS", "Commanders": "WAS"
        }
        
        # NBA team mappings
        nba_mappings = {
            "Atlanta Hawks": "ATL", "Hawks": "ATL",
            "Boston Celtics": "BOS", "Celtics": "BOS",
            "Brooklyn Nets": "BKN", "Nets": "BKN",
            "Charlotte Hornets": "CHA", "Hornets": "CHA",
            "Chicago Bulls": "CHI", "Bulls": "CHI",
            "Cleveland Cavaliers": "CLE", "Cavaliers": "CLE", "Cavs": "CLE",
            "Dallas Mavericks": "DAL", "Mavericks": "DAL", "Mavs": "DAL",
            "Denver Nuggets": "DEN", "Nuggets": "DEN",
            "Detroit Pistons": "DET", "Pistons": "DET",
            "Golden State Warriors": "GSW", "Warriors": "GSW",
            "Houston Rockets": "HOU", "Rockets": "HOU",
            "Indiana Pacers": "IND", "Pacers": "IND",
            "Los Angeles Clippers": "LAC", "Clippers": "LAC",
            "Los Angeles Lakers": "LAL", "Lakers": "LAL",
            "Memphis Grizzlies": "MEM", "Grizzlies": "MEM",
            "Miami Heat": "MIA", "Heat": "MIA",
            "Milwaukee Bucks": "MIL", "Bucks": "MIL",
            "Minnesota Timberwolves": "MIN", "Timberwolves": "MIN", "Wolves": "MIN",
            "New Orleans Pelicans": "NOP", "Pelicans": "NOP",
            "New York Knicks": "NYK", "Knicks": "NYK",
            "Oklahoma City Thunder": "OKC", "Thunder": "OKC",
            "Orlando Magic": "ORL", "Magic": "ORL",
            "Philadelphia 76ers": "PHI", "76ers": "PHI", "Sixers": "PHI",
            "Phoenix Suns": "PHX", "Suns": "PHX",
            "Portland Trail Blazers": "POR", "Trail Blazers": "POR", "Blazers": "POR",
            "Sacramento Kings": "SAC", "Kings": "SAC",
            "San Antonio Spurs": "SAS", "Spurs": "SAS",
            "Toronto Raptors": "TOR", "Raptors": "TOR",
            "Utah Jazz": "UTA", "Jazz": "UTA",
            "Washington Wizards": "WAS", "Wizards": "WAS"
        }
        
        # NHL team mappings  
        nhl_mappings = {
            "Anaheim Ducks": "ANA", "Ducks": "ANA",
            "Arizona Coyotes": "ARI", "Coyotes": "ARI",
            "Boston Bruins": "BOS", "Bruins": "BOS",
            "Buffalo Sabres": "BUF", "Sabres": "BUF",
            "Calgary Flames": "CGY", "Flames": "CGY",
            "Carolina Hurricanes": "CAR", "Hurricanes": "CAR",
            "Chicago Blackhawks": "CHI", "Blackhawks": "CHI",
            "Colorado Avalanche": "COL", "Avalanche": "COL",
            "Columbus Blue Jackets": "CBJ", "Blue Jackets": "CBJ",
            "Dallas Stars": "DAL", "Stars": "DAL",
            "Detroit Red Wings": "DET", "Red Wings": "DET",
            "Edmonton Oilers": "EDM", "Oilers": "EDM",
            "Florida Panthers": "FLA", "Panthers": "FLA",
            "Los Angeles Kings": "LAK", "Kings": "LAK",
            "Minnesota Wild": "MIN", "Wild": "MIN",
            "Montreal Canadiens": "MTL", "Canadiens": "MTL", "Habs": "MTL",
            "Nashville Predators": "NSH", "Predators": "NSH",
            "New Jersey Devils": "NJD", "Devils": "NJD",
            "New York Islanders": "NYI", "Islanders": "NYI",
            "New York Rangers": "NYR", "Rangers": "NYR",
            "Ottawa Senators": "OTT", "Senators": "OTT",
            "Philadelphia Flyers": "PHI", "Flyers": "PHI",
            "Pittsburgh Penguins": "PIT", "Penguins": "PIT",
            "San Jose Sharks": "SJS", "Sharks": "SJS",
            "Seattle Kraken": "SEA", "Kraken": "SEA",
            "St. Louis Blues": "STL", "Blues": "STL",
            "Tampa Bay Lightning": "TBL", "Lightning": "TBL",
            "Toronto Maple Leafs": "TOR", "Maple Leafs": "TOR", "Leafs": "TOR",
            "Vancouver Canucks": "VAN", "Canucks": "VAN",
            "Vegas Golden Knights": "VGK", "Golden Knights": "VGK",
            "Washington Capitals": "WSH", "Capitals": "WSH", "Caps": "WSH",
            "Winnipeg Jets": "WPG", "Jets": "WPG"
        }
        
        # Select appropriate mapping based on sport
        if sport == 'mlb':
            return mlb_mappings.get(team_name, team_name)
        elif sport == 'nfl':
            return nfl_mappings.get(team_name, team_name)
        elif sport == 'nba':
            return nba_mappings.get(team_name, team_name)
        elif sport == 'nhl':
            return nhl_mappings.get(team_name, team_name)
        else:
            # Try all mappings if sport unknown
            for mapping in [mlb_mappings, nfl_mappings, nba_mappings, nhl_mappings]:
                if team_name in mapping:
                    return mapping[team_name]
            return team_name

# Test function for development
def test_updated_kalshi_client():
    """Test the updated Kalshi client functionality"""
    try:
        client = KalshiClientUpdated("../keys/kalshi_credentials.txt")
        
        # Test 1: Search for all sports markets
        print("=== SEARCHING FOR ALL SPORTS MARKETS ===")
        sports_data = client.search_sports_markets('all')
        print(f"Found {len(sports_data.get('data', []))} total sports markets")
        
        # Test 2: Get easy data view
        print("\n=== EASY DATA VIEW ===")
        easy_view = client.get_easy_data_view('all', 10)
        if easy_view.get('success'):
            print(f"\nShowing {easy_view['showing']} of {easy_view['total_found']} markets:")
            for market in easy_view['data']:
                print(f"  {market['sport']}: {market['title'][:50]}... | {market['pricing']}")
        
        # Test 3: Test normalization
        if sports_data.get('data'):
            print(f"\n=== NORMALIZING SPORTS DATA ===")
            normalized_games = client.normalize_kalshi_data(sports_data)
            print(f"Normalized {len(normalized_games)} games")
            
            if normalized_games:
                print(f"\nSample normalized game:")
                sample = normalized_games[0]
                print(f"  Sport: {sample['sport']}")
                print(f"  Game: {sample['away_team']} @ {sample['home_team']}")
                print(f"  Home Odds: {sample['home_odds']}")
                print(f"  Away Odds: {sample['away_odds']}")
        
        return sports_data.get('data', [])
        
    except Exception as e:
        print(f"Test failed: {e}")
        return []

if __name__ == "__main__":
    test_updated_kalshi_client()