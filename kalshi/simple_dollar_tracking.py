#!/usr/bin/env python3
"""
Simple dollar tracking: Track every dollar from $16k deposit
Cost already includes fees, so we just track: Cost → Payout
"""

import json
import os

def track_every_dollar():
    """Track every dollar from the $16k deposit."""
    filename = "data/fills_with_resolutions_current.json"
    
    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found!")
        return
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    fills = data.get('fills', [])
    
    print("=" * 80)
    print("SIMPLE DOLLAR TRACKING - EVERY DOLLAR FROM $16K")
    print("=" * 80)
    
    # Track where each dollar went
    total_spent_on_positions = 0
    total_received_back = 0
    cash_from_open_positions = 0
    
    resolved_trades = []
    open_trades = []
    
    for fill in fills:
        ticker = fill.get('ticker', 'Unknown')
        side = fill.get('side', 'yes')
        action = fill.get('action', 'buy')
        count = fill.get('count', 0)
        yes_price = fill.get('yes_price', 0)
        no_price = fill.get('no_price', 0)
        market_status = fill.get('market_status', 'unknown')
        market_result = fill.get('market_result')
        
        # Calculate what you paid (fees included in the price)
        if side == 'yes':
            price_per_share = yes_price / 100  # Convert cents to dollars
        else:
            price_per_share = no_price / 100
        
        cost = count * price_per_share
        
        # Track money flow
        if action == 'buy':
            total_spent_on_positions += cost
        else:  # sell
            total_spent_on_positions -= cost  # Money received back from sell
        
        # Calculate payout for resolved positions
        status_lower = market_status.lower() if market_status else ''
        is_resolved = status_lower in ['closed', 'finalized', 'settled']
        
        if is_resolved and market_result is not None:
            # Calculate final payout
            if action == 'buy':
                if side == 'yes':
                    if market_result == 'yes':
                        final_payout = count * 1.00  # $1 per share
                    else:
                        final_payout = 0  # $0 per share
                else:  # side == 'no'
                    if market_result == 'no':
                        final_payout = count * 1.00  # $1 per share
                    else:
                        final_payout = 0  # $0 per share
            else:  # action == 'sell'
                # For sells, you already got money back when you sold
                # The "cost" is what you have to pay at settlement
                if side == 'yes':
                    if market_result == 'yes':
                        final_payout = -count * 1.00  # You owe $1 per share
                    else:
                        final_payout = 0  # You owe $0 per share
                else:  # side == 'no'
                    if market_result == 'no':
                        final_payout = -count * 1.00  # You owe $1 per share
                    else:
                        final_payout = 0  # You owe $0 per share
            
            total_received_back += final_payout
            net_pnl = final_payout - cost if action == 'buy' else final_payout + cost
            
            resolved_trades.append({
                'ticker': ticker,
                'action': action,
                'side': side,
                'count': count,
                'cost': cost,
                'payout': final_payout,
                'net_pnl': net_pnl,
                'result': market_result
            })
        else:
            # Open position - money is tied up
            cash_from_open_positions += cost
            open_trades.append({
                'ticker': ticker,
                'action': action,
                'side': side,
                'count': count,
                'cost': cost
            })
    
    # Current cash balance
    current_cash = 9818.85
    
    print(f"MONEY FLOW FROM $16,000 DEPOSIT:")
    print(f"")
    print(f"1. MONEY SPENT ON POSITIONS:")
    print(f"   Total spent on all positions: ${total_spent_on_positions:>10,.2f}")
    print(f"")
    print(f"2. MONEY RECEIVED BACK FROM RESOLVED POSITIONS:")
    print(f"   Total received from payouts:  ${total_received_back:>10,.2f}")
    print(f"")
    print(f"3. CURRENT ACCOUNT STATE:")
    print(f"   Cash in account:              ${current_cash:>10,.2f}")
    print(f"   Cash tied up in open trades:  ${cash_from_open_positions:>10,.2f}")
    print(f"   " + "-" * 45)
    print(f"   Total current value:          ${current_cash + cash_from_open_positions:>10,.2f}")
    print(f"")
    print(f"4. NET CHANGE FROM TRADING:")
    print(f"   Money lost to market:         ${total_spent_on_positions - total_received_back:>10,.2f}")
    print(f"")
    print(f"5. TOTAL DOLLAR ACCOUNTING:")
    print(f"   Started with (deposit):       ${16000:>10,.2f}")
    print(f"   Current cash:                 ${current_cash:>10,.2f}")
    print(f"   Money in open positions:      ${cash_from_open_positions:>10,.2f}")
    print(f"   Money lost to resolved bets:  ${total_spent_on_positions - total_received_back:>10,.2f}")
    print(f"   " + "-" * 45)
    print(f"   Total accounted for:          ${current_cash + cash_from_open_positions + (total_spent_on_positions - total_received_back):>10,.2f}")
    
    difference = 16000 - (current_cash + cash_from_open_positions + (total_spent_on_positions - total_received_back))
    print(f"   Difference from $16k:         ${difference:>10,.2f}")
    
    if abs(difference) < 50:
        print(f"\nPERFECT MATCH! All dollars accounted for.")
    else:
        print(f"\nThere's still a ${abs(difference):.2f} discrepancy")
        print(f"   This could be:")
        print(f"   - Platform fees not captured in trade data")
        print(f"   - Rounding differences")
        print(f"   - Deposit/withdrawal timing differences")
    
    print(f"\n" + "=" * 80)
    
    # Show some resolved trades for verification
    print(f"SAMPLE RESOLVED TRADES (showing P&L calculation):")
    print(f"{'Market':<35} | {'Cost':<8} | {'Payout':<8} | {'P&L':<8} | {'Result'}")
    print("-" * 80)
    
    # Sort by P&L and show top winners and losers
    resolved_trades.sort(key=lambda x: x['net_pnl'], reverse=True)
    
    for i, trade in enumerate(resolved_trades[:10]):  # Top 10 winners
        print(f"{trade['ticker'][:34]:<35} | ${trade['cost']:>7.2f} | ${trade['payout']:>7.2f} | ${trade['net_pnl']:>7.2f} | {trade['result']}")
    
    print("...")
    
    for trade in resolved_trades[-5:]:  # Top 5 losers
        print(f"{trade['ticker'][:34]:<35} | ${trade['cost']:>7.2f} | ${trade['payout']:>7.2f} | ${trade['net_pnl']:>7.2f} | {trade['result']}")
    
    return {
        'total_spent': total_spent_on_positions,
        'total_received': total_received_back,
        'current_cash': current_cash,
        'open_positions': cash_from_open_positions,
        'difference': difference
    }

if __name__ == "__main__":
    result = track_every_dollar()