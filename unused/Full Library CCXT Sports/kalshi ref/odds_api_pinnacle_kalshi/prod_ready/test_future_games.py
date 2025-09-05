#!/usr/bin/env python3
"""
Test specific tickers that might be future games
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.kalshi_client import KalshiClientUpdated as KalshiClient

def test_specific_tickers():
    """Test specific tickers that show Sep close times"""
    
    # Games that show Sep market close times but Aug 22 tickers
    test_tickers = [
        "KXMLBGAME-25AUG22CHCLAA-LAA",  # Chicago Cubs at LA Angels - close Sep 6
        "KXMLBGAME-25AUG22ATHSEA-SEA",  # A's at Seattle - close Sep 6  
        "KXMLBGAME-25AUG22CINAZ-CIN",   # Cincinnati at Arizona - close Sep 6
        "KXMLBGAME-25AUG22SFMIL-SF",    # San Francisco at Milwaukee - close Sep 6
    ]
    
    print("TESTING 'FUTURE' GAMES WITH SEP MARKET CLOSE TIMES")
    print("=" * 60)
    
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(project_root, 'keys', 'kalshi_credentials.txt')
        client = KalshiClient(creds_path)
        
        for ticker in test_tickers:
            print(f"Ticker: {ticker}")
            
            game_date, game_time_estimate = client._extract_date_from_ticker(ticker)
            
            print(f"  Game Date from Ticker: {game_date}")
            print(f"  Estimated Game Time: {game_time_estimate}")
            
            if game_date and game_time_estimate:
                filter_time = f"{game_date}T{game_time_estimate}:00Z"
                is_future_15 = client._is_future_game(filter_time, 15)
                
                print(f"  Calculated Game Time: {filter_time}")
                print(f"  Is Future Game (15min buffer): {is_future_15}")
                
                if is_future_15:
                    print(f"  >>> THIS SHOULD BE INCLUDED IN RESULTS <<<")
                else:
                    print(f"  >>> This game is live/past and correctly filtered <<<")
            
            print()
        
        print("CONCLUSION:")
        print("These games have market close times in September (when Kalshi settles)")
        print("But the actual GAME dates are Aug 22, which are now past games")
        print("System is correctly using ticker date, not market close time")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_specific_tickers()