#!/usr/bin/env python3
"""
Export all trades to CSV for manual analysis
"""

import json
import os
import csv

def export_trades_to_csv():
    """Export all trades to CSV format."""
    filename = "data/fills_with_resolutions_current.json"
    
    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found!")
        return
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    fills = data.get('fills', [])
    
    # Prepare CSV data
    csv_data = []
    
    for i, fill in enumerate(fills, 1):
        ticker = fill.get('ticker', 'Unknown')
        side = fill.get('side', 'yes')
        action = fill.get('action', 'buy')
        count = fill.get('count', 0)
        yes_price = fill.get('yes_price', 0)
        no_price = fill.get('no_price', 0)
        market_status = fill.get('market_status', 'unknown')
        market_result = fill.get('market_result', '')
        created_time = fill.get('created_time', '')[:10]  # Just date
        is_taker = fill.get('is_taker', False)
        
        # Calculate cost
        if side == 'yes':
            price_cents = yes_price
        else:
            price_cents = no_price
        
        cost = (count * price_cents) / 100
        
        # Calculate payout if resolved
        status_lower = market_status.lower() if market_status else ''
        is_resolved = status_lower in ['closed', 'finalized', 'settled']
        
        payout = ""
        net_pnl = ""
        
        if is_resolved and market_result:
            if action == 'buy':
                if side == 'yes':
                    if market_result == 'yes':
                        payout = count * 1.00
                    else:
                        payout = 0
                else:  # side == 'no'
                    if market_result == 'no':
                        payout = count * 1.00
                    else:
                        payout = 0
            else:  # action == 'sell'
                if side == 'yes':
                    if market_result == 'yes':
                        payout = -count * 1.00
                    else:
                        payout = 0
                else:  # side == 'no'
                    if market_result == 'no':
                        payout = -count * 1.00
                    else:
                        payout = 0
            
            net_pnl = payout - cost if action == 'buy' else payout + cost
        
        # Add to CSV data
        csv_data.append({
            'Trade_Number': i,
            'Date': created_time,
            'Market_Ticker': ticker,
            'Action': action,
            'Side': side,
            'Count': count,
            'Price_Cents': price_cents,
            'Cost_Dollars': round(cost, 2),
            'Is_Taker': is_taker,
            'Market_Status': market_status,
            'Market_Result': market_result,
            'Payout_Dollars': round(payout, 2) if payout != "" else "",
            'Net_PnL': round(net_pnl, 2) if net_pnl != "" else "",
            'Trade_ID': fill.get('trade_id', ''),
            'Order_ID': fill.get('order_id', '')
        })
    
    # Write to CSV
    csv_filename = "all_trades_export.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Trade_Number', 'Date', 'Market_Ticker', 'Action', 'Side', 
            'Count', 'Price_Cents', 'Cost_Dollars', 'Is_Taker', 
            'Market_Status', 'Market_Result', 'Payout_Dollars', 'Net_PnL',
            'Trade_ID', 'Order_ID'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"=" * 80)
    print(f"TRADES EXPORTED TO CSV")
    print(f"=" * 80)
    print(f"File: {csv_filename}")
    print(f"Total trades: {len(csv_data)}")
    print(f"")
    print(f"Columns included:")
    print(f"- Trade_Number: Sequential number")
    print(f"- Date: Trade date")
    print(f"- Market_Ticker: Market identifier")
    print(f"- Action: buy/sell")
    print(f"- Side: yes/no")
    print(f"- Count: Number of contracts")
    print(f"- Price_Cents: Price per contract in cents")
    print(f"- Cost_Dollars: Total cost in dollars (fees included)")
    print(f"- Is_Taker: True/False (affects fees)")
    print(f"- Market_Status: open/closed/finalized/etc")
    print(f"- Market_Result: yes/no/empty")
    print(f"- Payout_Dollars: What you received (if resolved)")
    print(f"- Net_PnL: Profit/Loss for this trade")
    print(f"- Trade_ID: Kalshi trade identifier")
    print(f"- Order_ID: Kalshi order identifier")
    print(f"")
    print(f"You can now open {csv_filename} in Excel/Google Sheets")
    print(f"=" * 80)
    
    # Print summary stats
    total_cost = sum(row['Cost_Dollars'] for row in csv_data if row['Action'] == 'buy')
    total_received = sum(row['Cost_Dollars'] for row in csv_data if row['Action'] == 'sell')
    resolved_trades = [row for row in csv_data if row['Net_PnL'] != ""]
    total_pnl = sum(row['Net_PnL'] for row in resolved_trades if row['Net_PnL'] != "")
    
    print(f"SUMMARY FROM CSV DATA:")
    print(f"Total money spent (buys): ${total_cost:,.2f}")
    print(f"Total money received (sells): ${total_received:,.2f}")
    print(f"Net money spent: ${total_cost - total_received:,.2f}")
    print(f"Resolved trades: {len(resolved_trades)}")
    print(f"Total P&L from resolved: ${total_pnl:,.2f}")
    print(f"=" * 80)

if __name__ == "__main__":
    export_trades_to_csv()