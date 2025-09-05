"""
Simple Kalshi Prediction Market Client
Clean interface for getting games with odds data
"""

import requests
import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import pandas as pd
import pytz

class KalshiClient:
    """Simple client for fetching Kalshi market data"""
    
    def __init__(self, credentials_file: Optional[str] = None):
        """Initialize client (no auth required for public market data)"""
        # Use the working endpoints from prod_ready
        self.production_url = "https://api.elections.kalshi.com/trade-api/v2"
        self.demo_url = "https://demo-api.kalshi.co/trade-api/v2"
        self.base_url = self.production_url  # Start with production
        
        # League/sport mappings for Kalshi series tickers
        self.league_map = {
            'mlb': 'KXMLBGAME',
            'nfl': 'KXNFLGAME', 
            'nba': 'KXNBAGAME',
            'nhl': 'KXNHLGAME',
            'wnba': 'KXWNBAGAME',
            'ncaaf': 'KXNCAAFGAME',
            'soccer': 'KXEPLGAME'  # Premier League as example
        }
    
    def get_games(self, league: str = 'mlb', remove_live_games: bool = True) -> List[Dict]:
        """
        Get all games for a league
        
        Args:
            league: League name ('mlb', 'nfl', 'nba', 'nhl', 'wnba', 'soccer')
            remove_live_games: If True, filter out markets that are closed/finalized
            
        Returns:
            List of game dictionaries with standardized format
        """
        if league not in self.league_map:
            raise ValueError(f"Unsupported league: {league}. Available: {list(self.league_map.keys())}")
        
        series_ticker = self.league_map[league]
        
        # Fetch all markets for this sport
        markets = self._fetch_all_markets(series_ticker)
        
        if not markets:
            print(f"No {league.upper()} markets found")
            return []
        
        games = []
        current_time = datetime.now(timezone.utc)
        
        # Group markets by game (they come in pairs - one for each team)
        game_groups = self._group_markets_by_game(markets)
        
        for game_id, game_markets in game_groups.items():
            if len(game_markets) < 2:
                continue  # Need both teams
            
            # Parse game info from first market
            first_market = game_markets[0]
            
            # Always filter out finalized games, optionally filter closed games
            status = first_market.get('status', 'unknown')
            if status in ['finalized', 'settled', 'resolved']:
                continue  # Always skip finalized/settled/resolved games
            if remove_live_games and status in ['closed', 'live']:
                continue  # Skip closed/live games only if remove_live_games is True
            
            # Extract teams and odds
            game_info = self._parse_game_from_markets(game_markets, league)
            if game_info:
                games.append(game_info)
        
        return games
    
    def _fetch_all_markets(self, series_ticker: str) -> List[Dict]:
        """Fetch all markets for a series ticker with pagination"""
        # Try both endpoints like the working prod_ready version
        endpoints_to_try = [
            (self.production_url, "production"),
            (self.demo_url, "demo")
        ]
        
        for base_url, source_name in endpoints_to_try:
            try:
                all_markets = []
                cursor = None
                page = 1
                
                print(f"Trying {source_name} endpoint for {series_ticker}...")
                
                while True:
                    url = f"{base_url}/markets"
                    params = {
                        'series_ticker': series_ticker,
                        'limit': 200
                    }
                    if cursor:
                        params['cursor'] = cursor
                    
                    response = requests.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    
                    data = response.json()
                    markets = data.get('markets', [])
                    all_markets.extend(markets)
                    
                    print(f"  Page {page}: {len(markets)} markets (total: {len(all_markets)})")
                    
                    # Check for more pages
                    cursor = data.get('cursor')
                    if not cursor or len(markets) == 0:
                        break
                    
                    page += 1
                
                print(f"Found {len(all_markets)} total markets for {series_ticker} from {source_name}")
                
                if len(all_markets) > 0:
                    self.base_url = base_url  # Update to working endpoint
                    return all_markets
                    
            except Exception as e:
                print(f"Error with {source_name} endpoint: {e}")
                continue
        
        print(f"No markets found for {series_ticker} from any endpoint")
        return []
    
    def _group_markets_by_game(self, markets: List[Dict]) -> Dict[str, List[Dict]]:
        """Group markets by game (extract game identifier from ticker)"""
        game_groups = {}
        
        for market in markets:
            ticker = market.get('ticker', '')
            
            # Debug: Check for Ohio/Rutgers tickers (remove this debug line when not needed)
            # if 'OHIO' in ticker.upper() or 'RUTG' in ticker.upper():
            #     print(f"DEBUG FOUND TICKER: {ticker} - Status: {market.get('status', 'unknown')}")
            
            # Extract game portion from ticker (e.g., KXMLBGAME-25AUG26BOSBAL-BOS -> BOSBAL)
            game_id = self._extract_game_id(ticker)
            
            if game_id:
                if game_id not in game_groups:
                    game_groups[game_id] = []
                game_groups[game_id].append(market)
        
        return game_groups
    
    def _extract_game_id(self, ticker: str) -> Optional[str]:
        """Extract game identifier from ticker"""
        try:
            # Pattern: KXMLBGAME-25AUG26BOSBAL-BOS
            parts = ticker.split('-')
            if len(parts) >= 2:
                # Get the date+teams part (25AUG26BOSBAL)
                date_teams = parts[1]
                # Extract teams part (last 6 chars typically)
                if len(date_teams) >= 6:
                    teams_part = date_teams[-6:]  # BOSBAL
                    return teams_part
        except:
            pass
        return None
    
    def _parse_game_from_markets(self, markets: List[Dict], league: str) -> Optional[Dict]:
        """Parse game information from market pair"""
        try:
            # Sort markets to get consistent ordering
            markets = sorted(markets, key=lambda x: x.get('ticker', ''))
            
            if len(markets) < 2:
                return None
            
            # Extract teams from title or ticker
            game_info = self._extract_teams_from_markets(markets)
            if not game_info:
                return None
            
            # Get odds from market prices
            home_odds, away_odds, home_cents, away_cents = self._extract_odds_from_markets(markets, game_info)
            
            # Get game time (try to extract from ticker or use close_time)
            game_time_str, game_datetime, game_date = self._extract_game_time(markets[0])
            
            # Filter out games from the past with buffer
            if game_datetime:
                current_time = datetime.now(timezone.utc)
                time_buffer = timedelta(minutes=30)  # 30 minute buffer for Kalshi
                if game_datetime <= (current_time + time_buffer):
                    print(f"Filtered past/live Kalshi game: {game_info.get('home_team', 'Unknown')} vs {game_info.get('away_team', 'Unknown')} at {game_datetime}")
                    return None
            
            # Determine favorite and dog
            if home_odds < away_odds:
                favorite_team = game_info['home_team']
                favorite_odds = home_odds
                favorite_cents = home_cents
                dog_team = game_info['away_team']
                dog_odds = away_odds
                dog_cents = away_cents
            else:
                favorite_team = game_info['away_team']
                favorite_odds = away_odds
                favorite_cents = away_cents
                dog_team = game_info['home_team']
                dog_odds = home_odds
                dog_cents = home_cents

            return {
                'league': league.upper(),
                'favorite': favorite_team,
                'dog': dog_team,
                'fav_odds': favorite_odds,
                'dog_odds': dog_odds,
                'fav_cents': favorite_cents,
                'dog_cents': dog_cents,
                'game_time': game_time_str,
                'game_date': game_date,
                'source': 'kalshi',
                'status': markets[0].get('status', 'unknown'),
                'raw_close_time': markets[0].get('close_time', 'N/A'),
                'parsed_game_time': game_datetime.isoformat() if game_datetime else None,
                'ticker': markets[0].get('ticker', 'N/A')
            }
            
        except Exception as e:
            print(f"Error parsing game from markets: {e}")
            return None
    
    def _extract_teams_from_markets(self, markets: List[Dict]) -> Optional[Dict]:
        """Extract team names from market data"""
        try:
            # Try to get from title first
            title = markets[0].get('title', '')
            
            # Common patterns: "Team1 vs Team2 Winner?" or "Team1 at Team2 Winner?"
            if ' vs ' in title:
                teams = title.replace(' Winner?', '').split(' vs ')
            elif ' at ' in title:
                teams = title.replace(' Winner?', '').split(' at ')
            else:
                # Try to extract from ticker
                return self._extract_teams_from_ticker(markets[0].get('ticker', ''))
            
            if len(teams) == 2:
                away_team = self._normalize_team_name(teams[0].strip())
                home_team = self._normalize_team_name(teams[1].strip())
                return {'home_team': home_team, 'away_team': away_team}
                
        except:
            pass
        return None
    
    def _extract_teams_from_ticker(self, ticker: str) -> Optional[Dict]:
        """Extract teams from ticker pattern"""
        try:
            # Debug specific ticker
            if 'OHIO' in ticker.upper() and 'RUTG' in ticker.upper():
                print(f"DEBUG OHIO-RUTGERS TICKER: {ticker}")
            
            # Pattern: KXMLBGAME-25AUG26BOSBAL-BOS (MLB 6 chars)
            # Pattern: KXNCAAFGAME-25AUG28OHIORUTG-OHIO (NCAAF variable length)
            game_id = self._extract_game_id(ticker)
            
            if game_id:
                # print(f"DEBUG: Extracted game_id: {game_id} from ticker: {ticker}")
                
                # For college football, handle variable length team names
                if 'NCAAF' in ticker:
                    # Try to parse college team names (more complex)
                    return self._parse_college_teams(game_id)
                elif len(game_id) == 6:
                    # Standard 3+3 format for pro sports
                    away_team = self._normalize_team_name(game_id[:3])
                    home_team = self._normalize_team_name(game_id[3:])
                    return {'home_team': home_team, 'away_team': away_team}
        except Exception as e:
            if 'OHIO' in ticker.upper():
                print(f"DEBUG ERROR parsing {ticker}: {e}")
            pass
        return None
    
    def _parse_college_teams(self, game_id: str) -> Optional[Dict]:
        """Parse college team names from game_id like OHIORUTG"""
        try:
            # Known college team mappings for parsing
            college_teams = {
                'OHIO': 'Ohio',
                'RUTG': 'Rutgers', 
                'RUTGERS': 'Rutgers',
                'BSU': 'Boise State',
                'BOISE': 'Boise State',
                'USF': 'South Florida',
                'SOUTHFLA': 'South Florida',
                'MIAMI': 'Miami (OH)',
                'MIAMIOH': 'Miami (OH)',
                'NCSTATE': 'NC State',
                'ECU': 'East Carolina',
                'WYOMING': 'Wyoming',
                'AKRON': 'Akron',
                'UCF': 'UCF',
                'JSU': 'Jacksonville State',
                'WSU': 'Washington St.',
                'SDSU': 'San Diego St.',
                'WASH': 'Washington',
                'UW': 'Washington',
                'ASU': 'Arizona St.',
                'MSST': 'Mississippi St.',
                'UCLA': 'UCLA',
                'UNLV': 'UNLV',
                # Add more as needed
            }
            
            # Try different parsing strategies
            for team_code, team_name in college_teams.items():
                if game_id.startswith(team_code):
                    remaining = game_id[len(team_code):]
                    if remaining in college_teams:
                        away_team = self._normalize_team_name(team_name)
                        home_team = self._normalize_team_name(college_teams[remaining])
                        print(f"DEBUG: Parsed {game_id} as {away_team} @ {home_team}")
                        return {'home_team': home_team, 'away_team': away_team}
            
            # If no match found, try reverse
            for team_code, team_name in college_teams.items():
                if game_id.endswith(team_code):
                    prefix = game_id[:-len(team_code)]
                    if prefix in college_teams:
                        away_team = self._normalize_team_name(college_teams[prefix])
                        home_team = self._normalize_team_name(team_name)
                        print(f"DEBUG: Parsed {game_id} as {away_team} @ {home_team}")
                        return {'home_team': home_team, 'away_team': away_team}
            
            print(f"DEBUG: Could not parse college teams from {game_id}")
            return None
            
        except Exception as e:
            print(f"DEBUG ERROR in _parse_college_teams({game_id}): {e}")
            return None
    
    def _extract_odds_from_markets(self, markets: List[Dict], game_info: Dict) -> tuple:
        """Extract odds from market ask prices (actual crossable prices)"""
        home_odds = None
        away_odds = None
        home_cents = None
        away_cents = None
        
        for market in markets:
            # Use yes_ask (the price you pay to buy YES shares)
            # This is the actual crossable price, not last_price
            yes_ask_price = market.get('yes_ask', 50)  # Default to 50 cents (even odds)
            
            # Convert Kalshi cents to American odds using ask price
            american_odds = self._kalshi_cents_to_american(yes_ask_price)
            
            # Determine which team this market is for by ticker suffix
            ticker = market.get('ticker', '')
            
            # Extract the team code from ticker suffix (e.g., -WSU, -SDSU)
            if '-' in ticker:
                team_code = ticker.split('-')[-1]  # Get last part after final dash
                
                # Map team codes back to full team names using our college_teams mapping
                college_teams = {
                    'OHIO': 'Ohio', 'RUTG': 'Rutgers', 'RUTGERS': 'Rutgers',
                    'BSU': 'Boise State', 'BOISE': 'Boise State',
                    'USF': 'South Florida', 'SOUTHFLA': 'South Florida',
                    'MIAMI': 'Miami (OH)', 'MIAMIOH': 'Miami (OH)',
                    'NCSTATE': 'NC State', 'ECU': 'East Carolina',
                    'WYOMING': 'Wyoming', 'AKRON': 'Akron',
                    'UCF': 'UCF', 'JSU': 'Jacksonville State',
                    'WSU': 'Washington St.', 'SDSU': 'San Diego St.',
                    'WASH': 'Washington', 'UW': 'Washington',
                    'ASU': 'Arizona St.', 'MSST': 'Mississippi St.',
                    'UCLA': 'UCLA', 'UNLV': 'UNLV',
                }
                
                if team_code in college_teams:
                    team_name = self._normalize_team_name(college_teams[team_code])
                    
                    if team_name == game_info['home_team']:
                        home_odds = american_odds
                        home_cents = yes_ask_price
                    elif team_name == game_info['away_team']:
                        away_odds = american_odds
                        away_cents = yes_ask_price
        
        # If we couldn't match, assign based on order using ask prices
        if home_odds is None or away_odds is None:
            if len(markets) >= 2:
                if home_odds is None:
                    home_cents = markets[0].get('yes_ask', 50)
                    home_odds = self._kalshi_cents_to_american(home_cents)
                if away_odds is None:
                    away_cents = markets[1].get('yes_ask', 50)
                    away_odds = self._kalshi_cents_to_american(away_cents)
        
        return home_odds, away_odds, home_cents, away_cents
    
    def _kalshi_cents_to_american(self, cents: int) -> int:
        """Convert Kalshi ask price cents (1-99) to American odds using the correct formula"""
        # Use the correct Kalshi converter
        from kalshi_converter.converter import kalshi_cents_to_american_odds
        
        # Ensure cents is in valid range
        if cents <= 0:
            cents = 1
        elif cents >= 100:
            cents = 99
        
        # Get the string result and convert to int
        odds_str = kalshi_cents_to_american_odds(cents)
        
        # Convert string like "-113" or "+108" to int
        return int(odds_str)
    
    def _extract_game_time(self, market: Dict) -> tuple:
        """Extract game time from market data, return (formatted_string, datetime_obj, game_date)"""
        ticker = market.get('ticker', 'NO_TICKER')
        close_time = market.get('close_time', 'NO_CLOSE_TIME')
        
        # Debug: Show first few close_time examples (disable when not needed)
        # import random
        # if random.random() < 0.05:  # 5% chance to debug any market
        #     print(f"DEBUG DATE SAMPLE: {ticker[:30]}... close_time: {close_time}")
        
        game_datetime = None
        
        # PRIORITY: Parse date from ticker first (has correct year), then use close_time for time component
        ticker = market.get('ticker', '')
        ticker_date_parsed = False
        try:
            parts = ticker.split('-')
            if len(parts) >= 2:
                date_part = parts[1]  # e.g., 25AUG26SDSEA
                if len(date_part) >= 7:
                    # Extract date: 25AUG26 = 2025-08-26
                    year_part = date_part[:2]  # 25
                    month_part = date_part[2:5]  # AUG
                    day_part = date_part[5:7]   # 26
                    
                    # Convert month
                    months = {
                        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
                        'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
                        'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
                    }
                    
                    if month_part in months:
                        year = f"20{year_part}"
                        month = months[month_part]
                        day = day_part
                        
                        # Now try to get the correct TIME from close_time
                        if close_time:
                            try:
                                close_dt = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
                                # Use ticker date but close_time's time
                                game_datetime = datetime(
                                    int(year), int(month), int(day), 
                                    close_dt.hour, close_dt.minute, close_dt.second, 
                                    tzinfo=timezone.utc
                                )
                                # Convert to CST
                                cst = pytz.timezone('US/Central')
                                cst_datetime = game_datetime.astimezone(cst)
                                formatted_time = cst_datetime.strftime('%Y-%m-%d %H:%M CST')
                                game_date = game_datetime.strftime('%Y-%m-%d')
                                ticker_date_parsed = True
                                return formatted_time, game_datetime, game_date
                            except Exception as e:
                                print(f"Warning: Could not combine ticker date with close_time: {e}")
                        
                        # Fallback: Use ticker date with noon time
                        game_datetime = datetime(int(year), int(month), int(day), 12, 0, tzinfo=timezone.utc)
                        formatted_time = game_datetime.strftime('%Y-%m-%d %H:%M UTC')
                        game_date = game_datetime.strftime('%Y-%m-%d')
                        ticker_date_parsed = True
                        return formatted_time, game_datetime, game_date
        except Exception as e:
            print(f"Warning: Could not parse ticker {ticker}: {e}")
        
        # Fallback to close_time only (may have wrong year)
        if close_time and not ticker_date_parsed:
            try:
                game_datetime = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
                # Convert to CST
                cst = pytz.timezone('US/Central')
                cst_datetime = game_datetime.astimezone(cst)
                formatted_time = cst_datetime.strftime('%Y-%m-%d %H:%M CST')
                game_date = game_datetime.strftime('%Y-%m-%d')
                print(f"WARNING: Using close_time year which may be incorrect: {formatted_time}")
                return formatted_time, game_datetime, game_date
            except Exception as e:
                print(f"Warning: Could not parse close_time {close_time}: {e}")
        
        # Final fallback
        return "Unknown", None, "Unknown"
    
    def _normalize_team_name(self, team_name: str) -> str:
        """Normalize team names to common abbreviations"""
        # Remove common suffixes
        team_name = team_name.replace(' Winner?', '').strip()
        
        team_map = {
            # MLB
            'Arizona': 'ARI', 'Arizona Diamondbacks': 'ARI',
            'Atlanta': 'ATL', 'Atlanta Braves': 'ATL',
            'Baltimore': 'BAL', 'Baltimore Orioles': 'BAL', 
            'Boston': 'BOS', 'Boston Red Sox': 'BOS',
            'Chicago White Sox': 'CWS', 'Chicago Cubs': 'CHC',
            'Cincinnati': 'CIN', 'Cincinnati Reds': 'CIN',
            'Cleveland': 'CLE', 'Cleveland Guardians': 'CLE',
            'Colorado': 'COL', 'Colorado Rockies': 'COL',
            'Detroit': 'DET', 'Detroit Tigers': 'DET',
            'Houston': 'HOU', 'Houston Astros': 'HOU',
            'Kansas City': 'KC', 'Kansas City Royals': 'KC',
            'Los Angeles A': 'LAA', 'Los Angeles Angels': 'LAA',
            'Los Angeles D': 'LAD', 'Los Angeles Dodgers': 'LAD',
            'Miami': 'MIA', 'Miami Marlins': 'MIA',
            'Milwaukee': 'MIL', 'Milwaukee Brewers': 'MIL',
            'Minnesota': 'MIN', 'Minnesota Twins': 'MIN',
            'New York Y': 'NYY', 'New York Yankees': 'NYY',
            'New York M': 'NYM', 'New York Mets': 'NYM',
            'Oakland': 'OAK', 'Oakland Athletics': 'OAK',
            'Philadelphia': 'PHI', 'Philadelphia Phillies': 'PHI',
            'Pittsburgh': 'PIT', 'Pittsburgh Pirates': 'PIT',
            'San Diego': 'SD', 'San Diego Padres': 'SD',
            'San Francisco': 'SF', 'San Francisco Giants': 'SF',
            'Seattle': 'SEA', 'Seattle Mariners': 'SEA',
            'St Louis': 'STL', 'St. Louis Cardinals': 'STL',
            'Tampa Bay': 'TB', 'Tampa Bay Rays': 'TB',
            'Texas': 'TEX', 'Texas Rangers': 'TEX',
            'Toronto': 'TOR', 'Toronto Blue Jays': 'TOR',
            'Washington': 'WAS', 'Washington Nationals': 'WAS',
            
            # NFL
            'Arizona': 'ARI', 'Arizona Cardinals': 'ARI',
            'Atlanta': 'ATL', 'Atlanta Falcons': 'ATL',
            'Baltimore': 'BAL', 'Baltimore Ravens': 'BAL',
            'Buffalo': 'BUF', 'Buffalo Bills': 'BUF',
            'Carolina': 'CAR', 'Carolina Panthers': 'CAR',
            'Chicago': 'CHI', 'Chicago Bears': 'CHI',
            'Cincinnati': 'CIN', 'Cincinnati Bengals': 'CIN',
            'Cleveland': 'CLE', 'Cleveland Browns': 'CLE',
            'Dallas': 'DAL', 'Dallas Cowboys': 'DAL',
            'Denver': 'DEN', 'Denver Broncos': 'DEN',
            'Detroit': 'DET', 'Detroit Lions': 'DET',
            'Green Bay': 'GB', 'Green Bay Packers': 'GB',
            'Houston': 'HOU', 'Houston Texans': 'HOU',
            'Indianapolis': 'IND', 'Indianapolis Colts': 'IND',
            'Jacksonville': 'JAX', 'Jacksonville Jaguars': 'JAX',
            'Kansas City': 'KC', 'Kansas City Chiefs': 'KC',
            'Las Vegas': 'LV', 'Las Vegas Raiders': 'LV',
            'Los Angeles C': 'LAC', 'Los Angeles Chargers': 'LAC',
            'Los Angeles R': 'LAR', 'Los Angeles Rams': 'LAR',
            'Miami': 'MIA', 'Miami Dolphins': 'MIA',
            'Minnesota': 'MIN', 'Minnesota Vikings': 'MIN',
            'New England': 'NE', 'New England Patriots': 'NE',
            'New Orleans': 'NO', 'New Orleans Saints': 'NO',
            'New York G': 'NYG', 'New York Giants': 'NYG',
            'New York J': 'NYJ', 'New York Jets': 'NYJ',
            'Philadelphia': 'PHI', 'Philadelphia Eagles': 'PHI',
            'Pittsburgh': 'PIT', 'Pittsburgh Steelers': 'PIT',
            'San Francisco': 'SF', 'San Francisco 49ers': 'SF',
            'Seattle': 'SEA', 'Seattle Seahawks': 'SEA',
            'Tampa Bay': 'TB', 'Tampa Bay Buccaneers': 'TB',
            'Tennessee': 'TEN', 'Tennessee Titans': 'TEN',
            'Washington': 'WAS', 'Washington Commanders': 'WAS',
            
            # NCAAF - College Football Teams
            'Ohio': 'Ohio', 'Ohio Bobcats': 'Ohio',
            'Rutgers': 'Rutgers', 'Rutgers Scarlet Knights': 'Rutgers',
            'Boise State': 'Boise St.', 'Boise State Broncos': 'Boise St.',
            'South Florida': 'South Florida', 'South Florida Bulls': 'South Florida',
            'Wyoming': 'Wyoming', 'Wyoming Cowboys': 'Wyoming',
            'Akron': 'Akron', 'Akron Zips': 'Akron',
            'East Carolina': 'East Carolina', 'East Carolina Pirates': 'East Carolina',
            'NC State': 'North Carolina St.', 'NC State Wolfpack': 'North Carolina St.',
            'North Carolina St.': 'North Carolina St.',
            'UCF': 'UCF', 'UCF Knights': 'UCF',
            'Jacksonville State': 'Jacksonville St.', 'Jacksonville State Gamecocks': 'Jacksonville St.',
            'Jacksonville St.': 'Jacksonville St.',
            
            # Additional NCAAF Teams for comprehensive matching
            'Purdue': 'Purdue', 'Purdue Boilermakers': 'Purdue',
            'Ball St.': 'Ball St.', 'Ball State Cardinals': 'Ball St.',
            'Ohio St.': 'Ohio St.', 'Ohio State Buckeyes': 'Ohio St.',
            'TEX': 'TEX', 'Texas Longhorns': 'TEX',
            'TEN': 'TEN', 'Tennessee Volunteers': 'TEN',
            'Syracuse': 'Syracuse', 'Syracuse Orange': 'Syracuse',
            'Kentucky': 'Kentucky', 'Kentucky Wildcats': 'Kentucky',
            'Toledo': 'Toledo', 'Toledo Rockets': 'Toledo',
            'Indiana': 'Indiana', 'Indiana Hoosiers': 'Indiana',
            'Old Dominion': 'Old Dominion', 'Old Dominion Monarchs': 'Old Dominion',
            'Alabama': 'Alabama', 'Alabama Crimson Tide': 'Alabama',
            'Florida St.': 'Florida St.', 'Florida State Seminoles': 'Florida St.',
            'Temple': 'Temple', 'Temple Owls': 'Temple',
            'UMass': 'UMass', 'UMass Minutemen': 'UMass',
            'Virginia': 'Virginia', 'Virginia Cavaliers': 'Virginia',
            'Coastal Carolina': 'Coastal Carolina', 'Coastal Carolina Chanticleers': 'Coastal Carolina',
            'Clemson': 'Clemson', 'Clemson Tigers': 'Clemson',
            'LSU': 'LSU', 'LSU Tigers': 'LSU',
            'Utah St.': 'Utah St.', 'Utah State Aggies': 'Utah St.',
            'UTEP': 'UTEP', 'UTEP Miners': 'UTEP',
            'Georgia Tech': 'Georgia Tech', 'Georgia Tech Yellow Jackets': 'Georgia Tech',
            'COL': 'COL', 'Colorado Buffaloes': 'COL',
            'Auburn': 'Auburn', 'Auburn Tigers': 'Auburn',
            'Baylor': 'Baylor', 'Baylor Bears': 'Baylor',
            'UNLV': 'UNLV', 'UNLV Rebels': 'UNLV',
            'Sam Houston': 'Sam Houston', 'Sam Houston State Bearkats': 'Sam Houston',
            'San Jose St.': 'San Jose St.', 'San Jose State Spartans': 'San Jose St.',
            'Central Michigan': 'Central Michigan', 'Central Michigan Chippewas': 'Central Michigan',
            'Maryland': 'Maryland', 'Maryland Terrapins': 'Maryland',
            'Florida Atlantic': 'Florida Atlantic', 'Florida Atlantic Owls': 'Florida Atlantic',
            'Mississippi St.': 'Mississippi St.', 'Mississippi State Bulldogs': 'Mississippi St.',
            'Southern Miss': 'Southern Miss', 'Southern Mississippi Golden Eagles': 'Southern Miss',
            'Tulane': 'Tulane', 'Tulane Green Wave': 'Tulane',
            'Northwestern': 'Northwestern', 'Northwestern Wildcats': 'Northwestern',
            
            # Comprehensive NCAAF team mappings for all dates
            'Notre Dame': 'Notre Dame', 'Notre Dame Fighting Irish': 'Notre Dame',
            'Miami (FL)': 'Miami (FL)', 'Miami Hurricanes': 'Miami (FL)',
            'South Carolina': 'South Carolina', 'South Carolina Gamecocks': 'South Carolina',
            'Virginia Tech': 'Virginia Tech', 'Virginia Tech Hokies': 'Virginia Tech',
            'Texas St.': 'Texas St.', 'Texas State Bobcats': 'Texas St.',
            'Eastern Michigan': 'Eastern Michigan', 'Eastern Michigan Eagles': 'Eastern Michigan',
            'Louisiana': 'Louisiana', 'Louisiana Ragin Cajuns': 'Louisiana',
            'Rice': 'Rice', 'Rice Owls': 'Rice',
            'Texas A&M': 'Texas A&M', 'Texas A&M Aggies': 'Texas A&M',
            'UTSA': 'UTSA', 'UTSA Roadrunners': 'UTSA',
            'Georgia Southern': 'Georgia Southern', 'Georgia Southern Eagles': 'Georgia Southern',
            'Fresno St.': 'Fresno St.', 'Fresno State Bulldogs': 'Fresno St.',
            'ARI': 'ARI', 'Arizona Wildcats': 'ARI',
            'Hawai\'i': 'Hawai\'i', 'Hawaii Rainbow Warriors': 'Hawai\'i',
            'Oregon St.': 'Oregon St.', 'Oregon State Beavers': 'Oregon St.',
            'California': 'California', 'California Golden Bears': 'California',
            'WAS': 'WAS', 'Washington Huskies': 'WAS',
            'Colorado St.': 'Colorado St.', 'Colorado State Rams': 'Colorado St.',
            'Utah': 'Utah', 'Utah Utes': 'Utah',
            'UCLA': 'UCLA', 'UCLA Bruins': 'UCLA',
            'Michigan': 'Michigan', 'Michigan Wolverines': 'Michigan',
            'Michigan St.': 'Michigan St.', 'Michigan State Spartans': 'Michigan St.',
            'Western Michigan': 'Western Michigan', 'Western Michigan Broncos': 'Western Michigan',
            'Wisconsin': 'Wisconsin', 'Wisconsin Badgers': 'Wisconsin',
            'Miami (OH)': 'Miami (OH)', 'Miami (OH) RedHawks': 'Miami (OH)',
            'MIN': 'MIN', 'Minnesota Golden Gophers': 'MIN',
            'BUF': 'BUF', 'Buffalo Bulls': 'BUF',
            'Wake Forest': 'Wake Forest', 'Wake Forest Demon Deacons': 'Wake Forest',
            'Kennesaw St.': 'Kennesaw St.', 'Kennesaw State Owls': 'Kennesaw St.',
            'Nebraska': 'Nebraska', 'Nebraska Cornhuskers': 'Nebraska',
            'CIN': 'CIN', 'Cincinnati Bearcats': 'CIN',
            'Appalachian St.': 'Appalachian St.', 'Appalachian State Mountaineers': 'Appalachian St.',
            'Charlotte': 'Charlotte', 'Charlotte 49ers': 'Charlotte'
        }
        
        return team_map.get(team_name, team_name)
    
    def print_games_table(self, games: List[Dict]):
        """Print games in a clean table format"""
        if not games:
            print("No games found")
            return
        
        df = pd.DataFrame(games)
        
        # Sort by date first, then by dog odds (highest to lowest)
        df = df.sort_values(['game_date', 'dog_odds'], ascending=[True, False])
        
        df = df[['league', 'game_date', 'favorite', 'dog', 'fav_odds', 'dog_odds', 'game_time', 'status']]
        df.columns = ['League', 'Date', 'Favorite', 'Dog', 'Fav Odds', 'Dog Odds', 'Game Time', 'Status']
        
        print(f"\nKALSHI GAMES ({len(games)} found) - Sorted by Dog Odds")
        print("=" * 95)
        print(df.to_string(index=False))
        print()

if __name__ == "__main__":
    # Test the client
    client = KalshiClient()
    
    for league in ['ncaaf']:
        print(f"\nTesting {league.upper()}...")
        games = client.get_games(league=league, remove_live_games=True)
        client.print_games_table(games)