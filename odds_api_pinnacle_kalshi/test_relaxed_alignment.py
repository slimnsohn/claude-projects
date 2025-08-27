"""
Test Relaxed Alignment - Lower Confidence Threshold
Test alignment with different confidence thresholds to find optimal setting
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

def test_with_confidence_threshold(pinnacle_games, kalshi_games, min_confidence):
    """Test alignment with specific confidence threshold"""
    from data_aligner import GameMatcher
    
    # Create custom matcher with relaxed threshold
    matcher = GameMatcher(time_threshold_hours=24*4)  # 4 days to handle date differences
    
    # Temporarily modify the minimum confidence threshold
    original_threshold = 0.7
    
    aligned_games = []
    used_kalshi_indices = set()
    
    for pinnacle_game in pinnacle_games:
        best_match = None
        best_confidence = 0.0
        best_index = -1
        
        for i, kalshi_game in enumerate(kalshi_games):
            if i in used_kalshi_indices:
                continue
                
            confidence = matcher._calculate_match_confidence(pinnacle_game, kalshi_game)
            
            if confidence > best_confidence and confidence >= min_confidence:
                best_match = kalshi_game
                best_confidence = confidence
                best_index = i
        
        if best_match is not None:
            used_kalshi_indices.add(best_index)
            
            aligned_game = {
                'match_id': f"match_{len(aligned_games) + 1}",
                'pinnacle_data': pinnacle_game,
                'kalshi_data': best_match,
                'match_confidence': best_confidence
            }
            
            aligned_games.append(aligned_game)
    
    return aligned_games

def main():
    """Test various confidence thresholds"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\test_relaxed_alignment.py"
    print(f"Script: {script_path}")
    print()
    print("RELAXED ALIGNMENT TESTING")
    print("Testing different confidence thresholds to find optimal alignment")
    print("=" * 70)
    
    try:
        from pinnacle_client import PinnacleClient
        from kalshi_client import KalshiClientUpdated as KalshiClient
        
        # Get data
        pinnacle = PinnacleClient("keys/odds_api_key.txt")
        kalshi = KalshiClient("keys/kalshi_credentials.txt")
        
        pinnacle_raw = pinnacle.get_sports_odds('mlb')
        kalshi_raw = kalshi.search_sports_markets('mlb')
        
        if not pinnacle_raw.get('success') or not kalshi_raw.get('success'):
            print("ERROR: Failed to fetch data")
            return
        
        pinnacle_games = pinnacle.normalize_pinnacle_data(pinnacle_raw, 15)
        kalshi_games = kalshi.normalize_kalshi_data(kalshi_raw, 15)
        
        print(f"Data: {len(pinnacle_games)} Pinnacle games, {len(kalshi_games)} Kalshi games")
        
        # Test different confidence thresholds
        thresholds = [0.7, 0.5, 0.4, 0.3, 0.2, 0.1]
        
        for threshold in thresholds:
            print(f"\nTesting confidence threshold: {threshold:.1%}")
            aligned_games = test_with_confidence_threshold(pinnacle_games, kalshi_games, threshold)
            
            print(f"  Aligned games: {len(aligned_games)}")
            
            if aligned_games:
                for i, match in enumerate(aligned_games):
                    conf = match['match_confidence']
                    p_game = match['pinnacle_data']
                    k_game = match['kalshi_data']
                    
                    print(f"    Match {i+1}: {conf:.1%} confidence")
                    print(f"      Pinnacle: {p_game['away_team']} @ {p_game['home_team']} ({p_game['game_date']})")
                    print(f"      Kalshi:   {k_game['away_team']} @ {k_game['home_team']} ({k_game['game_date']})")
                    
                    # Show odds comparison
                    p_home = p_game['home_odds']['implied_probability']
                    p_away = p_game['away_odds']['implied_probability']
                    k_home = k_game['home_odds']['implied_probability']
                    k_away = k_game['away_odds']['implied_probability']
                    
                    home_diff = abs(p_home - k_home)
                    away_diff = abs(p_away - k_away)
                    max_edge = max(home_diff, away_diff)
                    
                    print(f"      Odds: Home {p_home:.1%} vs {k_home:.1%} (diff: {home_diff:.1%})")
                    print(f"            Away {p_away:.1%} vs {k_away:.1%} (diff: {away_diff:.1%})")
                    print(f"      MAX EDGE: {max_edge:.1%}")
                    
                    if max_edge >= 0.05:  # 5% edge
                        print(f"      *** PROFITABLE OPPORTUNITY: {max_edge:.1%} edge! ***")
                    print()
                
                # If we found alignments, test with original system
                if len(aligned_games) > 0:
                    print(f"SUCCESS at {threshold:.1%} threshold!")
                    print("These games should align with mispricing detection system.")
                    break
        
        if not any(test_with_confidence_threshold(pinnacle_games, kalshi_games, t) for t in thresholds):
            print("\nNo alignment found even with very relaxed thresholds.")
            print("The games might be on completely different dates/schedules.")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nScript path: {script_path}")

if __name__ == "__main__":
    main()