#!/usr/bin/env python3

import json

def test_grouped_positions():
    """Test the grouped positions functionality"""
    
    # Load data
    with open('dashboard_data.json', 'r') as f:
        data = json.load(f)
    
    with open('current_prices.json', 'r') as f:
        price_data = json.load(f)

    positions = data['positions']
    prices = price_data['prices']

    def is_index_fund(ticker):
        return (
            ticker.startswith('V') and ticker.endswith('X') or
            ticker.startswith('F') and ticker.endswith('X') or
            ticker in ['VOO', 'SPY'] or
            ticker in ['CSEIX', 'RNWGX'] or
            ticker == 'USO'
        )

    index_funds_data = []
    stocks_data = []

    for ticker, ticker_positions in positions.items():
        total_shares = sum(p['shares'] for p in ticker_positions)
        total_value = total_shares * prices.get(ticker, 0)
        
        position_data = {
            'ticker': ticker,
            'shares': total_shares,
            'value': total_value,
            'accounts': len(ticker_positions)
        }
        
        if is_index_fund(ticker):
            index_funds_data.append(position_data)
        else:
            stocks_data.append(position_data)

    # Calculate totals
    index_total = sum(pos['value'] for pos in index_funds_data)
    stocks_total = sum(pos['value'] for pos in stocks_data)
    grand_total = index_total + stocks_total

    print("=== GROUPED POSITIONS TEST ===")
    print(f"Index Funds: {len(index_funds_data)} holdings, ${index_total:,.2f} ({index_total/grand_total*100:.1f}%)")
    print(f"Stocks: {len(stocks_data)} holdings, ${stocks_total:,.2f} ({stocks_total/grand_total*100:.1f}%)")
    print(f"Total Portfolio: ${grand_total:,.2f}")
    print()
    
    print("TOP 5 INDEX FUNDS:")
    for i, pos in enumerate(sorted(index_funds_data, key=lambda x: x['value'], reverse=True)[:5]):
        print(f"  {i+1}. {pos['ticker']:8} | ${pos['value']:12,.2f} | {pos['shares']:8.1f} shares")
    
    print("\nTOP 5 INDIVIDUAL STOCKS:")
    for i, pos in enumerate(sorted(stocks_data, key=lambda x: x['value'], reverse=True)[:5]):
        print(f"  {i+1}. {pos['ticker']:8} | ${pos['value']:12,.2f} | {pos['shares']:8.1f} shares")

if __name__ == "__main__":
    test_grouped_positions()