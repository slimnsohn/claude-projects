"""
Combined Kalshi-Pinnacle Client
Shows each game's odds from both platforms side by side
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pinnacle.client import PinnacleClient
from kalshi.client import KalshiClient
from typing import List, Dict
import pandas as pd

class CombinedClient:
    """Combined client showing Kalshi and Pinnacle odds side by side"""
    
    def __init__(self):
        """Initialize both clients"""
        self.pinnacle = PinnacleClient()
        self.kalshi = KalshiClient()
    
    def get_combined_games(self, league='mlb', remove_live_games=True) -> List[Dict]:
        """
        Get games from both platforms and match them up
        
        Args:
            league: League name ('mlb', 'nfl', 'nba', 'nhl')
            remove_live_games: Filter out live/started games
            
        Returns:
            List of combined game data with both Kalshi and Pinnacle odds
        """
        print(f"Fetching {league.upper()} games from both platforms...")
        
        # Get games from both platforms
        pinnacle_games = self.pinnacle.get_games(league=league, remove_live_games=remove_live_games)
        kalshi_games = self.kalshi.get_games(league=league, remove_live_games=remove_live_games)
        
        print(f"Found {len(pinnacle_games)} Pinnacle games, {len(kalshi_games)} Kalshi games")
        
        # Match games by teams
        combined_games = self._match_games(pinnacle_games, kalshi_games)
        
        return combined_games
    
    def _match_games(self, pinnacle_games: List[Dict], kalshi_games: List[Dict]) -> List[Dict]:
        """Match games between platforms by team names AND dates with strict date enforcement"""
        combined = []
        all_games = {}
        
        # Add Pinnacle games
        for game in pinnacle_games:
            teams_key = self._create_teams_key(game['favorite'], game['dog'])
            date_key = game['game_date']
            full_key = f"{teams_key}_{date_key}"
            
            if full_key not in all_games:
                all_games[full_key] = {
                    'favorite': game['favorite'],
                    'dog': game['dog'],
                    'game_date': game['game_date'],
                    'league': game['league'],
                    'pinnacle': game,
                    'kalshi': None
                }
        
        # Try to match Kalshi games with strict date matching
        for kalshi_game in kalshi_games:
            kalshi_teams_key = self._create_teams_key(kalshi_game['favorite'], kalshi_game['dog'])
            kalshi_date_key = kalshi_game['game_date']
            kalshi_full_key = f"{kalshi_teams_key}_{kalshi_date_key}"
            
            matched = False
            
            # Try direct match first (same teams, same date)
            if kalshi_full_key in all_games:
                all_games[kalshi_full_key]['kalshi'] = kalshi_game
                matched = True
            else:
                # Try reverse match (fav/dog swapped, same date)
                reverse_teams_key = self._create_teams_key(kalshi_game['dog'], kalshi_game['favorite'])
                reverse_full_key = f"{reverse_teams_key}_{kalshi_date_key}"
                
                if reverse_full_key in all_games:
                    all_games[reverse_full_key]['kalshi'] = kalshi_game
                    matched = True
                else:
                    # Try fuzzy date matching ONLY within ±1 day
                    from datetime import datetime, timedelta
                    try:
                        kalshi_date = datetime.strptime(kalshi_date_key, '%Y-%m-%d')
                        for delta_days in [-1, 1]:  # Check 1 day before and after
                            check_date = (kalshi_date + timedelta(days=delta_days)).strftime('%Y-%m-%d')
                            check_key = f"{kalshi_teams_key}_{check_date}"
                            reverse_check_key = f"{reverse_teams_key}_{check_date}"
                            
                            if check_key in all_games:
                                all_games[check_key]['kalshi'] = kalshi_game
                                matched = True
                                break
                            elif reverse_check_key in all_games:
                                all_games[reverse_check_key]['kalshi'] = kalshi_game
                                matched = True
                                break
                    except:
                        pass
            
            # If no match found, add as Kalshi-only game
            if not matched:
                all_games[kalshi_full_key] = {
                    'favorite': kalshi_game['favorite'],
                    'dog': kalshi_game['dog'],
                    'game_date': kalshi_game['game_date'],
                    'league': kalshi_game['league'],
                    'pinnacle': None,
                    'kalshi': kalshi_game
                }
        
        # Convert to list and sort
        for full_key, game_data in all_games.items():
            # Determine the best dog odds from available sources
            dog_odds = 0
            if game_data['pinnacle']:
                dog_odds = max(dog_odds, game_data['pinnacle']['dog_odds'])
            if game_data['kalshi']:
                kalshi_dog = game_data['kalshi']['dog_odds']
                if kalshi_dog < 1000:  # Filter out the extreme odds from conversion issues
                    dog_odds = max(dog_odds, kalshi_dog)
            
            game_data['best_dog_odds'] = dog_odds
            combined.append(game_data)
        
        # Sort by date first, then by best dog odds within each date
        combined.sort(key=lambda x: (x['game_date'], -x['best_dog_odds']))
        
        return combined
    
    def _create_teams_key(self, team1: str, team2: str) -> str:
        """Create a consistent key for team matching"""
        teams = sorted([team1.strip(), team2.strip()])
        return f"{teams[0]}_{teams[1]}"
    
    def _odds_to_cents(self, american_odds: int) -> int:
        """Convert American odds to Kalshi cents (0-100) accounting for fees"""
        if abs(american_odds) > 2500:  # Skip extreme odds
            return 0
        
        # Convert American odds to basic probability first
        if american_odds > 0:
            basic_probability = 100 / (american_odds + 100)
        else:
            basic_probability = abs(american_odds) / (abs(american_odds) + 100)
        
        # Since we now account for fees in the cents-to-odds conversion,
        # we need to reverse-engineer what the Kalshi price would be
        # This is an approximation since the fee structure is complex
        
        # For display purposes, we can use a simplified adjustment
        # The key insight is that our calibrated conversion accounts for fees,
        # so this reverse conversion should be approximate for display only
        
        return round(basic_probability * 100)
    
    def print_combined_table(self, games: List[Dict]):
        """Print games organized by date with side-by-side format"""
        if not games:
            print("No games found")
            return
        
        print(f"\nCOMBINED ODDS COMPARISON ({len(games)} games)")
        print("=" * 120)
        
        # Group games by date
        games_by_date = {}
        for game in games:
            game_date = game['game_date']
            if game_date not in games_by_date:
                games_by_date[game_date] = []
            games_by_date[game_date].append(game)
        
        # Print each date section
        for date in sorted(games_by_date.keys()):
            date_games = games_by_date[date]
            
            print(f"\n>> {date} ({len(date_games)} games)")
            print("=" * 120)
            
            for game in date_games:
                favorite = game['favorite']
                dog = game['dog']
                
                print(f"{favorite} vs {dog}")
                print("-" * 60)
                
                # Pinnacle row
                if game['pinnacle']:
                    pin_game = game['pinnacle']
                    pin_fav_odds = pin_game['fav_odds']
                    pin_dog_odds = pin_game['dog_odds']
                    pin_time = pin_game['game_time'].split(' ')[1] if ' ' in pin_game['game_time'] else pin_game['game_time']
                    
                    # Calculate cents for Pinnacle odds
                    pin_fav_cents = self._odds_to_cents(pin_fav_odds)
                    pin_dog_cents = self._odds_to_cents(pin_dog_odds)
                    
                    print(f"Pinnacle:  {favorite:>8} {pin_fav_odds:>6} ({pin_fav_cents}¢)  |  {dog:<8} {pin_dog_odds:>6} ({pin_dog_cents}¢)  |  {pin_time}")
                else:
                    print(f"Pinnacle:  {'N/A':>8} {'N/A':>6} {'':>6}  |  {'N/A':<8} {'N/A':>6} {'':>6}  |  N/A")
                
                # Kalshi row
                if game['kalshi']:
                    kal_game = game['kalshi']
                    kal_fav_odds = kal_game['fav_odds']
                    kal_dog_odds = kal_game['dog_odds']
                    kal_time = kal_game['game_time'].split(' ')[1] if ' ' in kal_game['game_time'] else kal_game['game_time']
                    kal_status = kal_game.get('status', 'unknown')
                    
                    # Calculate cents for Kalshi odds
                    kal_fav_cents = self._odds_to_cents(kal_fav_odds)
                    kal_dog_cents = self._odds_to_cents(kal_dog_odds)
                    
                    print(f"Kalshi:    {favorite:>8} {kal_fav_odds:>6} ({kal_fav_cents}¢)  |  {dog:<8} {kal_dog_odds:>6} ({kal_dog_cents}¢)  |  {kal_time} ({kal_status})")
                else:
                    print(f"Kalshi:    {'N/A':>8} {'N/A':>6} {'':>6}  |  {'N/A':<8} {'N/A':>6} {'':>6}  |  N/A")
                
                # Calculate potential edge if both available
                if game['pinnacle'] and game['kalshi']:
                    pin_fav = game['pinnacle']['fav_odds']
                    kal_fav = game['kalshi']['fav_odds']
                    
                    # Only calculate if Kalshi odds look reasonable (not the extreme -9899 values)
                    if abs(kal_fav) < 1000 and abs(pin_fav) < 1000:
                        fav_diff = abs(pin_fav - kal_fav)
                        if fav_diff > 10:  # Meaningful difference
                            print(f"Edge:      Favorite odds difference: {fav_diff} points")
                
                print()  # Blank row between games
    
    def get_summary_stats(self, games: List[Dict]) -> Dict:
        """Get summary statistics including detailed edge information"""
        stats = {
            'total_games': len(games),
            'pinnacle_only': len([g for g in games if g['pinnacle'] and not g['kalshi']]),
            'kalshi_only': len([g for g in games if g['kalshi'] and not g['pinnacle']]),
            'both_platforms': len([g for g in games if g['pinnacle'] and g['kalshi']]),
            'potential_edges': 0,
            'edge_games': []
        }
        
        # Find games with potential arbitrage opportunities
        for game in games:
            if game['pinnacle'] and game['kalshi']:
                pin_fav = game['pinnacle']['fav_odds']
                kal_fav = game['kalshi']['fav_odds']
                pin_dog = game['pinnacle']['dog_odds'] 
                kal_dog = game['kalshi']['dog_odds']
                
                if abs(kal_fav) < 2500 and abs(pin_fav) < 2500:  # Reasonable odds range
                    fav_diff = abs(pin_fav - kal_fav)
                    dog_diff = abs(pin_dog - kal_dog)
                    max_diff = max(fav_diff, dog_diff)
                    
                    if max_diff > 15:  # 15+ point difference is meaningful edge
                        # Determine which side has better odds where
                        if fav_diff > dog_diff:
                            # Favorite has bigger difference
                            if pin_fav > kal_fav:  # Pinnacle favorite odds are worse (higher negative)
                                better_side = f"Kalshi {game['favorite']}"
                                edge_info = f"{pin_fav:+d} vs {kal_fav:+d}"
                            else:  # Kalshi favorite odds are worse
                                better_side = f"Pinnacle {game['favorite']}"
                                edge_info = f"{kal_fav:+d} vs {pin_fav:+d}"
                            edge_diff = fav_diff
                        else:
                            # Dog has bigger difference  
                            if pin_dog < kal_dog:  # Pinnacle dog odds are worse (lower positive)
                                better_side = f"Kalshi {game['dog']}"
                                edge_info = f"{pin_dog:+d} vs {kal_dog:+d}"
                            else:  # Kalshi dog odds are worse
                                better_side = f"Pinnacle {game['dog']}"
                                edge_info = f"{kal_dog:+d} vs {pin_dog:+d}"
                            edge_diff = dog_diff
                        
                        edge_game = {
                            'matchup': f"{game['favorite']} vs {game['dog']}",
                            'game_date': game['game_date'],
                            'edge_diff': edge_diff,
                            'better_side': better_side,
                            'edge_info': edge_info,
                            'pinnacle_fav': pin_fav,
                            'kalshi_fav': kal_fav,
                            'pinnacle_dog': pin_dog,
                            'kalshi_dog': kal_dog
                        }
                        
                        stats['edge_games'].append(edge_game)
                        stats['potential_edges'] += 1
        
        # Sort edge games by difference size
        stats['edge_games'].sort(key=lambda x: x['edge_diff'], reverse=True)
        
        return stats

def view_combined_games(league='mlb', remove_live_games=True, require_both_platforms=False):
    """Main function to view combined games"""
    print(f"\n{'='*120}")
    print(f"COMBINED KALSHI-PINNACLE {league.upper()} ODDS COMPARISON")
    print(f"Remove Live Games: {remove_live_games}")
    print(f"Require Both Platforms: {require_both_platforms}")
    print(f"{'='*120}")
    
    try:
        client = CombinedClient()
        games = client.get_combined_games(league=league, remove_live_games=remove_live_games)
        
        # Filter out any games with finalized Kalshi status
        games = [game for game in games if not (game['kalshi'] and game['kalshi'].get('status') in ['finalized', 'settled', 'resolved'])]
        
        # Filter to only games with both platforms if requested
        if require_both_platforms:
            games = [game for game in games if game['pinnacle'] and game['kalshi']]
            print(f"Filtered to {len(games)} games with both platforms")
        
        client.print_combined_table(games)
        
        # Print summary
        stats = client.get_summary_stats(games)
        print(f"{'='*120}")
        print("SUMMARY:")
        print(f"Total Games: {stats['total_games']}")
        print(f"Pinnacle Only: {stats['pinnacle_only']}")
        print(f"Kalshi Only: {stats['kalshi_only']}")
        print(f"Both Platforms: {stats['both_platforms']}")
        print(f"Potential Edges: {stats['potential_edges']}")
        
        # Show detailed edge information
        if stats['potential_edges'] > 0:
            print()
            print("EDGE OPPORTUNITIES:")
            for i, edge in enumerate(stats['edge_games'], 1):
                print(f"{i}. {edge['matchup']} ({edge['game_date']})")
                print(f"   Best: {edge['better_side']} ({edge['edge_info']}) - {edge['edge_diff']} point edge")
                print(f"   Full odds: Pinnacle {edge['pinnacle_fav']:+d}/{edge['pinnacle_dog']:+d} | Kalshi {edge['kalshi_fav']:+d}/{edge['kalshi_dog']:+d}")
        
        print(f"{'='*120}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # ====== EDIT THESE VARIABLES ======
    LEAGUE = 'ncaaf'                  # 'mlb', 'nfl', 'nba', 'nhl', 'ncaaf', 'ncaab'
    REMOVE_LIVE_GAMES = True          # True = only future games, False = include live/closed
    REQUIRE_BOTH_PLATFORMS = True # True = only show games with both Kalshi and Pinnacle odds
    # ===================================
    
    view_combined_games(
        league=LEAGUE, 
        remove_live_games=REMOVE_LIVE_GAMES,
        require_both_platforms=REQUIRE_BOTH_PLATFORMS
    )