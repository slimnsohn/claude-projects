"""
Refined Polymarket Client
Uses both web scraping and API approaches to find NFL games
Based on working URL patterns: https://polymarket.com/event/nfl-{team1}-{team2}-{date}
"""

import requests
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
import time

class RefinedPolymarketClient:
    """Refined Polymarket client that combines web and API approaches"""
    
    def __init__(self):
        self.web_base_url = "https://polymarket.com"
        self.api_base_url = "https://gamma-api.polymarket.com"
        self.clob_base_url = "https://clob.polymarket.com"
        
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Team abbreviation mappings
        self.team_mappings = {
            'KC': ['Chiefs', 'Kansas City'],
            'LAC': ['Chargers', 'LA Chargers', 'Los Angeles Chargers'],
            'PHI': ['Eagles', 'Philadelphia'],
            'DAL': ['Cowboys', 'Dallas'],
            'DEN': ['Broncos', 'Denver'],
            'TEN': ['Titans', 'Tennessee'],
            'ARI': ['Cardinals', 'Arizona'],
            'NO': ['Saints', 'New Orleans'],
            'WAS': ['Commanders', 'Washington'],
            'NYG': ['Giants', 'NY Giants', 'New York Giants'],
            'CIN': ['Bengals', 'Cincinnati'],
            'CLE': ['Browns', 'Cleveland'],
            'JAX': ['Jaguars', 'Jacksonville'],
            'CAR': ['Panthers', 'Carolina'],
            'BAL': ['Ravens', 'Baltimore'],
            'BUF': ['Bills', 'Buffalo'],
            'MIN': ['Vikings', 'Minnesota'],
            'CHI': ['Bears', 'Chicago'],
            'GB': ['Packers', 'Green Bay'],
            'DET': ['Lions', 'Detroit'],
            'SF': ['49ers', 'San Francisco'],
            'SEA': ['Seahawks', 'Seattle'],
            'LAR': ['Rams', 'LA Rams', 'Los Angeles Rams'],
            'TB': ['Buccaneers', 'Tampa Bay'],
            'ATL': ['Falcons', 'Atlanta'],
            'MIA': ['Dolphins', 'Miami'],
            'NE': ['Patriots', 'New England'],
            'NYJ': ['Jets', 'NY Jets', 'New York Jets'],
            'PIT': ['Steelers', 'Pittsburgh'],
            'HOU': ['Texans', 'Houston'],
            'IND': ['Colts', 'Indianapolis'],
            'LV': ['Raiders', 'Las Vegas']
        }

    def _get_kalshi_games_for_reference(self) -> List[Dict]:
        """Get current NFL games from Kalshi for reference"""
        try:
            # Import and use the existing Kalshi client
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            
            from kalshi.client import KalshiClient
            kalshi = KalshiClient()
            games = kalshi.get_games(league='nfl', remove_live_games=True)
            
            return games
        except Exception as e:
            print(f"Could not get Kalshi reference games: {e}")
            return []

    def _generate_game_urls(self, target_games: List[Dict] = None) -> List[Dict]:
        """Generate potential Polymarket URLs for target games"""
        if target_games is None:
            # Use reference games from Kalshi
            kalshi_games = self._get_kalshi_games_for_reference()
            target_games = []
            
            for game in kalshi_games:
                target_games.append({
                    'teams': [game['favorite'], game['dog']],
                    'date': game['game_date']
                })
        
        urls = []
        
        for game in target_games:
            teams = game['teams']
            date = game['date']
            
            # Convert team abbreviations to lowercase for URLs
            team1_lower = teams[0].lower()
            team2_lower = teams[1].lower()
            
            # Generate different URL patterns
            patterns = [
                f"nfl-{team1_lower}-{team2_lower}-{date}",
                f"nfl-{team2_lower}-{team1_lower}-{date}",
            ]
            
            for pattern in patterns:
                urls.append({
                    'slug': pattern,
                    'url': f"{self.web_base_url}/event/{pattern}",
                    'teams': teams,
                    'date': date
                })
        
        return urls

    def _test_market_url(self, url_info: Dict) -> Optional[Dict]:
        """Test if a market URL works and extract basic info"""
        try:
            response = self.session.get(url_info['url'], timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Check if it contains team references
                teams = url_info['teams']
                team_mentions = {}
                
                for team in teams:
                    count = content.upper().count(team.upper())
                    team_mentions[team] = count
                    
                    # Also check for full team names
                    if team in self.team_mappings:
                        for full_name in self.team_mappings[team]:
                            count += content.upper().count(full_name.upper())
                        team_mentions[team] = count
                
                # If we found significant team mentions, consider it valid
                if sum(team_mentions.values()) > 10:
                    return {
                        'url': url_info['url'],
                        'slug': url_info['slug'],
                        'teams': teams,
                        'date': url_info['date'],
                        'team_mentions': team_mentions,
                        'status_code': 200,
                        'content_length': len(content)
                    }
            
            return None
            
        except Exception as e:
            return None

    def _extract_market_data_from_page(self, url_info: Dict) -> Optional[Dict]:
        """Extract market data from a working Polymarket page"""
        try:
            response = self.session.get(url_info['url'], timeout=10)
            
            if response.status_code != 200:
                return None
            
            content = response.text
            
            # Look for JSON data in the page
            market_data = {}
            
            # Pattern 1: Look for market data in script tags
            script_patterns = [
                r'window\.__PRELOADED_STATE__\s*=\s*({.*?});',
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'"market"\s*:\s*({[^}]+})',
                r'"condition"\s*:\s*"([^"]+)"',
                r'"tokens"\s*:\s*(\[[^\]]+\])',
            ]
            
            for pattern in script_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                if matches:
                    for match in matches:
                        try:
                            if match.startswith('{') or match.startswith('['):
                                data = json.loads(match)
                                if isinstance(data, dict) and any(key in data for key in ['market', 'tokens', 'outcomes']):
                                    market_data['json_data'] = data
                                    break
                        except json.JSONDecodeError:
                            continue
            
            # Pattern 2: Look for specific market indicators
            price_pattern = r'[\$]?(\d*\.?\d+)[\s]*(?:¢|cents?)'
            prices = re.findall(price_pattern, content)
            if prices:
                market_data['prices'] = [float(p) for p in prices if p]
            
            # Pattern 3: Look for outcome names
            outcome_patterns = [
                r'(Yes|No)',
                rf"({url_info['teams'][0]}|{url_info['teams'][1]})",
            ]
            
            outcomes = []
            for pattern in outcome_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                outcomes.extend(matches)
            
            if outcomes:
                market_data['outcomes'] = list(set(outcomes))
            
            # Check if market appears active
            market_data['appears_active'] = any(
                word in content.lower() 
                for word in ['trade', 'buy', 'sell', 'active', 'betting', 'odds']
            )
            
            return {
                'url_info': url_info,
                'market_data': market_data
            }
            
        except Exception as e:
            return None

    def find_working_nfl_markets(self) -> List[Dict]:
        """Find working NFL markets on Polymarket"""
        print("Finding working NFL markets on Polymarket...")
        
        # Generate URLs to test
        url_candidates = self._generate_game_urls()
        print(f"Testing {len(url_candidates)} potential market URLs...")
        
        working_markets = []
        
        for i, url_info in enumerate(url_candidates, 1):
            if i % 5 == 0:
                print(f"Tested {i}/{len(url_candidates)} URLs...")
            
            # Test if URL works
            basic_info = self._test_market_url(url_info)
            
            if basic_info:
                print(f"FOUND: {basic_info['teams'][0]} vs {basic_info['teams'][1]} - {basic_info['url']}")
                
                # Extract detailed market data
                detailed_info = self._extract_market_data_from_page(url_info)
                
                if detailed_info:
                    working_markets.append(detailed_info)
            
            # Rate limiting
            time.sleep(0.5)
        
        print(f"Found {len(working_markets)} working markets")
        return working_markets

    def convert_to_standard_format(self, working_markets: List[Dict]) -> List[Dict]:
        """Convert working markets to standard format matching Pinnacle/Kalshi"""
        games = []
        
        for market_info in working_markets:
            url_info = market_info['url_info']
            market_data = market_info['market_data']
            
            # Extract basic info
            teams = url_info['teams']
            date = url_info['date']
            
            # Try to determine favorite/underdog and odds
            # For now, just use placeholder odds since we need to parse the page content more
            game = {
                'favorite': teams[0],  # Placeholder - would need better parsing
                'dog': teams[1],       # Placeholder - would need better parsing
                'fav_odds': -150,      # Placeholder - would extract from market_data
                'dog_odds': 130,       # Placeholder - would extract from market_data
                'game_date': date,
                'game_time': f"{date} TBD",
                'league': 'nfl',
                'status': 'active' if market_data.get('appears_active', False) else 'unknown',
                'market_url': url_info['url'],
                'platform': 'polymarket'
            }
            
            games.append(game)
        
        return games

    def get_games(self, league: str = 'nfl', remove_live_games: bool = True) -> List[Dict]:
        """
        Get games in standard format matching Pinnacle/Kalshi
        """
        if league.lower() != 'nfl':
            print(f"League {league} not supported yet")
            return []
        
        # Find working markets
        working_markets = self.find_working_nfl_markets()
        
        # Convert to standard format
        games = self.convert_to_standard_format(working_markets)
        
        return games

    def print_games_table(self, games: List[Dict]):
        """Print games in formatted table"""
        if not games:
            print("No games found")
            return
        
        print(f"\nPOLYMARKET NFL GAMES ({len(games)} total)")
        print("=" * 80)
        
        for game in games:
            print(f"{game['favorite']} vs {game['dog']} | {game['game_date']} | {game['status']}")
            print(f"  URL: {game.get('market_url', 'N/A')}")

def test_refined_client():
    """Test the refined client"""
    print("TESTING REFINED POLYMARKET CLIENT")
    print("=" * 60)
    
    client = RefinedPolymarketClient()
    games = client.get_games(league='nfl', remove_live_games=True)
    
    if games:
        client.print_games_table(games)
        print(f"\nSUCCESS: Found {len(games)} Polymarket NFL games!")
    else:
        print("No games found")
    
    return games

if __name__ == "__main__":
    test_refined_client()