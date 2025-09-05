#!/usr/bin/env python3
"""
Research all available sports ticker patterns on Kalshi
"""

import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.kalshi_client import KalshiClientUpdated as KalshiClient

def research_sports_tickers():
    """Research all available sports ticker patterns"""
    
    print("RESEARCHING ALL SPORTS TICKER PATTERNS ON KALSHI")
    print("=" * 70)
    
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(project_root, 'keys', 'kalshi_credentials.txt')
        client = KalshiClient(creds_path)
        
        # Known patterns to test
        potential_tickers = [
            # Already confirmed
            'KXNFLGAME',      # NFL (confirmed working)
            'KXMLBGAME',      # MLB (confirmed working) 
            'KXWNBAGAME',     # WNBA (confirmed working)
            
            # Likely patterns for major sports
            'KXNBAGAME',      # NBA - pro basketball
            'KXNHLGAME',      # NHL - pro hockey
            
            # College sports patterns
            'KXNCAAFGAME',    # NCAA Football
            'KXNCAABGAME',    # NCAA Basketball
            'KXCOLLEGEFOOTBALL', # College Football alternative
            'KXCOLLEGEBASKETBALL', # College Basketball alternative
            
            # Combat sports
            'KXUFCGAME',      # UFC
            'KXUFCEVENT',     # UFC Event
            'KXMMAGAME',      # MMA
            'KXMMAEVENT',     # MMA Event
            'KXFIGHTGAME',    # Fight Game
            'KXBOXINGGAME',   # Boxing
            
            # Other sports variations
            'KXSOCCERGAME',   # Soccer
            'KXFOOTBALLGAME', # Football (could be soccer or American)
            'KXBASKETBALLGAME', # Basketball
            'KXBASEBALLGAME', # Baseball
            'KXHOCKEYGAME',   # Hockey
            'KXTENNISGAME',   # Tennis
            
            # European soccer leagues (we saw these earlier)
            'KXBUNDESLIGAGAME', # German Bundesliga
            'KXLALIGAGAME',     # Spanish La Liga  
            'KXEPLGAME',        # English Premier League
            'KXSERIEAGAME',     # Italian Serie A
            'KXLIGUE1GAME',     # French Ligue 1
        ]
        
        found_patterns = []
        
        for ticker_pattern in potential_tickers:
            print(f"Testing: {ticker_pattern}")
            
            try:
                url = f"{client.base_url}/markets"
                params = {'series_ticker': ticker_pattern}
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    markets = data.get('markets', [])
                    
                    if len(markets) > 0:
                        print(f"  SUCCESS: {len(markets)} markets")
                        
                        # Show a few examples
                        for i, market in enumerate(markets[:3], 1):
                            ticker = market.get('ticker', '')
                            title = market.get('title', '')
                            status = market.get('status', 'unknown')
                            print(f"    {i}. {ticker} - {title} ({status})")
                        
                        if len(markets) > 3:
                            print(f"    ... and {len(markets) - 3} more")
                        
                        found_patterns.append({
                            'pattern': ticker_pattern,
                            'count': len(markets),
                            'examples': markets[:3]
                        })
                    else:
                        print(f"  NONE: No markets found")
                        
                else:
                    print(f"  HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ERROR: {e}")
            
            print()
        
        # Summary
        print("="*70)
        print("SUMMARY OF FOUND SPORTS PATTERNS:")
        print("="*70)
        
        major_sports = {
            'KXNFLGAME': 'NFL (Professional American Football)',
            'KXMLBGAME': 'MLB (Major League Baseball)', 
            'KXNBAGAME': 'NBA (Professional Basketball)',
            'KXNHLGAME': 'NHL (Professional Hockey)',
            'KXWNBAGAME': 'WNBA (Women\'s Professional Basketball)',
            'KXNCAAFGAME': 'NCAA Football (College Football)',
            'KXNCAABGAME': 'NCAA Basketball (College Basketball)',
            'KXUFCGAME': 'UFC (Mixed Martial Arts)',
            'KXUFCEVENT': 'UFC Events',
            'KXMMAGAME': 'MMA (Mixed Martial Arts)'
        }
        
        print("\nMAJOR US SPORTS AVAILABILITY:")
        for pattern in found_patterns:
            ticker = pattern['pattern']
            count = pattern['count']
            
            if ticker in major_sports:
                sport_name = major_sports[ticker]
                print(f"[+] {ticker:<15} ({count:3d} markets) - {sport_name}")
        
        print("\nOTHER SPORTS FOUND:")
        for pattern in found_patterns:
            ticker = pattern['pattern']
            count = pattern['count']
            
            if ticker not in major_sports:
                print(f"[*] {ticker:<15} ({count:3d} markets)")
        
        print("\nNOT FOUND (may not exist or use different patterns):")
        for ticker_pattern in potential_tickers:
            if not any(p['pattern'] == ticker_pattern for p in found_patterns):
                expected_sport = major_sports.get(ticker_pattern, 'Unknown')
                print(f"[-] {ticker_pattern:<15} - {expected_sport}")
        
        print(f"\nTOTAL SPORTS PATTERNS FOUND: {len(found_patterns)}")
        
        return found_patterns
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    research_sports_tickers()