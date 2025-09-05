#!/usr/bin/env python3
"""
Test UFC search with the correct ticker pattern
"""

import sys
import os
import requests
from datetime import datetime, timezone
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.kalshi_client import KalshiClientUpdated as KalshiClient

def test_ufc_search():
    """Test UFC search with various ticker patterns"""
    
    print("TESTING UFC SEARCH ON KALSHI")
    print("=" * 60)
    print(f"Looking for: KXUFCFIGHT-25AUG23ORTSTE (specific fight from URL)")
    print(f"Current time: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(project_root, 'keys', 'kalshi_credentials.txt')
        client = KalshiClient(creds_path)
        
        # Test various UFC ticker patterns
        ufc_patterns = [
            'KXUFCFIGHT',    # From the URL you provided
            'KXUFCEVENT',    # Alternative pattern
            'KXUFCGAME',     # What I tested before
            'KXMMA',         # MMA alternative
            'KXMMAFIGHT',    # MMA Fight
            'KXMMAEVENT',    # MMA Event
            'KXFIGHT',       # Generic Fight
        ]
        
        found_patterns = []
        
        for pattern in ufc_patterns:
            print(f"Testing ticker pattern: {pattern}")
            
            try:
                url = f"{client.base_url}/markets"
                params = {'series_ticker': pattern}
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    markets = data.get('markets', [])
                    
                    if len(markets) > 0:
                        print(f"  SUCCESS: Found {len(markets)} markets")
                        found_patterns.append({'pattern': pattern, 'markets': markets})
                        
                        # Show examples
                        for i, market in enumerate(markets[:5], 1):
                            ticker = market.get('ticker', '')
                            title = market.get('title', '')
                            status = market.get('status', 'unknown')
                            print(f"    {i}. {ticker} - {title} ({status})")
                        
                        if len(markets) > 5:
                            print(f"    ... and {len(markets) - 5} more")
                        
                        # Look for the specific fight: ORTSTE
                        specific_fight = [m for m in markets if 'ORTSTE' in m.get('ticker', '')]
                        if specific_fight:
                            print(f"    FOUND SPECIFIC FIGHT:")
                            for fight in specific_fight:
                                print(f"      {fight.get('ticker')} - {fight.get('title')}")
                        
                    else:
                        print(f"  No markets found")
                else:
                    print(f"  HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ERROR: {e}")
            
            print()
        
        # Summary
        print("=" * 60)
        print("UFC/MMA SEARCH RESULTS:")
        print("=" * 60)
        
        if found_patterns:
            print(f"FOUND {len(found_patterns)} UFC/MMA ticker patterns:")
            
            for result in found_patterns:
                pattern = result['pattern']
                markets = result['markets']
                print(f"\n[+] {pattern}: {len(markets)} markets")
                
                # Show a few recent examples
                recent_markets = [m for m in markets if 'AUG23' in m.get('ticker', '')][:3]
                for market in recent_markets:
                    ticker = market.get('ticker', '')
                    title = market.get('title', '')
                    print(f"    {ticker} - {title}")
                
                if not recent_markets and markets:
                    # Show any examples if no recent ones
                    for market in markets[:2]:
                        ticker = market.get('ticker', '')
                        title = market.get('title', '')
                        print(f"    {ticker} - {title}")
        else:
            print("No UFC/MMA markets found with any tested patterns")
            print("UFC/MMA may not be available on Kalshi or use different patterns")
        
        return found_patterns
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    test_ufc_search()