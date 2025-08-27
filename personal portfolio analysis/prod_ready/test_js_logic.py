#!/usr/bin/env python3

import json

def test_javascript_logic():
    """Test the JavaScript logic in Python to debug position loading"""
    
    # Load the data like JavaScript would
    with open('dashboard_data.json', 'r') as f:
        portfolio_data = json.load(f)
    
    with open('current_prices.json', 'r') as f:
        price_data = json.load(f)
    
    positions = portfolio_data['positions']
    prices = price_data['prices']
    
    def get_ticker_price(ticker):
        return prices.get(ticker, 1.0)
    
    def get_owner_from_account(account_name):
        account_lower = account_name.lower()
        if 'sammy' in account_lower:
            return 'Sammy'
        elif 'nalae' in account_lower:
            return 'Nalae'
        return 'Unknown'
    
    def get_brokerage_from_account(account_name):
        account_lower = account_name.lower()
        if 'schwab' in account_lower:
            return 'Schwab'
        elif 'fidelity' in account_lower:
            return 'Fidelity'
        elif 'vanguard' in account_lower:
            return 'Vanguard'
        return 'Unknown'
    
    # Simulate the JavaScript loadAllPositions function
    all_positions_data = []
    
    for ticker, ticker_positions in positions.items():
        total_shares = sum(p['shares'] for p in ticker_positions)
        total_value = sum(p['shares'] * get_ticker_price(ticker) for p in ticker_positions)
        
        owners = list(set(get_owner_from_account(p['account_name']) for p in ticker_positions))
        brokerages = list(set(get_brokerage_from_account(p['account_name']) for p in ticker_positions))
        
        position_data = {
            'ticker': ticker,
            'shares': total_shares,
            'value': total_value,
            'accounts': len(ticker_positions),
            'owner': ', '.join(owners),
            'brokerage': ', '.join(brokerages),
            'positions': ticker_positions
        }
        
        all_positions_data.append(position_data)
    
    print(f"Processed {len(all_positions_data)} positions for display")
    
    # Show first 10 positions
    print("\nFirst 10 positions:")
    for i, pos in enumerate(sorted(all_positions_data, key=lambda x: x['value'], reverse=True)[:10]):
        print(f"{i+1:2d}. {pos['ticker']:8} | {pos['shares']:8.1f} shares | ${pos['value']:12,.2f} | {pos['accounts']} accounts | {pos['owner']} | {pos['brokerage']}")
    
    # Test search functionality
    search_term = "AAP"
    filtered_data = [pos for pos in all_positions_data if search_term.upper() in pos['ticker'].upper()]
    print(f"\nSearch for '{search_term}' found {len(filtered_data)} results:")
    for pos in filtered_data:
        print(f"  {pos['ticker']} | {pos['shares']} shares | ${pos['value']:.2f}")

if __name__ == "__main__":
    test_javascript_logic()