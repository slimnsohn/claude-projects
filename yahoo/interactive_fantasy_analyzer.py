#!/usr/bin/env python3
"""
Interactive Fantasy Basketball Analyzer

Quick tool for analyzing specific players and making draft decisions.
"""

from fantasy_basketball_analyzer import FantasyBasketballAnalyzer
import sys

class InteractiveAnalyzer:
    def __init__(self):
        print("Loading Fantasy Basketball Analyzer...")
        self.analyzer = FantasyBasketballAnalyzer()
        self.analyzer.load_data(min_games=20)
        self.analyzer.normalize_stats()
        print("Ready to analyze!")
        
    def analyze_player(self, player_name, season=2024):
        """Analyze a specific player."""
        print(f"\\n{'='*60}")
        print(f"PLAYER ANALYSIS: {player_name}")
        print(f"{'='*60}")
        
        profile = self.analyzer.get_player_profile(player_name, season)
        if not profile:
            print(f"Could not find {player_name} in {season} season")
            return None
        
        print(f"\\nBASIC INFO:")
        print(f"Name: {profile['name']}")
        print(f"Season: {profile['season']}")
        print(f"Team: {profile['team']}")
        print(f"Games: {profile['games']}")
        print(f"Overall Fantasy Value: {profile['fantasy_value']:.1f}")
        
        print(f"\\n📈 CATEGORY PERCENTILES (vs all NBA players):")
        categories = list(profile['percentiles'].items())
        categories.sort(key=lambda x: x[1], reverse=True)
        
        for cat, percentile in categories:
            if percentile >= 90:
                grade = "🟢 ELITE"
            elif percentile >= 75:
                grade = "🔵 VERY GOOD"  
            elif percentile >= 60:
                grade = "🟡 GOOD"
            elif percentile >= 40:
                grade = "🟠 AVERAGE"
            else:
                grade = "🔴 BELOW AVERAGE"
                
            print(f"  {cat:12}: {percentile:5.1f}th percentile {grade}")
        
        print(f"\\n💡 FANTASY INSIGHTS:")
        
        # Identify strengths
        strengths = [cat for cat, pct in categories[:3]]
        print(f"✓ Best categories: {', '.join(strengths)}")
        
        # Identify weaknesses  
        weaknesses = [cat for cat, pct in categories[-2:] if pct < 40]
        if weaknesses:
            print(f"⚠ Weak categories: {', '.join(weaknesses)}")
        
        # Draft advice
        elite_cats = [cat for cat, pct in categories if pct >= 90]
        if elite_cats:
            print(f"🎯 ELITE in: {', '.join(elite_cats)} - Major competitive advantage!")
        
        scarce_cats = ['Blocks', 'Steals', '3PM']
        elite_scarce = [cat for cat in elite_cats if cat in scarce_cats]
        if elite_scarce:
            print(f"💎 SCARCE CATEGORY SPECIALIST: {', '.join(elite_scarce)}")
            print(f"   → Draft priority - these categories win weeks!")
        
        return profile
        
    def compare_multiple_players(self, player_names, season=2024):
        """Compare multiple players side by side."""
        print(f"\\n{'='*80}")
        print(f"PLAYER COMPARISON - {season} Season")
        print(f"{'='*80}")
        
        comparison = self.analyzer.compare_players(player_names, season)
        if comparison is None:
            return
        
        # Display comparison table
        print(comparison.to_string(index=False))
        
        print(f"\\n🏆 CATEGORY WINNERS:")
        categories = [col for col in comparison.columns if col not in ['Player', 'Season']]
        
        for cat in categories:
            max_val = comparison[cat].max()
            winner = comparison[comparison[cat] == max_val]['Player'].iloc[0]
            print(f"  {cat:12}: {winner} ({max_val:.1f}th percentile)")
        
        print(f"\\n📊 OVERALL RANKINGS:")
        # Calculate total percentile score
        comparison['Total_Score'] = comparison[categories].sum(axis=1)
        ranked = comparison.sort_values('Total_Score', ascending=False)
        
        for i, (_, player) in enumerate(ranked.iterrows(), 1):
            print(f"  {i}. {player['Player']:20} Total Score: {player['Total_Score']:.1f}")
        
        return comparison
        
    def simulate_matchup(self, team1, team2, season=2024):
        """Simulate head-to-head matchup."""
        print(f"\\n{'='*60}")
        print(f"HEAD-TO-HEAD SIMULATION")  
        print(f"{'='*60}")
        
        result = self.analyzer.simulate_head_to_head(team1, team2, season)
        
        if result:
            print(f"\\n💡 MATCHUP INSIGHTS:")
            team1_wins = sum(1 for r in result.values() if r['winner'] == 'Team 1')
            team2_wins = sum(1 for r in result.values() if r['winner'] == 'Team 2')
            
            if team1_wins > team2_wins:
                print(f"Team 1 has the advantage ({team1_wins}-{team2_wins})")
            elif team2_wins > team1_wins:
                print(f"Team 2 has the advantage ({team2_wins}-{team1_wins})")
            else:
                print("Very close matchup - could go either way!")
        
        return result
        
    def find_sleepers(self, season=2024):
        """Find potential sleeper picks."""
        print(f"\\n{'='*60}")
        print(f"SLEEPER CANDIDATES - {season}")
        print(f"{'='*60}")
        
        undervalued = self.analyzer.identify_undervalued_players(season)
        
        print(f"\\n🎯 TOP SLEEPER TARGETS:")
        print(f"(Players with high value but may be overlooked)")
        
        top_sleepers = undervalued.head(10)
        for i, (_, player) in enumerate(top_sleepers.iterrows(), 1):
            print(f"{i:2d}. {player['Player']:20} "
                  f"Team: {player['Team']:4} "
                  f"Value: {player['Fantasy_Value']:5.1f} "
                  f"Balance: {player['Balance_Score']:.2f}")
        
        return undervalued

def main():
    """Interactive menu system."""
    analyzer = InteractiveAnalyzer()
    
    while True:
        print(f"\\n{'='*60}")
        print("FANTASY BASKETBALL ANALYZER")
        print(f"{'='*60}")
        print("1. Analyze single player")
        print("2. Compare multiple players") 
        print("3. Simulate head-to-head matchup")
        print("4. Find sleeper candidates")
        print("5. Category specialists")
        print("6. Exit")
        
        choice = input("\\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            player_name = input("Enter player name: ").strip()
            season = input("Season (default 2024): ").strip() or "2024"
            analyzer.analyze_player(player_name, int(season))
            
        elif choice == '2':
            players_input = input("Enter player names (comma-separated): ").strip()
            players = [p.strip() for p in players_input.split(',')]
            season = input("Season (default 2024): ").strip() or "2024"
            analyzer.compare_multiple_players(players, int(season))
            
        elif choice == '3':
            print("Enter Team 1 players:")
            team1_input = input("Players (comma-separated): ").strip()
            team1 = [p.strip() for p in team1_input.split(',')]
            
            print("Enter Team 2 players:")
            team2_input = input("Players (comma-separated): ").strip()  
            team2 = [p.strip() for p in team2_input.split(',')]
            
            season = input("Season (default 2024): ").strip() or "2024"
            analyzer.simulate_matchup(team1, team2, int(season))
            
        elif choice == '4':
            season = input("Season (default 2024): ").strip() or "2024"
            analyzer.find_sleepers(int(season))
            
        elif choice == '5':
            category = input("Category (Points, Rebounds, Assists, Steals, Blocks, 3PM, FG%, FT%, Turnovers): ").strip()
            season = input("Season (default 2024): ").strip() or "2024"
            top_n = input("How many players (default 15): ").strip() or "15"
            
            specialists = analyzer.analyzer.find_category_specialists(category, int(season), int(top_n))
            if specialists is not None:
                print(f"\\n🏆 TOP {category.upper()} PLAYERS:")
                print(specialists.to_string(index=False))
                
        elif choice == '6':
            print("Thanks for using the Fantasy Basketball Analyzer!")
            break
            
        else:
            print("Invalid choice. Please enter 1-6.")
        
        input("\\nPress Enter to continue...")

if __name__ == "__main__":
    main()