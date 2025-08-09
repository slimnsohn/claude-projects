#!/usr/bin/env python3
"""
Data management utilities for Kalshi trading data.
Handles storage, retrieval, and export of trading data in various formats.
"""

import os
import json
import csv
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class DataManager:
    """Manages local storage and export of Kalshi trading data."""

    def __init__(self, data_dir: str = "data"):
        """Initialize with data directory."""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def save_data(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save data to JSON file with timestamp."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kalshi_data_{timestamp}.json"

        filepath = os.path.join(self.data_dir, filename)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Data saved to {filepath}")
        return filepath

    def load_latest_data(self) -> Optional[Dict[str, Any]]:
        """Load the most recent data file."""
        json_files = [f for f in os.listdir(self.data_dir) if f.endswith(".json")]
        if not json_files:
            logger.warning("No data files found")
            return None

        # Sort by filename (which includes timestamp)
        latest_file = sorted(json_files)[-1]
        filepath = os.path.join(self.data_dir, latest_file)

        with open(filepath, "r") as f:
            data = json.load(f)

        logger.info(f"Loaded data from {filepath}")
        return data

    def load_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load specific data file."""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return None

        with open(filepath, "r") as f:
            data = json.load(f)

        return data

    def export_to_csv(
        self, data: Dict[str, Any], export_dir: str = "exports"
    ) -> Dict[str, str]:
        """Export data to separate CSV files for each data type."""
        os.makedirs(export_dir, exist_ok=True)
        exported_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # All transaction data types to export
        data_types_to_export = [
            "orders",
            "fills",
            "positions",
            "settlements",
            "transactions",
            "account_history",
        ]

        # Export each data type
        for data_type in data_types_to_export:
            if (
                data_type in data
                and data[data_type]
                and isinstance(data[data_type], list)
            ):
                df = pd.DataFrame(data[data_type])
                filename = f"{data_type}_{timestamp}.csv"
                filepath = os.path.join(export_dir, filename)
                df.to_csv(filepath, index=False)
                exported_files[data_type] = filepath
                logger.info(f"Exported {data_type} to {filepath}")

        # Export structured data (balance, user_info) as JSON files if they have content
        structured_data = ["balance", "user_info"]
        for data_type in structured_data:
            if (
                data_type in data
                and data[data_type]
                and isinstance(data[data_type], dict)
                and data[data_type] != {"status": "success", "raw_response": ""}
            ):

                filename = f"{data_type}_{timestamp}.json"
                filepath = os.path.join(export_dir, filename)
                with open(filepath, "w") as f:
                    json.dump(data[data_type], f, indent=2, default=str)
                exported_files[data_type] = filepath
                logger.info(f"Exported {data_type} to {filepath}")

        return exported_files

    def get_data_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics of all transaction data."""
        summary = {
            "fetched_at": data.get("fetched_at", "Unknown"),
            "data_counts": {},
            "date_ranges": {},
            "account_info": {},
        }

        # All transaction data types to summarize
        transaction_data_types = [
            "orders",
            "fills",
            "positions",
            "settlements",
            "transactions",
            "account_history",
        ]

        # Count records for each data type
        for data_type in transaction_data_types:
            if data_type in data and isinstance(data[data_type], list):
                summary["data_counts"][data_type] = len(data[data_type])

                # Try to get date range for time-based data
                if data[data_type]:
                    dates = []
                    for item in data[data_type]:
                        if not isinstance(item, dict):
                            continue
                        # Look for common date fields
                        for date_field in [
                            "created_at",
                            "timestamp",
                            "date",
                            "ts",
                            "settled_at",
                            "updated_at",
                        ]:
                            if date_field in item and item[date_field]:
                                try:
                                    dates.append(item[date_field])
                                    break
                                except:
                                    continue

                    if dates:
                        summary["date_ranges"][data_type] = {
                            "earliest": min(dates),
                            "latest": max(dates),
                        }
            else:
                summary["data_counts"][data_type] = 0

        # Add account info summary
        if "balance" in data and isinstance(data["balance"], dict):
            summary["account_info"]["balance"] = data["balance"]

        if "user_info" in data and isinstance(data["user_info"], dict):
            summary["account_info"]["user_info"] = data["user_info"]

        return summary

    def list_data_files(self) -> List[Dict[str, Any]]:
        """List all available data files with metadata."""
        files = []
        json_files = [f for f in os.listdir(self.data_dir) if f.endswith(".json")]

        for filename in sorted(json_files):
            filepath = os.path.join(self.data_dir, filename)
            stat = os.stat(filepath)

            files.append(
                {
                    "filename": filename,
                    "filepath": filepath,
                    "size_bytes": stat.st_size,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )

        return files

    def cleanup_old_files(self, keep_days: int = 30):
        """Remove data files older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        removed_count = 0

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.data_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))

                if file_time < cutoff_date:
                    os.remove(filepath)
                    removed_count += 1
                    logger.info(f"Removed old file: {filename}")

        logger.info(
            f"Cleanup complete. Removed {removed_count} files older than {keep_days} days."
        )


def main():
    """Test the data manager functionality."""
    dm = DataManager()

    # List available files
    files = dm.list_data_files()
    if files:
        print("\nAvailable data files:")
        for file_info in files:
            print(f"  {file_info['filename']} ({file_info['size_bytes']} bytes)")

        # Load latest data
        data = dm.load_latest_data()
        if data:
            summary = dm.get_data_summary(data)
            print(f"\nData Summary:")
            print(f"  Fetched at: {summary['fetched_at']}")
            print(f"  Record counts: {summary['data_counts']}")

            # Export to CSV
            exported = dm.export_to_csv(data)
            print(f"\nExported CSV files: {list(exported.values())}")
    else:
        print("No data files found. Run fetch_data.py first.")


if __name__ == "__main__":
    main()
