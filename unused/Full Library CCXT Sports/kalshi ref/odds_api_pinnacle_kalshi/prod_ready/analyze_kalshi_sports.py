#!/usr/bin/env python3
"""
Analyze what sports are actually available on Kalshi
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.kalshi_client import KalshiClientUpdated as KalshiClient
from collections import defaultdict

def analyze_available_sports():
    """Analyze what sports are actually available on Kalshi"""
    
    print("ANALYZING AVAILABLE SPORTS ON KALSHI")
    print("=" * 60)
    
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(project_root, 'keys', 'kalshi_credentials.txt')
        client = KalshiClient(creds_path)
        
        # Get all markets
        all_markets = client._get_all_markets_paginated()
        all_markets_data = all_markets.get('data', [])
        
        print(f"Analyzing {len(all_markets_data)} total markets...")
        print()
        
        # Categorize by ticker patterns
        ticker_patterns = defaultdict(list)
        
        for market in all_markets_data:
            ticker = market.get('ticker', '')
            title = market.get('title', '')
            
            # Extract the main ticker prefix (before first hyphen)
            ticker_prefix = ticker.split('-')[0] if '-' in ticker else ticker
            
            ticker_patterns[ticker_prefix].append({
                'ticker': ticker,
                'title': title
            })
        
        # Sort by count and show the most common patterns
        sorted_patterns = sorted(ticker_patterns.items(), key=lambda x: len(x[1]), reverse=True)
        
        print("TOP MARKET CATEGORIES BY TICKER PREFIX:")
        print("-" * 60)
        
        for i, (prefix, markets) in enumerate(sorted_patterns[:20], 1):
            print(f"{i:2d}. {prefix:<20} ({len(markets):4d} markets)")
            # Show a few examples
            for j, market in enumerate(markets[:3], 1):
                title = market['title'][:60] + "..." if len(market['title']) > 60 else market['title']
                print(f"     {j}. {title}")
            if len(markets) > 3:
                print(f"     ... and {len(markets) - 3} more")
            print()
        
        print("=" * 60)
        
        # Look specifically for sports-related patterns
        print("SPORTS-RELATED PATTERNS:")
        print("-" * 40)
        
        sports_keywords = ['game', 'sport', 'football', 'baseball', 'basketball', 'soccer', 'nfl', 'mlb', 'nba']
        
        for prefix, markets in sorted_patterns:
            prefix_lower = prefix.lower()
            if any(keyword in prefix_lower for keyword in sports_keywords):
                print(f"{prefix}: {len(markets)} markets")
                # Show one example
                if markets:
                    example_title = markets[0]['title'][:80]
                    print(f"  Example: {example_title}")
        
        print()
        print("CONCLUSION:")
        print("- Check which sports categories actually exist")
        print("- NFL games may not be available during off-season")
        print("- Kalshi may focus on different types of markets")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_available_sports()