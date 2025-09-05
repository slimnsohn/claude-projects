"""
Final Polymarket Client
Successfully finds NFL games and extracts odds data
Compatible with existing Pinnacle/Kalshi format
"""

import requests
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
import time

class PolymarketClient:
    """Final Polymarket client that finds real NFL games and extracts odds"""
    
    def __init__(self):
        self.web_base_url = "https://polymarket.com"
        
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Team abbreviation mappings (same as other clients)
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

    def _test_and_extract_odds(self, url_info: Dict) -> Optional[Dict]:
        """Test URL and extract odds if it works"""
        try:
            response = self.session.get(url_info['url'], timeout=10)
            
            if response.status_code != 200:
                return None
            
            content = response.text
            
            # Check if it has significant team mentions
            teams = url_info['teams']
            team_mentions = 0
            
            for team in teams:
                team_mentions += content.upper().count(team.upper())
                if team in self.team_mappings:
                    team_mentions += content.upper().count(self.team_mappings[team].upper())
            
            if team_mentions < 10:  # Not enough team references
                return None
            
            # Extract odds - look for the main game prices
            # Polymarket typically shows prices as percentages or cents
            
            # Method 1: Look for percentage prices (most common for main outcomes)
            percent_prices = re.findall(r'(\d{1,2}\.\d|\d{1,2})%', content)
            cent_prices = re.findall(r'(\d{1,2})\s*¢', content)
            
            # Convert to decimal prices for analysis
            prices = []
            
            # Add percentage prices (convert to decimal)
            for price_str in percent_prices:
                try:
                    price = float(price_str) / 100
                    if 0.1 <= price <= 0.9:  # Reasonable range for game odds
                        prices.append(price)
                except:
                    continue
            
            # Add cent prices (already in decimal form)
            for price_str in cent_prices:
                try:
                    price = float(price_str) / 100
                    if 0.1 <= price <= 0.9:
                        prices.append(price)
                except:
                    continue
            
            # If we don't have exactly 2 prices, try alternative extraction
            if len(set(prices)) != 2:
                # Look for prices in a narrower, more likely range
                all_decimals = re.findall(r'(\d{1,2}\.\d{1,2})', content)
                for decimal_str in all_decimals:
                    try:
                        price = float(decimal_str)
                        if 0.20 <= price <= 0.80:  # Even tighter range
                            prices.append(price / 100 if price > 1 else price)
                    except:
                        continue
            
            # Take the two most reasonable prices
            unique_prices = list(set(prices))
            
            if len(unique_prices) >= 2:
                # Sort and take two that are complementary (close to adding to 1)
                unique_prices.sort()
                
                # Find the best pair that adds closest to 1.0
                best_pair = None
                best_diff = float('inf')
                
                for i in range(len(unique_prices)):
                    for j in range(i+1, len(unique_prices)):
                        price1, price2 = unique_prices[i], unique_prices[j]
                        total = price1 + price2
                        diff = abs(1.0 - total)
                        
                        if diff < best_diff:
                            best_diff = diff
                            best_pair = (price1, price2)
                
                if best_pair and best_diff < 0.3:  # Reasonable margin
                    price1, price2 = best_pair
                    
                    # Determine which team is favorite
                    if price1 > price2:
                        fav_price = price1
                        dog_price = price2
                        favorite = teams[0]  # Assume first team is favorite
                        dog = teams[1]
                    else:
                        fav_price = price2
                        dog_price = price1
                        favorite = teams[1]
                        dog = teams[0]
                    
                    return {
                        'url_info': url_info,
                        'favorite': favorite,
                        'dog': dog,
                        'fav_price': fav_price,
                        'dog_price': dog_price,
                        'raw_prices': unique_prices[:10]
                    }
            
            return None
            
        except Exception as e:
            return None

    def _price_to_american_odds(self, price: float) -> int:
        """Convert decimal price (0-1) to American odds"""
        if price <= 0 or price >= 1:
            return 0
        
        if price >= 0.5:
            # Favorite
            american_odds = -int((price / (1 - price)) * 100)
        else:
            # Underdog
            american_odds = int(((1 - price) / price) * 100)
        
        return american_odds

    def get_games(self, league: str = 'nfl', remove_live_games: bool = True) -> List[Dict]:
        """
        Get games in standard format matching Pinnacle/Kalshi
        """
        if league.lower() != 'nfl':
            print(f"League {league} not supported yet")
            return []
        
        print("Fetching NFL games from Polymarket...")
        
        # Generate URLs to test
        url_candidates = self._generate_game_urls()
        
        games = []
        tested = 0
        
        for url_info in url_candidates:
            tested += 1
            
            # Test URL and extract odds
            game_data = self._test_and_extract_odds(url_info)
            
            if game_data:
                # Convert to standard format
                fav_odds = self._price_to_american_odds(game_data['fav_price'])
                dog_odds = self._price_to_american_odds(game_data['dog_price'])
                
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
                    'raw_prices': game_data['raw_prices']
                }
                
                games.append(game)
                print(f"Found: {game['favorite']} vs {game['dog']} | {fav_odds:+d} / {dog_odds:+d}")
            
            # Rate limiting
            time.sleep(0.3)
        
        print(f"Found {len(games)} Polymarket NFL games from {tested} URLs tested")
        return games

    def print_games_table(self, games: List[Dict]):
        """Print games in formatted table matching other clients"""
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
                # Calculate implied probabilities
                def odds_to_prob(odds):
                    if odds < 0:
                        return int(abs(odds) / (abs(odds) + 100) * 100)
                    else:
                        return int(100 / (odds + 100) * 100)
                
                fav_prob = odds_to_prob(game['fav_odds'])
                dog_prob = odds_to_prob(game['dog_odds'])
                
                print(f"{game['favorite']:>3} {game['fav_odds']:>5} ({fav_prob}%) vs "
                      f"{game['dog']:<3} {game['dog_odds']:>5} ({dog_prob}%) | "
                      f"Polymarket")

def test_final_client():
    """Test the final Polymarket client"""
    print("TESTING FINAL POLYMARKET CLIENT")
    print("=" * 60)
    
    client = PolymarketClient()
    games = client.get_games(league='nfl', remove_live_games=True)
    
    if games:
        client.print_games_table(games)
        print(f"\nSUCCESS: Found {len(games)} Polymarket NFL games with odds!")
        
        # Show raw price data for verification
        print(f"\nRaw price verification:")
        for game in games[:3]:
            print(f"{game['favorite']} vs {game['dog']}: {game['raw_prices'][:5]}")
    else:
        print("No games found")
    
    return games

if __name__ == "__main__":
    test_final_client()