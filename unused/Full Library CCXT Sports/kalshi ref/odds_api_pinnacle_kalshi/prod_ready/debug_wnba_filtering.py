#!/usr/bin/env python3
"""
Debug WNBA game filtering - why Las Vegas vs Washington isn't showing
"""

import sys
import os
from datetime import datetime, timezone
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.kalshi_client import KalshiClientUpdated as KalshiClient

def debug_wnba_filtering():
    """Debug why LV vs WSH WNBA game is being filtered"""
    
    print("DEBUGGING WNBA GAME FILTERING")
    print("=" * 60)
    print(f"Looking for: KXWNBAGAME-25AUG23LVWSH (Las Vegas vs Washington)")
    print(f"Current UTC time: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(project_root, 'keys', 'kalshi_credentials.txt')
        client = KalshiClient(creds_path)
        
        # Get WNBA markets using series_ticker
        print("1. Fetching WNBA markets...")
        raw_data = client._get_markets_by_series_ticker('KXWNBAGAME')
        print(f"Found {len(raw_data)} WNBA markets")
        
        # Look for Las Vegas vs Washington specifically
        lv_wsh_markets = []
        
        for market in raw_data:
            ticker = market.get('ticker', '')
            title = market.get('title', '')
            
            # Look for LV/WSH game
            if ('LVWSH' in ticker.upper()) or \
               ('las vegas' in title.lower() and 'washington' in title.lower()) or \
               ('lv' in ticker.upper() and 'wsh' in ticker.upper()):
                lv_wsh_markets.append(market)
        
        print(f"\n2. Found {len(lv_wsh_markets)} Las Vegas vs Washington markets:")
        
        for i, market in enumerate(lv_wsh_markets, 1):
            ticker = market.get('ticker')
            title = market.get('title')
            status = market.get('status', 'unknown')
            close_time = market.get('close_time')
            
            print(f"  {i}. {ticker}")
            print(f"     Title: {title}")
            print(f"     Status: {status}")
            print(f"     Close Time: {close_time}")
            
            # Test the time extraction
            game_date, game_time_estimate = client._extract_date_from_ticker(ticker)
            print(f"     Extracted Date: {game_date}")
            print(f"     Extracted Time: {game_time_estimate}")
            
            if game_date and game_time_estimate:
                filter_time = f"{game_date}T{game_time_estimate}:00Z"
                print(f"     Filter Time: {filter_time}")
                
                # Test filtering with different buffers
                is_future_0 = client._is_future_game(filter_time, 0)
                is_future_15 = client._is_future_game(filter_time, 15)
                is_future_60 = client._is_future_game(filter_time, 60)
                
                print(f"     Is Future (0min): {is_future_0}")
                print(f"     Is Future (15min): {is_future_15}")
                print(f"     Is Future (60min): {is_future_60}")
                
                if not is_future_0:
                    print(f"     >>> GAME IS LIVE OR PAST <<<")
                elif not is_future_15:
                    print(f"     >>> GAME STARTING SOON (filtered by 15min buffer) <<<")
                else:
                    print(f"     >>> Game should be included <<<")
            
            print()
        
        # Test full normalization process
        print("3. Testing full normalization process...")
        
        # Simulate the search_sports_markets call
        mock_raw_data = {
            'success': True,
            'data': raw_data,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Test with different time buffers
        for buffer_min in [0, 15, 30]:
            print(f"\nTesting with {buffer_min}-minute buffer:")
            normalized_games = client.normalize_kalshi_data(mock_raw_data, buffer_min)
            
            lv_wsh_normalized = [g for g in normalized_games if 
                               ('las vegas' in g.get('away_team', '').lower() and 'washington' in g.get('home_team', '').lower()) or
                               ('washington' in g.get('away_team', '').lower() and 'las vegas' in g.get('home_team', '').lower()) or
                               ('lv' in g.get('away_team', '').lower() and 'wsh' in g.get('home_team', '').lower()) or
                               ('wsh' in g.get('away_team', '').lower() and 'lv' in g.get('home_team', '').lower())]
            
            print(f"  Total normalized games: {len(normalized_games)}")
            print(f"  LV vs WSH games found: {len(lv_wsh_normalized)}")
            
            for game in lv_wsh_normalized:
                print(f"    {game['away_team']} @ {game['home_team']} - {game['game_time_display']}")
        
        print("\nDIAGNOSIS:")
        print("- Check if game time extraction is correct")
        print("- Verify if live game filtering is too aggressive")
        print("- Ensure team name extraction works for WNBA")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_wnba_filtering()