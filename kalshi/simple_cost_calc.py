#!/usr/bin/env python3
"""
Simple calculation of total money spent from fills data
"""

import json
import os

def calculate_total_spent():
    """Calculate total money spent from all fills."""
    filename = "data/fills_with_resolutions_current.json"
    
    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found!")
        return
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    fills = data.get('fills', [])
    
    print("=" * 80)
    print("SIMPLE COST CALCULATION")
    print("=" * 80)
    print(f"Processing {len(fills)} fills...")
    
    total_spent = 0
    closed_spent = 0
    open_spent = 0
    
    closed_positions = []
    open_positions = []
    
    for fill in fills:
        ticker = fill.get('ticker', 'Unknown')
        side = fill.get('side', 'yes')
        action = fill.get('action', 'buy')
        count = fill.get('count', 0)
        yes_price = fill.get('yes_price', 0)
        no_price = fill.get('no_price', 0)
        market_status = fill.get('market_status', 'unknown')
        
        # Calculate cost for this fill
        if side == 'yes':
            price_cents = yes_price
        else:
            price_cents = no_price
        
        # Convert to dollars
        cost_dollars = (count * price_cents) / 100
        
        # Only count buys as money spent (sells give money back)
        if action == 'buy':
            total_spent += cost_dollars
            
            # Categorize as closed or open
            status_lower = market_status.lower() if market_status else ''
            if status_lower in ['closed', 'finalized', 'settled']:
                closed_spent += cost_dollars
                closed_positions.append({
                    'ticker': ticker,
                    'cost': cost_dollars,
                    'result': fill.get('market_result', 'unknown')
                })
            else:
                open_spent += cost_dollars
                open_positions.append({
                    'ticker': ticker,
                    'cost': cost_dollars
                })
        else:
            # This is a sell - money came back
            total_spent -= cost_dollars
            print(f"   SELL detected: {ticker} - ${cost_dollars:.2f} received back")
    
    print(f"\nTOTAL MONEY SPENT BREAKDOWN:")
    print(f"   Closed positions:    ${closed_spent:>10,.2f}")
    print(f"   Open positions:      ${open_spent:>10,.2f}")
    print(f"   " + "-" * 40)
    print(f"   TOTAL SPENT:         ${total_spent:>10,.2f}")
    
    print(f"\nCLOSED POSITIONS ({len(closed_positions)} markets):")
    # Group by ticker since there can be multiple fills per market
    closed_by_ticker = {}
    for pos in closed_positions:
        ticker = pos['ticker']
        if ticker not in closed_by_ticker:
            closed_by_ticker[ticker] = {'cost': 0, 'result': pos['result']}
        closed_by_ticker[ticker]['cost'] += pos['cost']
    
    sorted_closed = sorted(closed_by_ticker.items(), key=lambda x: x[1]['cost'], reverse=True)
    for ticker, data in sorted_closed:
        print(f"   {ticker[:50]:<50} | ${data['cost']:>8.2f} | {data['result']}")
    
    print(f"\nOPEN POSITIONS ({len(set(p['ticker'] for p in open_positions))} markets):")
    # Group by ticker
    open_by_ticker = {}
    for pos in open_positions:
        ticker = pos['ticker']
        if ticker not in open_by_ticker:
            open_by_ticker[ticker] = 0
        open_by_ticker[ticker] += pos['cost']
    
    sorted_open = sorted(open_by_ticker.items(), key=lambda x: x[1], reverse=True)
    for ticker, cost in sorted_open:
        print(f"   {ticker[:50]:<50} | ${cost:>8.2f}")
    
    return {
        'total_spent': total_spent,
        'closed_spent': closed_spent,
        'open_spent': open_spent
    }

if __name__ == "__main__":
    result = calculate_total_spent()
    if result:
        print(f"\n" + "=" * 80)
        print(f"FINAL SUMMARY:")
        print(f"   You spent ${result['total_spent']:,.2f} total on positions")
        print(f"   Current balance + Spent = Your deposits")
        print(f"   $9,818.85 + ${result['total_spent']:,.2f} = ${9818.85 + result['total_spent']:,.2f}")
        print(f"=" * 80)