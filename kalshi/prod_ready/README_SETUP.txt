KALSHI DASHBOARD SETUP INSTRUCTIONS
===================================

QUICK START:
1. Double-click "Launch_Kalshi_Dashboard.bat" to start the server
2. Your browser will automatically open to http://localhost:8000
3. Use the dashboard to view your Kalshi trading data
4. Click "🔄 Refresh Data" to get latest trades from Kalshi API

ALTERNATIVE LAUNCHERS:
- "Launch_Kalshi_Dashboard.bat" - Shows detailed console output
- "Quick_Launch.cmd" - Minimal launcher that auto-opens browser

CREATING A DESKTOP SHORTCUT:
1. Right-click on "Launch_Kalshi_Dashboard.bat"
2. Select "Send to" > "Desktop (create shortcut)"
3. Optional: Right-click the desktop shortcut > Properties > Change Icon
4. Now you can launch from your desktop!

FOLDER CONTENTS:
- dashboard_improved.html - Main dashboard interface
- deposits.txt - Your deposit tracking file
- serve_dashboard.py - Dashboard server
- python/ - Backend scripts and data files
- Launch_Kalshi_Dashboard.bat - Main launcher
- Quick_Launch.cmd - Simple launcher

REQUIREMENTS:
- Python must be installed and in your system PATH
- Internet connection for API calls
- Valid Kalshi API credentials in python/private_key.pem

TROUBLESHOOTING:
- If Python error: Install Python from python.org
- If API error: Check python/private_key.pem exists
- If port 8000 busy: Close other programs using port 8000
- If refresh fails: Check internet connection

Press Ctrl+C in the console window to stop the server when done.