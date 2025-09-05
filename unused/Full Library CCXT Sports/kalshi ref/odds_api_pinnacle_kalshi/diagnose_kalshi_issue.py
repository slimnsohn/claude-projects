"""
Diagnose Kalshi Issue - Why is the simple test returning nothing?
Step-by-step debugging to identify the problem
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

def test_imports():
    """Test if imports are working"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\diagnose_kalshi_issue.py"
    print(f"Script: {script_path}")
    print()
    print("=== STEP 1: TESTING IMPORTS ===")
    
    try:
        print("Importing KalshiClient...")
        from kalshi_client import KalshiClientUpdated as KalshiClient
        print("SUCCESS: KalshiClient imported")
        return True
    except Exception as e:
        print(f"ERROR importing KalshiClient: {e}")
        return False

def test_client_creation():
    """Test if client can be created"""
    print("\n=== STEP 2: TESTING CLIENT CREATION ===")
    
    try:
        from kalshi_client import KalshiClientUpdated as KalshiClient
        print("Creating KalshiClient...")
        client = KalshiClient("keys/kalshi_credentials.txt")
        print("SUCCESS: KalshiClient created")
        return client
    except Exception as e:
        print(f"ERROR creating KalshiClient: {e}")
        return None

def test_ticker_parsing(client):
    """Test ticker parsing method"""
    print("\n=== STEP 3: TESTING TICKER PARSING ===")
    
    if not client:
        print("ERROR: No client available")
        return
    
    try:
        print("Testing _extract_date_from_ticker method...")
        
        # Test with a simple ticker
        ticker = "KXMLBGAME-25AUG21HOUBAL-HOU"
        print(f"Testing ticker: {ticker}")
        
        date, time = client._extract_date_from_ticker(ticker)
        print(f"Result: date={date}, time={time}")
        
        if date and time:
            print("SUCCESS: Ticker parsing works")
        else:
            print("ERROR: Ticker parsing failed")
            
    except Exception as e:
        print(f"ERROR in ticker parsing: {e}")

def test_market_search(client):
    """Test market search"""
    print("\n=== STEP 4: TESTING MARKET SEARCH ===")
    
    if not client:
        print("ERROR: No client available")
        return None
    
    try:
        print("Searching for MLB markets...")
        raw_data = client.search_sports_markets('mlb')
        
        print(f"Search result success: {raw_data.get('success')}")
        
        if raw_data.get('success'):
            markets = raw_data.get('data', [])
            print(f"Markets found: {len(markets)}")
            
            if markets:
                print("First market ticker:", markets[0].get('ticker'))
                print("First market title:", markets[0].get('title'))
                return raw_data
            else:
                print("WARNING: No markets in data")
        else:
            print(f"ERROR in search: {raw_data.get('error')}")
            
    except Exception as e:
        print(f"ERROR in market search: {e}")
    
    return None

def test_normalization(client, raw_data):
    """Test data normalization"""
    print("\n=== STEP 5: TESTING NORMALIZATION ===")
    
    if not client or not raw_data:
        print("ERROR: Missing client or raw data")
        return
    
    try:
        print("Normalizing data...")
        normalized_games = client.normalize_kalshi_data(raw_data, 15)
        
        print(f"Normalized games: {len(normalized_games)}")
        
        if normalized_games:
            game = normalized_games[0]
            print("First game:")
            print(f"  Teams: {game.get('away_team')} @ {game.get('home_team')}")
            print(f"  Date: {game.get('game_date')}")
            print(f"  Time: {game.get('game_time')}")
            print("SUCCESS: Normalization works")
        else:
            print("WARNING: No normalized games")
            
    except Exception as e:
        print(f"ERROR in normalization: {e}")

def test_file_paths():
    """Test if key files exist"""
    print("\n=== STEP 0: TESTING FILE PATHS ===")
    
    key_file = "keys/kalshi_credentials.txt"
    print(f"Checking for: {key_file}")
    
    if os.path.exists(key_file):
        print(f"SUCCESS: {key_file} exists")
        
        # Check if readable
        try:
            with open(key_file, 'r') as f:
                content = f.read().strip()
                if content:
                    print(f"SUCCESS: File has content ({len(content)} characters)")
                else:
                    print("WARNING: File is empty")
        except Exception as e:
            print(f"ERROR reading file: {e}")
    else:
        print(f"ERROR: {key_file} not found")
        print("Current directory:", os.getcwd())
        print("Files in current directory:", os.listdir('.'))

def main():
    """Run all diagnostic tests"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\diagnose_kalshi_issue.py"
    
    print("KALSHI DIAGNOSTIC TOOL")
    print("Finding out why test_kalshi_dates_simple.py returns nothing")
    print("=" * 60)
    
    # Step 0: Check file paths
    test_file_paths()
    
    # Step 1: Test imports
    if not test_imports():
        print("\nDIAGNOSIS: Import failure - check Python path")
        return
    
    # Step 2: Test client creation
    client = test_client_creation()
    if not client:
        print("\nDIAGNOSIS: Client creation failure - check credentials")
        return
    
    # Step 3: Test ticker parsing
    test_ticker_parsing(client)
    
    # Step 4: Test market search
    raw_data = test_market_search(client)
    
    # Step 5: Test normalization
    test_normalization(client, raw_data)
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print()
    print("If all steps show SUCCESS, then the issue might be:")
    print("1. Script execution environment")
    print("2. Output buffering")
    print("3. Exception being caught silently")
    print()
    print("Try running this diagnostic script to see where it fails.")
    print()
    print(f"Script path: {script_path}")

if __name__ == "__main__":
    main()