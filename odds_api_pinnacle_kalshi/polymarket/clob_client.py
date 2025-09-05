"""
Polymarket CLOB Client for Sports Markets
Uses the official py-clob-client to fetch NFL and other sports markets
"""

from py_clob_client.client import ClobClient
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import re

class PolymarketCLOBClient:
    """Polymarket CLOB client for sports betting markets"""
    
    def __init__(self):
        # Initialize CLOB client (no auth needed for public data)
        self.client = ClobClient(
            host="https://clob.polymarket.com",
            chain_id=137  # Polygon mainnet
        )
        
        # NFL team mappings
        self.nfl_teams = {
            'Bills': 'BUF', 'Buffalo': 'BUF',
            'Dolphins': 'MIA', 'Miami': 'MIA',
            'Patriots': 'NE', 'New England': 'NE',
            'Jets': 'NYJ', 'NY Jets': 'NYJ',
            'Ravens': 'BAL', 'Baltimore': 'BAL',
            'Bengals': 'CIN', 'Cincinnati': 'CIN',
            'Browns': 'CLE', 'Cleveland': 'CLE',
            'Steelers': 'PIT', 'Pittsburgh': 'PIT',
            'Texans': 'HOU', 'Houston': 'HOU',
            'Colts': 'IND', 'Indianapolis': 'IND',
            'Jaguars': 'JAX', 'Jacksonville': 'JAX',
            'Titans': 'TEN', 'Tennessee': 'TEN',
            'Broncos': 'DEN', 'Denver': 'DEN',
            'Chiefs': 'KC', 'Kansas City': 'KC',
            'Raiders': 'LV', 'Las Vegas': 'LV',
            'Chargers': 'LAC', 'LA Chargers': 'LAC',
            'Cowboys': 'DAL', 'Dallas': 'DAL',
            'Giants': 'NYG', 'NY Giants': 'NYG',
            'Eagles': 'PHI', 'Philadelphia': 'PHI',
            'Commanders': 'WAS', 'Washington': 'WAS',
            'Bears': 'CHI', 'Chicago': 'CHI',
            'Lions': 'DET', 'Detroit': 'DET',
            'Packers': 'GB', 'Green Bay': 'GB',
            'Vikings': 'MIN', 'Minnesota': 'MIN',
            'Falcons': 'ATL', 'Atlanta': 'ATL',
            'Panthers': 'CAR', 'Carolina': 'CAR',
            'Saints': 'NO', 'New Orleans': 'NO',
            'Buccaneers': 'TB', 'Tampa Bay': 'TB',
            'Cardinals': 'ARI', 'Arizona': 'ARI',
            '49ers': 'SF', 'San Francisco': 'SF',
            'Seahawks': 'SEA', 'Seattle': 'SEA',
            'Rams': 'LAR', 'LA Rams': 'LAR'
        }

    def _normalize_team_name(self, team_name: str) -> str:
        """Normalize team names to abbreviations"""
        for full_name, abbrev in self.nfl_teams.items():
            if full_name.lower() in team_name.lower():
                return abbrev
        return team_name

    def _extract_teams_from_question(self, question: str) -> tuple:
        """Extract team names from market question"""
        found_teams = []
        
        for team_name, abbrev in self.nfl_teams.items():
            if team_name.lower() in question.lower():
                if abbrev not in found_teams:
                    found_teams.append(abbrev)
        
        if len(found_teams) >= 2:
            return (found_teams[0], found_teams[1])
        elif len(found_teams) == 1:
            return (found_teams[0], None)
        return (None, None)

    def _is_nfl_game_market(self, question: str) -> bool:
        """Check if market is an NFL game winner market"""
        q_lower = question.lower()
        
        # Exclude non-game markets
        exclude_keywords = [
            'super bowl', 'championship', 'season', 'mvp', 'award',
            'draft', 'rookie', 'playoff', 'division', 'record',
            'touchdown', 'yard', 'pass', 'rush', 'reception',
            'total', 'over', 'under', 'spread', 'margin', 'points'
        ]
        
        if any(keyword in q_lower for keyword in exclude_keywords):
            return False
        
        # Check for NFL teams
        teams = self._extract_teams_from_question(question)
        has_teams = teams[0] is not None
        
        # Check for game winner keywords
        winner_keywords = ['win', 'beat', 'defeat', 'winner']
        has_winner_keyword = any(keyword in q_lower for keyword in winner_keywords)
        
        return has_teams and has_winner_keyword

    def _price_to_american_odds(self, price: float) -> int:
        """Convert decimal price to American odds"""
        if price <= 0 or price >= 1:
            return 0
        
        if price >= 0.5:
            # Favorite
            american_odds = -int((price / (1 - price)) * 100)
        else:
            # Underdog
            american_odds = int(((1 - price) / price) * 100)
        
        return american_odds

    def get_nfl_markets(self) -> List[Dict]:
        """Get all NFL game markets"""
        print("Fetching NFL markets from Polymarket CLOB...")
        
        try:
            # Get all markets - returns a dict with 'data' key
            response = self.client.get_markets()
            
            # Extract the actual markets list
            if isinstance(response, dict) and 'data' in response:
                markets = response['data']
            elif isinstance(response, list):
                markets = response
            else:
                print(f"Unexpected response type: {type(response)}")
                return []
            
            # Filter for NFL games
            nfl_markets = []
            for market in markets:
                if isinstance(market, dict) and self._is_nfl_game_market(market.get('question', '')):
                    nfl_markets.append(market)
            
            print(f"Found {len(nfl_markets)} NFL game markets")
            return nfl_markets
            
        except Exception as e:
            print(f"Error fetching markets: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_games(self, league: str = 'nfl', remove_live_games: bool = True) -> List[Dict]:
        """
        Get games in standard format matching Pinnacle/Kalshi
        """
        if league.lower() != 'nfl':
            print(f"League {league} not yet supported in Polymarket client")
            return []
        
        markets = self.get_nfl_markets()
        games = []
        
        for market in markets:
            # Skip closed markets if removing live games
            if remove_live_games and market.get('closed', False):
                continue
            
            # Extract teams
            teams = self._extract_teams_from_question(market.get('question', ''))
            if not teams[0] or not teams[1]:
                continue
            
            # Get token info for prices
            tokens = market.get('tokens', [])
            if len(tokens) < 2:
                continue
            
            # Determine favorite and underdog
            token1 = tokens[0]
            token2 = tokens[1]
            
            # Get current prices from order book
            try:
                # Get order book for each token
                book1 = self.client.get_book(token1['token_id'])
                book2 = self.client.get_book(token2['token_id'])
                
                # Use mid price if available
                price1 = self._get_mid_price(book1)
                price2 = self._get_mid_price(book2)
                
                if price1 is None or price2 is None:
                    continue
                
            except:
                # Fall back to last trade price if available
                price1 = float(token1.get('price', 0))
                price2 = float(token2.get('price', 0))
                
                if price1 == 0 or price2 == 0:
                    continue
            
            # Determine favorite (higher price = favorite)
            if price1 > price2:
                favorite = teams[0]
                dog = teams[1]
                fav_price = price1
                dog_price = price2
            else:
                favorite = teams[1]
                dog = teams[0]
                fav_price = price2
                dog_price = price1
            
            # Convert to American odds
            fav_odds = self._price_to_american_odds(fav_price)
            dog_odds = self._price_to_american_odds(dog_price)
            
            # Parse date
            end_date_str = market.get('end_date_iso', '')
            if end_date_str:
                try:
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                    game_date = end_date.strftime('%Y-%m-%d')
                    game_time = end_date.strftime('%Y-%m-%d %H:%M')
                except:
                    game_date = 'TBD'
                    game_time = 'TBD'
            else:
                game_date = 'TBD'
                game_time = 'TBD'
            
            game = {
                'favorite': favorite,
                'dog': dog,
                'fav_odds': fav_odds,
                'dog_odds': dog_odds,
                'game_date': game_date,
                'game_time': game_time,
                'league': 'nfl',
                'status': 'active' if not market.get('closed', False) else 'closed',
                'volume': float(market.get('volume', 0)),
                'market_id': market.get('condition_id', ''),
                'question': market.get('question', '')
            }
            
            games.append(game)
        
        # Sort by date
        games.sort(key=lambda x: x['game_date'])
        
        return games

    def _get_mid_price(self, order_book: Dict) -> Optional[float]:
        """Calculate mid price from order book"""
        try:
            bids = order_book.get('bids', [])
            asks = order_book.get('asks', [])
            
            if not bids or not asks:
                return None
            
            best_bid = float(bids[0]['price'])
            best_ask = float(asks[0]['price'])
            
            return (best_bid + best_ask) / 2
            
        except:
            return None

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
            print(f"\n{date}")
            print("-" * 80)
            
            for game in games_by_date[date]:
                # Calculate implied probabilities
                def odds_to_prob(odds):
                    if odds < 0:
                        return int(abs(odds) / (abs(odds) + 100) * 100)
                    else:
                        return int(100 / (odds + 100) * 100)
                
                fav_prob = odds_to_prob(game['fav_odds'])
                dog_prob = odds_to_prob(game['dog_odds'])
                
                volume_str = f"${game['volume']:,.0f}" if game.get('volume') else "N/A"
                
                print(f"{game['favorite']:>3} {game['fav_odds']:>5} ({fav_prob}%) vs "
                      f"{game['dog']:<3} {game['dog_odds']:>5} ({dog_prob}%) | "
                      f"Vol: {volume_str:>10} | {game['status']}")

def test_clob_client():
    """Test the CLOB client"""
    print("\n" + "="*60)
    print("TESTING POLYMARKET CLOB CLIENT")
    print("="*60)
    
    client = PolymarketCLOBClient()
    
    # Get NFL games
    games = client.get_games(league='nfl', remove_live_games=True)
    
    if games:
        client.print_games_table(games)
    else:
        print("\nNo NFL games found. Trying to fetch raw markets...")
        
        # Try getting raw markets for debugging
        try:
            markets = client.client.get_markets()
            print(f"\nTotal markets available: {len(markets)}")
            
            # Show first few markets
            print("\nFirst 5 markets:")
            market_list = markets['data'] if isinstance(markets, dict) else markets
            for i, market in enumerate(market_list[:5] if isinstance(market_list, list) else [], 1):
                if isinstance(market, dict):
                    print(f"{i}. {market.get('question', 'N/A')[:80]}...")
                    print(f"   Active: {not market.get('closed', False)}")
                
            # Search for anything NFL related
            nfl_related = []
            if isinstance(market_list, list):
                for m in market_list:
                    if isinstance(m, dict) and 'nfl' in m.get('question', '').lower():
                        nfl_related.append(m)
            print(f"\nMarkets with 'NFL' in question: {len(nfl_related)}")
            
            if nfl_related:
                print("\nNFL-related markets:")
                for market in nfl_related[:3]:
                    print(f"- {market.get('question', 'N/A')}")
                    
        except Exception as e:
            print(f"Error getting raw markets: {e}")
    
    return games

if __name__ == "__main__":
    test_clob_client()