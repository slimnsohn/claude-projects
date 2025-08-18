# Kalshi Portfolio Checker Guide

## Quick Start

You now have working tools to check your Kalshi balances, deposits, and portfolio data. Here's how to use them:

## 🚀 Main Tools

### 1. **Complete Portfolio Check** (Recommended)
```bash
python rsa_kalshi_client.py
```
**What it does:**
- Checks all portfolio data (balance, orders, fills, positions, history)
- Saves detailed JSON report to `data/` folder
- Shows comprehensive summary

### 2. **Deposit-Focused Check**
```bash
python modern_deposit_checker.py
```
**What it does:**
- Focuses specifically on deposits and withdrawals
- Shows current balance
- Lists recent trading activity
- Saves deposit-focused report

### 3. **API Setup Test**
```bash
python test_api_setup.py
```
**What it does:**
- Tests if your API credentials are working
- Verifies connectivity to Kalshi
- Good for troubleshooting

## 📊 What You Can Check

### Portfolio Balance
- **Cash balance** - Available money for trading
- **Portfolio value** - Total account value
- **Settled positions** - Completed trades

### Deposits & Withdrawals
- **Deposit history** - All money added to account
- **Withdrawal history** - All money removed
- **Transaction dates** - When each deposit/withdrawal occurred
- **Total amounts** - Sum of all deposits/withdrawals

### Trading Activity
- **Open orders** - Current pending trades
- **Order history** - All orders (filled, cancelled, pending)
- **Fills/Trades** - Completed transactions
- **Current positions** - Active market positions
- **Profit/Loss** - Performance of trades

### Account History
- **Settlement records** - Market resolution payouts
- **Fee history** - Trading fees paid
- **Account events** - All account activity

## 🔧 Setup Requirements

### 1. API Credentials
Make sure your `.env` file has:
```
KALSHI_API_KEY=your_api_key_here
KALSHI_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----
your_private_key_here_with_proper_line_breaks
-----END RSA PRIVATE KEY-----
```

### 2. Get API Keys
1. Go to https://kalshi.com/account/profile
2. Find "API Keys" section
3. Click "Create New API Key"
4. Copy both the Key ID and Private Key
5. Add them to your `.env` file

## 📁 Output Files

All tools save data to the `data/` folder:

### JSON Files
- `rsa_kalshi_data_YYYYMMDD_HHMMSS.json` - Complete portfolio data
- `deposit_check_YYYYMMDD_HHMMSS.json` - Deposit-focused data

### File Contents
```json
{
  "exchange_status": {...},
  "balance": {
    "cash": 1000.50,
    "portfolio_value": 1250.00
  },
  "orders": [...],
  "fills": [...],
  "positions": [...],
  "account_history": [...]
}
```

## 🎯 Common Use Cases

### Check Current Balance
```bash
python rsa_kalshi_client.py
```
Look for the balance section in the output or JSON file.

### Find All Deposits
```bash
python modern_deposit_checker.py
```
This will show a summary of all deposits with dates and amounts.

### Get Trading Performance
```bash
python rsa_kalshi_client.py
```
Check the fills and positions sections for profit/loss data.

### Verify Recent Activity
```bash
python modern_deposit_checker.py
```
Shows recent orders and fills to verify latest activity.

## 🚨 Troubleshooting

### "Authentication Error"
- Check your API key and private key in `.env`
- Make sure private key has proper line breaks
- Verify your Kalshi account has API access enabled

### "No Data Found"
- Normal if you haven't made deposits or trades yet
- Check if your account is active and verified
- Try the test script: `python test_api_setup.py`

### "Connection Failed"
- Check internet connection
- Verify Kalshi API is not down
- Try again in a few minutes

## 📈 Dashboard (Optional)

For visual analysis:
1. Run any tool to generate data files
2. Start web server: `python -m http.server 8000`
3. Open http://localhost:8000/dashboard.html
4. Upload your JSON data file

## 🔄 Regular Monitoring

### Daily Check
```bash
python modern_deposit_checker.py
```

### Weekly Deep Dive
```bash
python rsa_kalshi_client.py
```

### After Trading Activity
```bash
python rsa_kalshi_client.py
```

## 🔐 Security Notes

- Never share your `.env` file
- Keep your private key secure
- The `.env` file is already in `.gitignore`
- API keys can be regenerated if compromised

## 💡 Pro Tips

1. **Save outputs** - All data is saved to JSON for later analysis
2. **Check regularly** - Monitor your portfolio performance
3. **Compare files** - Track changes over time
4. **Use dashboard** - Visual analysis is easier than reading JSON
5. **Test first** - Always run `test_api_setup.py` if having issues

Your portfolio checker is now ready to use! 🎉