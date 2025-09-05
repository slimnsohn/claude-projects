"""
Debug Kalshi Raw Market Data
Examines the actual raw data from Kalshi API to identify timestamp issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from kalshi_client import KalshiClientUpdated as KalshiClient
import json
from datetime import datetime, timezone

def examine_ticker_date_parsing(sport='mlb', limit=10):
    """Examine how to extract dates from Kalshi tickers"""
    print("=" * 80)
    print(f"KALSHI TICKER DATE EXTRACTION ANALYSIS")
    print("=" * 80)
    
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        raw_data = client.search_sports_markets(sport)
        
        if not raw_data.get('success'):
            print(f"❌ ERROR: {raw_data.get('error')}")
            return
        
        markets = raw_data.get('data', [])
        print(f"✅ Found {len(markets)} raw markets")
        print()
        
        print("TICKER DATE PARSING EXAMPLES:")
        print("=" * 60)
        
        for i, market in enumerate(markets[:limit], 1):
            ticker = market.get('ticker', 'N/A')
            title = market.get('title', 'N/A')
            
            print(f"{i}. {ticker}")
            print(f"   Title: {title}")
            
            # Parse date from ticker: KXMLBGAME-25AUG21HOUBAL-HOU
            if '-' in ticker:
                parts = ticker.split('-')
                if len(parts) >= 2:
                    date_part = parts[1][:7]  # First 7 characters: 25AUG21
                    print(f"   Date part: {date_part}")
                    
                    # Parse 25AUG21 format
                    try:
                        day = date_part[:2]       # 25
                        month_str = date_part[2:5] # AUG
                        year = date_part[5:7]     # 21
                        
                        # Convert month abbreviation
                        month_map = {
                            'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
                            'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08', 
                            'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
                        }
                        month = month_map.get(month_str, '??')
                        
                        # Assume 20XX for year
                        full_year = f"20{year}"
                        
                        parsed_date = f"{full_year}-{month}-{day}"
                        print(f"   ✅ Parsed date: {parsed_date}")
                        
                        # Validate
                        from datetime import datetime
                        dt = datetime.strptime(parsed_date, '%Y-%m-%d')
                        print(f"   ✅ Validated: {dt.strftime('%B %d, %Y')}")
                        
                    except Exception as e:
                        print(f"   ❌ Parse error: {e}")
                else:
                    print(f"   ❌ Ticker format unexpected")
            else:
                print(f"   ❌ No date found in ticker")
            
            print()
    
    except Exception as e:
        print(f"❌ ERROR: {e}")

def examine_raw_kalshi_data(sport='mlb', limit=10):
    """Examine raw Kalshi market data before any processing"""
    print("=" * 80)
    print(f"RAW KALSHI {sport.upper()} MARKET DATA EXAMINATION")
    print("=" * 80)
    
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        
        # Get raw search results - no normalization yet
        print(f"Step 1: Searching for {sport} markets...")
        raw_data = client.search_sports_markets(sport)
        
        if not raw_data.get('success'):
            print(f"❌ ERROR: {raw_data.get('error')}")
            return
        
        markets = raw_data.get('data', [])
        print(f"✅ Found {len(markets)} raw markets")
        print(f"Sport breakdown: {raw_data.get('sport_counts', {})}")
        print()
        
        # Examine first few markets in detail
        print("DETAILED RAW MARKET EXAMINATION:")
        print("=" * 60)
        
        for i, market in enumerate(markets[:limit], 1):
            print(f"\n{i}. MARKET RAW DATA:")
            print("-" * 40)
            
            # Show key fields
            ticker = market.get('ticker', 'N/A')
            title = market.get('title', 'N/A')
            status = market.get('status', 'N/A')
            detected_sport = market.get('detected_sport', 'N/A')
            
            print(f"Ticker: {ticker}")
            print(f"Title: {title}")
            print(f"Status: {status}")
            print(f"Detected Sport: {detected_sport}")
            
            # TIMESTAMP FIELDS - This is the key issue
            print("\n📅 TIMESTAMP FIELDS:")
            close_time = market.get('close_time')
            expire_time = market.get('expire_time') 
            start_time = market.get('start_time')
            created_time = market.get('created_time')
            updated_time = market.get('updated_time')
            
            print(f"close_time: {close_time}")
            print(f"expire_time: {expire_time}")
            print(f"start_time: {start_time}")
            print(f"created_time: {created_time}")
            print(f"updated_time: {updated_time}")
            
            # Try to parse and understand these timestamps
            print("\n🔍 TIMESTAMP ANALYSIS:")
            for field_name, timestamp_str in [
                ('close_time', close_time),
                ('expire_time', expire_time),
                ('start_time', start_time)
            ]:
                if timestamp_str:
                    try:
                        # Try to parse the timestamp
                        if timestamp_str.endswith('Z'):
                            clean_ts = timestamp_str[:-1] + '+00:00'
                        else:
                            clean_ts = timestamp_str
                            
                        dt = datetime.fromisoformat(clean_ts)
                        
                        print(f"{field_name:12}: {timestamp_str}")
                        print(f"{'':12}  → Parsed: {dt}")
                        print(f"{'':12}  → Display: {dt.strftime('%Y-%m-%d %H:%M UTC')}")
                        
                    except Exception as e:
                        print(f"{field_name:12}: {timestamp_str} (PARSE ERROR: {e})")
                else:
                    print(f"{field_name:12}: None")
            
            # PRICING FIELDS  
            print("\n💰 PRICING FIELDS:")
            yes_bid = market.get('yes_bid')
            no_bid = market.get('no_bid')
            yes_ask = market.get('yes_ask')
            no_ask = market.get('no_ask')
            yes_price = market.get('yes_price')
            no_price = market.get('no_price')
            
            print(f"yes_bid: {yes_bid} (cents)")
            print(f"no_bid: {no_bid} (cents)")
            print(f"yes_ask: {yes_ask}")
            print(f"no_ask: {no_ask}")
            print(f"yes_price: {yes_price}")
            print(f"no_price: {no_price}")
            
            if yes_bid and no_bid:
                print(f"Pricing: {yes_bid}% / {no_bid}%")
            
            # OTHER RELEVANT FIELDS
            print("\n📋 OTHER FIELDS:")
            category = market.get('category')
            subcategory = market.get('subcategory')
            market_type = market.get('market_type')
            
            print(f"category: {category}")
            print(f"subcategory: {subcategory}")
            print(f"market_type: {market_type}")
            
            print("\n" + "="*60)
    
    except Exception as e:
        print(f"❌ ERROR examining raw data: {e}")

def compare_timestamp_fields():
    """Compare different timestamp fields to understand which one to use"""
    print("\n" + "=" * 80)
    print("TIMESTAMP FIELD COMPARISON")
    print("=" * 80)
    
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        raw_data = client.search_sports_markets('mlb')
        
        if not raw_data.get('success'):
            print(f"❌ ERROR: {raw_data.get('error')}")
            return
        
        markets = raw_data.get('data', [])
        print(f"Analyzing timestamp fields from {len(markets)} markets...\n")
        
        # Analyze patterns in timestamp fields
        field_stats = {
            'close_time': {'count': 0, 'sample_values': []},
            'expire_time': {'count': 0, 'sample_values': []},
            'start_time': {'count': 0, 'sample_values': []}
        }
        
        for market in markets[:20]:  # Check first 20
            for field in field_stats.keys():
                value = market.get(field)
                if value:
                    field_stats[field]['count'] += 1
                    if len(field_stats[field]['sample_values']) < 3:
                        field_stats[field]['sample_values'].append(value)
        
        print("TIMESTAMP FIELD USAGE:")
        for field, stats in field_stats.items():
            print(f"{field:12}: {stats['count']}/{len(markets[:20])} markets have this field")
            for sample in stats['sample_values']:
                try:
                    if sample.endswith('Z'):
                        clean_ts = sample[:-1] + '+00:00'
                    else:
                        clean_ts = sample
                    dt = datetime.fromisoformat(clean_ts)
                    print(f"{'':14} Sample: {dt.strftime('%Y-%m-%d %H:%M')} ({sample})")
                except:
                    print(f"{'':14} Sample: PARSE ERROR ({sample})")
        
        # Recommendation
        print(f"\n🎯 RECOMMENDATION:")
        best_field = max(field_stats.keys(), key=lambda x: field_stats[x]['count'])
        print(f"Use '{best_field}' as primary timestamp field")
        print(f"It appears in {field_stats[best_field]['count']}/{len(markets[:20])} markets")
        
    except Exception as e:
        print(f"❌ ERROR in timestamp comparison: {e}")

def show_current_normalization_vs_raw():
    """Show how current normalization handles the data vs raw"""
    print("\n" + "=" * 80)
    print("CURRENT NORMALIZATION VS RAW DATA")
    print("=" * 80)
    
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        
        # Get raw data
        raw_data = client.search_sports_markets('mlb')
        if not raw_data.get('success'):
            print(f"❌ ERROR: {raw_data.get('error')}")
            return
        
        # Get normalized data
        normalized_data = client.normalize_kalshi_data(raw_data, 15)
        
        raw_markets = raw_data.get('data', [])
        print(f"Raw markets: {len(raw_markets)}")
        print(f"Normalized games: {len(normalized_data)}")
        print(f"Markets lost in normalization: {len(raw_markets) - len(normalized_data)}")
        print()
        
        # Compare first few
        print("NORMALIZATION COMPARISON (first 3):")
        for i in range(min(3, len(raw_markets))):
            if i < len(normalized_data):
                raw_market = raw_markets[i]
                normalized_game = normalized_data[i]
                
                print(f"\n{i+1}. COMPARISON:")
                print(f"Raw title: {raw_market.get('title', 'N/A')}")
                print(f"Raw close_time: {raw_market.get('close_time', 'N/A')}")
                print(f"Raw expire_time: {raw_market.get('expire_time', 'N/A')}")
                print(f"→ Normalized game_time: {normalized_game.get('game_time', 'N/A')}")
                print(f"→ Normalized game_time_display: {normalized_game.get('game_time_display', 'N/A')}")
                print(f"→ Normalized teams: {normalized_game.get('away_team', 'N/A')} @ {normalized_game.get('home_team', 'N/A')}")
            else:
                raw_market = raw_markets[i]
                print(f"\n{i+1}. RAW MARKET (NOT NORMALIZED):")
                print(f"Title: {raw_market.get('title', 'N/A')}")
                print(f"Reason: Likely filtered out or failed team extraction")
    
    except Exception as e:
        print(f"❌ ERROR in normalization comparison: {e}")

def main():
    """Main debug function"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\debug_kalshi_raw_data.py"
    print(f"Script: {script_path}")
    print()
    print("KALSHI RAW DATA DEBUGGER")
    print("Investigating ticker date extraction and market data issues")
    print("=" * 80)
    
    # NEW: Examine ticker date parsing first
    examine_ticker_date_parsing('mlb', 5)
    
    # Examine raw market data in detail
    examine_raw_kalshi_data('mlb', 5)
    
    # Compare timestamp fields
    compare_timestamp_fields()
    
    # Compare normalization
    show_current_normalization_vs_raw()
    
    print("\n" + "=" * 80)
    print("KALSHI DATA DEBUG COMPLETE")
    print("=" * 80)
    print("\n🎯 KEY FINDINGS:")
    print("1. Game dates are embedded in tickers: KXMLBGAME-25AUG21HOUBAL-HOU")
    print("   Format: DD+MMM+YY (25AUG21 = August 21, 2025)")
    print("2. close_time/expire_time are market settlement dates (September)")
    print("3. We need to extract game date from ticker, not timestamps")
    print()
    print("🔧 REQUIRED FIX:")
    print("Update Kalshi client to parse dates from tickers instead of close_time")
    print()
    print(f"Script path: {script_path}")

if __name__ == "__main__":
    main()