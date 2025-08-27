#!/usr/bin/env python3
"""
Test direct access to NFL markets using different approaches
"""

import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.kalshi_client import KalshiClientUpdated as KalshiClient

def test_direct_nfl_access():
    """Test different ways to access NFL markets"""
    
    print("TESTING DIRECT NFL MARKET ACCESS")
    print("=" * 60)
    
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(project_root, 'keys', 'kalshi_credentials.txt')
        client = KalshiClient(creds_path)
        
        # Test 1: Try different pagination limits
        print("TEST 1: Trying different pagination parameters...")
        
        for limit in [100, 500, 1000]:
            print(f"  Testing with limit={limit}...")
            
            url = f"{client.base_url}/markets"
            params = {'limit': limit, 'status': 'active'}
            
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                markets = data.get('markets', [])
                
                # Look for NFL in this batch
                nfl_found = [m for m in markets if 'KXNFLGAME' in m.get('ticker', '')]
                print(f"    Retrieved {len(markets)} markets, found {len(nfl_found)} NFL markets")
                
                for nfl_market in nfl_found:
                    print(f"      {nfl_market.get('ticker')} - {nfl_market.get('title')}")
                    
            except Exception as e:
                print(f"    Error with limit {limit}: {e}")
        
        # Test 2: Try searching with different status filters
        print(f"\nTEST 2: Trying different market status filters...")
        
        for status in ['active', 'closed', 'settled', None]:
            print(f"  Testing with status={status}...")
            
            url = f"{client.base_url}/markets"
            params = {'limit': 1000}
            if status:
                params['status'] = status
            
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                markets = data.get('markets', [])
                
                # Look for NFL in this batch
                nfl_found = [m for m in markets if 'KXNFLGAME' in m.get('ticker', '')]
                aug23_found = [m for m in markets if 'AUG23' in m.get('ticker', '')]
                
                print(f"    Retrieved {len(markets)} markets")
                print(f"    NFL markets: {len(nfl_found)}")
                print(f"    Aug 23 markets: {len(aug23_found)}")
                
                for nfl_market in nfl_found[:3]:  # Show first 3
                    print(f"      {nfl_market.get('ticker')} - {nfl_market.get('title')}")
                    
            except Exception as e:
                print(f"    Error with status {status}: {e}")
        
        # Test 3: Try searching by category
        print(f"\nTEST 3: Trying category-based search...")
        
        categories = ['sports', 'football', 'nfl']
        for category in categories:
            print(f"  Testing category={category}...")
            
            url = f"{client.base_url}/markets"
            params = {'limit': 1000, 'category': category}
            
            try:
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    markets = data.get('markets', [])
                    nfl_found = [m for m in markets if 'KXNFLGAME' in m.get('ticker', '')]
                    print(f"    Retrieved {len(markets)} markets, found {len(nfl_found)} NFL markets")
                else:
                    print(f"    Category {category} returned status {response.status_code}")
                    
            except Exception as e:
                print(f"    Error with category {category}: {e}")
        
        # Test 4: Try a direct search for the ticker
        print(f"\nTEST 4: Try searching for specific ticker pattern...")
        
        search_terms = ['KXNFLGAME', 'INDCIN', 'indianapolis', 'cincinnati']
        for term in search_terms:
            print(f"  Searching for '{term}'...")
            
            url = f"{client.base_url}/markets"
            params = {'limit': 1000, 'search': term}
            
            try:
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    markets = data.get('markets', [])
                    print(f"    Search for '{term}' returned {len(markets)} markets")
                    
                    # Show any interesting results
                    for market in markets[:5]:
                        ticker = market.get('ticker', '')
                        title = market.get('title', '')
                        if 'nfl' in ticker.lower() or 'nfl' in title.lower() or \
                           'football' in title.lower() or 'game' in ticker.lower():
                            print(f"      {ticker} - {title}")
                else:
                    print(f"    Search failed with status {response.status_code}")
                    
            except Exception as e:
                print(f"    Error searching for {term}: {e}")
        
        print(f"\nCONCLUSION:")
        print("Testing different API access methods to find NFL markets")
        print("If no NFL markets found, they may be in a different API section")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_nfl_access()