"""
Corrected Polymarket Client
Uses the fixed odds extraction method to get accurate percentages
Compatible with existing Pinnacle/Kalshi format
"""

import requests
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
import time

class PolymarketClient:
    """Corrected Polymarket client that extracts accurate odds"""
    
    def __init__(self):
        self.web_base_url = "https://polymarket.com"
        
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Team abbreviation mappings
        self.team_mappings = {
            'KC': 'Chiefs', 'LAC': 'Chargers', 'PHI': 'Eagles', 'DAL': 'Cowboys',
            'DEN': 'Broncos', 'TEN': 'Titans', 'ARI': 'Cardinals', 'NO': 'Saints',
            'WAS': 'Commanders', 'NYG': 'Giants', 'CIN': 'Bengals', 'CLE': 'Browns',
            'JAX': 'Jaguars', 'CAR': 'Panthers', 'BAL': 'Ravens', 'BUF': 'Bills',
            'MIN': 'Vikings', 'CHI': 'Bears', 'GB': 'Packers', 'DET': 'Lions',
            'SF': '49ers', 'SEA': 'Seahawks', 'LAR': 'Rams', 'TB': 'Buccaneers',
            'ATL': 'Falcons', 'MIA': 'Dolphins', 'NE': 'Patriots', 'NYJ': 'Jets',
            'PIT': 'Steelers', 'HOU': 'Texans', 'IND': 'Colts', 'LV': 'Raiders'
        }

    def _get_kalshi_games_for_reference(self) -> List[Dict]:
        """Get current NFL games from Kalshi for reference"""
        try:
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

    def _generate_game_urls(self) -> List[Dict]:
        """Generate Polymarket URLs for current NFL games"""
        kalshi_games = self._get_kalshi_games_for_reference()
        
        urls = []
        
        for game in kalshi_games:
            teams = [game['favorite'], game['dog']]
            date = game['game_date']
            
            # Generate URL patterns (both team orders)
            patterns = [
                f"nfl-{teams[0].lower()}-{teams[1].lower()}-{date}",
                f"nfl-{teams[1].lower()}-{teams[0].lower()}-{date}",
            ]
            
            for pattern in patterns:
                urls.append({
                    'slug': pattern,
                    'url': f"{self.web_base_url}/event/{pattern}",
                    'teams': teams,
                    'date': date
                })
        
        return urls

    def _extract_real_odds(self, url_info: Dict) -> Optional[Dict]:
        """Extract the actual displayed odds from Polymarket page using fixed method"""
        try:
            response = self.session.get(url_info['url'], timeout=10)
            
            if response.status_code != 200:
                return None
            
            content = response.text
            teams = url_info['teams']
            
            # Check for team mentions (basic validation)
            team_mentions = 0
            for team in teams:
                team_mentions += content.upper().count(team.upper())
                if team in self.team_mappings:
                    team_mentions += content.upper().count(self.team_mappings[team].upper())
            
            if team_mentions < 5:  # Not enough team references
                return None
            
            # Extract percentages using the corrected method
            # Multiple patterns to catch the odds in HTML
            patterns = [
                r'>(\d{1,2}(?:\.\d)?)\%<',  # >XX%<
                r'class="[^"]*">\s*(\d{1,2}(?:\.\d)?)\%\s*</[^>]*>',  # in CSS classes
                r'css">\s*(\d{1,2}(?:\.\d)?)\%\s*</p>',  # specific pattern we found
                r'(\d{1,2}(?:\.\d)?)\%\s*</(?:p|span|div)',  # broader closing tags
            ]
            
            all_percentages = []
            for pattern in patterns:
                matches = re.findall(pattern, content)
                all_percentages.extend(matches)
            
            # Convert to floats and filter for reasonable game odds
            valid_percentages = []
            for p in all_percentages:
                try:
                    val = float(p)
                    if 15 <= val <= 85:  # Expanded range to catch more games
                        valid_percentages.append(val)
                except:
                    continue
            
            # Remove duplicates and sort
            unique_percentages = sorted(list(set(valid_percentages)))
            
            if len(unique_percentages) >= 2:
                # Find the best pair that adds up closest to 100%
                best_pair = None
                best_score = 0
                
                for i in range(len(unique_percentages)):
                    for j in range(i+1, len(unique_percentages)):
                        p1, p2 = unique_percentages[i], unique_percentages[j]
                        total = p1 + p2
                        
                        # Score pairs that add up close to 100%
                        if 85 <= total <= 115:  # Allow margin for fees/vig
                            score = 100 - abs(100 - total)
                            
                            if score > best_score:
                                best_score = score
                                best_pair = (p1, p2)
                
                if best_pair:
                    p1, p2 = best_pair
                    
                    # Determine which team is favorite (higher percentage)
                    if p1 > p2:
                        fav_percent = p1
                        dog_percent = p2
                        favorite = teams[0]  # Could be refined with team name matching
                        dog = teams[1]
                    else:
                        fav_percent = p2
                        dog_percent = p1
                        favorite = teams[1]
                        dog = teams[0]
                    
                    return {
                        'url_info': url_info,
                        'favorite': favorite,
                        'dog': dog,
                        'fav_percent': fav_percent,
                        'dog_percent': dog_percent,
                        'total_percent': fav_percent + dog_percent,
                        'raw_percentages': unique_percentages
                    }
            
            return None
            
        except Exception as e:
            return None

    def _percent_to_american_odds(self, percent: float) -> int:
        """Convert percentage to American odds"""
        if percent <= 0 or percent >= 100:
            return 0
        
        decimal = percent / 100
        
        if decimal >= 0.5:
            # Favorite
            american_odds = int(-decimal / (1 - decimal) * 100)
        else:
            # Underdog
            american_odds = int((1 - decimal) / decimal * 100)
        
        return american_odds

    def get_games(self, league: str = 'nfl', remove_live_games: bool = True) -> List[Dict]:
        """
        Get games with corrected odds extraction
        """
        if league.lower() != 'nfl':
            print(f"League {league} not supported yet")
            return []
        
        print("Fetching NFL games from Polymarket with corrected odds...")
        
        # Generate URLs to test
        url_candidates = self._generate_game_urls()
        
        games = []
        tested = 0
        
        for url_info in url_candidates:
            tested += 1
            
            # Extract odds using corrected method
            game_data = self._extract_real_odds(url_info)
            
            if game_data:
                # Convert percentages to American odds
                fav_odds = self._percent_to_american_odds(game_data['fav_percent'])
                dog_odds = self._percent_to_american_odds(game_data['dog_percent'])
                
                game = {
                    'favorite': game_data['favorite'],
                    'dog': game_data['dog'],
                    'fav_odds': fav_odds,
                    'dog_odds': dog_odds,
                    'game_date': url_info['date'],
                    'game_time': f"{url_info['date']} TBD",
                    'league': 'nfl',
                    'status': 'active',
                    'market_url': url_info['url'],
                    'platform': 'polymarket',
                    # Store original percentages for verification
                    'fav_percent': game_data['fav_percent'],
                    'dog_percent': game_data['dog_percent'],
                    'total_percent': game_data['total_percent']
                }
                
                games.append(game)
                print(f"Found: {game['favorite']} {game['fav_percent']:.1f}% ({fav_odds:+d}) vs {game['dog']} {game['dog_percent']:.1f}% ({dog_odds:+d})")
            
            # Rate limiting
            time.sleep(0.3)
        
        print(f"Found {len(games)} Polymarket NFL games with corrected odds from {tested} URLs tested")
        return games

    def print_games_table(self, games: List[Dict]):
        """Print games in formatted table"""
        if not games:
            print("No games found")
            return
        
        print(f"\nPOLYMARKET NFL GAMES ({len(games)} total)")
        print("=" * 80)
        
        # Group by date
        games_by_date = {}
        for game in games:
            date = game['game_date']
            if date not in games_by_date:
                games_by_date[date] = []
            games_by_date[date].append(game)
        
        for date in sorted(games_by_date.keys()):
            print(f"\n>> {date}")
            print("-" * 60)
            
            for game in games_by_date[date]:
                fav_pct = game.get('fav_percent', 0)
                dog_pct = game.get('dog_percent', 0)
                
                print(f"{game['favorite']:>3} {game['fav_odds']:>5} ({fav_pct:.0f}%) vs "
                      f"{game['dog']:<3} {game['dog_odds']:>5} ({dog_pct:.0f}%) | "
                      f"Polymarket")

def test_corrected_client():
    """Test the corrected Polymarket client"""
    print("TESTING CORRECTED POLYMARKET CLIENT")
    print("=" * 60)
    
    client = PolymarketClient()
    games = client.get_games(league='nfl', remove_live_games=True)
    
    if games:
        client.print_games_table(games)
        print(f"\nSUCCESS: Found {len(games)} Polymarket NFL games with corrected odds!")
        
        # Show verification data
        print(f"\nVerification (showing percentage totals):")
        for game in games[:5]:  # Show first 5
            total = game.get('total_percent', 0)
            print(f"{game['favorite']} vs {game['dog']}: {game.get('fav_percent', 0):.1f}% + {game.get('dog_percent', 0):.1f}% = {total:.1f}%")
    else:
        print("No games found")
    
    return games

if __name__ == "__main__":
    test_corrected_client()