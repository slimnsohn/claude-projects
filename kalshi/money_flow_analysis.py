#!/usr/bin/env python3
"""
Complete money flow analysis: $17k deposits vs current balance + P&L + open positions
"""

import json
import os
from collections import defaultdict
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from git_clients import KalshiHttpClient, Environment

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

def load_fills_data():
    """Load the current fills data."""
    filename = "data/fills_with_resolutions_current.json"
    
    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found!")
        print("Run get_fills_with_resolutions.py first to generate the data.")
        return None
    
    with open(filename, 'r') as f:
        return json.load(f)

def money_flow_analysis():
    """Complete breakdown of $17k deposits vs current state."""
    print("=" * 80)
    print("COMPLETE MONEY FLOW ANALYSIS")
    print("=" * 80)
    
    # 1. Get current balance
    print("1. Getting current balance...")
    balance_response = client.get_balance()
    current_balance_cents = balance_response.get('balance', 0)
    current_balance_dollars = current_balance_cents / 100
    print(f"   Current balance: ${current_balance_dollars:,.2f}")
    
    # 2. Load fills data
    print("\n2. Loading trading data...")
    data = load_fills_data()
    if not data:
        return
    
    fills = data.get('fills', [])
    print(f"   Loaded {len(fills)} fills")
    
    # 3. Calculate position values and P&L
    print("\n3. Analyzing positions...")
    
    # Group by ticker for position analysis
    positions = defaultdict(lambda: {
        'ticker': '',
        'net_position_yes': 0,
        'net_position_no': 0,
        'total_cost': 0,
        'market_status': 'unknown',
        'market_result': None,
        'realized_pnl': 0,
        'current_value': 0,
        'fills': []
    })
    
    total_money_spent = 0
    total_realized_pnl = 0
    
    # Process each fill
    for fill in fills:
        ticker = fill.get('ticker', 'Unknown')
        side = fill.get('side', 'yes')
        action = fill.get('action', 'buy')
        count = fill.get('count', 0)
        yes_price = fill.get('yes_price', 0)
        no_price = fill.get('no_price', 0)
        
        pos = positions[ticker]
        pos['ticker'] = ticker
        pos['market_status'] = fill.get('market_status', 'unknown')
        pos['market_result'] = fill.get('market_result')
        pos['fills'].append(fill)
        
        # Calculate money spent/received
        if side == 'yes':
            price_per_share = yes_price / 100  # Convert cents to dollars
            if action == 'buy':
                money_flow = count * price_per_share
                total_money_spent += money_flow
                pos['total_cost'] += money_flow
                pos['net_position_yes'] += count
            else:  # sell
                money_flow = count * price_per_share
                total_money_spent -= money_flow  # Money received back
                pos['total_cost'] -= money_flow
                pos['net_position_yes'] -= count
        else:  # no side
            price_per_share = no_price / 100
            if action == 'buy':
                money_flow = count * price_per_share
                total_money_spent += money_flow
                pos['total_cost'] += money_flow
                pos['net_position_no'] += count
            else:  # sell
                money_flow = count * price_per_share
                total_money_spent -= money_flow
                pos['total_cost'] -= money_flow
                pos['net_position_no'] -= count
    
    # Calculate realized P&L and current position values
    total_open_position_value = 0
    
    for ticker, pos in positions.items():
        status_lower = pos['market_status'].lower() if pos['market_status'] else ''
        
        if status_lower in ['closed', 'finalized', 'settled'] and pos['market_result'] is not None:
            # Closed position - calculate realized P&L
            if pos['market_result'] == 'yes':
                final_value_yes = 1.0  # $1 per share
                final_value_no = 0.0
            else:
                final_value_yes = 0.0
                final_value_no = 1.0
            
            # Calculate what we got back
            payout_yes = pos['net_position_yes'] * final_value_yes
            payout_no = pos['net_position_no'] * final_value_no
            total_payout = payout_yes + payout_no
            
            # Realized P&L = what we got back - what we spent
            pos['realized_pnl'] = total_payout - pos['total_cost']
            total_realized_pnl += pos['realized_pnl']
            
        else:
            # Open position - estimate current value (assuming we could sell at break-even)
            # For open positions, current value = what we spent (conservative estimate)
            pos['current_value'] = pos['total_cost']
            total_open_position_value += pos['current_value']
    
    # 4. Summary calculations
    print(f"\n4. Money flow summary...")
    
    deposited = 16000  # User deposited $16k
    accounted_for = current_balance_dollars + total_realized_pnl + total_open_position_value
    
    print(f"\n" + "=" * 80)
    print(f"MONEY FLOW BREAKDOWN")
    print(f"=" * 80)
    print(f"MONEY IN:")
    print(f"   Deposited:                     ${deposited:>10,.2f}")
    print(f"")
    print(f"MONEY ALLOCATION:")
    print(f"   Current cash balance:          ${current_balance_dollars:>10,.2f}")
    print(f"   Realized P&L (closed positions): ${total_realized_pnl:>10,.2f}")
    print(f"   Open position value (cost):    ${total_open_position_value:>10,.2f}")
    print(f"   " + "-" * 50)
    print(f"   Total accounted for:           ${accounted_for:>10,.2f}")
    print(f"")
    print(f"RECONCILIATION:")
    difference = deposited - accounted_for
    print(f"   Deposited:                     ${deposited:>10,.2f}")
    print(f"   Accounted for:                 ${accounted_for:>10,.2f}")
    print(f"   Difference:                    ${difference:>10,.2f}")
    
    if abs(difference) < 10:
        print(f"   BALANCED (difference < $10)")
    else:
        print(f"   IMBALANCE detected")
        print(f"   Possible reasons:")
        print(f"   - Fees/commissions not tracked")
        print(f"   - Partial fills or cancellations")
        print(f"   - Deposits/withdrawals not in fills data")
    
    # 5. Detailed breakdown
    print(f"\n" + "=" * 80)
    print(f"DETAILED POSITION BREAKDOWN")
    print(f"=" * 80)
    
    # Show closed positions
    closed_positions = {k: v for k, v in positions.items() if v['market_status'].lower() in ['closed', 'finalized', 'settled']}
    open_positions = {k: v for k, v in positions.items() if v['market_status'].lower() not in ['closed', 'finalized', 'settled']}
    
    if closed_positions:
        print(f"\nCLOSED POSITIONS ({len(closed_positions)} markets):")
        print(f"   {'Market':<40} | {'Cost':<10} | {'P&L':<10} | {'Result'}")
        print(f"   " + "-" * 75)
        
        sorted_closed = sorted(closed_positions.items(), key=lambda x: x[1]['realized_pnl'], reverse=True)
        for ticker, pos in sorted_closed[:20]:  # Top 20
            result = pos['market_result'] or 'unknown'
            print(f"   {ticker[:39]:<40} | ${pos['total_cost']:>8.2f} | ${pos['realized_pnl']:>8.2f} | {result}")
        
        if len(sorted_closed) > 20:
            remaining = len(sorted_closed) - 20
            remaining_cost = sum(pos['total_cost'] for _, pos in sorted_closed[20:])
            remaining_pnl = sum(pos['realized_pnl'] for _, pos in sorted_closed[20:])
            print(f"   ... and {remaining} more positions     | ${remaining_cost:>8.2f} | ${remaining_pnl:>8.2f} | various")
    
    if open_positions:
        print(f"\nOPEN POSITIONS ({len(open_positions)} markets):")
        print(f"   {'Market':<40} | {'Cost':<10} | {'Status'}")
        print(f"   " + "-" * 65)
        
        sorted_open = sorted(open_positions.items(), key=lambda x: x[1]['current_value'], reverse=True)
        for ticker, pos in sorted_open:
            print(f"   {ticker[:39]:<40} | ${pos['current_value']:>8.2f} | Open")
    
    print(f"\n" + "=" * 80)
    
    return {
        'deposited': deposited,
        'current_balance': current_balance_dollars,
        'realized_pnl': total_realized_pnl,
        'open_position_value': total_open_position_value,
        'total_accounted': accounted_for,
        'difference': difference
    }

if __name__ == "__main__":
    result = money_flow_analysis()
    
    if result:
        print(f"\nSUMMARY:")
        if abs(result['difference']) < 50:
            print(f"Your $17k is fully accounted for!")
        else:
            print(f"There's a ${abs(result['difference']):.2f} discrepancy to investigate")