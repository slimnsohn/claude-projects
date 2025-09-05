#!/usr/bin/env python3
"""
Get all data from Kalshi API in one script
"""

from get_balance import get_balance
from get_fills import get_fills_with_resolutions
from calculate_pnl import calculate_pnl

def get_all_data():
    """Get all Kalshi data: balance, fills, and calculate P&L."""
    print("=" * 60)
    print("GETTING ALL KALSHI DATA")
    print("=" * 60)
    
    # 1. Get current balance
    print("\n1. Getting balance...")
    try:
        balance_data = get_balance()
        print(f"   Current Balance: ${balance_data['balance_dollars']:,.2f}")
    except Exception as e:
        print(f"   ERROR getting balance: {e}")
        balance_data = None
    
    # 2. Get fills with market resolutions
    print("\n2. Getting fills with resolutions...")
    try:
        fills_data = get_fills_with_resolutions()
        if "error" not in fills_data:
            print(f"   Retrieved {fills_data['total_fills']} fills")
        else:
            print(f"   ERROR: {fills_data['error']}")
            fills_data = None
    except Exception as e:
        print(f"   ERROR getting fills: {e}")
        fills_data = None
    
    # 3. Calculate P&L
    print("\n3. Calculating P&L...")
    try:
        pnl_data = calculate_pnl()
        if pnl_data:
            print(f"   Total Events: {pnl_data['total_events']}")
            print(f"   Resolved: {pnl_data['resolved_events']} | Open: {pnl_data['open_events']}")
            print(f"   Net P&L: ${pnl_data['net_trading_pnl']:,.2f}")
    except Exception as e:
        print(f"   ERROR calculating P&L: {e}")
        pnl_data = None
    
    # 4. Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if balance_data and pnl_data:
        current_balance = balance_data['balance_dollars']
        total_spent = pnl_data['total_spent']
        open_positions = sum(event['total_cost'] for event in pnl_data['open_events_data'].values())
        net_pnl = pnl_data['net_trading_pnl']
        
        print(f"Current Balance: ${current_balance:,.2f}")
        print(f"Open Positions: ${open_positions:,.2f}")
        print(f"Net P&L: ${net_pnl:,.2f}")
        print(f"Total Account Value: ${current_balance + open_positions:,.2f}")
        print(f"Implied Deposits: ${current_balance + open_positions - net_pnl:,.2f}")
    
    print("=" * 60)
    
    return {
        'balance': balance_data,
        'fills': fills_data,
        'pnl': pnl_data
    }

if __name__ == "__main__":
    result = get_all_data()