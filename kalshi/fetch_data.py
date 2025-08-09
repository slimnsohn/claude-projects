#!/usr/bin/env python3
"""
Script to fetch all Kalshi trading data and store it locally.
Run this script to update your local data with latest transactions.
"""

import sys
import argparse
from datetime import datetime
from kalshi_client import KalshiClient
from data_manager import DataManager
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fetch_and_store_data(output_filename: str = None) -> bool:
    """Fetch data from Kalshi API and store locally."""
    try:
        # Initialize client and data manager
        client = KalshiClient()
        dm = DataManager()

        # Authenticate first
        logger.info("Authenticating with Kalshi API...")
        if not client.authenticate():
            logger.error("❌ Authentication failed!")
            return False

        # Fetch all data
        logger.info("Fetching all trading data...")
        all_data = client.fetch_all_data()

        # Store data
        filepath = dm.save_data(all_data, output_filename)

        # Generate and display summary
        summary = dm.get_data_summary(all_data)

        print("\n" + "=" * 50)
        print("DATA FETCH COMPLETE")
        print("=" * 50)
        print(f"Fetched at: {summary['fetched_at']}")
        print(f"Saved to: {filepath}")
        print("\nRecord Counts:")
        for data_type, count in summary["data_counts"].items():
            print(f"  {data_type.replace('_', ' ').title()}: {count}")

        print("\nDate Ranges:")
        for data_type, date_range in summary.get("date_ranges", {}).items():
            print(
                f"  {data_type.replace('_', ' ').title()}: {date_range['earliest']} to {date_range['latest']}"
            )

        # Export to CSV for easy analysis
        exported_files = dm.export_to_csv(all_data)
        if exported_files:
            print(f"\nCSV exports created in 'exports/' directory:")
            for data_type, filepath in exported_files.items():
                print(f"  {data_type}: {filepath}")

        print("\nData fetch completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Error during data fetch: {e}")
        return False


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Fetch Kalshi trading data")
    parser.add_argument("-o", "--output", help="Output filename (optional)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print("Kalshi Data Fetcher")
    print("=" * 30)
    print("This script will fetch all your trading data from Kalshi API")
    print("Make sure you have set up your credentials in .env file")
    print()

    # Check if .env exists
    import os

    if not os.path.exists(".env"):
        print("ERROR: .env file not found!")
        print("Please copy .env.example to .env and add your credentials:")
        print("  cp .env.example .env")
        print("  # Then edit .env with your API key or email/password")
        sys.exit(1)

    # Fetch data
    success = fetch_and_store_data(args.output)

    if success:
        print("\nNext steps:")
        print("1. Review the exported CSV files in 'exports/' directory")
        print("2. Run the web dashboard: python -m http.server 8000")
        print("3. Open http://localhost:8000 in your browser")
        sys.exit(0)
    else:
        print("\nData fetch failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
