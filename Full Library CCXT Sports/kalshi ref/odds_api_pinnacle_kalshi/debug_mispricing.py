"""
Debug Mispricing Detection
Test the mispricing detector directly with our aligned games
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

def main():
    """Debug mispricing detection step by step"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\debug_mispricing.py"
    print(f"Script: {script_path}")
    print()
    print("MISPRICING DETECTION DEBUG")
    print("Testing detector with our aligned games")
    print("=" * 60)
    
    try:
        from data_aligner import MispricingDetector
        
        # Test with explicit settings
        print("Creating MispricingDetector with:")
        print("  min_edge_threshold=0.03 (3%)")
        print("  min_confidence=0.4 (40%)")
        
        detector = MispricingDetector(
            min_edge_threshold=0.03,
            min_confidence=0.4
        )
        
        print(f"\nDetector settings:")
        print(f"  min_edge: {detector.min_edge}")
        print(f"  min_confidence: {detector.min_confidence}")
        
        # Create mock aligned games with our data
        aligned_games = [
            {
                'match_id': 'test_1',
                'match_confidence': 0.48,
                'pinnacle_data': {
                    'home_odds': {'implied_probability': 0.537},
                    'away_odds': {'implied_probability': 0.481}
                },
                'kalshi_data': {
                    'home_odds': {'implied_probability': 0.472},
                    'away_odds': {'implied_probability': 0.519}
                }
            },
            {
                'match_id': 'test_2', 
                'match_confidence': 0.409,
                'pinnacle_data': {
                    'home_odds': {'implied_probability': 0.488},
                    'away_odds': {'implied_probability': 0.531}
                },
                'kalshi_data': {
                    'home_odds': {'implied_probability': 0.510},
                    'away_odds': {'implied_probability': 0.472}
                }
            }
        ]
        
        print(f"\nTesting with {len(aligned_games)} aligned games...")
        
        # Test each game individually first
        for i, game in enumerate(aligned_games):
            print(f"\nGame {i+1} (confidence: {game['match_confidence']:.1%}):")
            
            # Check confidence filter
            if game.get('match_confidence', 0) < detector.min_confidence:
                print(f"  FILTERED OUT: confidence {game['match_confidence']:.1%} < {detector.min_confidence:.1%}")
                continue
            else:
                print(f"  PASSED confidence filter: {game['match_confidence']:.1%} >= {detector.min_confidence:.1%}")
            
            # Manually check for mispricing
            p_data = game['pinnacle_data']
            k_data = game['kalshi_data']
            
            p_home = p_data['home_odds']['implied_probability']
            p_away = p_data['away_odds']['implied_probability']
            k_home = k_data['home_odds']['implied_probability']
            k_away = k_data['away_odds']['implied_probability']
            
            home_edge = abs(p_home - k_home)
            away_edge = abs(p_away - k_away)
            max_edge = max(home_edge, away_edge)
            
            print(f"  Pinnacle: Home {p_home:.1%}, Away {p_away:.1%}")
            print(f"  Kalshi:   Home {k_home:.1%}, Away {k_away:.1%}")
            print(f"  Edges:    Home {home_edge:.1%}, Away {away_edge:.1%}")
            print(f"  Max edge: {max_edge:.1%}")
            
            if max_edge >= detector.min_edge:
                print(f"  OPPORTUNITY: {max_edge:.1%} >= {detector.min_edge:.1%}")
            else:
                print(f"  NO OPPORTUNITY: {max_edge:.1%} < {detector.min_edge:.1%}")
        
        # Now test with the actual detector
        print(f"\n" + "=" * 40)
        print("TESTING WITH ACTUAL DETECTOR:")
        opportunities = detector.detect_opportunities(aligned_games)
        
        print(f"Opportunities detected: {len(opportunities)}")
        
        if opportunities:
            for i, opp in enumerate(opportunities):
                print(f"\nOpportunity {i+1}:")
                max_edge = opp['discrepancy']['max_edge']
                side = opp['discrepancy']['recommended_side']
                print(f"  Max edge: {max_edge:.1%} on {side}")
        else:
            print("No opportunities detected by the system")
            print("\nThis indicates a bug in the detection logic!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nScript path: {script_path}")

if __name__ == "__main__":
    main()