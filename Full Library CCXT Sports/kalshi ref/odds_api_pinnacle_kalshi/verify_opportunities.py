"""
Manual Opportunity Verification
Manually calculate edges from the saved alignment data to verify why opportunities aren't detected
"""

def main():
    """Manually verify opportunities from aligned games"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\verify_opportunities.py"
    print(f"Script: {script_path}")
    print()
    print("MANUAL OPPORTUNITY VERIFICATION")
    print("Calculating edges from saved alignment data")
    print("=" * 60)
    
    # Manual data from the saved results
    games = [
        {
            "name": "HOU @ BAL",
            "pinnacle_home": 0.5370370370370371,
            "pinnacle_away": 0.4807692307692307,
            "kalshi_home": 0.4716981132075471,
            "kalshi_away": 0.5192307692307692,
            "confidence": 0.48
        },
        {
            "name": "BOS @ NYY", 
            "pinnacle_home": 0.5833333333333333,
            "pinnacle_away": 0.4366812227074236,
            "kalshi_home": 0.5689655172413793,
            "kalshi_away": 0.42016806722689076,
            "confidence": 0.4885
        },
        {
            "name": "STL @ TB",
            "pinnacle_home": 0.48780487804878053,
            "pinnacle_away": 0.5305164319248826,
            "kalshi_home": 0.5098039215686274,
            "kalshi_away": 0.4716981132075471,
            "confidence": 0.4091
        }
    ]
    
    min_edge_threshold = 0.03  # 3% from main_system.py
    min_confidence = 0.4       # Updated value
    
    print(f"Checking with:")
    print(f"  Minimum edge threshold: {min_edge_threshold:.1%}")
    print(f"  Minimum confidence: {min_confidence:.1%}")
    print()
    
    opportunities_found = 0
    
    for i, game in enumerate(games):
        print(f"Game {i+1}: {game['name']}")
        print(f"  Match confidence: {game['confidence']:.1%}")
        
        # Calculate edges
        home_edge = abs(game['pinnacle_home'] - game['kalshi_home'])
        away_edge = abs(game['pinnacle_away'] - game['kalshi_away'])
        max_edge = max(home_edge, away_edge)
        
        print(f"  Pinnacle: Home {game['pinnacle_home']:.1%}, Away {game['pinnacle_away']:.1%}")
        print(f"  Kalshi:   Home {game['kalshi_home']:.1%}, Away {game['kalshi_away']:.1%}")
        print(f"  Edges:    Home {home_edge:.1%}, Away {away_edge:.1%}")
        print(f"  MAX EDGE: {max_edge:.1%}")
        
        # Check if it qualifies as opportunity
        confidence_ok = game['confidence'] >= min_confidence
        edge_ok = max_edge >= min_edge_threshold
        
        print(f"  Confidence check: {confidence_ok} ({game['confidence']:.1%} >= {min_confidence:.1%})")
        print(f"  Edge check: {edge_ok} ({max_edge:.1%} >= {min_edge_threshold:.1%})")
        
        if confidence_ok and edge_ok:
            opportunities_found += 1
            which_side = "Home" if home_edge > away_edge else "Away"
            print(f"  *** OPPORTUNITY DETECTED: {max_edge:.1%} edge on {which_side} ***")
        else:
            print(f"  No opportunity (failed {'confidence' if not confidence_ok else 'edge'} check)")
        
        print()
    
    print("=" * 60)
    print(f"MANUAL VERIFICATION RESULTS:")
    print(f"  Total opportunities found: {opportunities_found}")
    print(f"  System reported: 0")
    
    if opportunities_found > 0:
        print(f"\nISSUE IDENTIFIED: System should detect {opportunities_found} opportunities!")
        print("Possible causes:")
        print("1. Configuration not being applied correctly")
        print("2. Bug in mispricing detection logic")
        print("3. Data transformation issues")
    else:
        print("\nNo manual opportunities found - system is working correctly")
    
    print(f"\nScript path: {script_path}")

if __name__ == "__main__":
    main()