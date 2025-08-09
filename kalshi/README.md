# Kalshi PNL Analysis Tool

A comprehensive tool for analyzing your Kalshi trading performance. Fetch data via API, calculate PNL metrics, and visualize results in a web dashboard.

## Features

### 📊 Data Fetching
- **Kalshi API Integration**: Fetch all your trading data directly from Kalshi
- **Comprehensive Data**: Orders, fills, positions, and account history
- **Local Storage**: Save data locally for analysis and backup
- **Multiple Formats**: Export to JSON and CSV formats

### 📈 PNL Analysis
- **Real-time Calculations**: Profit/loss, win rates, trading metrics
- **Position Analysis**: Performance breakdown by market
- **Time-based Analysis**: Daily PNL tracking and cumulative performance
- **Risk Metrics**: Drawdown analysis, profit factor, best/worst trades

### 🎯 Web Dashboard
- **Interactive Charts**: Cumulative PNL, win rates, performance trends
- **Key Metrics**: Total PNL, win rate, average wins/losses
- **Data Tables**: Position performance, best/worst trades
- **Responsive Design**: Works on desktop and mobile

## Quick Start

### 1. Setup
```bash
# Install dependencies
python setup.py

# Configure credentials (copy .env.example to .env and add your Kalshi API key)
cp .env.example .env
# Edit .env with your credentials
```

### 2. Fetch Your Data
```bash
# Fetch all trading data from Kalshi API
python fetch_data.py
```

### 3. View Analysis
```bash
# Start local web server
python -m http.server 8000

# Open in browser
# http://localhost:8000/dashboard.html
```

## Files Overview

### Core Components
- **`kalshi_client.py`** - Kalshi API client for fetching trading data
- **`fetch_data.py`** - Main script to fetch and store data
- **`data_manager.py`** - Data storage and export utilities
- **`pnl_calculator.py`** - PNL calculation engine
- **`dashboard.html/js`** - Web-based analysis dashboard

### Configuration
- **`.env`** - Your Kalshi API credentials (create from .env.example)
- **`requirements.txt`** - Python dependencies
- **`setup.py`** - Automated setup script

## Usage Guide

### Getting Your API Credentials

1. **API Key Method** (Recommended):
   - Log into your Kalshi account
   - Go to Account Settings → API Keys
   - Generate a new API key
   - Add to `.env` file: `KALSHI_API_KEY=your_key_here`

2. **Email/Password Method**:
   - Add to `.env` file:
     ```
     KALSHI_EMAIL=your_email@example.com
     KALSHI_PASSWORD=your_password
     ```

### Fetching Data

```bash
# Basic fetch
python fetch_data.py

# Verbose output
python fetch_data.py -v

# Custom output filename
python fetch_data.py -o my_data.json
```

### Analyzing Data

```bash
# Generate PNL report
python pnl_calculator.py

# Manage data files
python data_manager.py
```

### Web Dashboard

1. Start web server: `python -m http.server 8000`
2. Open `http://localhost:8000/dashboard.html`
3. Upload your data file or use sample data
4. View interactive analysis

## Dashboard Features

### Key Metrics
- **Total PNL**: Overall profit/loss
- **Win Rate**: Percentage of winning trades
- **Profit Factor**: Ratio of gross profit to gross loss
- **Average Win/Loss**: Mean profit per winning/losing trade

### Visualizations
- **Cumulative PNL Chart**: Track performance over time
- **Win Rate by Position**: Success rate by market
- **Position Performance Table**: Detailed breakdown by market
- **Best/Worst Trades**: Your top performers and biggest losses

### Data Upload
- **JSON Files**: Full data from `fetch_data.py`
- **CSV Files**: Exported trade data
- **Sample Data**: Built-in demo for testing

## Data Structure

The tool expects Kalshi data in this format:

```json
{
  "orders": [...],
  "fills": [...],
  "positions": [...],
  "account_history": [...],
  "fetched_at": "2024-01-20T10:00:00Z"
}
```

Key fields for PNL calculation:
- `cost`: Amount paid for position
- `payout`: Amount received when position resolves
- `fees`: Trading fees (if available)
- `ticker`: Market identifier
- `created_at`: Trade timestamp

## Troubleshooting

### Authentication Issues
- Verify API key is correct in `.env` file
- Check if API key has necessary permissions
- Try email/password method if API key fails

### Data Issues
- Ensure you have trading history in your Kalshi account
- Check that data files aren't empty
- Verify CSV format matches expected structure

### Dashboard Issues
- Use modern browser (Chrome, Firefox, Safari)
- Check browser console for JavaScript errors
- Ensure data file format is correct

## Advanced Usage

### Custom Analysis
Extend `pnl_calculator.py` to add your own metrics:
```python
def custom_analysis(trades):
    # Your custom analysis here
    return results
```

### API Customization
Modify `kalshi_client.py` to fetch additional data:
```python
def get_custom_data(self):
    # Custom API calls
    return data
```

### Dashboard Customization
Edit `dashboard.js` to add new visualizations or modify existing ones.

## Future Enhancements

- **Live Data**: Real-time API refresh
- **Advanced Metrics**: Sharpe ratio, maximum drawdown duration
- **Export Features**: PDF reports, Excel exports  
- **Market Analysis**: Sector performance, market comparisons
- **Alerts**: Performance notifications and targets

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages in console/terminal
3. Verify data format and API credentials
4. Create GitHub issue with detailed information

## License

This project is for personal use. Ensure compliance with Kalshi's Terms of Service when using their API.