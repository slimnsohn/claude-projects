#!/usr/bin/env python3

import json
from collections import defaultdict

def categorize_holdings():
    """Categorize holdings into stocks vs index funds"""
    
    # Load data
    with open('dashboard_data.json', 'r') as f:
        data = json.load(f)

    with open('current_prices.json', 'r') as f:
        price_data = json.load(f)

    positions = data['positions']
    prices = price_data['prices']

    # Categorize tickers
    index_funds = []
    individual_stocks = []

    for ticker in positions.keys():
        # Index fund patterns:
        # - Vanguard funds: VFIAX, VHYAX, VBILX, VEMAX, VGSLX, VSMAX, VFIFX, VSORX
        # - Fidelity funds: FXAIX, FXNAX, FSSNX
        # - ETFs: VOO, SPY
        # - Money market: VMFXX
        # - Other funds: CSEIX, RNWGX, USO (commodity ETF)
        
        is_index_fund = (
            ticker.startswith('V') and ticker.endswith('X') or  # Vanguard funds
            ticker.startswith('F') and ticker.endswith('X') or  # Fidelity funds  
            ticker in ['VOO', 'SPY'] or  # ETFs
            ticker in ['CSEIX', 'RNWGX'] or  # Other mutual funds
            ticker == 'USO'  # Commodity ETF
        )
        
        if is_index_fund:
            index_funds.append(ticker)
        else:
            individual_stocks.append(ticker)

    print('INDEX FUNDS/ETFs:')
    index_total = 0
    for ticker in sorted(index_funds):
        shares = sum(p['shares'] for p in positions[ticker])
        value = shares * prices.get(ticker, 0)
        index_total += value
        print(f'  {ticker:8} | {shares:8.1f} shares | ${value:12,.2f}')

    print(f'\nINDEX FUNDS TOTAL: ${index_total:,.2f}')

    print('\nINDIVIDUAL STOCKS:')
    stock_total = 0
    for ticker in sorted(individual_stocks):
        shares = sum(p['shares'] for p in positions[ticker])
        value = shares * prices.get(ticker, 0)
        stock_total += value
        print(f'  {ticker:8} | {shares:8.1f} shares | ${value:12,.2f}')

    print(f'\nSTOCKS TOTAL: ${stock_total:,.2f}')
    print(f'GRAND TOTAL: ${index_total + stock_total:,.2f}')
    print(f'\nAllocation: {index_total/(index_total + stock_total)*100:.1f}% index funds, {stock_total/(index_total + stock_total)*100:.1f}% individual stocks')
    
    return index_funds, individual_stocks

if __name__ == "__main__":
    categorize_holdings()