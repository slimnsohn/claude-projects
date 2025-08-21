#!/usr/bin/env python3
"""Simple test of the fantasy basketball analyzer."""

from fantasy_basketball_analyzer import FantasyBasketballAnalyzer

def test_analyzer():
    print("Testing Fantasy Basketball Analyzer...")
    
    # Initialize
    analyzer = FantasyBasketballAnalyzer()
    
    # Load data
    data = analyzer.load_data(min_games=30)
    normalized = analyzer.normalize_stats()
    
    print("\n" + "="*60)
    print("TESTING PLAYER ANALYSIS")
    print("="*60)
    
    # Test player analysis
    test_players = ["Victor Wembanyama", "LeBron James", "Stephen Curry"]
    
    for player in test_players:
        print(f"\nAnalyzing {player}...")
        profile = analyzer.get_player_profile(player, season=2024)
        
        if profile:
            print(f"Name: {profile['name']}")
            print(f"Team: {profile['team']}")
            print(f"Games: {profile['games']}")
            print(f"Fantasy Value: {profile['fantasy_value']:.1f}")
            
            print("Top 3 categories:")
            categories = sorted(profile['percentiles'].items(), key=lambda x: x[1], reverse=True)
            for cat, pct in categories[:3]:
                print(f"  {cat}: {pct:.1f}th percentile")
        else:
            print(f"Player {player} not found")
    
    print("\n" + "="*60) 
    print("TESTING PLAYER COMPARISON")
    print("="*60)
    
    # Test comparison
    comparison = analyzer.compare_players(["Victor Wembanyama", "Nikola Jokic"], season=2024)
    if comparison is not None:
        print(comparison.to_string(index=False))
    
    print("\n" + "="*60)
    print("TESTING CATEGORY SPECIALISTS")  
    print("="*60)
    
    # Test specialists
    blocks_leaders = analyzer.find_category_specialists("Blocks", season=2024, top_n=5)
    if blocks_leaders is not None:
        print("\nTop 5 Shot Blockers:")
        print(blocks_leaders.to_string(index=False))
    
    print("\n" + "="*60)
    print("TESTING HEAD-TO-HEAD SIMULATION")
    print("="*60)
    
    # Test simulation
    result = analyzer.simulate_head_to_head(
        ["Victor Wembanyama", "LeBron James"],
        ["Nikola Jokic", "Luka Doncic"],
        season=2024
    )
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_analyzer()