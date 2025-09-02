"""
Get ALL Kalshi markets using cursor pagination
"""

import requests
import json
from datetime import datetime, timezone

def fetch_all_markets_with_pagination():
    """Use cursor pagination to get every single market"""
    base_url = "https://api.elections.kalshi.com/trade-api/v2"
    
    all_markets = []
    cursor = None
    page = 1
    
    print("FETCHING ALL KALSHI MARKETS WITH PAGINATION")
    print("=" * 60)
    
    while True:
        print(f"\nPage {page}:")
        
        try:
            url = f"{base_url}/markets"
            params = {'limit': 1000}  # Maximum reasonable limit
            if cursor:
                params['cursor'] = cursor
            
            print(f"  Requesting up to 1000 markets...")
            response = requests.get(url, params=params, timeout=60)
            
            if response.status_code != 200:
                print(f"  Error {response.status_code}: {response.text[:200]}")
                break
            
            data = response.json()
            markets = data.get('markets', [])
            new_cursor = data.get('cursor', '')
            
            print(f"  Received: {len(markets)} markets")
            print(f"  New cursor: {new_cursor[:50]}..." if new_cursor else "  No cursor")
            
            all_markets.extend(markets)
            
            # Check if we're done
            if not new_cursor or new_cursor == cursor or len(markets) == 0:
                print(f"  No more pages - finished!")
                break
            
            cursor = new_cursor
            page += 1
            
            # Safety limit
            if page > 20:
                print(f"  Safety limit reached (20 pages)")
                break
                
        except Exception as e:
            print(f"  Exception: {e}")
            break
    
    print(f"\nTOTAL MARKETS FOUND: {len(all_markets)}")
    return all_markets

def find_a_vs_minnesota_game(markets):
    """Specifically look for A's vs Minnesota pattern"""
    print(f"\nSPECIFIC SEARCH: A's @ Minnesota game (53%/47%)")
    print("=" * 60)
    
    potential_games = []
    
    for i, market in enumerate(markets):
        ticker = market.get('ticker', '').lower()
        title = market.get('title', '').lower()
        yes_bid = market.get('yes_bid', 0)
        no_bid = market.get('no_bid', 0)
        
        yes_pct = yes_bid / 100 if yes_bid else 0
        no_pct = no_bid / 100 if no_bid else 0
        
        # Look for Oakland/A's + Minnesota/Twins + 53%/47% pattern
        has_oakland = any(term in ticker or term in title for term in [
            'oakland', 'athletics', 'a\'s', 'ath'
        ])
        
        has_minnesota = any(term in ticker or term in title for term in [
            'minnesota', 'twins', 'min', 'twin'
        ])
        
        has_53_47_pattern = (
            (50 <= yes_pct*100 <= 56 and 44 <= no_pct*100 <= 50) or
            (44 <= yes_pct*100 <= 50 and 50 <= no_pct*100 <= 56)
        )
        
        # Score the match
        score = 0
        reasons = []
        
        if has_oakland:
            score += 10
            reasons.append("Oakland/A's")
        if has_minnesota:
            score += 10
            reasons.append("Minnesota/Twins")
        if has_53_47_pattern:
            score += 5
            reasons.append(f"53%/47% pattern ({yes_pct:.1%}/{no_pct:.1%})")
        
        # Look for any two-team pattern
        vs_pattern = 'vs' in title or ' v ' in title or ' at ' in title
        if vs_pattern:
            score += 2
            reasons.append("vs/at pattern")
        
        # Look for game/match/win language
        game_pattern = any(word in title for word in ['win', 'beat', 'game', 'match'])
        if game_pattern:
            score += 1
            reasons.append("game language")
        
        if score >= 3:  # Threshold for interesting markets
            potential_games.append({
                'index': i,
                'ticker': market.get('ticker'),
                'title': market.get('title'),
                'yes_pct': yes_pct,
                'no_pct': no_pct,
                'score': score,
                'reasons': reasons,
                'status': market.get('status')
            })
    
    # Sort by score
    potential_games.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"Found {len(potential_games)} potential matches:")
    for game in potential_games[:20]:  # Show top 20
        print(f"  Score {game['score']:2d}: {game['ticker']}")
        print(f"          {game['title']}")
        print(f"          {game['yes_pct']:.1%} / {game['no_pct']:.1%}")
        print(f"          Reasons: {', '.join(game['reasons'])}")
        print()
    
    return potential_games

def export_complete_search(markets, potential_games):
    """Export everything"""
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Complete data export
    with open('debug/complete_kalshi_search.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total_markets': len(markets),
            'potential_games_count': len(potential_games),
            'search_method': 'pagination_with_scoring',
            'markets': markets,
            'potential_a_minnesota_games': potential_games
        }, f, indent=2, default=str)
    
    # Human readable summary
    with open('debug/complete_kalshi_search_summary.txt', 'w', encoding='utf-8') as f:
        f.write(f"COMPLETE KALSHI MARKET SEARCH\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Total Markets: {len(markets)}\n")
        f.write(f"Potential A's @ Minnesota Games: {len(potential_games)}\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("TOP POTENTIAL MATCHES:\n")
        f.write("-" * 40 + "\n")
        for game in potential_games[:10]:
            f.write(f"Score {game['score']}: {game['ticker']}\n")
            f.write(f"  {game['title']}\n")
            f.write(f"  Prices: {game['yes_pct']:.1%} / {game['no_pct']:.1%}\n")
            f.write(f"  Reasons: {', '.join(game['reasons'])}\n")
            f.write(f"  Status: {game['status']}\n\n")
    
    print(f"\nEXPORTED:")
    print(f"  - debug/complete_kalshi_search.json")
    print(f"  - debug/complete_kalshi_search_summary.txt")

def main():
    """Main execution"""
    # Get all markets
    all_markets = fetch_all_markets_with_pagination()
    
    if not all_markets:
        print("Failed to fetch any markets")
        return
    
    # Search for A's @ Minnesota specifically
    potential_games = find_a_vs_minnesota_game(all_markets)
    
    # Export everything
    export_complete_search(all_markets, potential_games)
    
    print(f"\nCOMPLETE SEARCH RESULTS:")
    print(f"  Total Markets Found: {len(all_markets)}")
    print(f"  Potential A's @ Minnesota Games: {len(potential_games)}")
    print(f"  Best Match Score: {potential_games[0]['score'] if potential_games else 0}")

if __name__ == "__main__":
    main()