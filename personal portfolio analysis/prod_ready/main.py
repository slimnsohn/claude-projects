#!/usr/bin/env python3

import os
from portfolio_engine import PortfolioEngine
from data_model import load_ref_data
from csv_parser import parse_all_portfolio_csvs

def main():
    # Set up paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    ref_folder = os.path.join(parent_dir, "ref_data")
    account_data_folder = os.path.join(parent_dir, "account data")
    output_file = os.path.join(current_dir, "dashboard_data.json")
    
    print(f"Looking for reference data in: {ref_folder}")
    print(f"Looking for account CSVs in: {account_data_folder}")
    print(f"Will output dashboard data to: {output_file}")
    
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
        
        # Create portfolio engine with parsed data
        engine = PortfolioEngine.__new__(PortfolioEngine)
        engine.ref_data = ref_data
        engine.holdings = holdings
        
        # Generate and export dashboard data
        engine.export_dashboard_json(output_file)
        print(f"SUCCESS: Dashboard data generated successfully at {output_file}")
        
        # Print summary statistics
        data = engine.generate_dashboard_data()
        print(f"\nPortfolio Summary:")
        print(f"Account Types: {data['accountTypes']}")
        print(f"Tax Types: {data['taxTypes']}")
        print(f"Asset Classes: {data['assetClasses']}")
        
        total_value = sum(data['accountTypes'].values())
        print(f"Total Portfolio Value: ${total_value:,.2f}")
        
        if data['topPositions']:
            print(f"\nTop 5 Positions:")
            for i, pos in enumerate(data['topPositions'][:5], 1):
                print(f"  {i}. {pos['ticker']}: ${pos['total_market_value']:,.2f}")
        
    except Exception as e:
        print(f"ERROR: Error generating dashboard: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())