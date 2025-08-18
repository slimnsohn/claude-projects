#!/usr/bin/env python3
"""
Modern deposit checker using RSA authentication.
Gets deposits and account history from Kalshi API.
"""

import json
from datetime import datetime
from rsa_kalshi_client import RSAKalshiClient
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_deposits():
    """Check deposits and account history using modern RSA authentication."""
    try:
        print("=== Modern Kalshi Deposit Checker ===")
        print("Using RSA API key authentication...")
        
        # Initialize the RSA client
        client = RSAKalshiClient()
        print("SUCCESS: RSA client initialized")
        
        # Test public endpoint first
        print("\nTesting API connectivity...")
        status = client.get_exchange_status()
        if not status:
            print("ERROR: Cannot connect to Kalshi API")
            return
        print(f"SUCCESS: API connected - Exchange active: {status.get('exchange_active', False)}")
        
        # Get account history (includes deposits, withdrawals, settlements)
        print("\nFetching account history...")
        history = client.get_account_history(limit=100)
        
        if not history:
            print("WARNING: No account history found or authentication failed")
            print("Note: This might be normal if you haven't made any trades/deposits yet")
        else:
            print(f"SUCCESS: Found {len(history)} account history records")
            
            # Filter for deposits specifically
            deposits = []
            withdrawals = []
            other_transactions = []
            
            for record in history:
                transaction_type = record.get('type', '').lower()
                amount = record.get('amount', 0)
                
                if 'deposit' in transaction_type:
                    deposits.append(record)
                elif 'withdrawal' in transaction_type:
                    withdrawals.append(record)
                else:
                    other_transactions.append(record)
            
            # Display results
            print(f"\nTransaction Summary:")
            print(f"  Deposits: {len(deposits)}")
            print(f"  Withdrawals: {len(withdrawals)}")
            print(f"  Other transactions: {len(other_transactions)}")
            
            if deposits:
                print(f"\nDeposits Found:")
                total_deposits = 0
                for i, deposit in enumerate(deposits, 1):
                    amount = deposit.get('amount', 0)
                    date = deposit.get('created_at', 'Unknown date')
                    desc = deposit.get('description', 'No description')
                    total_deposits += amount
                    print(f"  {i}. ${amount} on {date} - {desc}")
                
                print(f"  Total deposited: ${total_deposits}")
            else:
                print("\nNo deposits found in account history")
        
        # Get current balance
        print("\nFetching current balance...")
        balance = client.get_portfolio_balance()
        
        if balance:
            print(f"SUCCESS: Current balance retrieved")
            cash_balance = balance.get('cash', 0)
            print(f"  Cash balance: ${cash_balance}")
        else:
            print("WARNING: Could not retrieve current balance")
        
        # Get recent orders/fills for context
        print("\nFetching recent trading activity...")
        orders = client.get_portfolio_orders(limit=10)
        fills = client.get_portfolio_fills(limit=10)
        
        print(f"  Recent orders: {len(orders)}")
        print(f"  Recent fills: {len(fills)}")
        
        # Save detailed data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/deposit_check_{timestamp}.json"
        
        deposit_data = {
            "check_time": datetime.now().isoformat(),
            "exchange_status": status,
            "account_history": history,
            "current_balance": balance,
            "recent_orders": orders,
            "recent_fills": fills,
            "summary": {
                "total_deposits": len(deposits) if history else 0,
                "total_withdrawals": len(withdrawals) if history else 0,
                "current_cash": balance.get('cash', 0) if balance else 0
            }
        }
        
        import os
        os.makedirs("data", exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(deposit_data, f, indent=2, default=str)
        
        print(f"\nDetailed data saved to: {filename}")
        print("\nSUCCESS: Deposit check complete!")
        
        return deposit_data
        
    except Exception as e:
        logger.error(f"Error during deposit check: {e}")
        print(f"\nERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your API key and private key are correct in .env")
        print("2. Verify your Kalshi account is active")
        print("3. Check if you have any trading/deposit history")
        return None


def main():
    """Main function."""
    result = check_deposits()
    
    if result:
        print("\nSUCCESS: Deposit checker is working!")
        
        # Quick summary
        summary = result.get('summary', {})
        if summary.get('total_deposits', 0) > 0:
            print(f"Found {summary['total_deposits']} deposits")
        
        if summary.get('current_cash', 0) > 0:
            print(f"Current cash balance: ${summary['current_cash']}")
    else:
        print("\nNext steps:")
        print("1. Check your .env file has correct KALSHI_API_KEY and KALSHI_PRIVATE_KEY")
        print("2. Try the RSA client test: python rsa_kalshi_client.py")
        print("3. Make sure your Kalshi account has API access enabled")


if __name__ == "__main__":
    main()