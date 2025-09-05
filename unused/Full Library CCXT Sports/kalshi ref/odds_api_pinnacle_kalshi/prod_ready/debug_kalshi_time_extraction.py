#!/usr/bin/env python3
"""
Debug script to test Kalshi time extraction from tickers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.kalshi_client import KalshiClientUpdated as KalshiClient
from datetime import datetime, timezone

def test_time_extraction():
    """Test time extraction from specific tickers"""
    
    # Example tickers from the output
    test_tickers = [
        "KXMLBGAME-25AUG22HOUBAL-HOU",  # Should be Aug 22, 2025
        "KXMLBGAME-25AUG21HOUBAL-BAL",  # Should be Aug 21, 2025
        "KXMLBGAME-25AUG22STLTB-TB",    # Should be Aug 22, 2025
        "KXMLBGAME-25AUG21SFSD-SD"      # Should be Aug 21, 2025
    ]
    
    print("TESTING KALSHI TIME EXTRACTION")
    print("=" * 60)
    print(f"Current UTC time: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    try:
        # Initialize client
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(project_root, 'keys', 'kalshi_credentials.txt')
        client = KalshiClient(creds_path)
        
        for ticker in test_tickers:
            print(f"Ticker: {ticker}")
            
            # Test the extraction
            game_date, game_time_estimate = client._extract_date_from_ticker(ticker)
            
            print(f"  Extracted Date: {game_date}")
            print(f"  Extracted Time: {game_time_estimate}")
            
            if game_date and game_time_estimate:
                # Test the filter time construction
                filter_time = f"{game_date}T{game_time_estimate}:00Z"
                print(f"  Filter Time: {filter_time}")
                
                # Test if it's considered future with different buffers
                is_future_0 = client._is_future_game(filter_time, 0)
                is_future_15 = client._is_future_game(filter_time, 15)
                is_future_1440 = client._is_future_game(filter_time, 1440)  # 24 hours
                
                print(f"  Is Future (0min buffer): {is_future_0}")
                print(f"  Is Future (15min buffer): {is_future_15}")  
                print(f"  Is Future (24hr buffer): {is_future_1440}")
                
                if not is_future_0:
                    print(f"  >>> GAME IS LIVE OR PAST <<<")
                elif not is_future_15:
                    print(f"  >>> GAME STARTING SOON (within 15 min) <<<")
                else:
                    print(f"  >>> Game should be included <<<")
            else:
                print(f"  >>> FAILED TO EXTRACT DATE/TIME <<<")
            
            print()
        
        print("=" * 60)
        print("TESTING SUMMARY:")
        print("Check if dates are being extracted correctly from tickers")
        print("Aug 21 games should be past/live")
        print("Aug 22 games might be live depending on current time")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_time_extraction()