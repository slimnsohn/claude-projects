"""
Slim Game Viewer - Simplified version to check all games on Pinnacle and Kalshi
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
        key_file = 'keys/odds_api_key.txt'
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
    """Minimal Kalshi client for fetching market data"""
    
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
        
        # Parse markets into games
        games = []
        processed_games = set()
        
        for market in all_markets:
            # Extract team info from title
            title = market.get('title', '')
            if ' vs ' in title or ' v ' in title:
                # Parse teams
                if ' vs ' in title:
                    parts = title.split(' vs ')
                elif ' v ' in title:
                    parts = title.split(' v ')
                else:
                    continue
                
                if len(parts) != 2:
                    continue
                
                team1 = parts[0].strip()
                team2 = parts[1].strip()
                
                # Remove "Will " prefix if present
                if team1.startswith('Will '):
                    team1 = team1[5:]
                
                # Remove " win?" suffix if present
                if team2.endswith(' win?'):
                    team2 = team2[:-5]
                
                # Create game key to avoid duplicates
                game_key = f"{min(team1, team2)}_{max(team1, team2)}"
                if game_key in processed_games:
                    continue
                processed_games.add(game_key)
                
                # Extract odds (yes price = win probability)
                yes_price = market.get('yes_ask', market.get('last_price'))
                if yes_price:
                    # Convert probability to American odds
                    prob = yes_price / 100
                    if prob >= 0.5:
                        odds = -100 / ((1/prob) - 1)
                    else:
                        odds = 100 * ((1/prob) - 1)
                    odds = int(odds)
                else:
                    odds = None
                
                # Get close time
                close_time = market.get('close_time', '')
                if close_time:
                    try:
                        dt = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
                        game_time = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        game_time = 'Unknown'
                else:
                    game_time = 'Unknown'
                
                games.append({
                    'platform': 'Kalshi',
                    'league': league.upper(),
                    'home': team1,
                    'away': team2,
                    'home_odds': odds,
                    'away_odds': None,  # Kalshi markets are one-sided
                    'game_time': game_time,
                    'status': market.get('status', 'unknown')
                })
        
        return games

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
    
    for key in sorted(platform_counts.keys()):
        print(f"  {key}: {platform_counts[key]} games")
    
    print(f"\nTotal games found: {len(all_games)}")
    print("="*120)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Slim viewer for all games on Pinnacle and Kalshi')
    parser.add_argument('--leagues', nargs='+', default=['mlb', 'nfl', 'nba', 'nhl'],
                       help='Leagues to check (mlb, nfl, nba, nhl, ncaaf, ncaab, wnba, soccer)')
    
    args = parser.parse_args()
    
    view_all_games(args.leagues)