#!/usr/bin/env python3

import os
import json
from portfolio_engine import PortfolioEngine
from data_model import load_ref_data
from csv_parser import parse_all_portfolio_csvs
from price_lookup import PriceLookup, create_price_file

def main():
    # Set up paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    ref_folder = os.path.join(parent_dir, "ref_data")
    account_data_folder = os.path.join(parent_dir, "account data")
    output_file = os.path.join(current_dir, "dashboard_data.json")
    prices_file = os.path.join(current_dir, "current_prices.json")
    
    print(f"Looking for reference data in: {ref_folder}")
    print(f"Looking for account CSVs in: {account_data_folder}")
    print(f"Will output dashboard data to: {output_file}")
    print(f"Will output prices to: {prices_file}")
    
    # Check if required directories exist
    if not os.path.exists(ref_folder):
        print(f"Error: Reference data folder not found at {ref_folder}")
        return 1
        
    if not os.path.exists(account_data_folder):
        print(f"Error: Account data folder not found at {account_data_folder}")
        return 1
    
    # Load reference data and parse portfolio CSVs
    try:
        print("Loading reference data...")
        ref_data = load_ref_data(ref_folder)
        
        print("Parsing portfolio CSV files...")
        holdings = parse_all_portfolio_csvs(account_data_folder, ref_data)
        
        print(f"Loaded {len(holdings)} holdings from {len(ref_data)} accounts")
        
        # Get unique tickers for price lookup
        unique_tickers = list(set([h.ticker for h in holdings if h.ticker and h.ticker != 'Cash & Cash Investments']))
        print(f"Found {len(unique_tickers)} unique tickers: {unique_tickers}")
        
        # Try to fetch current prices, fallback to manual prices
        manual_prices_file = os.path.join(current_dir, "manual_prices.json")
        
        print("Fetching current market prices...")
        try:
            price_data = create_price_file(unique_tickers, prices_file)
            prices = price_data['prices']
            
            # If most prices failed, use manual prices as fallback
            successful_count = len([p for p in prices.values() if p > 0])
            if successful_count < len(unique_tickers) * 0.5:  # Less than 50% success
                print(f"API lookup had low success rate ({successful_count}/{len(unique_tickers)}), using manual prices...")
                with open(manual_prices_file, 'r') as f:
                    manual_data = json.load(f)
                    manual_prices = manual_data['prices']
                    
                # Combine: use API prices where available, manual as fallback
                for ticker in unique_tickers:
                    if ticker in manual_prices and (ticker not in prices or prices[ticker] <= 0):
                        prices[ticker] = manual_prices[ticker]
                
                # Update price metadata
                price_data['source'] = 'manual_fallback'
                price_data['successful_lookups'] = len([p for p in prices.values() if p > 0])
        
        except Exception as e:
            print(f"API lookup failed: {e}")
            print("Using manual prices...")
            with open(manual_prices_file, 'r') as f:
                manual_data = json.load(f)
                prices = manual_data['prices']
                price_data = {
                    'timestamp': manual_data['timestamp'],
                    'source': 'manual_only',
                    'tickers_count': len(unique_tickers),
                    'successful_lookups': len([t for t in unique_tickers if t in prices and prices[t] > 0])
                }
        
        # Update holdings with real market values
        total_portfolio_value = 0
        for holding in holdings:
            if holding.ticker in prices and prices[holding.ticker] > 0:
                holding.market_value = holding.shares * prices[holding.ticker]
            else:
                # For cash and unknown tickers, assume $1 per share
                holding.market_value = holding.shares * 1.0
            total_portfolio_value += holding.market_value
        
        # Create portfolio engine with updated holdings
        engine = PortfolioEngine.__new__(PortfolioEngine)
        engine.ref_data = ref_data
        engine.holdings = holdings
        
        # Generate and export dashboard data with price metadata
        dashboard_data = engine.generate_dashboard_data()
        dashboard_data['price_metadata'] = {
            'timestamp': price_data['timestamp'],
            'successful_lookups': price_data['successful_lookups'],
            'total_tickers': price_data['tickers_count'],
            'price_file': prices_file
        }
        
        with open(output_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
        print(f"SUCCESS: Dashboard data generated successfully at {output_file}")
        
        # Print summary statistics
        print(f"\nPortfolio Summary (with real-time prices):")
        print(f"Account Types: {dashboard_data['accountTypes']}")
        print(f"Tax Types: {dashboard_data['taxTypes']}")
        print(f"Asset Classes: {dashboard_data['assetClasses']}")
        
        print(f"Total Portfolio Value: ${total_portfolio_value:,.2f}")
        print(f"Price Lookup Success: {price_data['successful_lookups']}/{price_data['tickers_count']} tickers")
        
        if dashboard_data['topPositions']:
            print(f"\nTop 5 Positions (with real-time values):")
            for i, pos in enumerate(dashboard_data['topPositions'][:5], 1):
                ticker_price = prices.get(pos['ticker'], 1.0)
                print(f"  {i}. {pos['ticker']}: {pos['total_shares']:.0f} shares @ ${ticker_price:.2f} = ${pos['total_market_value']:,.2f}")
        
        print(f"\nOwners: {dashboard_data['owners']}")
        print(f"Brokerages: {dashboard_data['brokerages']}")
        
    except Exception as e:
        print(f"ERROR: Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())