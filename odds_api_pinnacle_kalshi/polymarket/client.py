"""
Polymarket Sports Client
Fetches game winner markets from Polymarket API
Compatible with existing Pinnacle/Kalshi client format
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

class PolymarketClient:
    """Polymarket client for sports betting markets"""
    
    def __init__(self):
        self.base_url = "https://gamma-api.polymarket.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'Sports-Market-Fetcher/1.0'
        })
        
        # Sports team mappings for multiple leagues
        self.team_mappings = {
            'nfl': {
                # Full names to abbreviations
                'Bills': 'BUF', 'Buffalo Bills': 'BUF', 'Buffalo': 'BUF',
                'Dolphins': 'MIA', 'Miami Dolphins': 'MIA', 'Miami': 'MIA',
                'Patriots': 'NE', 'New England Patriots': 'NE', 'New England': 'NE',
                'Jets': 'NYJ', 'New York Jets': 'NYJ', 'NY Jets': 'NYJ',
                'Ravens': 'BAL', 'Baltimore Ravens': 'BAL', 'Baltimore': 'BAL',
                'Bengals': 'CIN', 'Cincinnati Bengals': 'CIN', 'Cincinnati': 'CIN',
                'Browns': 'CLE', 'Cleveland Browns': 'CLE', 'Cleveland': 'CLE',
                'Steelers': 'PIT', 'Pittsburgh Steelers': 'PIT', 'Pittsburgh': 'PIT',
                'Texans': 'HOU', 'Houston Texans': 'HOU', 'Houston': 'HOU',
                'Colts': 'IND', 'Indianapolis Colts': 'IND', 'Indianapolis': 'IND',
                'Jaguars': 'JAX', 'Jacksonville Jaguars': 'JAX', 'Jacksonville': 'JAX',
                'Titans': 'TEN', 'Tennessee Titans': 'TEN', 'Tennessee': 'TEN',
                'Broncos': 'DEN', 'Denver Broncos': 'DEN', 'Denver': 'DEN',
                'Chiefs': 'KC', 'Kansas City Chiefs': 'KC', 'Kansas City': 'KC',
                'Raiders': 'LV', 'Las Vegas Raiders': 'LV', 'Las Vegas': 'LV',
                'Chargers': 'LAC', 'Los Angeles Chargers': 'LAC', 'LA Chargers': 'LAC',
                'Cowboys': 'DAL', 'Dallas Cowboys': 'DAL', 'Dallas': 'DAL',
                'Giants': 'NYG', 'New York Giants': 'NYG', 'NY Giants': 'NYG',
                'Eagles': 'PHI', 'Philadelphia Eagles': 'PHI', 'Philadelphia': 'PHI',
                'Commanders': 'WAS', 'Washington Commanders': 'WAS', 'Washington': 'WAS',
                'Bears': 'CHI', 'Chicago Bears': 'CHI', 'Chicago': 'CHI',
                'Lions': 'DET', 'Detroit Lions': 'DET', 'Detroit': 'DET',
                'Packers': 'GB', 'Green Bay Packers': 'GB', 'Green Bay': 'GB',
                'Vikings': 'MIN', 'Minnesota Vikings': 'MIN', 'Minnesota': 'MIN',
                'Falcons': 'ATL', 'Atlanta Falcons': 'ATL', 'Atlanta': 'ATL',
                'Panthers': 'CAR', 'Carolina Panthers': 'CAR', 'Carolina': 'CAR',
                'Saints': 'NO', 'New Orleans Saints': 'NO', 'New Orleans': 'NO',
                'Buccaneers': 'TB', 'Tampa Bay Buccaneers': 'TB', 'Tampa Bay': 'TB',
                'Cardinals': 'ARI', 'Arizona Cardinals': 'ARI', 'Arizona': 'ARI',
                '49ers': 'SF', 'San Francisco 49ers': 'SF', 'San Francisco': 'SF',
                'Seahawks': 'SEA', 'Seattle Seahawks': 'SEA', 'Seattle': 'SEA',
                'Rams': 'LAR', 'Los Angeles Rams': 'LAR', 'LA Rams': 'LAR'
            },
            'nba': {
                # Add NBA team mappings if needed
                'Lakers': 'LAL', 'Los Angeles Lakers': 'LAL',
                'Warriors': 'GSW', 'Golden State Warriors': 'GSW',
                'Celtics': 'BOS', 'Boston Celtics': 'BOS',
                # ... add more as needed
            },
            'mlb': {
                # Add MLB team mappings if needed
                'Yankees': 'NYY', 'New York Yankees': 'NYY',
                'Red Sox': 'BOS', 'Boston Red Sox': 'BOS',
                'Dodgers': 'LAD', 'Los Angeles Dodgers': 'LAD',
                # ... add more as needed
            }
        }

    def _normalize_team_name(self, team_name: str, league: str = 'nfl') -> str:
        """Normalize team names to match other platforms"""
        mappings = self.team_mappings.get(league.lower(), {})
        
        # Try exact match first
        if team_name in mappings:
            return mappings[team_name]
        
        # Try case-insensitive match
        for full_name, abbrev in mappings.items():
            if team_name.lower() == full_name.lower():
                return abbrev
        
        # Return original if no mapping found
        return team_name

    def _extract_teams_from_question(self, question: str, league: str = 'nfl') -> tuple:
        """Extract and normalize team names from market question"""
        mappings = self.team_mappings.get(league.lower(), {})
        found_teams = []
        
        q_lower = question.lower()
        
        # Look for team names in the question
        for team_name, abbrev in mappings.items():
            if team_name.lower() in q_lower:
                if abbrev not in found_teams:
                    found_teams.append(abbrev)
        
        # Return first two teams found
        if len(found_teams) >= 2:
            return (found_teams[0], found_teams[1])
        elif len(found_teams) == 1:
            return (found_teams[0], None)
        else:
            return (None, None)

    def _is_game_winner_market(self, question: str, league: str = 'nfl') -> bool:
        """Check if market is about game winner (not props/futures)"""
        q_lower = question.lower()
        
        # Exclude futures and non-game markets
        exclude_keywords = [
            'super bowl', 'championship', 'season', 'mvp', 'award',
            'draft', 'rookie', 'playoff', 'division', 'record',
            'touchdown', 'yard', 'pass', 'rush', 'reception',
            'total', 'over', 'under', 'spread', 'margin', 'points'
        ]
        
        if any(keyword in q_lower for keyword in exclude_keywords):
            return False
        
        # Include game winner markets
        winner_keywords = ['win', 'beat', 'defeat', 'winner']
        has_winner_keyword = any(keyword in q_lower for keyword in winner_keywords)
        
        # Check if it's about the right league
        league_keywords = {
            'nfl': ['nfl', 'football'],
            'nba': ['nba', 'basketball'],
            'mlb': ['mlb', 'baseball'],
            'nhl': ['nhl', 'hockey']
        }
        
        is_right_league = any(
            keyword in q_lower 
            for keyword in league_keywords.get(league.lower(), [league.lower()])
        )
        
        # Or check if it has team names from the league
        teams = self._extract_teams_from_question(question, league)
        has_teams = teams[0] is not None
        
        return has_winner_keyword and (is_right_league or has_teams)

    def _polymarket_price_to_american_odds(self, price: float) -> int:
        """Convert Polymarket price (0-1) to American odds"""
        if price <= 0 or price >= 1:
            return 0
        
        # Calculate implied probability (already is the price in Polymarket)
        implied_prob = price
        
        # Convert to American odds
        if implied_prob >= 0.5:
            # Favorite (negative odds)
            american_odds = -int((implied_prob / (1 - implied_prob)) * 100)
        else:
            # Underdog (positive odds)
            american_odds = int(((1 - implied_prob) / implied_prob) * 100)
        
        return american_odds

    def _search_markets(self, search_term: str, limit: int = 100) -> List[Dict]:
        """Search for markets by term"""
        try:
            params = {
                'search': search_term,
                'limit': limit,
                'active': 'true'
            }
            
            response = self.session.get(f"{self.base_url}/markets", params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', data) if isinstance(data, dict) else data
            
        except Exception as e:
            print(f"Error searching Polymarket for '{search_term}': {e}")
            return []

    def _get_market_details(self, market_id: str) -> Optional[Dict]:
        """Get detailed market information"""
        try:
            response = self.session.get(f"{self.base_url}/markets/{market_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching Polymarket market {market_id}: {e}")
            return None

    def get_games(self, league: str = 'nfl', remove_live_games: bool = True) -> List[Dict]:
        """
        Get games from Polymarket in the same format as Pinnacle/Kalshi
        
        Returns list of dicts with keys:
        - favorite: favorite team abbreviation
        - dog: underdog team abbreviation  
        - fav_odds: American odds for favorite
        - dog_odds: American odds for underdog
        - game_date: YYYY-MM-DD format
        - game_time: YYYY-MM-DD HH:MM format
        - league: league name
        - status: 'active', 'closed', etc.
        """
        print(f"Fetching {league.upper()} games from Polymarket...")
        
        # Search for game winner markets
        search_terms = [f'{league} win', f'{league} beat', f'{league} winner']
        all_markets = []
        
        for term in search_terms:
            markets = self._search_markets(term)
            game_markets = [
                m for m in markets 
                if self._is_game_winner_market(m.get('question', ''), league)
            ]
            all_markets.extend(game_markets)
            time.sleep(0.2)  # Rate limiting
        
        # Remove duplicates
        unique_markets = []
        seen_ids = set()
        for market in all_markets:
            if market['id'] not in seen_ids:
                unique_markets.append(market)
                seen_ids.add(market['id'])
        
        # Convert to our standard format
        games = []
        for market in unique_markets:
            # Get detailed market info
            details = self._get_market_details(market['id'])
            if not details:
                continue
            
            # Skip if not active and we're removing live games
            if remove_live_games and not details.get('active', False):
                continue
            
            # Extract teams
            teams = self._extract_teams_from_question(details.get('question', ''), league)
            if not teams[0] or not teams[1]:
                continue  # Skip if we can't identify both teams
            
            # Get outcomes and prices
            outcomes = details.get('outcomes', [])
            if len(outcomes) != 2:
                continue  # Skip if not exactly 2 outcomes
            
            # Determine favorite and underdog based on prices
            outcome1 = outcomes[0]
            outcome2 = outcomes[1]
            
            price1 = float(outcome1.get('price', 0))
            price2 = float(outcome2.get('price', 0))
            
            if price1 > price2:
                # Outcome 1 is favorite
                fav_outcome = outcome1
                dog_outcome = outcome2
                favorite = teams[0]
                dog = teams[1]
            else:
                # Outcome 2 is favorite
                fav_outcome = outcome2
                dog_outcome = outcome1
                favorite = teams[1]
                dog = teams[0]
            
            # Convert prices to American odds
            fav_odds = self._polymarket_price_to_american_odds(float(fav_outcome.get('price', 0)))
            dog_odds = self._polymarket_price_to_american_odds(float(dog_outcome.get('price', 0)))
            
            # Parse date
            end_date_str = details.get('end_date', '')
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
            
            # Create game dict in standard format
            game = {
                'favorite': favorite,
                'dog': dog,
                'fav_odds': fav_odds,
                'dog_odds': dog_odds,
                'game_date': game_date,
                'game_time': game_time,
                'league': league.lower(),
                'status': 'active' if details.get('active') else 'closed',
                'volume': float(details.get('volume', 0)),
                'market_id': details['id'],
                'question': details.get('question', '')
            }
            
            games.append(game)
        
        # Sort by date
        games.sort(key=lambda x: x['game_date'])
        
        print(f"Found {len(games)} Polymarket {league.upper()} game winner markets")
        return games

    def print_games_table(self, games: List[Dict]):
        """Print games in a formatted table"""
        if not games:
            print("No games found")
            return
        
        print(f"\nPOLYMARKET GAMES ({len(games)} total)")
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

def test_polymarket():
    """Test Polymarket client"""
    client = PolymarketClient()
    
    # Test NFL games
    print("\n" + "="*60)
    print("TESTING POLYMARKET NFL GAMES")
    print("="*60)
    
    nfl_games = client.get_games(league='nfl', remove_live_games=True)
    client.print_games_table(nfl_games)
    
    return nfl_games

if __name__ == "__main__":
    test_polymarket()