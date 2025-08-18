#!/usr/bin/env python3
"""
Simple individual trade analysis - each trade independently
"""

import json
import os

def analyze_individual_trades():
    """Analyze each trade independently."""
    filename = "data/fills_with_resolutions_current.json"
    
    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found!")
        return
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    fills = data.get('fills', [])
    
    print("=" * 100)
    print("INDIVIDUAL TRADE ANALYSIS")
    print("=" * 100)
    print(f"Analyzing {len(fills)} individual trades...")
    
    closed_trades = []
    open_trades = []
    
    total_closed_cost = 0
    total_closed_pnl = 0
    total_open_cost = 0
    
    for i, fill in enumerate(fills, 1):
        ticker = fill.get('ticker', 'Unknown')
        side = fill.get('side', 'yes')
        action = fill.get('action', 'buy')
        count = fill.get('count', 0)
        yes_price = fill.get('yes_price', 0)
        no_price = fill.get('no_price', 0)
        market_status = fill.get('market_status', 'unknown')
        market_result = fill.get('market_result')
        created_time = fill.get('created_time', '')[:10]  # Just date
        
        # Calculate cost for this individual trade
        if side == 'yes':
            price_cents = yes_price
        else:
            price_cents = no_price
        
        cost_dollars = (count * price_cents) / 100
        
        # Determine if trade is closed and calculate P&L
        status_lower = market_status.lower() if market_status else ''
        is_closed = status_lower in ['closed', 'finalized', 'settled']
        
        trade_info = {
            'trade_num': i,
            'ticker': ticker,
            'date': created_time,
            'action': action,
            'side': side,
            'count': count,
            'price_cents': price_cents,
            'cost_dollars': cost_dollars,
            'is_closed': is_closed,
            'result': market_result,
            'pnl': 0
        }
        
        if is_closed and market_result is not None:
            # Calculate P&L for this individual trade
            if action == 'buy':
                if side == 'yes':
                    if market_result == 'yes':
                        # Won - paid price_cents, got 100 cents per share
                        pnl_cents = count * (100 - price_cents)
                    else:
                        # Lost - paid price_cents, got 0
                        pnl_cents = count * (0 - price_cents)
                else:  # side == 'no'
                    if market_result == 'no':
                        # Won - paid price_cents, got 100 cents per share
                        pnl_cents = count * (100 - price_cents)
                    else:
                        # Lost - paid price_cents, got 0
                        pnl_cents = count * (0 - price_cents)
            else:  # action == 'sell'
                # For sells, reverse the logic
                if side == 'yes':
                    if market_result == 'yes':
                        # Lost on sell - received price_cents, had to pay 100
                        pnl_cents = count * (price_cents - 100)
                    else:
                        # Won on sell - received price_cents, had to pay 0
                        pnl_cents = count * (price_cents - 0)
                else:  # side == 'no'
                    if market_result == 'no':
                        # Lost on sell - received price_cents, had to pay 100
                        pnl_cents = count * (price_cents - 100)
                    else:
                        # Won on sell - received price_cents, had to pay 0
                        pnl_cents = count * (price_cents - 0)
            
            trade_info['pnl'] = pnl_cents / 100  # Convert to dollars
            closed_trades.append(trade_info)
            total_closed_cost += cost_dollars if action == 'buy' else -cost_dollars
            total_closed_pnl += trade_info['pnl']
        else:
            open_trades.append(trade_info)
            total_open_cost += cost_dollars if action == 'buy' else -cost_dollars
    
    # Display results
    print(f"\nCLOSED TRADES ({len(closed_trades)} trades):")
    print(f"{'#':<3} | {'Date':<10} | {'Market':<35} | {'Action':<4} | {'Side':<3} | {'Count':<5} | {'Price':<3} | {'Cost':<8} | {'Result':<3} | {'P&L':<8}")
    print("-" * 100)
    
    # Sort closed trades by P&L (best to worst)
    closed_trades.sort(key=lambda x: x['pnl'], reverse=True)
    
    for trade in closed_trades:
        pnl_str = f"${trade['pnl']:>7.2f}"
        cost_str = f"${trade['cost_dollars']:>7.2f}"
        if trade['action'] == 'sell':
            cost_str = f"-${trade['cost_dollars']:>6.2f}"  # Negative for sells
        
        print(f"{trade['trade_num']:<3} | {trade['date']:<10} | {trade['ticker'][:34]:<35} | {trade['action']:<4} | {trade['side']:<3} | {trade['count']:<5} | {trade['price_cents']:<3}¢ | {cost_str:<8} | {trade['result']:<3} | {pnl_str:<8}")
    
    print(f"\nOPEN TRADES ({len(open_trades)} trades):")
    print(f"{'#':<3} | {'Date':<10} | {'Market':<35} | {'Action':<4} | {'Side':<3} | {'Count':<5} | {'Price':<3} | {'Cost':<8} | {'Status'}")
    print("-" * 95)
    
    for trade in open_trades:
        cost_str = f"${trade['cost_dollars']:>7.2f}"
        if trade['action'] == 'sell':
            cost_str = f"-${trade['cost_dollars']:>6.2f}"
            
        print(f"{trade['trade_num']:<3} | {trade['date']:<10} | {trade['ticker'][:34]:<35} | {trade['action']:<4} | {trade['side']:<3} | {trade['count']:<5} | {trade['price_cents']:<3}¢ | {cost_str:<8} | Open")
    
    print(f"\n" + "=" * 100)
    print(f"SUMMARY:")
    print(f"   Closed trades: {len(closed_trades)}")
    print(f"   Open trades: {len(open_trades)}")
    print(f"   Total P&L from closed trades: ${total_closed_pnl:,.2f}")
    print(f"   Money in open trades: ${total_open_cost:,.2f}")
    print(f"=" * 100)

if __name__ == "__main__":
    analyze_individual_trades()