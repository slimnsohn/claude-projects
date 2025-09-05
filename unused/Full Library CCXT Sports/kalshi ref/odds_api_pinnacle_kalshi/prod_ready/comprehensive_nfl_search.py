#!/usr/bin/env python3
"""
Comprehensive search for NFL markets across all possible states
"""

import sys
import os
import requests
from datetime import datetime, timezone
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.kalshi_client import KalshiClientUpdated as KalshiClient

def comprehensive_nfl_search():
    """Search for NFL markets in all possible ways"""
    
    print("COMPREHENSIVE NFL MARKET SEARCH")
    print("=" * 60)
    print(f"Current time: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(project_root, 'keys', 'kalshi_credentials.txt')
        client = KalshiClient(creds_path)
        
        # Get a comprehensive view of all markets with different status
        print("COMPREHENSIVE SEARCH ACROSS ALL MARKET STATES...")
        
        all_found_nfl = []
        all_found_games = []
        
        # Try pagination with no status filter (gets all markets)
        print("\n1. Getting ALL markets via pagination (no filters)...")
        
        try:
            all_markets_result = client._get_all_markets_paginated()
            all_markets = all_markets_result.get('data', [])
            print(f"   Retrieved {len(all_markets)} total markets")
            
            # Search through all markets
            nfl_markets = []
            game_markets = []
            indcin_markets = []
            
            for market in all_markets:
                ticker = market.get('ticker', '')
                title = market.get('title', '').lower()
                
                # Look for NFL specifically
                if 'KXNFLGAME' in ticker.upper():
                    nfl_markets.append(market)
                    all_found_nfl.append(market)
                
                # Look for any games on Aug 23
                if 'GAME' in ticker.upper() and 'AUG23' in ticker.upper():
                    game_markets.append(market)
                    all_found_games.append(market)
                
                # Look for Indianapolis/Cincinnati
                if ('ind' in ticker.upper() and 'cin' in ticker.upper()) or \
                   ('indianapolis' in title and 'cincinnati' in title) or \
                   ('colts' in title and 'bengals' in title):
                    indcin_markets.append(market)
            
            print(f"   NFL markets found: {len(nfl_markets)}")
            print(f"   Aug 23 game markets: {len(game_markets)}")
            print(f"   Indy/Cincy markets: {len(indcin_markets)}")
            
            # Show what we found
            for market in nfl_markets:
                print(f"      NFL: {market.get('ticker')} - {market.get('title')} - {market.get('status', 'unknown')}")
                
            for market in indcin_markets:
                print(f"      IND/CIN: {market.get('ticker')} - {market.get('title')} - {market.get('status', 'unknown')}")
                
        except Exception as e:
            print(f"   Error with pagination: {e}")
        
        # Try direct API calls with different parameters
        print(f"\n2. Direct API calls with various parameters...")
        
        api_tests = [
            {'params': {}, 'desc': 'No parameters'},
            {'params': {'limit': 5000}, 'desc': 'High limit'},
            {'params': {'status': 'open'}, 'desc': 'Open markets'},
            {'params': {'status': 'closed'}, 'desc': 'Closed markets'},
            {'params': {'series_ticker': 'KXNFLGAME'}, 'desc': 'Series ticker'},
        ]
        
        for test in api_tests:
            try:
                print(f"   Testing: {test['desc']}")
                
                url = f"{client.base_url}/markets"
                response = requests.get(url, params=test['params'], timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    markets = data.get('markets', [])
                    
                    nfl_found = [m for m in markets if 'KXNFLGAME' in m.get('ticker', '')]
                    
                    print(f"      Status 200: {len(markets)} markets, {len(nfl_found)} NFL")
                    
                    for nfl in nfl_found:
                        print(f"        FOUND: {nfl.get('ticker')} - {nfl.get('status', 'unknown')}")
                        all_found_nfl.append(nfl)
                else:
                    print(f"      Status {response.status_code}")
                    
            except Exception as e:
                print(f"      Error: {e}")
        
        # Try the events endpoint
        print(f"\n3. Testing events endpoint...")
        
        try:
            url = f"{client.base_url}/events"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                print(f"   Found {len(events)} events")
                
                # Look for NFL/football events
                for event in events:
                    ticker = event.get('series_ticker', '')
                    title = event.get('title', '')
                    
                    if 'nfl' in ticker.lower() or 'football' in title.lower():
                        print(f"      EVENT: {ticker} - {title}")
                        
            else:
                print(f"   Events endpoint returned {response.status_code}")
                
        except Exception as e:
            print(f"   Events endpoint error: {e}")
        
        # Summary
        print(f"\n" + "="*60)
        print("FINAL SUMMARY:")
        print(f"Total unique NFL markets found: {len(set(m.get('ticker') for m in all_found_nfl))}")
        
        if not all_found_nfl:
            print("\nPOSSIBLE REASONS NFL MARKETS NOT FOUND:")
            print("1. Markets may only be available during specific time windows")
            print("2. NFL markets may require special access/permissions")
            print("3. Markets may be in a different API endpoint not yet tested")
            print("4. The specific market may have been created after our data snapshot")
            print("5. API may have rate limiting affecting market visibility")
            
        print(f"\nRECOMMENDATION:")
        print("Since the market exists at the URL you provided, the issue is likely:")
        print("- Timing: Market appears/disappears at certain times")
        print("- API endpoint: Different endpoint needed for active NFL games")
        print("- Authentication: May need user login to see all markets")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    comprehensive_nfl_search()