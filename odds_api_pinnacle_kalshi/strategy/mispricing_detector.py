"""
Kalshi Mispricing Strategy Detector
Uses Pinnacle as golden source to find Kalshi mispricing opportunities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from kal_pin.client import CombinedClient
from typing import List, Dict, Tuple
import math

class MispricingDetector:
    """Detect mispricing opportunities where Kalshi deviates from Pinnacle (golden source)"""
    
    def __init__(self, min_delta_threshold: int = 20):
        """
        Initialize mispricing detector
        
        Args:
            min_delta_threshold: Minimum raw point difference to qualify as mispricing
                                Example: 20 means -140 vs -125 = 15 (no), -160 vs -130 = 30 (yes)
        """
        self.min_delta_threshold = min_delta_threshold
        self.combined_client = CombinedClient()
    
    def find_mispricing_opportunities(self, league='nfl', remove_live_games=True) -> List[Dict]:
        """
        Find all mispricing opportunities where Kalshi odds differ significantly from Pinnacle
        
        Returns:
            List of mispricing opportunities with analysis
        """
        print(f"ANALYZING {league.upper()} MISPRICING OPPORTUNITIES")
        print(f"Pinnacle = Golden Source | Kalshi = Target for Mispricing")
        print(f"Minimum Delta Threshold: {self.min_delta_threshold} points")
        print("=" * 80)
        
        # Get combined games data
        games = self.combined_client.get_combined_games(league=league, remove_live_games=remove_live_games)
        
        # Filter to only games with both platforms
        both_platform_games = [game for game in games if game['pinnacle'] and game['kalshi']]
        print(f"Found {len(both_platform_games)} games with both Pinnacle and Kalshi odds")
        
        opportunities = []
        
        for game in both_platform_games:
            pinnacle_game = game['pinnacle']
            kalshi_game = game['kalshi']
            
            # Analyze favorite mispricing
            fav_opportunity = self._analyze_odds_pair(
                pinnacle_odds=pinnacle_game['fav_odds'],
                kalshi_odds=kalshi_game['fav_odds'],
                team=game['favorite'],
                side='favorite',
                game_info=game
            )
            
            if fav_opportunity:
                opportunities.append(fav_opportunity)
            
            # Analyze dog mispricing  
            dog_opportunity = self._analyze_odds_pair(
                pinnacle_odds=pinnacle_game['dog_odds'],
                kalshi_odds=kalshi_game['dog_odds'], 
                team=game['dog'],
                side='dog',
                game_info=game
            )
            
            if dog_opportunity:
                opportunities.append(dog_opportunity)
        
        # Sort by largest mispricing (highest delta) first
        opportunities.sort(key=lambda x: x['delta_points'], reverse=True)
        
        return opportunities
    
    def _analyze_odds_pair(self, pinnacle_odds: int, kalshi_odds: int, team: str, side: str, game_info: Dict) -> Dict:
        """
        Analyze a pair of odds to determine if there's a mispricing opportunity
        
        Args:
            pinnacle_odds: Pinnacle odds (golden source)
            kalshi_odds: Kalshi odds (target for mispricing)
            team: Team name
            side: 'favorite' or 'dog'
            game_info: Full game information
            
        Returns:
            Mispricing opportunity dict if qualifying, None otherwise
        """
        # Skip if either odds are extreme (likely bad data)
        if abs(pinnacle_odds) > 1000 or abs(kalshi_odds) > 1000:
            return None
        
        # Calculate raw point difference
        delta_points = abs(pinnacle_odds - kalshi_odds)
        
        # Check if meets minimum threshold
        if delta_points < self.min_delta_threshold:
            return None
        
        # Determine direction of mispricing
        if kalshi_odds > pinnacle_odds:
            # Kalshi offering better odds (higher payout) - GOOD for betting Kalshi
            direction = "KALSHI_BETTER"
            recommendation = f"BET {team} on Kalshi"
            value_analysis = "Kalshi offering more favorable odds than Pinnacle"
        else:
            # Kalshi offering worse odds (lower payout) - BAD, avoid Kalshi
            direction = "KALSHI_WORSE" 
            recommendation = f"AVOID {team} on Kalshi (bet Pinnacle if available)"
            value_analysis = "Kalshi offering less favorable odds than Pinnacle"
        
        # Calculate implied probabilities for deeper analysis
        pinnacle_prob = self._odds_to_probability(pinnacle_odds)
        kalshi_prob = self._odds_to_probability(kalshi_odds)
        prob_diff = abs(pinnacle_prob - kalshi_prob) * 100
        
        # Calculate Kalshi cents (their internal pricing)
        pinnacle_cents = round(pinnacle_prob * 100)
        kalshi_cents = round(kalshi_prob * 100)
        
        # Calculate expected value advantage
        ev_advantage = self._calculate_ev_advantage(pinnacle_odds, kalshi_odds)
        
        return {
            'game': f"{game_info['favorite']} vs {game_info['dog']}",
            'game_date': game_info['game_date'],
            'team': team,
            'side': side,
            'pinnacle_odds': pinnacle_odds,
            'kalshi_odds': kalshi_odds,
            'pinnacle_cents': pinnacle_cents,
            'kalshi_cents': kalshi_cents,
            'delta_points': delta_points,
            'direction': direction,
            'recommendation': recommendation,
            'value_analysis': value_analysis,
            'pinnacle_prob': round(pinnacle_prob * 100, 1),
            'kalshi_prob': round(kalshi_prob * 100, 1),
            'prob_diff_pct': round(prob_diff, 1),
            'ev_advantage_pct': round(ev_advantage * 100, 2),
            'pinnacle_game_time': game_info['pinnacle']['game_time'] if game_info['pinnacle'] else 'N/A',
            'kalshi_status': game_info['kalshi']['status'] if game_info['kalshi'] else 'N/A'
        }
    
    def _odds_to_probability(self, american_odds: int) -> float:
        """Convert American odds to implied probability"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def _calculate_ev_advantage(self, golden_odds: int, target_odds: int) -> float:
        """
        Calculate expected value advantage when betting target odds vs golden odds
        Positive EV = good opportunity, Negative EV = bad opportunity
        """
        if target_odds > golden_odds:
            # Target offering better payout - positive EV
            golden_prob = self._odds_to_probability(golden_odds)
            if target_odds > 0:
                target_payout = target_odds / 100
            else:
                target_payout = 100 / abs(target_odds)
            
            ev = (golden_prob * target_payout) - (1 - golden_prob) * 1
            return ev
        else:
            # Target offering worse payout - negative EV
            golden_prob = self._odds_to_probability(golden_odds)
            if target_odds > 0:
                target_payout = target_odds / 100
            else:
                target_payout = 100 / abs(target_odds)
            
            ev = (golden_prob * target_payout) - (1 - golden_prob) * 1
            return ev
    
    def print_opportunities_table(self, opportunities: List[Dict]):
        """Print mispricing opportunities in a clean table format"""
        if not opportunities:
            print("No mispricing opportunities found meeting the criteria")
            return
        
        print(f"\nMISPRICING OPPORTUNITIES FOUND: {len(opportunities)}")
        print("=" * 120)
        
        # Group by date for clean display
        opportunities_by_date = {}
        for opp in opportunities:
            date = opp['game_date']
            if date not in opportunities_by_date:
                opportunities_by_date[date] = []
            opportunities_by_date[date].append(opp)
        
        for date in sorted(opportunities_by_date.keys()):
            date_opportunities = opportunities_by_date[date]
            
            print(f"\n>> {date} ({len(date_opportunities)} opportunities)")
            print("=" * 120)
            
            for opp in date_opportunities:
                # Color coding based on direction
                status_symbol = "🟢" if opp['direction'] == "KALSHI_BETTER" else "🔴"
                
                print(f"{opp['game']} - {opp['team']} ({opp['side']})")
                print(f"  Pinnacle: {opp['pinnacle_odds']:>6} ({opp['pinnacle_prob']}% | {opp['pinnacle_cents']}¢)")
                print(f"  Kalshi:   {opp['kalshi_odds']:>6} ({opp['kalshi_prob']}% | {opp['kalshi_cents']}¢)")
                print(f"  Delta: {opp['delta_points']} points  |  Prob Diff: {opp['prob_diff_pct']}%  |  "
                      f"EV: {opp['ev_advantage_pct']:+.2f}%")
                print(f"  {opp['direction']}: {opp['recommendation']}")
                print(f"  {opp['value_analysis']}")
                print()
    
    def get_summary_stats(self, opportunities: List[Dict]) -> Dict:
        """Get summary statistics for mispricing opportunities"""
        if not opportunities:
            return {
                'total_opportunities': 0,
                'kalshi_better_count': 0,
                'kalshi_worse_count': 0,
                'avg_delta': 0,
                'max_delta': 0,
                'positive_ev_count': 0
            }
        
        kalshi_better = len([o for o in opportunities if o['direction'] == 'KALSHI_BETTER'])
        kalshi_worse = len([o for o in opportunities if o['direction'] == 'KALSHI_WORSE'])
        positive_ev = len([o for o in opportunities if o['ev_advantage_pct'] > 0])
        
        return {
            'total_opportunities': len(opportunities),
            'kalshi_better_count': kalshi_better,
            'kalshi_worse_count': kalshi_worse,
            'avg_delta': round(sum(o['delta_points'] for o in opportunities) / len(opportunities), 1),
            'max_delta': max(o['delta_points'] for o in opportunities),
            'positive_ev_count': positive_ev,
            'avg_ev': round(sum(o['ev_advantage_pct'] for o in opportunities) / len(opportunities), 2)
        }

def run_mispricing_analysis(league='nfl', remove_live_games=True, min_delta_threshold=20):
    """Main function to run mispricing analysis"""
    print(f"\n{'='*120}")
    print(f"KALSHI MISPRICING STRATEGY ANALYSIS")
    print(f"League: {league.upper()} | Remove Live Games: {remove_live_games} | Min Delta: {min_delta_threshold}")
    print(f"{'='*120}")
    
    try:
        detector = MispricingDetector(min_delta_threshold=min_delta_threshold)
        opportunities = detector.find_mispricing_opportunities(league=league, remove_live_games=remove_live_games)
        
        detector.print_opportunities_table(opportunities)
        
        # Print summary
        stats = detector.get_summary_stats(opportunities)
        print(f"{'='*120}")
        print("SUMMARY STATISTICS:")
        print(f"Total Mispricing Opportunities: {stats['total_opportunities']}")
        print(f"Kalshi Better (Good Bets): {stats['kalshi_better_count']}")
        print(f"Kalshi Worse (Avoid): {stats['kalshi_worse_count']}")
        print(f"Positive EV Opportunities: {stats['positive_ev_count']}")
        print(f"Average Delta: {stats['avg_delta']} points")
        print(f"Max Delta: {stats['max_delta']} points")
        print(f"Average EV: {stats['avg_ev']:+.2f}%")
        print(f"{'='*120}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # ====== EDIT THESE VARIABLES ======
    LEAGUE = 'nfl'                # 'mlb', 'nfl', 'nba', 'nhl'
    REMOVE_LIVE_GAMES = True      # True = only future games, False = include live/closed
    MIN_DELTA_THRESHOLD = 20      # Minimum raw point difference to qualify as mispricing
    # ===================================
    
    run_mispricing_analysis(
        league=LEAGUE,
        remove_live_games=REMOVE_LIVE_GAMES,
        min_delta_threshold=MIN_DELTA_THRESHOLD
    )