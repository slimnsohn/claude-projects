#!/usr/bin/env python3
"""
Debug P&L calculation to find the error
"""

import json
import os

def debug_pnl():
    """Debug the P&L calculation step by step."""
    filename = "data/fills_with_resolutions_current.json"
    
    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found!")
        return
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    fills = data.get('fills', [])
    
    print("=" * 80)
    print("DEBUGGING P&L CALCULATION")
    print("=" * 80)
    
    total_money_out = 0  # Money you spent
    total_money_in = 0   # Money you received back
    
    resolved_trades = []
    open_trades = []
    
    for i, fill in enumerate(fills, 1):
        ticker = fill.get('ticker', 'Unknown')
        side = fill.get('side', 'yes')
        action = fill.get('action', 'buy')
        count = fill.get('count', 0)
        yes_price = fill.get('yes_price', 0)
        no_price = fill.get('no_price', 0)
        market_status = fill.get('market_status', 'unknown')
        market_result = fill.get('market_result', '')
        
        # Calculate what you paid/received for this trade
        if side == 'yes':
            price_per_share = yes_price / 100
        else:
            price_per_share = no_price / 100
        
        trade_amount = count * price_per_share
        
        if action == 'buy':
            total_money_out += trade_amount
            money_direction = f"-${trade_amount:.2f}"
        else:  # sell
            total_money_out -= trade_amount  # This reduces your net spending
            money_direction = f"+${trade_amount:.2f}"
        
        # Check if resolved
        status_lower = market_status.lower() if market_status else ''
        is_resolved = status_lower in ['closed', 'finalized', 'settled']
        
        if is_resolved:
            # Calculate what you received at settlement
            if market_result == 'yes':
                yes_payout = 1.00
                no_payout = 0.00
            elif market_result == 'no':
                yes_payout = 0.00
                no_payout = 1.00
            else:  # tie
                yes_payout = 0.50
                no_payout = 0.50
            
            if action == 'buy':
                if side == 'yes':
                    settlement_amount = count * yes_payout
                else:
                    settlement_amount = count * no_payout
                total_money_in += settlement_amount
                settlement_direction = f"+${settlement_amount:.2f}"
            else:  # sell
                if side == 'yes':
                    settlement_amount = count * yes_payout
                else:
                    settlement_amount = count * no_payout
                total_money_in -= settlement_amount  # You owe money on sells
                settlement_direction = f"-${settlement_amount:.2f}"
            
            net_trade_pnl = settlement_amount - trade_amount if action == 'buy' else -(settlement_amount - trade_amount)
            
            resolved_trades.append({
                'trade': i,
                'ticker': ticker[:40],
                'action': action,
                'side': side,
                'count': count,
                'trade_flow': money_direction,
                'settlement_flow': settlement_direction,
                'net_pnl': net_trade_pnl,
                'result': market_result if market_result else 'TIE'
            })
        else:
            open_trades.append({
                'trade': i,
                'ticker': ticker[:40],
                'action': action,
                'side': side,
                'count': count,
                'trade_flow': money_direction
            })
    
    print(f"MONEY FLOW SUMMARY:")
    print(f"Total money OUT (spent): ${total_money_out:,.2f}")
    print(f"Total money IN (received): ${total_money_in:,.2f}")
    print(f"Net trading loss: ${total_money_out - total_money_in:,.2f}")
    
    print(f"\nRESOLVED TRADES (first 10):")
    print(f"{'#':<3} | {'Ticker':<25} | {'Trade Flow':<10} | {'Settlement':<10} | {'Net P&L':<10} | {'Result'}")
    print("-" * 80)
    
    for trade in resolved_trades[:10]:
        print(f"{trade['trade']:<3} | {trade['ticker']:<25} | {trade['trade_flow']:<10} | {trade['settlement_flow']:<10} | ${trade['net_pnl']:>8.2f} | {trade['result']}")
    
    print(f"... and {len(resolved_trades) - 10} more resolved trades")
    
    print(f"\nOPEN TRADES:")
    total_open_cost = sum(float(trade['trade_flow'].replace('$', '').replace('-', '').replace('+', '')) for trade in open_trades)
    print(f"Money tied up in open positions: ${total_open_cost:,.2f}")
    
    print(f"\nFINAL RECONCILIATION:")
    current_balance = 9818.85
    print(f"Current balance: ${current_balance:,.2f}")
    print(f"Open positions: ${total_open_cost:,.2f}")
    print(f"Net trading loss: ${total_money_out - total_money_in:,.2f}")
    print(f"Total needed: ${current_balance + total_open_cost + (total_money_out - total_money_in):,.2f}")
    
    difference = 16000 - (current_balance + total_open_cost + (total_money_out - total_money_in))
    print(f"Difference from $16k: ${difference:,.2f}")
    
    if abs(difference) < 100:
        print("✅ MATCH! The math works out.")
    else:
        print("❌ Still a discrepancy - need to investigate further")

if __name__ == "__main__":
    debug_pnl()