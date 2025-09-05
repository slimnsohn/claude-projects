#!/usr/bin/env python3
"""
Export current fills data to CSV
"""

import json
import os
import csv

def export_to_csv():
    """Export fills data to CSV format."""
    filename = "data/fills_with_resolutions_current.json"
    
    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found! Run get_fills.py first.")
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
        
        if is_resolved:
            # Handle ties as 50¢ payout
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
            
            net_pnl = payout - cost if action == 'buy' else payout + cost
        
        csv_data.append({
            'Trade_Number': i,
            'Date': created_time,
            'Market_Ticker': ticker,
            'Action': action,
            'Side': side,
            'Count': count,
            'Price_Cents': price_cents,
            'Cost_Dollars': round(cost, 2),
            'Market_Status': market_status,
            'Market_Result': market_result if market_result else 'TIE' if is_resolved else '',
            'Payout_Dollars': round(payout, 2) if payout != "" else "",
            'Net_PnL': round(net_pnl, 2) if net_pnl != "" else ""
        })
    
    # Write to CSV
    csv_filename = "trades_export.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Trade_Number', 'Date', 'Market_Ticker', 'Action', 'Side', 
            'Count', 'Price_Cents', 'Cost_Dollars', 'Market_Status', 
            'Market_Result', 'Payout_Dollars', 'Net_PnL'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"Exported {len(csv_data)} trades to {csv_filename}")
    
    return csv_filename

if __name__ == "__main__":
    export_to_csv()