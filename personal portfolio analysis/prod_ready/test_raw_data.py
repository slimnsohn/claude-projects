#!/usr/bin/env python3

import json

def test_raw_data_view():
    """Test the raw data view functionality"""
    
    # Load data
    with open('dashboard_data.json', 'r') as f:
        data = json.load(f)
    
    with open('current_prices.json', 'r') as f:
        price_data = json.load(f)

    positions = data['positions']
    prices = price_data['prices']

    def get_ticker_price(ticker):
        return prices.get(ticker, 1.0)

    def get_owner_from_account(account_name):
        if 'sammy' in account_name.lower():
            return 'Sammy'
        elif 'nalae' in account_name.lower():
            return 'Nalae'
        return 'Unknown'

    def get_brokerage_from_account(account_name):
        name_lower = account_name.lower()
        if 'schwab' in name_lower:
            return 'Schwab'
        elif 'fidelity' in name_lower:
            return 'Fidelity'
        elif 'vanguard' in name_lower:
            return 'Vanguard'
        return 'Unknown'

    # Process positions to create account-level data (simulate JavaScript logic)
    account_map = {}
    
    for ticker, ticker_positions in positions.items():
        for position in ticker_positions:
            account_key = position['account_id']
            
            if account_key not in account_map:
                account_map[account_key] = {
                    'account_id': position['account_id'],
                    'account_name': position['account_name'],
                    'account_type': position['account_type'],
                    'tax_type': position['tax_type'],
                    'owner': get_owner_from_account(position['account_name']),
                    'brokerage': get_brokerage_from_account(position['account_name']),
                    'holdings': [],
                    'total_value': 0
                }
            
            account = account_map[account_key]
            holding_value = position['shares'] * get_ticker_price(ticker)
            
            account['holdings'].append({
                'ticker': ticker,
                'shares': position['shares'],
                'price': get_ticker_price(ticker),
                'value': holding_value
            })
            
            account['total_value'] += holding_value

    accounts_data = list(account_map.values())
    for account in accounts_data:
        account['holdings_count'] = len(account['holdings'])

    print("=== RAW DATA VIEW TEST ===")
    print(f"Total Accounts: {len(accounts_data)}")
    
    # Summary by account type and tax type
    account_types = {}
    tax_types = {}
    owners = {}
    brokerages = {}
    
    for account in accounts_data:
        # Account type summary
        acct_type = account['account_type']
        if acct_type not in account_types:
            account_types[acct_type] = {'count': 0, 'balance': 0}
        account_types[acct_type]['count'] += 1
        account_types[acct_type]['balance'] += account['total_value']
        
        # Tax type summary
        tax_type = account['tax_type']
        if tax_type not in tax_types:
            tax_types[tax_type] = {'count': 0, 'balance': 0}
        tax_types[tax_type]['count'] += 1
        tax_types[tax_type]['balance'] += account['total_value']
        
        # Owner summary
        owner = account['owner']
        if owner not in owners:
            owners[owner] = {'count': 0, 'balance': 0}
        owners[owner]['count'] += 1
        owners[owner]['balance'] += account['total_value']
        
        # Brokerage summary  
        brokerage = account['brokerage']
        if brokerage not in brokerages:
            brokerages[brokerage] = {'count': 0, 'balance': 0}
        brokerages[brokerage]['count'] += 1
        brokerages[brokerage]['balance'] += account['total_value']

    print("\nACCOUNT TYPE BREAKDOWN:")
    for acct_type, summary in account_types.items():
        print(f"  {acct_type}: {summary['count']} accounts, ${summary['balance']:,.2f}")
    
    print("\nTAX TYPE BREAKDOWN:")
    for tax_type, summary in tax_types.items():
        print(f"  {tax_type}: {summary['count']} accounts, ${summary['balance']:,.2f}")
    
    print("\nOWNER BREAKDOWN:")
    for owner, summary in owners.items():
        print(f"  {owner}: {summary['count']} accounts, ${summary['balance']:,.2f}")
    
    print("\nBROKERAGE BREAKDOWN:")
    for brokerage, summary in brokerages.items():
        print(f"  {brokerage}: {summary['count']} accounts, ${summary['balance']:,.2f}")

    print("\nTOP 10 ACCOUNTS BY BALANCE:")
    sorted_accounts = sorted(accounts_data, key=lambda x: x['total_value'], reverse=True)
    for i, account in enumerate(sorted_accounts[:10]):
        print(f"  {i+1:2d}. {account['account_name']:<30} | {account['owner']:<6} | {account['brokerage']:<8} | {account['tax_type']:<15} | ${account['total_value']:>12,.2f} | {account['holdings_count']:2d} holdings")

    total_balance = sum(account['total_value'] for account in accounts_data)
    total_holdings = sum(account['holdings_count'] for account in accounts_data)
    print(f"\nGRAND TOTALS:")
    print(f"  Total Balance: ${total_balance:,.2f}")
    print(f"  Total Holdings: {total_holdings}")
    print(f"  Average per Account: ${total_balance/len(accounts_data):,.2f}")

if __name__ == "__main__":
    test_raw_data_view()