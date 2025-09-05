#!/usr/bin/env python3
"""
Simple verification: just track money in vs money out
"""

import json
import os

def simple_verification():
    """Simple money in vs money out calculation."""
    filename = "data/fills_with_resolutions_current.json"
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    fills = data.get('fills', [])
    
    print("=" * 60)
    print("SIMPLE MONEY VERIFICATION")
    print("=" * 60)
    
    # Just track: money spent vs money received back
    cash_spent_on_buys = 0
    cash_received_from_sells = 0
    cash_received_from_settlements = 0
    cash_in_open_positions = 0
    
    for fill in fills:
        side = fill.get('side', 'yes')
        action = fill.get('action', 'buy')
        count = fill.get('count', 0)
        yes_price = fill.get('yes_price', 0)
        no_price = fill.get('no_price', 0)
        market_status = fill.get('market_status', 'unknown')
        market_result = fill.get('market_result', '')
        
        # Calculate trade amount
        if side == 'yes':
            price_per_share = yes_price / 100
        else:
            price_per_share = no_price / 100
        
        trade_amount = count * price_per_share
        
        if action == 'buy':
            # You spent money
            status_lower = market_status.lower() if market_status else ''
            is_resolved = status_lower in ['closed', 'finalized', 'settled']
            
            if is_resolved:
                cash_spent_on_buys += trade_amount
                
                # Calculate what you got back at settlement
                if market_result == 'yes':
                    settlement_rate = 1.00 if side == 'yes' else 0.00
                elif market_result == 'no':
                    settlement_rate = 0.00 if side == 'yes' else 1.00
                else:  # tie
                    settlement_rate = 0.50
                
                cash_received_from_settlements += count * settlement_rate
            else:
                # Open position
                cash_in_open_positions += trade_amount
                
        else:  # sell
            # You received money when you sold
            cash_received_from_sells += trade_amount
            
            # But you may owe money at settlement if it goes against you
            status_lower = market_status.lower() if market_status else ''
            is_resolved = status_lower in ['closed', 'finalized', 'settled']
            
            if is_resolved:
                if market_result == 'yes':
                    settlement_rate = 1.00 if side == 'yes' else 0.00
                elif market_result == 'no':
                    settlement_rate = 0.00 if side == 'yes' else 1.00
                else:  # tie
                    settlement_rate = 0.50
                
                # What you owe at settlement
                cash_received_from_settlements -= count * settlement_rate
    
    # Calculate net result
    net_cash_out = cash_spent_on_buys - cash_received_from_sells
    net_cash_back = cash_received_from_settlements
    net_trading_loss = net_cash_out - net_cash_back
    
    print(f"Cash spent on buys: ${cash_spent_on_buys:,.2f}")
    print(f"Cash received from sells: ${cash_received_from_sells:,.2f}")
    print(f"Net cash spent: ${net_cash_out:,.2f}")
    print(f"")
    print(f"Cash received from settlements: ${cash_received_from_settlements:,.2f}")
    print(f"")
    print(f"Net trading loss: ${net_trading_loss:,.2f}")
    print(f"Cash in open positions: ${cash_in_open_positions:,.2f}")
    print(f"")
    print(f"Current balance: $9,818.85")
    print(f"")
    print(f"TOTAL: $9,818.85 + ${cash_in_open_positions:,.2f} + ${net_trading_loss:,.2f} = ${9818.85 + cash_in_open_positions + net_trading_loss:,.2f}")
    
    total_account_value = 9818.85 + cash_in_open_positions + net_trading_loss
    difference = total_account_value - 16000
    
    print(f"")
    print(f"Difference from $16k: ${difference:,.2f}")
    
    if abs(difference) < 100:
        print("✅ MATCH!")
    else:
        print(f"❌ Still ${abs(difference):,.2f} off")

if __name__ == "__main__":
    simple_verification()