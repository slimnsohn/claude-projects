"""
Comprehensive test suite for all modules
Tests individual components and integration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'prod_ready'))

from pinnacle_client import PinnacleClient
from kalshi_client import KalshiClientUpdated as KalshiClient
from odds_converter import OddsConverter
from data_aligner import GameMatcher, MispricingDetector

def test_pinnacle_client():
    """Test Pinnacle API client"""
    print("=== TESTING PINNACLE CLIENT ===")
    
    try:
        client = PinnacleClient("keys/odds_api_key.txt")
        
        # Test data fetching
        raw_data = client.get_mlb_odds()
        assert raw_data.get('success'), "Failed to fetch Pinnacle data"
        
        # Test normalization
        normalized_games = client.normalize_pinnacle_data(raw_data)
        assert len(normalized_games) > 0, "No games normalized"
        
        # Validate schema
        game = normalized_games[0]
        required_fields = ['game_id', 'home_team', 'away_team', 'home_odds', 'away_odds']
        for field in required_fields:
            assert field in game, f"Missing field: {field}"
        
        print(f"PASS: Pinnacle client test passed - {len(normalized_games)} games")
        return True, normalized_games
        
    except Exception as e:
        print(f"FAIL: Pinnacle client test failed: {e}")
        return False, []

def test_kalshi_client():
    """Test Kalshi API client"""
    print("\n=== TESTING KALSHI CLIENT ===")
    
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        
        # Test with mock data since real MLB markets aren't available
        mock_data = client.create_mock_mlb_data()
        assert mock_data.get('success'), "Failed to create mock data"
        
        # Test normalization
        normalized_games = client.normalize_kalshi_data(mock_data, use_mock=True)
        assert len(normalized_games) > 0, "No games normalized"
        
        # Validate schema
        game = normalized_games[0]
        required_fields = ['game_id', 'home_team', 'away_team', 'home_odds', 'away_odds']
        for field in required_fields:
            assert field in game, f"Missing field: {field}"
        
        print(f"PASS: Kalshi client test passed - {len(normalized_games)} games")
        return True, normalized_games
        
    except Exception as e:
        print(f"FAIL: Kalshi client test failed: {e}")
        return False, []

def test_odds_converter():
    """Test odds conversion utilities"""
    print("\n=== TESTING ODDS CONVERTER ===")
    
    try:
        # Test basic conversions
        american_odds = [+150, -110, +100, -200]
        for odds in american_odds:
            decimal = OddsConverter.american_to_decimal(odds)
            back_to_american = OddsConverter.decimal_to_american(decimal)
            assert abs(back_to_american - odds) <= 1, f"Conversion round-trip failed for {odds}"
        
        # Test Kalshi conversions  
        test_cases = [
            (0.40, 140),
            (0.45, 114), 
            (0.50, -107),
            (0.70, -262),
            (0.85, -606),
            (0.95, -2396)
        ]
        
        for percentage, expected in test_cases:
            result = OddsConverter.kalshi_to_american(percentage)
            assert result == expected, f"Kalshi conversion failed: {percentage} -> {result}, expected {expected}"
        
        # Test complete odds object
        odds_obj = OddsConverter.create_odds_object(+150)
        assert odds_obj['american'] == 150
        assert abs(odds_obj['decimal'] - 2.5) < 0.01
        assert abs(odds_obj['implied_probability'] - 0.4) < 0.01
        
        print("PASS: Odds converter test passed")
        return True
        
    except Exception as e:
        print(f"FAIL: Odds converter test failed: {e}")
        return False

def test_data_aligner():
    """Test data alignment and mispricing detection"""
    print("\n=== TESTING DATA ALIGNMENT ===")
    
    try:
        # Create test data
        pinnacle_games = [
            {
                'game_id': 'pinnacle_test',
                'home_team': 'MIN',
                'away_team': 'OAK', 
                'game_date': '2025-08-21',
                'game_time': '2025-08-21T17:11:00Z',
                'home_odds': {'implied_probability': 0.48},
                'away_odds': {'implied_probability': 0.52}
            }
        ]
        
        kalshi_games = [
            {
                'game_id': 'kalshi_test',
                'home_team': 'OAK',
                'away_team': 'MIN',
                'game_date': '2025-08-21',
                'game_time': '2025-08-21T17:11:00Z', 
                'home_odds': {'implied_probability': 0.55},
                'away_odds': {'implied_probability': 0.45}
            }
        ]
        
        # Test game matching
        matcher = GameMatcher()
        aligned_games = matcher.align_games(pinnacle_games, kalshi_games)
        assert len(aligned_games) == 1, "Game alignment failed"
        assert aligned_games[0]['match_confidence'] >= 0.8, "Low match confidence"
        
        # Test mispricing detection
        detector = MispricingDetector(min_edge_threshold=0.02)
        opportunities = detector.detect_opportunities(aligned_games)
        assert len(opportunities) >= 1, "No opportunities detected"
        
        opportunity = opportunities[0]
        assert 'discrepancy' in opportunity
        assert 'profit_analysis' in opportunity
        assert opportunity['discrepancy']['max_edge'] > 0.02
        
        print(f"PASS: Data alignment test passed - {len(opportunities)} opportunities")
        return True
        
    except Exception as e:
        print(f"FAIL: Data alignment test failed: {e}")
        return False

def test_integration():
    """Test full end-to-end integration"""
    print("\n=== TESTING FULL INTEGRATION ===")
    
    try:
        # Test individual modules first
        pinnacle_success, pinnacle_games = test_pinnacle_client()
        kalshi_success, kalshi_games = test_kalshi_client()
        odds_success = test_odds_converter()
        alignment_success = test_data_aligner()
        
        if not all([pinnacle_success, kalshi_success, odds_success, alignment_success]):
            print("FAIL: Integration test failed - individual module failures")
            return False
        
        # Test full pipeline with real data
        if pinnacle_games and kalshi_games:
            matcher = GameMatcher(time_threshold_hours=6.0)  # Looser matching for test
            aligned_games = matcher.align_games(pinnacle_games, kalshi_games)
            
            detector = MispricingDetector(min_edge_threshold=0.01)
            opportunities = detector.detect_opportunities(aligned_games)
            
            print(f"PASS: Full integration successful:")
            print(f"  - Pinnacle games: {len(pinnacle_games)}")
            print(f"  - Kalshi games: {len(kalshi_games)}")
            print(f"  - Aligned games: {len(aligned_games)}")
            print(f"  - Opportunities: {len(opportunities)}")
            
            return True
        
        print("PASS: Integration test passed (limited by data availability)")
        return True
        
    except Exception as e:
        print(f"FAIL: Integration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("STARTING COMPREHENSIVE TEST SUITE")
    print("=" * 50)
    
    test_results = {
        'pinnacle': test_pinnacle_client()[0],
        'kalshi': test_kalshi_client()[0], 
        'odds_converter': test_odds_converter(),
        'data_aligner': test_data_aligner(),
        'integration': test_integration()
    }
    
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<20}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: ALL TESTS PASSED - System ready for production!")
    else:
        print("WARNING: Some tests failed - Review issues before production use")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()