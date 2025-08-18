#!/usr/bin/env python3
"""
Script to analyze positions from fills_with_resolutions_current.json
Shows position summary, open vs closed positions, and P&L analysis.
"""

import json
import os
from datetime import datetime
from collections import defaultdict

def load_fills_data():
    """Load the current fills data."""
    filename = "data/fills_with_resolutions_current.json"
    
    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found!")
        print("Run get_fills_with_resolutions.py first to generate the data.")
        return None
    
    with open(filename, 'r') as f:
        return json.load(f)

def analyze_positions():
    """Analyze all positions from fills data."""
    data = load_fills_data()
    if not data:
        return
    
    fills = data.get('fills', [])
    
    print("=" * 80)
    print("POSITION ANALYSIS")
    print("=" * 80)
    print(f"Data retrieved: {data.get('retrieved_at', 'Unknown')}")
    print(f"Total fills: {len(fills)}")
    
    # Group fills by ticker to calculate net positions
    positions = defaultdict(lambda: {
        'ticker': '',
        'total_bought_yes': 0,
        'total_sold_yes': 0,
        'total_bought_no': 0,
        'total_sold_no': 0,
        'total_cost_yes': 0,
        'total_cost_no': 0,
        'net_position_yes': 0,
        'net_position_no': 0,
        'status': 'unknown',
        'result': None,
        'last_price': None,
        'pnl_cents': 0,
        'pnl_dollars': 0,
        'fills_count': 0,
        'first_trade': None,
        'last_trade': None
    })
    
    # Process each fill
    for fill in fills:
        ticker = fill.get('ticker', 'Unknown')
        side = fill.get('side', 'yes')
        action = fill.get('action', 'buy')
        count = fill.get('count', 0)
        yes_price = fill.get('yes_price', 0)
        no_price = fill.get('no_price', 0)
        created_time = fill.get('created_time', '')
        
        pos = positions[ticker]
        pos['ticker'] = ticker
        pos['fills_count'] += 1
        pos['status'] = fill.get('market_status', 'unknown')
        pos['result'] = fill.get('market_result')
        pos['last_price'] = fill.get('final_price')
        
        # Track first and last trade times
        if not pos['first_trade'] or created_time < pos['first_trade']:
            pos['first_trade'] = created_time
        if not pos['last_trade'] or created_time > pos['last_trade']:
            pos['last_trade'] = created_time
        
        # Update position based on side and action
        if side == 'yes':
            if action == 'buy':
                pos['total_bought_yes'] += count
                pos['total_cost_yes'] += count * yes_price
            else:  # sell
                pos['total_sold_yes'] += count
                pos['total_cost_yes'] -= count * yes_price
        else:  # no side
            if action == 'buy':
                pos['total_bought_no'] += count
                pos['total_cost_no'] += count * no_price
            else:  # sell
                pos['total_sold_no'] += count
                pos['total_cost_no'] -= count * no_price
    
    # Calculate net positions and P&L
    for ticker, pos in positions.items():
        pos['net_position_yes'] = pos['total_bought_yes'] - pos['total_sold_yes']
        pos['net_position_no'] = pos['total_bought_no'] - pos['total_sold_no']
        
        # Calculate P&L if market is resolved
        if pos['status'] == 'closed' and pos['result'] is not None:
            if pos['result'] == 'yes':
                final_value_yes = 100
                final_value_no = 0
            else:
                final_value_yes = 0
                final_value_no = 100
            
            # P&L from yes positions
            if pos['net_position_yes'] != 0:
                avg_cost_yes = pos['total_cost_yes'] / pos['total_bought_yes'] if pos['total_bought_yes'] > 0 else 0
                pnl_yes = pos['net_position_yes'] * (final_value_yes - avg_cost_yes)
                pos['pnl_cents'] += pnl_yes
            
            # P&L from no positions
            if pos['net_position_no'] != 0:
                avg_cost_no = pos['total_cost_no'] / pos['total_bought_no'] if pos['total_bought_no'] > 0 else 0
                pnl_no = pos['net_position_no'] * (final_value_no - avg_cost_no)
                pos['pnl_cents'] += pnl_no
            
            pos['pnl_dollars'] = pos['pnl_cents'] / 100
    
    # Separate open and closed positions
    open_positions = {k: v for k, v in positions.items() if v['status'] != 'closed'}
    closed_positions = {k: v for k, v in positions.items() if v['status'] == 'closed'}
    
    # Calculate statistics
    total_positions = len(positions)
    total_open = len(open_positions)
    total_closed = len(closed_positions)
    total_pnl_closed = sum(pos['pnl_dollars'] for pos in closed_positions.values())
    
    print(f"\nPOSITION SUMMARY")
    print(f"   Total unique positions: {total_positions}")
    print(f"   Open positions: {total_open}")
    print(f"   Closed positions: {total_closed}")
    print(f"   Total P&L from closed: ${total_pnl_closed:.2f}")
    
    # Show closed positions with P&L
    if closed_positions:
        print(f"\nCLOSED POSITIONS (P&L)")
        print("   " + "="*76)
        sorted_closed = sorted(closed_positions.items(), key=lambda x: x[1]['pnl_dollars'], reverse=True)
        
        for ticker, pos in sorted_closed:
            result_icon = "WIN" if pos['result'] == 'yes' else "LOSE"
            pnl_icon = "+" if pos['pnl_dollars'] > 0 else "-" if pos['pnl_dollars'] < 0 else "="
            
            net_yes = pos['net_position_yes']
            net_no = pos['net_position_no']
            position_str = ""
            if net_yes > 0:
                avg_cost = pos['total_cost_yes'] / pos['total_bought_yes'] if pos['total_bought_yes'] > 0 else 0
                position_str = f"{net_yes} YES @ ${avg_cost/100:.2f}"
            if net_no > 0:
                avg_cost = pos['total_cost_no'] / pos['total_bought_no'] if pos['total_bought_no'] > 0 else 0
                if position_str:
                    position_str += f", {net_no} NO @ ${avg_cost/100:.2f}"
                else:
                    position_str = f"{net_no} NO @ ${avg_cost/100:.2f}"
            
            print(f"   {pnl_icon} {ticker[:45]:<45} | {position_str[:20]:<20} | {result_icon} {pos['result']:<3} | ${pos['pnl_dollars']:>8.2f}")
    
    # Show top open positions
    if open_positions:
        print(f"\nTOP OPEN POSITIONS")
        print("   " + "="*76)
        
        # Calculate position value for sorting
        open_with_value = []
        for ticker, pos in open_positions.items():
            total_value = 0
            if pos['net_position_yes'] > 0:
                avg_cost = pos['total_cost_yes'] / pos['total_bought_yes'] if pos['total_bought_yes'] > 0 else 0
                total_value += pos['net_position_yes'] * avg_cost / 100
            if pos['net_position_no'] > 0:
                avg_cost = pos['total_cost_no'] / pos['total_bought_no'] if pos['total_bought_no'] > 0 else 0
                total_value += pos['net_position_no'] * avg_cost / 100
            open_with_value.append((ticker, pos, total_value))
        
        # Sort by total value
        open_with_value.sort(key=lambda x: x[2], reverse=True)
        
        for i, (ticker, pos, value) in enumerate(open_with_value[:15], 1):
            net_yes = pos['net_position_yes']
            net_no = pos['net_position_no']
            position_str = ""
            
            if net_yes > 0:
                avg_cost = pos['total_cost_yes'] / pos['total_bought_yes'] if pos['total_bought_yes'] > 0 else 0
                position_str = f"{net_yes} YES @ ${avg_cost/100:.2f}"
            if net_no > 0:
                avg_cost = pos['total_cost_no'] / pos['total_bought_no'] if pos['total_bought_no'] > 0 else 0
                if position_str:
                    position_str += f", {net_no} NO @ ${avg_cost/100:.2f}"
                else:
                    position_str = f"{net_no} NO @ ${avg_cost/100:.2f}"
            
            last_trade_date = pos['last_trade'][:10] if pos['last_trade'] else "Unknown"
            
            print(f"   {i:2}. {ticker[:40]:<40} | {position_str[:25]:<25} | ${value:>8.2f} | {last_trade_date}")
    
    # Trading activity summary
    print(f"\nTRADING ACTIVITY")
    print("   " + "="*76)
    
    # Most active markets
    most_active = sorted(positions.items(), key=lambda x: x[1]['fills_count'], reverse=True)[:10]
    print(f"   Most traded markets:")
    for i, (ticker, pos) in enumerate(most_active, 1):
        print(f"     {i:2}. {ticker[:50]:<50} | {pos['fills_count']:>2} fills")
    
    # Recent activity
    recent_fills = sorted(fills, key=lambda x: x.get('created_time', ''), reverse=True)[:5]
    print(f"\n   Recent trades:")
    for i, fill in enumerate(recent_fills, 1):
        ticker = fill.get('ticker', 'Unknown')[:40]
        side = fill.get('side', 'unknown')
        action = fill.get('action', 'unknown')
        count = fill.get('count', 0)
        price = fill.get('yes_price' if fill.get('side') == 'yes' else 'no_price', 0)
        date = fill.get('created_time', '')[:10]
        
        print(f"     {i}. {ticker:<40} | {action} {count:>4} {side} @ {price:>3}¢ | {date}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    analyze_positions()