"""
All Kalshi Markets with Actual Prices (Bid/Ask Data)
Generated to help find the A's @ Minnesota game mentioned
"""

import json

# Load the market data
with open('all_kalshi_markets.json', 'r') as f:
    data = json.load(f)

print(f"ALL KALSHI MARKETS WITH PRICING DATA")
print(f"Total Markets: {len(data['markets'])}")
print(f"Timestamp: {data['timestamp']}")
print("=" * 100)

potential_matches = []

for i, market in enumerate(data['markets'], 1):
    ticker = market.get('ticker', 'NO_TICKER')
    title = market.get('title', 'NO_TITLE')
    
    # Get pricing data
    yes_bid = market.get('yes_bid', 0)
    yes_ask = market.get('yes_ask', 0)
    no_bid = market.get('no_bid', 0)
    no_ask = market.get('no_ask', 0)
    
    # Calculate percentages (prices are in cents, so divide by 100 for %)
    yes_bid_pct = yes_bid / 100 if yes_bid else 0
    yes_ask_pct = yes_ask / 100 if yes_ask else 0
    no_bid_pct = no_bid / 100 if no_bid else 0
    no_ask_pct = no_ask / 100 if no_ask else 0
    
    # Calculate mid prices for comparison
    yes_mid = (yes_bid_pct + yes_ask_pct) / 2 if yes_bid_pct and yes_ask_pct else 0
    no_mid = (no_bid_pct + no_ask_pct) / 2 if no_bid_pct and no_ask_pct else 0
    
    status = market.get('status', 'unknown')
    close_time = market.get('close_time', 'unknown')
    
    print(f"\nMARKET {i:3d}: {ticker}")
    print(f"  Title: {title}")
    print(f"  Status: {status}")
    print(f"  Close: {close_time}")
    print(f"  YES: Bid {yes_bid_pct:.1%} | Ask {yes_ask_pct:.1%} | Mid {yes_mid:.1%}")
    print(f"  NO:  Bid {no_bid_pct:.1%} | Ask {no_ask_pct:.1%} | Mid {no_mid:.1%}")
    
    # Flag any markets that might match the 53%/47% Oakland/Minnesota description
    if (40 <= yes_mid*100 <= 60) or (40 <= no_mid*100 <= 60):
        potential_matches.append({
            'market_num': i,
            'ticker': ticker,
            'title': title,
            'yes_mid': yes_mid,
            'no_mid': no_mid
        })
        print(f"  *** POTENTIAL MATCH: Close to 47%/53% split ***")
    
    print("-" * 100)

print(f"\n" + "="*100)
print(f"SUMMARY: POTENTIAL MATCHES FOR 53% OAKLAND / 47% MINNESOTA GAME")
print(f"="*100)

if potential_matches:
    print(f"Found {len(potential_matches)} markets with pricing around 47%-53%:")
    for match in potential_matches:
        print(f"  {match['market_num']:3d}. {match['ticker']}")
        print(f"       {match['title']}")
        print(f"       Yes: {match['yes_mid']:.1%} | No: {match['no_mid']:.1%}")
        print()
else:
    print("No markets found with pricing close to 47%/53% split")

print("\nNOTE: Looking for baseball-related terms in these potential matches...")
baseball_terms = ['baseball', 'mlb', 'athletic', 'twin', 'minnesota', 'oakland', 'a\'s']
for match in potential_matches:
    title_lower = match['title'].lower()
    ticker_lower = match['ticker'].lower()
    
    found_terms = [term for term in baseball_terms if term in title_lower or term in ticker_lower]
    if found_terms:
        print(f"BASEBALL MATCH: {match['ticker']} contains terms: {found_terms}")