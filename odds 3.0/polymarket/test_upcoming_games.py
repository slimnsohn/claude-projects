"""
Test to find truly upcoming/open NFL games on Polymarket
Check for markets that are active AND not closed
"""

import requests
from datetime import datetime, timedelta

def find_upcoming_nfl():
    """Look for upcoming NFL markets that are truly active"""
    
    base_url = "https://clob.polymarket.com"
    
    print("=== SEARCHING FOR UPCOMING NFL MARKETS ===")
    
    # Test with different status combinations
    status_tests = [
        {'closed': 'false'},
        {'active': 'true', 'closed': 'false'},
        {},  # No filters
    ]
    
    for test in status_tests:
        print(f"\nTesting with params: {test}")
        
        try:
            response = requests.get(f"{base_url}/markets", params={'limit': 1000, **test}, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                markets = data.get('data', [])
                
                print(f"  Total markets returned: {len(markets)}")
                
                # Look for truly open markets (active AND not closed)
                open_markets = []
                nfl_open = []
                
                for market in markets:
                    active = market.get('active', False)
                    closed = market.get('closed', True)
                    question = market.get('question', '').lower()
                    
                    # Check if truly open
                    if active and not closed:
                        open_markets.append(market)
                        
                        # Check if NFL
                        if ('nfl' in question or 'football' in question or 
                            any(team in question for team in ['chiefs', 'ravens', 'bills', 'cowboys', 'patriots'])):
                            nfl_open.append(market)
                
                print(f"  Truly open markets (active AND not closed): {len(open_markets)}")
                print(f"  Open NFL markets: {len(nfl_open)}")
                
                # Show first few open markets
                if open_markets:
                    print("  First few open markets:")
                    for market in open_markets[:5]:
                        print(f"    - {market.get('question')}")
                
                # Show NFL markets if any
                if nfl_open:
                    print("  Open NFL markets:")
                    for market in nfl_open:
                        print(f"    - {market.get('question')}")
                        
        except Exception as e:
            print(f"  Error: {e}")
    
    # Also check upcoming dates
    print(f"\n=== CHECKING FOR UPCOMING GAME DATES ===")
    
    # Try different date patterns for upcoming NFL games
    upcoming_dates = []
    today = datetime.now()
    
    # Get next few Sundays (typical NFL game days)
    for i in range(1, 8):  # Next 7 days
        date = today + timedelta(days=i)
        if date.weekday() == 6:  # Sunday
            upcoming_dates.append(date.strftime('%Y-%m-%d'))
    
    # Also add next Saturday and Monday (common NFL days)
    for i in range(1, 15):
        date = today + timedelta(days=i)
        if date.weekday() in [5, 0]:  # Saturday or Monday
            upcoming_dates.append(date.strftime('%Y-%m-%d'))
    
    print(f"Checking these upcoming dates: {upcoming_dates[:5]}")
    
    for date in upcoming_dates[:3]:  # Test first 3 dates
        # Try various event slug patterns
        event_patterns = [
            f"nfl-{date}",
            f"nfl-week-{date}",
            f"nfl-games-{date}",
        ]
        
        for pattern in event_patterns:
            try:
                params = {'event': pattern}
                response = requests.get(f"{base_url}/markets", params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    count = data.get('count', 0)
                    
                    if count > 0:
                        print(f"  Found {count} markets for event '{pattern}'")
                        
                        markets = data.get('data', [])[:3]  # First 3
                        for market in markets:
                            active = market.get('active', False)
                            closed = market.get('closed', True) 
                            question = market.get('question', '')
                            print(f"    - {question} (Active: {active}, Closed: {closed})")
                            
            except Exception as e:
                continue  # Skip errors

if __name__ == "__main__":
    find_upcoming_nfl()