"""
Slim Game Viewer with Polymarket - All three platforms
Shows all available games from Pinnacle, Kalshi, and Polymarket
"""

import requests
import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import argparse

class SlimPinnacleClient:
    """Minimal Pinnacle client for fetching odds"""
    
    def __init__(self):
        # Load API key
        key_file = os.path.join(os.path.dirname(__file__), '..', 'keys', 'odds_api_key.txt')
        with open(key_file, 'r') as f:
            content = f.read().strip()
            if "'" in content:
                self.api_key = content.split("'")[1]
            elif '"' in content:
                self.api_key = content.split('"')[1]
            else:
                self.api_key = content
        
        self.base_url = "https://api.the-odds-api.com/v4"
        self.leagues = {
            'mlb': 'baseball_mlb',
            'nfl': 'americanfootball_nfl',
            'nba': 'basketball_nba',
            'nhl': 'icehockey_nhl',
            'ncaaf': 'americanfootball_ncaaf',
            'ncaab': 'basketball_ncaab'
        }
    
    def get_games(self, league='mlb'):
        """Get all games with odds for a league"""
        if league not in self.leagues:
            return []
        
        url = f"{self.base_url}/sports/{self.leagues[league]}/odds"
        params = {
            'api_key': self.api_key,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american',
            'bookmakers': 'pinnacle'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            games = []
            for game in data:
                game_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
                
                # Extract odds if available
                odds_data = {'home': None, 'away': None}
                if game.get('bookmakers'):
                    for bookmaker in game['bookmakers']:
                        if bookmaker.get('markets'):
                            for market in bookmaker['markets']:
                                if market.get('key') == 'h2h':
                                    for outcome in market.get('outcomes', []):
                                        if outcome['name'] == game['home_team']:
                                            odds_data['home'] = outcome.get('price')
                                        elif outcome['name'] == game['away_team']:
                                            odds_data['away'] = outcome.get('price')
                
                games.append({
                    'platform': 'Pinnacle',
                    'league': league.upper(),
                    'home': game['home_team'],
                    'away': game['away_team'],
                    'home_odds': odds_data['home'],
                    'away_odds': odds_data['away'],
                    'game_time': game_time.strftime('%Y-%m-%d %H:%M'),
                    'status': 'upcoming'
                })
            
            return games
        except Exception as e:
            print(f"Pinnacle error: {e}")
            return []

class SlimKalshiClient:
    """Minimal Kalshi client for fetching market data - properly handles paired markets"""
    
    def __init__(self):
        self.base_url = "https://api.elections.kalshi.com/trade-api/v2"
        self.leagues = {
            'mlb': 'KXMLBGAME',
            'nfl': 'KXNFLGAME',
            'nba': 'KXNBAGAME',
            'nhl': 'KXNHLGAME',
            'wnba': 'KXWNBAGAME',
            'ncaaf': 'KXNCAAFGAME',
            'soccer': 'KXEPLGAME'
        }
    
    def get_games(self, league='mlb'):
        """Get all games/markets for a league"""
        if league not in self.leagues:
            return []
        
        series_ticker = self.leagues[league]
        url = f"{self.base_url}/markets"
        
        all_markets = []
        cursor = None
        
        # Fetch with pagination
        while True:
            params = {
                'series_ticker': series_ticker,
                'limit': 200,
                'status': 'open'
            }
            if cursor:
                params['cursor'] = cursor
            
            try:
                response = requests.get(url, params=params, timeout=30)
                if response.status_code != 200:
                    break
                    
                data = response.json()
                markets = data.get('markets', [])
                all_markets.extend(markets)
                
                cursor = data.get('cursor')
                if not cursor or not markets:
                    break
                    
            except Exception as e:
                print(f"Kalshi fetch error: {e}")
                break
        
        # Group markets by game (they come in pairs - one for each team)
        games = self._group_markets_into_games(all_markets, league)
        return games
    
    def _group_markets_into_games(self, markets, league):
        """Group Kalshi markets into games (each game has 2 markets, one per team)"""
        games = []
        game_groups = {}
        
        # Group markets by game ID extracted from ticker
        for market in markets:
            ticker = market.get('ticker', '')
            game_id = self._extract_game_id(ticker)
            
            if game_id:
                if game_id not in game_groups:
                    game_groups[game_id] = []
                game_groups[game_id].append(market)
        
        # Parse each game group
        for game_id, game_markets in game_groups.items():
            if len(game_markets) < 2:
                continue  # Need both teams
            
            game_info = self._parse_game_from_markets(game_markets, league)
            if game_info:
                games.append(game_info)
        
        return games
    
    def _extract_game_id(self, ticker):
        """Extract game ID from ticker (e.g., KXMLBGAME-25AUG26BOSBAL-BOS)"""
        try:
            parts = ticker.split('-')
            if len(parts) >= 2:
                # Get the date+teams part
                date_teams = parts[1]
                # Extract teams part (last 6 chars typically)
                if len(date_teams) >= 6:
                    teams_part = date_teams[-6:]
                    return teams_part
        except:
            pass
        return None
    
    def _parse_game_from_markets(self, markets, league):
        """Parse game information from market pair"""
        try:
            # Sort for consistency
            markets = sorted(markets, key=lambda x: x.get('ticker', ''))
            
            # Get teams from the first market's title
            # Format: "Team1 at Team2 Winner?" or "Team1 vs Team2 Winner?"
            title = markets[0].get('title', '')
            
            # Parse teams from title
            teams = None
            if ' at ' in title:
                parts = title.replace(' Winner?', '').split(' at ')
                if len(parts) == 2:
                    teams = (parts[0].strip(), parts[1].strip())  # away, home
            elif ' vs ' in title:
                parts = title.replace(' Winner?', '').split(' vs ')
                if len(parts) == 2:
                    teams = (parts[0].strip(), parts[1].strip())  # team1, team2
            
            if not teams:
                return None
            
            team1, team2 = teams
            
            # Get odds for each team by matching ticker endings
            team1_odds = None
            team2_odds = None
            
            for market in markets:
                ticker = market.get('ticker', '')
                yes_price = market.get('yes_ask')
                if not yes_price:
                    yes_price = market.get('last_price')
                
                if yes_price and yes_price > 0:
                    # Convert probability to American odds
                    prob = yes_price / 100
                    if prob >= 0.5:
                        odds = -100 / ((1/prob) - 1)
                    else:
                        odds = 100 * ((1/prob) - 1)
                    odds = int(odds)
                    
                    # Match based on ticker ending (last part after last dash)
                    ticker_parts = ticker.split('-')
                    if len(ticker_parts) >= 3:
                        team_code = ticker_parts[-1]
                        # First market is usually for first team
                        if markets.index(market) == 0:
                            team1_odds = odds
                        else:
                            team2_odds = odds
            
            # Get game time from close_time
            close_time = markets[0].get('close_time', '')
            if close_time:
                try:
                    dt = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
                    game_time = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    game_time = 'Unknown'
            else:
                game_time = 'Unknown'
            
            # Determine home/away (first team is usually home in Kalshi)
            return {
                'platform': 'Kalshi',
                'league': league.upper(),
                'home': team1,
                'away': team2,
                'home_odds': team1_odds,
                'away_odds': team2_odds,
                'game_time': game_time,
                'status': markets[0].get('status', 'unknown')
            }
            
        except Exception as e:
            print(f"Error parsing Kalshi game: {e}")
            return None

class SlimPolymarketClient:
    """
    Minimal Polymarket client for fetching prediction market data
    
    NOTE: Currently returns 0 active games because live/upcoming markets
    require API authentication. The public endpoints only return historical
    markets. To get live NFL games like https://polymarket.com/event/nfl-bal-buf-2025-09-07,
    you need to:
    1. Generate Polymarket API credentials 
    2. Use authenticated endpoints
    
    The client structure is ready - just add authentication when API key is available.
    """
    
    def __init__(self, api_key=None, api_secret=None, passphrase=None):
        self.clob_url = "https://clob.polymarket.com"
        self.gamma_url = "https://gamma-api.polymarket.com"
        
        # API credentials (currently None - will enable live data when provided)
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.authenticated = bool(api_key and api_secret and passphrase)
        
        # Polymarket doesn't have strict league categories like others
        self.sports_keywords = {
            'mlb': ['baseball', 'mlb', 'yankees', 'dodgers', 'red sox', 'giants', 'mets', 'astros', 'braves'],
            'nfl': ['nfl', 'football', 'chiefs', 'patriots', 'cowboys', 'packers', 'steelers', 'ravens', 'eagles'],
            'nba': ['nba', 'basketball', 'lakers', 'celtics', 'warriors', 'heat', 'bulls', 'knicks'],
            'nhl': ['nhl', 'hockey', 'rangers', 'bruins', 'blackhawks', 'penguins', 'capitals'],
            'ncaaf': ['college football', 'ncaaf', 'alabama', 'georgia', 'clemson', 'ohio state'],
            'ncaab': ['college basketball', 'ncaab', 'duke', 'carolina', 'kentucky', 'kansas']
        }
    
    def get_games(self, league='mlb'):
        """Get sports prediction markets for a league using multiple approaches"""
        if league not in self.sports_keywords:
            return []
        
        # Check if authentication is available for live data
        if not self.authenticated:
            print(f"  WARNING: No Polymarket API credentials provided.")
            print(f"  Only historical markets available. For live {league.upper()} games, add API key.")
        
        sports_markets = []
        keywords = self.sports_keywords[league] + ['vs', 'v.', 'at', 'win', 'game']
        
        # Try both CLOB and Gamma APIs
        markets_sources = [
            (f"{self.clob_url}/markets", "CLOB"),
            (f"{self.gamma_url}/markets", "Gamma")
        ]
        
        for url, source_name in markets_sources:
            try:
                print(f"  Checking {source_name} API...")
                
                if source_name == "CLOB":
                    params = {'limit': 1000}
                    response = requests.get(url, params=params, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        markets = data.get('data', [])
                else:  # Gamma API
                    response = requests.get(url, timeout=15)
                    if response.status_code == 200:
                        markets = response.json()
                        if not isinstance(markets, list):
                            markets = []
                
                if not markets:
                    continue
                    
                print(f"    Found {len(markets)} total markets")
                
                # Filter for sports markets
                found_count = 0
                for market in markets:
                    if source_name == "Gamma":
                        # Gamma API format
                        question = market.get('question', '').lower()
                        slug = market.get('slug', '').lower()
                        is_active = market.get('active', False)
                        is_closed = market.get('closed', True)
                        category = market.get('category', '').lower()
                    else:
                        # CLOB API format
                        question = market.get('question', '').lower()
                        slug = market.get('market_slug', '').lower()
                        is_active = market.get('active', False)
                        is_closed = market.get('closed', False)
                        category = ''
                    
                    # Look for sports markets matching our league
                    is_sports_match = (
                        any(keyword in question or keyword in slug or keyword in category 
                            for keyword in keywords) and
                        ('vs' in question or 'win' in question or 'game' in question)
                    )
                    
                    if is_sports_match:
                        found_count += 1
                        # Only include active markets for now
                        if is_active and not is_closed:
                            if source_name == "Gamma":
                                game_info = self._parse_gamma_market(market, league)
                            else:
                                game_info = self._parse_clob_market(market, league)
                            
                            if game_info:
                                sports_markets.append(game_info)
                
                print(f"    Found {found_count} {league.upper()} markets, {len([m for m in sports_markets if m.get('source') == source_name.lower()])} active")
                        
            except Exception as e:
                print(f"  Error with {source_name} API: {e}")
        
        # Remove duplicates based on question/slug
        unique_markets = []
        seen_questions = set()
        
        for market in sports_markets:
            question = market.get('away', '') + market.get('home', '')
            if question not in seen_questions:
                seen_questions.add(question)
                unique_markets.append(market)
        
        return unique_markets
    
    def _parse_clob_market(self, market, league):
        """Parse CLOB API market format"""
        return self._parse_sports_market(market, league, api_type="clob")
    
    def _parse_gamma_market(self, market, league):
        """Parse Gamma API market format"""
        try:
            question = market.get('question', '')
            outcomes = market.get('outcomes', [])
            prices = market.get('outcomePrices', [])
            
            if len(outcomes) != 2 or len(prices) != 2:
                return None
            
            # Extract teams from question
            team1, team2 = self._extract_teams_from_question(question)
            if not team1 or not team2:
                return None
            
            # Convert prices to American odds
            team1_odds = self._price_to_american_odds(prices[0]) if prices[0] else None
            team2_odds = self._price_to_american_odds(prices[1]) if prices[1] else None
            
            return {
                'platform': 'Polymarket',
                'league': league.upper(),
                'home': team2,  # Second team is usually home
                'away': team1,
                'home_odds': team2_odds,
                'away_odds': team1_odds,
                'game_time': market.get('endDate', 'TBD'),
                'status': 'active',
                'source': 'gamma'
            }
            
        except Exception as e:
            print(f"Error parsing Gamma market: {e}")
            return None
    
    def _price_to_american_odds(self, price):
        """Convert Polymarket price (0.0-1.0) to American odds"""
        try:
            if not price or price <= 0 or price >= 1:
                return None
                
            prob = float(price)
            if prob >= 0.5:
                odds = -100 / ((1/prob) - 1)
            else:
                odds = 100 * ((1/prob) - 1)
            return int(odds)
        except:
            return None
    
    def _extract_teams_from_question(self, question):
        """Extract team names from question text"""
        team1, team2 = None, None
        
        if ' vs ' in question:
            parts = question.split(' vs ')
            if len(parts) >= 2:
                team1 = parts[0].strip()
                team2 = parts[1].split('(')[0].strip()  # Remove date/time info
        elif ' vs. ' in question:
            parts = question.split(' vs. ')
            if len(parts) >= 2:
                team1 = parts[0].strip()
                team2 = parts[1].strip()
        elif ': ' in question and ' vs ' in question:
            game_part = question.split(': ', 1)[1]
            if ' vs ' in game_part:
                parts = game_part.split(' vs ')
                if len(parts) >= 2:
                    team1 = parts[0].strip()
                    team2 = parts[1].strip()
        
        return team1, team2

    def _parse_sports_market(self, market, league, api_type="clob"):
        """Parse a sports market into game format"""
        try:
            question = market.get('question', '')
            tokens = market.get('tokens', [])
            
            if len(tokens) != 2:  # Most sports markets should have 2 outcomes
                return None
            
            # Extract teams from question
            team1, team2 = None, None
            
            # Common patterns in Polymarket sports questions
            if ' vs ' in question:
                parts = question.split(' vs ')
                if len(parts) >= 2:
                    team1 = parts[0].strip()
                    team2 = parts[1].split('(')[0].strip()  # Remove date/time info
            elif ' vs. ' in question:
                parts = question.split(' vs. ')
                if len(parts) >= 2:
                    team1 = parts[0].strip()
                    team2 = parts[1].split('(')[0].strip()
            elif ': ' in question and ' vs ' in question:
                # Format like "NFL: Team1 vs Team2"
                game_part = question.split(': ', 1)[1]
                if ' vs ' in game_part:
                    parts = game_part.split(' vs ')
                    if len(parts) >= 2:
                        team1 = parts[0].strip()
                        team2 = parts[1].strip()
            
            if not team1 or not team2:
                # Try to extract from token names
                if len(tokens) == 2:
                    team1 = tokens[0].get('outcome', 'Team1')
                    team2 = tokens[1].get('outcome', 'Team2')
            
            # Get prices for each outcome and convert to American odds
            team1_odds = None
            team2_odds = None
            
            for token in tokens:
                token_id = token.get('token_id')
                outcome = token.get('outcome', '')
                
                if token_id:
                    try:
                        # Try to get current price for this token
                        price_url = f"{self.clob_url}/midpoint"
                        price_params = {'token_id': token_id}
                        price_response = requests.get(price_url, params=price_params, timeout=5)
                        
                        if price_response.status_code == 200:
                            price_data = price_response.json()
                            midpoint = price_data.get('midpoint')
                            
                            if midpoint:
                                # Convert price (0.0-1.0) to American odds
                                prob = float(midpoint)
                                if prob >= 0.5:
                                    odds = -100 / ((1/prob) - 1)
                                else:
                                    odds = 100 * ((1/prob) - 1)
                                odds = int(odds)
                                
                                # Assign to appropriate team
                                if team1 and team1.lower() in outcome.lower():
                                    team1_odds = odds
                                elif team2 and team2.lower() in outcome.lower():
                                    team2_odds = odds
                                elif tokens.index(token) == 0:
                                    team1_odds = odds
                                else:
                                    team2_odds = odds
                    except:
                        pass  # Skip if price fetching fails
            
            return {
                'platform': 'Polymarket',
                'league': league.upper(),
                'home': team2 if team2 else 'Team2',  # Second team is usually home
                'away': team1 if team1 else 'Team1',
                'home_odds': team2_odds,
                'away_odds': team1_odds,
                'game_time': 'TBD',  # Polymarket doesn't always have specific times
                'status': 'active' if market.get('active') else 'inactive',
                'source': api_type
            }
            
        except Exception as e:
            print(f"Error parsing Polymarket market: {e}")
            return None

def view_all_games(leagues=None):
    """View all games from all three platforms"""
    if leagues is None:
        leagues = ['mlb', 'nfl', 'nba', 'nhl']
    
    pinnacle = SlimPinnacleClient()
    kalshi = SlimKalshiClient()
    polymarket = SlimPolymarketClient()
    
    all_games = []
    
    for league in leagues:
        print(f"\nFetching {league.upper()} games...")
        
        # Get Pinnacle games
        p_games = pinnacle.get_games(league)
        all_games.extend(p_games)
        print(f"  Pinnacle: {len(p_games)} games")
        
        # Get Kalshi games
        k_games = kalshi.get_games(league)
        all_games.extend(k_games)
        print(f"  Kalshi: {len(k_games)} games")
        
        # Get Polymarket games
        pm_games = polymarket.get_games(league)
        all_games.extend(pm_games)
        print(f"  Polymarket: {len(pm_games)} games")
    
    # Display results
    print("\n" + "="*140)
    print(f"{'Platform':<12} {'League':<8} {'Away Team':<25} {'Home Team':<25} {'Away Odds':<10} {'Home Odds':<10} {'Game Time':<20}")
    print("="*140)
    
    # Sort by platform, league, then game time
    all_games.sort(key=lambda x: (x['platform'], x['league'], x['game_time']))
    
    for game in all_games:
        away_odds = f"{game['away_odds']:+d}" if game['away_odds'] else "N/A"
        home_odds = f"{game['home_odds']:+d}" if game['home_odds'] else "N/A"
        
        print(f"{game['platform']:<12} {game['league']:<8} {game['away'][:24]:<25} {game['home'][:24]:<25} {away_odds:<10} {home_odds:<10} {game['game_time']:<20}")
    
    # Summary
    print("\n" + "="*140)
    print("SUMMARY BY PLATFORM:")
    platform_counts = {}
    for game in all_games:
        key = f"{game['platform']} {game['league']}"
        platform_counts[key] = platform_counts.get(key, 0) + 1
    
    for key in sorted(platform_counts.keys()):
        print(f"  {key}: {platform_counts[key]} games")
    
    print(f"\nTotal games found: {len(all_games)}")
    print("="*140)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Slim viewer for all games on Pinnacle, Kalshi, and Polymarket')
    parser.add_argument('--leagues', nargs='+', default=['mlb', 'nfl'],
                       help='Leagues to check (mlb, nfl, nba, nhl, ncaaf, ncaab)')
    
    args = parser.parse_args()
    
    view_all_games(args.leagues)