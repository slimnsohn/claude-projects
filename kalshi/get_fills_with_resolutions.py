#!/usr/bin/env python3
"""
Script to retrieve all fills with market resolution data.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from git_clients import KalshiHttpClient, Environment
import time

# Load environment variables
load_dotenv()
env = Environment.PROD
KEYID = os.getenv('DEMO_KEYID') if env == Environment.DEMO else os.getenv('PROD_KEYID')
KEYFILE = os.getenv('DEMO_KEYFILE') if env == Environment.DEMO else os.getenv('PROD_KEYFILE')

try:
    with open(KEYFILE, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )
except FileNotFoundError:
    raise FileNotFoundError(f"Private key file not found at {KEYFILE}")
except Exception as e:
    raise Exception(f"Error loading private key: {str(e)}")

# Initialize the HTTP client
client = KalshiHttpClient(
    key_id=KEYID,
    private_key=private_key,
    environment=env
)

def get_fills_with_resolutions():
    """Retrieve all fills and get resolution data for each market."""
    print("=" * 80)
    print("RETRIEVING ALL FILLS WITH RESOLUTIONS")
    print("=" * 80)
    
    # First get all fills
    print("1. Getting all fills...")
    fills_response = client.get_fills(limit=1000)
    
    if 'fills' not in fills_response:
        print(f"No fills found: {fills_response}")
        return []
    
    fills = fills_response['fills']
    print(f"   Found {len(fills)} fills")
    
    # Get unique tickers
    unique_tickers = list(set(fill.get('ticker') for fill in fills))
    print(f"   Found {len(unique_tickers)} unique markets")
    
    # Get market data for each ticker
    print("\n2. Getting market resolution data...")
    market_data = {}
    
    for i, ticker in enumerate(unique_tickers, 1):
        print(f"   Getting market {i}/{len(unique_tickers)}: {ticker}")
        
        try:
            market_info = client.get_market(ticker)
            market_data[ticker] = market_info
            
            # Rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            print(f"      Error getting market {ticker}: {e}")
            market_data[ticker] = {"error": str(e)}
    
    # Analyze fills with resolution data
    print("\n3. Analyzing fills with resolutions...")
    
    enhanced_fills = []
    total_pnl = 0
    
    for fill in fills:
        ticker = fill.get('ticker')
        market_info = market_data.get(ticker, {})
        
        enhanced_fill = fill.copy()
        
        # Add market resolution data
        if 'market' in market_info:
            market = market_info['market']
            enhanced_fill['market_status'] = market.get('status')
            enhanced_fill['market_close_time'] = market.get('close_time')
            enhanced_fill['market_result'] = market.get('result')
            enhanced_fill['final_price'] = market.get('last_price')
            
            # Calculate P&L if market is resolved
            if market.get('status') == 'closed' and market.get('result') is not None:
                purchase_price = fill.get('yes_price', 0)
                count = fill.get('count', 0)
                side = fill.get('side', 'yes')
                action = fill.get('action', 'buy')
                
                # Determine final value based on result
                if market.get('result') == 'yes':
                    final_value = 100  # Yes resolves to 100¢
                else:
                    final_value = 0    # No resolves to 0¢
                
                # Calculate P&L based on side
                if side == 'yes':
                    if action == 'buy':
                        pnl = (final_value - purchase_price) * count
                    else:  # sell
                        pnl = (purchase_price - final_value) * count
                else:  # no side
                    no_purchase_price = fill.get('no_price', 0)
                    if action == 'buy':
                        pnl = ((100 - final_value) - no_purchase_price) * count
                    else:  # sell
                        pnl = (no_purchase_price - (100 - final_value)) * count
                
                enhanced_fill['pnl_cents'] = pnl
                enhanced_fill['pnl_dollars'] = pnl / 100
                total_pnl += pnl
            else:
                enhanced_fill['pnl_cents'] = None
                enhanced_fill['pnl_dollars'] = None
                
        enhanced_fills.append(enhanced_fill)
    
    # Display results
    print("\n" + "=" * 80)
    print("FILLS WITH RESOLUTION ANALYSIS")
    print("=" * 80)
    
    resolved_fills = [f for f in enhanced_fills if f.get('market_status') == 'closed']
    open_fills = [f for f in enhanced_fills if f.get('market_status') != 'closed']
    
    print(f"Total fills: {len(enhanced_fills)}")
    print(f"Resolved markets: {len(resolved_fills)}")
    print(f"Open/Active markets: {len(open_fills)}")
    
    if total_pnl != 0:
        print(f"Total P&L from resolved markets: ${total_pnl/100:.2f}")
    
    # Show resolved markets with P&L
    print(f"\nResolved Markets with P&L:")
    resolved_with_pnl = [f for f in resolved_fills if f.get('pnl_cents') is not None]
    
    for fill in resolved_with_pnl[:10]:  # Show first 10
        ticker = fill.get('ticker')
        count = fill.get('count', 0)
        side = fill.get('side')
        action = fill.get('action')
        purchase_price = fill.get('yes_price', fill.get('no_price', 0))
        result = fill.get('market_result')
        pnl = fill.get('pnl_dollars', 0)
        
        outcome = "✅ WIN" if pnl > 0 else "❌ LOSS" if pnl < 0 else "➖ BREAK EVEN"
        
        print(f"  {ticker[:40]:<40} | {action} {count:>4} {side} @ {purchase_price:>3}¢ | Result: {result:>3} | {outcome} ${pnl:>7.2f}")
    
    # Show top open positions
    print(f"\nTop Open Positions:")
    open_positions = {}
    for fill in open_fills:
        ticker = fill.get('ticker')
        count = fill.get('count', 0)
        side = fill.get('side')
        action = fill.get('action')
        
        key = f"{ticker}_{side}"
        if key not in open_positions:
            open_positions[key] = {'ticker': ticker, 'side': side, 'net_position': 0, 'total_cost': 0}
        
        if action == 'buy':
            open_positions[key]['net_position'] += count
            open_positions[key]['total_cost'] += count * fill.get('yes_price' if side == 'yes' else 'no_price', 0)
        else:  # sell
            open_positions[key]['net_position'] -= count
            open_positions[key]['total_cost'] -= count * fill.get('yes_price' if side == 'yes' else 'no_price', 0)
    
    # Filter to only net long positions
    net_positions = {k: v for k, v in open_positions.items() if v['net_position'] > 0}
    
    for i, (key, pos) in enumerate(list(net_positions.items())[:10], 1):
        avg_price = pos['total_cost'] / pos['net_position'] if pos['net_position'] > 0 else 0
        print(f"  {i}. {pos['ticker'][:50]:<50} | {pos['net_position']:>4} {pos['side']} @ ${avg_price/100:.2f} avg")
    
    # Save detailed data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data/fills_with_resolutions_{timestamp}.json"
    current_filename = "data/fills_with_resolutions_current.json"
    
    os.makedirs("data", exist_ok=True)
    
    data_to_save = {
        "retrieved_at": datetime.now().isoformat(),
        "total_fills": len(enhanced_fills),
        "resolved_fills": len(resolved_fills),
        "open_fills": len(open_fills),
        "total_pnl_cents": total_pnl,
        "total_pnl_dollars": total_pnl / 100,
        "fills": enhanced_fills,
        "market_data": market_data
    }
    
    # Save timestamped version
    with open(filename, 'w') as f:
        json.dump(data_to_save, f, indent=2, default=str)
    
    # Save current version (copy of latest)
    with open(current_filename, 'w') as f:
        json.dump(data_to_save, f, indent=2, default=str)
    
    print(f"\nDetailed data saved to: {filename}")
    print(f"Current data saved to: {current_filename}")
    return enhanced_fills

if __name__ == "__main__":
    fills = get_fills_with_resolutions()
    print(f"\nSUCCESS: Enhanced {len(fills)} fills with resolution data")