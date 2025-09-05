"""
Slim Game Viewer - Fixed version that properly handles Kalshi market structure
Shows all available games from both platforms with their odds
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

def view_all_games(leagues=None):
    """View all games from both platforms"""
    if leagues is None:
        leagues = ['mlb', 'nfl', 'nba', 'nhl']
    
    pinnacle = SlimPinnacleClient()
    kalshi = SlimKalshiClient()
    
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
    
    # Display results
    print("\n" + "="*120)
    print(f"{'Platform':<10} {'League':<8} {'Away Team':<25} {'Home Team':<25} {'Away Odds':<10} {'Home Odds':<10} {'Game Time':<20}")
    print("="*120)
    
    # Sort by platform, league, then game time
    all_games.sort(key=lambda x: (x['platform'], x['league'], x['game_time']))
    
    for game in all_games:
        away_odds = f"{game['away_odds']:+d}" if game['away_odds'] else "N/A"
        home_odds = f"{game['home_odds']:+d}" if game['home_odds'] else "N/A"
        
        print(f"{game['platform']:<10} {game['league']:<8} {game['away'][:24]:<25} {game['home'][:24]:<25} {away_odds:<10} {home_odds:<10} {game['game_time']:<20}")
    
    # Summary
    print("\n" + "="*120)
    print("SUMMARY BY PLATFORM:")
    platform_counts = {}
    for game in all_games:
        key = f"{game['platform']} {game['league']}"
        platform_counts[key] = platform_counts.get(key, 0) + 1
    
    for key in sorted(platform_counts.keys() ):
        print(f"  {key}: {platform_counts[key]} games")
    
    print(f"\nTotal games found: {len(all_games)}")
    print("="*120)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Slim viewer for all games on Pinnacle and Kalshi')
    parser.add_argument('--leagues', nargs='+', default=['mlb', 'nfl', 'nba', 'nhl'],
                       help='Leagues to check (mlb, nfl, nba, nhl, ncaaf, ncaab, wnba, soccer)')
    
    args = parser.parse_args()
    
    view_all_games(args.leagues)