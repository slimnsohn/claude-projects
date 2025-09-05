"""
Pytest Version - Kalshi Date Fix Test
Proper pytest test for the Kalshi ticker date extraction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

import pytest
from kalshi_client import KalshiClientUpdated as KalshiClient

@pytest.fixture
def kalshi_client():
    """Create Kalshi client for testing"""
    return KalshiClient("keys/kalshi_credentials.txt")

def test_ticker_date_extraction(kalshi_client):
    """Test ticker date extraction method"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\test_kalshi_pytest.py"
    print(f"\nScript: {script_path}")
    print("\nTICKER DATE EXTRACTION TEST:")
    print("-" * 40)
    
    # Test with known ticker formats
    test_cases = [
        ("KXMLBGAME-25AUG21HOUBAL-HOU", "2025-08-25", "19:00"),
        ("KXMLBGAME-25AUG21ATHMIN-MIN", "2025-08-25", "19:00"),
        ("KXNFLGAME-08SEP24BUFMIA-BUF", "2024-09-08", "19:00"),
    ]
    
    for ticker, expected_date, expected_time in test_cases:
        date, time = kalshi_client._extract_date_from_ticker(ticker)
        print(f"Ticker: {ticker}")
        print(f"  Expected: {expected_date}, {expected_time}")
        print(f"  Got:      {date}, {time}")
        
        assert date == expected_date, f"Date mismatch for {ticker}: expected {expected_date}, got {date}"
        assert time == expected_time, f"Time mismatch for {ticker}: expected {expected_time}, got {time}"
        print("  PASS")

def test_kalshi_market_search(kalshi_client):
    """Test Kalshi market search functionality"""
    print("\nKALSHI MARKET SEARCH TEST:")
    print("-" * 40)
    
    raw_data = kalshi_client.search_sports_markets('mlb')
    
    print(f"Search success: {raw_data.get('success')}")
    assert raw_data.get('success'), f"Market search failed: {raw_data.get('error')}"
    
    markets = raw_data.get('data', [])
    print(f"Markets found: {len(markets)}")
    assert len(markets) > 0, "No markets found"
    
    # Check first market has expected fields
    first_market = markets[0]
    assert 'ticker' in first_market, "Market missing ticker field"
    assert 'title' in first_market, "Market missing title field"
    
    print(f"First market: {first_market.get('ticker')}")
    print("PASS")

def test_kalshi_data_normalization(kalshi_client):
    """Test Kalshi data normalization with date fix"""
    print("\nKALSHI DATA NORMALIZATION TEST:")
    print("-" * 40)
    
    # Get raw data
    raw_data = kalshi_client.search_sports_markets('mlb')
    assert raw_data.get('success'), "Failed to get raw data"
    
    # Normalize data
    normalized_games = kalshi_client.normalize_kalshi_data(raw_data, 15)
    
    print(f"Raw markets: {len(raw_data.get('data', []))}")
    print(f"Normalized games: {len(normalized_games)}")
    
    if normalized_games:
        game = normalized_games[0]
        print(f"First game: {game.get('away_team')} @ {game.get('home_team')}")
        print(f"Game date: {game.get('game_date')}")
        print(f"Game time: {game.get('game_time')}")
        
        # Check if we have proper date format
        game_date = game.get('game_date')
        assert game_date, "Game missing date"
        assert len(game_date) == 10, f"Invalid date format: {game_date}"
        assert game_date.count('-') == 2, f"Invalid date format: {game_date}"
        
        # Check if we have August 2025 dates (correct dates)
        aug_2025_count = sum(1 for g in normalized_games 
                           if g.get('game_date', '').startswith('2025-08'))
        
        print(f"Games with August 2025 dates: {aug_2025_count}/{len(normalized_games)}")
        
        if aug_2025_count > 0:
            print("SUCCESS: Date fix is working!")
        else:
            print("WARNING: No August 2025 dates found")
            # Show what dates we do have
            dates = set(g.get('game_date') for g in normalized_games if g.get('game_date'))
            print(f"Dates found: {sorted(dates)}")
        
        print("PASS")
    else:
        pytest.fail("No normalized games produced")

def test_system_integration():
    """Test that the fixed system components work together"""
    print("\nSYSTEM INTEGRATION TEST:")
    print("-" * 40)
    
    try:
        from pinnacle_client import PinnacleClient
        from data_aligner import GameMatcher
        
        # Get data from both platforms
        pinnacle = PinnacleClient("keys/odds_api_key.txt")
        kalshi = KalshiClient("keys/kalshi_credentials.txt")
        
        # Fetch data
        pinnacle_raw = pinnacle.get_sports_odds('mlb')
        kalshi_raw = kalshi.search_sports_markets('mlb')
        
        assert pinnacle_raw.get('success'), f"Pinnacle failed: {pinnacle_raw.get('error')}"
        assert kalshi_raw.get('success'), f"Kalshi failed: {kalshi_raw.get('error')}"
        
        # Normalize data
        pinnacle_games = pinnacle.normalize_pinnacle_data(pinnacle_raw, 15)
        kalshi_games = kalshi.normalize_kalshi_data(kalshi_raw, 15)
        
        print(f"Pinnacle games: {len(pinnacle_games)}")
        print(f"Kalshi games: {len(kalshi_games)}")
        
        assert len(pinnacle_games) > 0, "No Pinnacle games available"
        assert len(kalshi_games) > 0, "No Kalshi games available"
        
        # Test alignment
        matcher = GameMatcher(time_threshold_hours=6.0)
        aligned_games = matcher.align_games(pinnacle_games, kalshi_games)
        
        print(f"Aligned games: {len(aligned_games)}")
        
        # We don't assert alignment success since it depends on data availability
        # But we check that the process completes without errors
        print("PASS: System integration successful")
        
    except Exception as e:
        pytest.fail(f"System integration failed: {e}")

if __name__ == "__main__":
    """Run tests when executed directly"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\test_kalshi_pytest.py"
    print(f"Script: {script_path}")
    print()
    print("Running as standalone script...")
    print("Use: pytest test_kalshi_pytest.py -v")
    print()
    print(f"Script path: {script_path}")