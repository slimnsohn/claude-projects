#!/usr/bin/env python3
"""
Calculate P&L from fills data
"""

import json
import os
from collections import defaultdict

def calculate_pnl():
    """Calculate P&L from current fills data."""
    filename = "data/fills_with_resolutions_current.json"
    
    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found! Run get_fills.py first.")
        return None
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    fills = data.get('fills', [])
    
    # Group by market ticker for position-level P&L
    events = defaultdict(lambda: {
        'ticker': '',
        'total_cost': 0,
        'total_payout': 0,
        'net_pnl': 0,
        'trades_count': 0,
        'status': 'unknown',
        'result': ''
    })
    
    total_spent = 0
    total_received = 0
    
    for fill in fills:
        ticker = fill.get('ticker', 'Unknown')
        side = fill.get('side', 'yes')
        action = fill.get('action', 'buy')
        count = fill.get('count', 0)
        yes_price = fill.get('yes_price', 0)
        no_price = fill.get('no_price', 0)
        market_status = fill.get('market_status', 'unknown')
        market_result = fill.get('market_result', '')
        
        event = events[ticker]
        event['ticker'] = ticker
        event['status'] = market_status
        event['result'] = market_result
        event['trades_count'] += 1
        
        # Calculate cost
        if side == 'yes':
            price_per_share = yes_price / 100
        else:
            price_per_share = no_price / 100
        
        cost = count * price_per_share
        
        if action == 'buy':
            event['total_cost'] += cost
            total_spent += cost
        else:  # sell
            event['total_cost'] -= cost
            total_spent -= cost
        
        # Calculate payout if resolved
        status_lower = market_status.lower() if market_status else ''
        is_resolved = status_lower in ['closed', 'finalized', 'settled']
        
        if is_resolved:
            # Handle ties (blank result) as 50¢ payout
            if market_result == 'yes':
                yes_payout = 1.00
                no_payout = 0.00
            elif market_result == 'no':
                yes_payout = 0.00
                no_payout = 1.00
            else:
                yes_payout = 0.50
                no_payout = 0.50
            
            if action == 'buy':
                if side == 'yes':
                    payout = count * yes_payout
                else:
                    payout = count * no_payout
            else:  # sell
                if side == 'yes':
                    payout = -count * yes_payout
                else:
                    payout = -count * no_payout
            
            event['total_payout'] += payout
            total_received += payout
    
    # Calculate net P&L for each event
    for ticker, event in events.items():
        event['net_pnl'] = event['total_payout'] - event['total_cost']
    
    # Separate resolved and open events
    resolved_events = {k: v for k, v in events.items() if v['status'].lower() in ['closed', 'finalized', 'settled']}
    open_events = {k: v for k, v in events.items() if v['status'].lower() not in ['closed', 'finalized', 'settled']}
    
    result = {
        'total_events': len(events),
        'resolved_events': len(resolved_events),
        'open_events': len(open_events),
        'total_spent': total_spent,
        'total_received': total_received,
        'net_trading_pnl': total_received - total_spent,
        'resolved_events_data': resolved_events,
        'open_events_data': open_events
    }
    
    return result

if __name__ == "__main__":
    result = calculate_pnl()
    if result:
        print(f"Total Events: {result['total_events']}")
        print(f"Resolved: {result['resolved_events']} | Open: {result['open_events']}")
        print(f"Total Spent: ${result['total_spent']:,.2f}")
        print(f"Total Received: ${result['total_received']:,.2f}")
        print(f"Net P&L: ${result['net_trading_pnl']:,.2f}")