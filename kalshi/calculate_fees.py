#!/usr/bin/env python3
"""
Calculate exact fees based on taker/maker status from fills data
"""

import json
import os

def calculate_exact_fees():
    """Calculate fees based on is_taker field and estimate fee structure."""
    filename = "data/fills_with_resolutions_current.json"
    
    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found!")
        return
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    fills = data.get('fills', [])
    
    print("=" * 80)
    print("KALSHI FEE CALCULATION")
    print("=" * 80)
    
    total_taker_volume = 0
    total_maker_volume = 0
    taker_trades = 0
    maker_trades = 0
    
    print(f"Analyzing {len(fills)} trades for fee calculation...")
    print(f"\nTRADE BREAKDOWN:")
    print(f"{'Trade#':<6} | {'Type':<6} | {'Market':<35} | {'Volume':<10} | {'Fee Est'}")
    print("-" * 80)
    
    for i, fill in enumerate(fills, 1):
        ticker = fill.get('ticker', 'Unknown')
        count = fill.get('count', 0)
        yes_price = fill.get('yes_price', 0)
        no_price = fill.get('no_price', 0)
        side = fill.get('side', 'yes')
        action = fill.get('action', 'buy')
        is_taker = fill.get('is_taker', False)
        
        # Calculate trade volume
        if side == 'yes':
            price_cents = yes_price
        else:
            price_cents = no_price
        
        trade_volume = (count * price_cents) / 100  # Convert to dollars
        
        # Categorize as taker or maker
        if is_taker:
            total_taker_volume += trade_volume
            taker_trades += 1
            trade_type = "TAKER"
            # Assume 1% taker fee (common structure)
            estimated_fee = trade_volume * 0.01
        else:
            total_maker_volume += trade_volume
            maker_trades += 1
            trade_type = "MAKER"
            # Assume 0% maker fee (common structure)
            estimated_fee = 0
        
        if i <= 20:  # Show first 20 trades
            print(f"{i:<6} | {trade_type:<6} | {ticker[:34]:<35} | ${trade_volume:>8.2f} | ${estimated_fee:>6.2f}")
    
    if len(fills) > 20:
        print(f"... and {len(fills) - 20} more trades")
    
    # Calculate total estimated fees
    estimated_taker_fees_1pct = total_taker_volume * 0.01
    estimated_taker_fees_05pct = total_taker_volume * 0.005
    
    print(f"\n" + "=" * 80)
    print(f"FEE ANALYSIS:")
    print(f"   Taker trades: {taker_trades} (${total_taker_volume:,.2f} volume)")
    print(f"   Maker trades: {maker_trades} (${total_maker_volume:,.2f} volume)")
    print(f"   Total volume: ${total_taker_volume + total_maker_volume:,.2f}")
    print(f"")
    print(f"ESTIMATED FEES (different scenarios):")
    print(f"   If 1.0% taker, 0% maker: ${estimated_taker_fees_1pct:,.2f}")
    print(f"   If 0.5% taker, 0% maker: ${estimated_taker_fees_05pct:,.2f}")
    
    # Calculate what total deposits would be
    current_balance = 9818.85
    net_pnl = -4428.30  # From previous analysis
    open_positions = 2298.14
    
    print(f"\n" + "=" * 80)
    print(f"DEPOSIT RECONCILIATION:")
    print(f"   Current balance:     ${current_balance:>10,.2f}")
    print(f"   Net P&L (realized):  ${net_pnl:>10,.2f}")
    print(f"   Open positions:      ${open_positions:>10,.2f}")
    print(f"   Estimated fees 1%:   ${estimated_taker_fees_1pct:>10,.2f}")
    print(f"   " + "-" * 40)
    print(f"   Implied deposits 1%: ${current_balance - net_pnl + open_positions + estimated_taker_fees_1pct:>10,.2f}")
    print(f"")
    print(f"   Estimated fees 0.5%: ${estimated_taker_fees_05pct:>10,.2f}")
    print(f"   Implied deposits 0.5%: ${current_balance - net_pnl + open_positions + estimated_taker_fees_05pct:>10,.2f}")
    
    # Show the gap
    stated_deposit = 16000
    implied_deposit_1pct = current_balance - net_pnl + open_positions + estimated_taker_fees_1pct
    implied_deposit_05pct = current_balance - net_pnl + open_positions + estimated_taker_fees_05pct
    
    print(f"\n   Your stated deposit: ${stated_deposit:>10,.2f}")
    print(f"   Gap with 1% fees:   ${implied_deposit_1pct - stated_deposit:>10,.2f}")
    print(f"   Gap with 0.5% fees: ${implied_deposit_05pct - stated_deposit:>10,.2f}")
    
    return {
        'taker_volume': total_taker_volume,
        'maker_volume': total_maker_volume,
        'estimated_fees_1pct': estimated_taker_fees_1pct,
        'estimated_fees_05pct': estimated_taker_fees_05pct
    }

if __name__ == "__main__":
    result = calculate_exact_fees()
    
    if result:
        print(f"\n" + "=" * 80)
        print(f"CONCLUSION:")
        if result['estimated_fees_1pct'] > 400:
            print(f"With 1% taker fees, your total fees would be ~${result['estimated_fees_1pct']:.0f}")
        else:
            print(f"Fees alone don't fully explain the gap - may need to check for other costs")
        print(f"=" * 80)