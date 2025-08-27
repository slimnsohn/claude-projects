#!/usr/bin/env python3
"""
Debug script to investigate Baltimore vs Houston game on Kalshi
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.kalshi_client import KalshiClientUpdated
from datetime import datetime, timezone
import json

def debug_baltimore_houston():
    """Debug the specific Baltimore vs Houston game"""
    print("DEBUGGING BALTIMORE vs HOUSTON KALSHI GAME")
    print("=" * 60)
    
    try:
        client = KalshiClientUpdated('../keys/kalshi_credentials.txt')
        
        # Get all MLB markets
        print("Fetching Kalshi MLB markets...")
        raw_data = client.search_sports_markets('mlb')
        
        if not raw_data.get('success'):
            print("ERROR: Could not fetch Kalshi markets")
            return
        
        markets = raw_data.get('data', [])
        print(f"Found {len(markets)} MLB markets")
        
        # Find Baltimore/Houston games
        hou_bal_games = []
        current_time = datetime.now(timezone.utc)
        print(f"Current UTC time: {current_time.isoformat()}")
        print()
        
        for market in markets:
            title = market.get('title', '').lower()
            ticker = market.get('ticker', '')
            
            # Look for Houston/Baltimore games
            if ('houston' in title and 'baltimore' in title) or \
               ('hou' in ticker.lower() and 'bal' in ticker.lower()) or \
               ('baltimore' in title and 'houston' in title):
                hou_bal_games.append(market)
        
        print(f"Found {len(hou_bal_games)} Houston vs Baltimore games:")
        print("-" * 50)
        
        for i, market in enumerate(hou_bal_games, 1):
            print(f"\nGame {i}:")
            print(f"  Ticker: {market.get('ticker')}")
            print(f"  Title: {market.get('title')}")
            print(f"  Close Time: {market.get('close_time')}")
            print(f"  Expire Time: {market.get('expire_time')}")
            print(f"  Status: {market.get('status')}")
            print(f"  Yes Price: {market.get('yes_bid', 'N/A')}")
            print(f"  No Price: {market.get('no_bid', 'N/A')}")
            
            # Test date extraction
            ticker = market.get('ticker', '')
            game_date, game_time_estimate = client._extract_date_from_ticker(ticker)
            print(f"  Extracted Date: {game_date}")
            print(f"  Extracted Time: {game_time_estimate}")
            
            # Test time filtering
            close_time = market.get('close_time')
            if close_time:
                try:
                    # Parse close time
                    if close_time.endswith('Z'):
                        close_time_clean = close_time[:-1] + '+00:00'
                    else:
                        close_time_clean = close_time
                    
                    close_dt = datetime.fromisoformat(close_time_clean)
                    if close_dt.tzinfo is None:
                        close_dt = close_dt.replace(tzinfo=timezone.utc)
                    
                    time_until_close = close_dt - current_time
                    minutes_until = time_until_close.total_seconds() / 60
                    
                    print(f"  Close DateTime: {close_dt.isoformat()}")
                    print(f"  Minutes until close: {minutes_until:.1f}")
                    print(f"  Is Future (15min buffer): {minutes_until > 15}")
                    print(f"  Is Future (0min buffer): {minutes_until > 0}")
                    
                    if minutes_until <= 0:
                        print("  *** GAME HAS STARTED OR MARKET CLOSED ***")
                    elif minutes_until <= 15:
                        print("  *** GAME STARTING SOON (within 15 minutes) ***")
                    
                except Exception as e:
                    print(f"  ERROR parsing close time: {e}")
            
            # Test the actual filtering function
            from timestamp_utils import parse_game_time_safe
            filter_time = market.get('close_time', market.get('expire_time'))
            is_future_15 = parse_game_time_safe(filter_time, 15)
            is_future_0 = parse_game_time_safe(filter_time, 0)
            
            print(f"  Filter result (15min): {is_future_15}")
            print(f"  Filter result (0min): {is_future_0}")
            
            if not is_future_0:
                print("  >>> THIS GAME SHOULD BE FILTERED OUT <<<")
            elif not is_future_15:
                print("  >>> THIS GAME SHOULD BE FILTERED OUT (15min buffer) <<<")
            else:
                print("  >>> This game should be included")
        
        # Test normalization with different buffers
        print(f"\n{'='*60}")
        print("TESTING NORMALIZATION WITH DIFFERENT BUFFERS:")
        print("-" * 60)
        
        for buffer in [0, 15, 30]:
            print(f"\nWith {buffer}-minute buffer:")
            normalized = client.normalize_kalshi_data(raw_data, buffer)
            hou_bal_normalized = [g for g in normalized if 
                                ('houston' in g.get('home_team', '').lower() and 'baltimore' in g.get('away_team', '').lower()) or
                                ('baltimore' in g.get('home_team', '').lower() and 'houston' in g.get('away_team', '').lower()) or
                                ('hou' in g.get('home_team', '').lower() and 'bal' in g.get('away_team', '').lower()) or
                                ('bal' in g.get('home_team', '').lower() and 'hou' in g.get('away_team', '').lower())]
            
            print(f"  Houston vs Baltimore games after normalization: {len(hou_bal_normalized)}")
            for game in hou_bal_normalized:
                print(f"    {game['away_team']} @ {game['home_team']} - {game['game_time_display']}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_baltimore_houston()