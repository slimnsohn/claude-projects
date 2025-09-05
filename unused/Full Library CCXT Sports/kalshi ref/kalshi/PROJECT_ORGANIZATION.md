# Kalshi Project Organization

## 🎯 **ACTIVE FILES (Use These)**

### Main Dashboard
- **`prod_ready/`** - Complete production-ready dashboard system
  - `Launch_Kalshi_Dashboard.bat` - **MAIN LAUNCHER** (double-click to start)
  - `Quick_Launch.cmd` - Alternative quick launcher
  - `dashboard_improved.html` - Main dashboard interface
  - `deposits.txt` - Your deposit tracking file
  - `serve_dashboard.py` - Web server with automatic refresh
  - `README_SETUP.txt` - Complete setup instructions

### Backend Scripts (Auto-managed)
- **`prod_ready/python/`** - Backend scripts and data
  - `get_fills.py` - Fetches trades from Kalshi API
  - `generate_dashboard.py` - Generates dashboard HTML
  - `git_clients.py` - Kalshi API client
  - `.env` - Environment variables
  - `private_key.pem` - API credentials
  - `data/` - Trade data storage

## 📚 **DOCUMENTATION**
- `API_SETUP_GUIDE.md` - How to set up Kalshi API
- `PORTFOLIO_GUIDE.md` - Portfolio management guide
- `README.md` - Project overview
- `PROJECT_ORGANIZATION.md` - This file

## 📦 **ARCHIVED FILES**
- **`archive_old_files/`** - Old versions and development files
  - `old_dashboards/` - Previous dashboard versions
  - `old_scripts/` - Duplicate/old Python scripts
  - `development_files/` - Debug and development tools
  - `data/` - Old data files
  - `venv/` - Old virtual environment
  - `deposits.txt` - Old deposit file

## 🚀 **QUICK START**
1. Double-click `prod_ready/Launch_Kalshi_Dashboard.bat`
2. Dashboard opens automatically at http://localhost:8000
3. Click "🔄 Refresh Data" to get latest trades
4. Press Ctrl+C in console to stop server

## ✨ **KEY FEATURES**
- ✅ One-click launcher with Windows batch files
- ✅ Automatic data refresh from Kalshi API
- ✅ Clean organized file structure
- ✅ All dependencies self-contained in prod_ready folder
- ✅ Desktop shortcut ready (right-click batch file → Send to Desktop)

## 🧹 **WHAT WAS CLEANED UP**
- Moved duplicate dashboard HTML files to archive
- Archived old/duplicate Python scripts
- Organized development and debug files
- Consolidated data folders
- Removed old virtual environment
- Created single source of truth in `prod_ready/`