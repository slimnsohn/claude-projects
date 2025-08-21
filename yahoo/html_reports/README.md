# Fantasy Basketball Analysis - Web Interface

## 🏀 Interactive Player Database

This web interface provides comprehensive analysis tools for your 15-year fantasy basketball dataset.

## 🚀 Getting Started

### Two Ways to Use:

**Option 1 - Standalone (Recommended)**:
1. **Double-click `standalone.html`** - works immediately in any browser
2. **No server required** - all data embedded in the file

**Option 2 - Server Mode**:
1. **Run server**: `python serve.py` from this folder
2. **Open browser**: Go to http://localhost:8080
3. **Stop server**: Press Ctrl+C when done

### Using the Interface:
1. **Search Players**: Use the search box to find specific players
2. **Explore Data**: Click on player cards to expand detailed statistics  
3. **View Insights**: Switch to the "Analysis & Insights" tab for strategic analysis

> **Important**: If `index.html` shows "0 players found", use `standalone.html` instead!

## 📊 Features

### Player Database Tab
- **Search & Filter**: Find players by name, draft status, value scores, or career length
- **Sortable Table**: Click column headers to sort by any statistic (name, seasons, value, etc.)
- **Compact List View**: See 20+ players per screen in table format
- **Expandable Details**: Click any row to expand and see:
  - Complete draft history with costs and teams
  - Season-by-season stats for all 9 fantasy categories
  - Career summaries and averages
  - Value analysis based on production vs. cost

### Analysis & Insights Tab
- **Top Values**: Players who provided the most production relative to draft cost
- **Consistent Performers**: Players with reliable, low-variance production
- **Strategic Insights**: Data-driven recommendations for future drafts

## 🎯 Value Analysis System

### Value Score Formula
`(Points + Rebounds + Assists - Turnovers) / Average Draft Cost × 10`

### Interpretation
- **High Value**: Score > 1.5 (excellent value)
- **Fair Value**: Score 0.8-1.5 (reasonable value)
- **Poor Value**: Score < 0.8 (overpaid)

## 📁 File Structure

```
html_reports/
├── index.html          # Main interface
├── css/style.css       # Styling
├── js/app.js           # Interactive functionality
└── data/               # JSON data files
    ├── players.json    # Complete player database
    ├── insights.json   # Analysis results
    ├── metadata.json   # Summary statistics
    └── player_index.json # Search index
```

## 🔄 Data Updates

To update the web interface with new data:

1. **Re-run data generation**: `python py_scripts/generate_web_data.py`
2. **Refresh browser**: The interface automatically loads updated data

## 💡 Usage Tips

1. **Draft Preparation**: Filter by "Drafted in League" to see historical league preferences
2. **Value Hunting**: Use "High Value" filter to find consistently undervalued players
3. **Consistency Check**: Look for players with low variance in key stats
4. **Recent Form**: Filter by "Recent Players" to focus on currently active players

## 🎨 Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Responsive design included

---

## 📈 Complete Draft History Coverage

The interface now includes **ALL 15 years** of draft data (2010-2024):

- **2,024 total players**: 1,708 NBA players + 316 Yahoo-only players  
- **2,366 total draft entries** across all years
- **Snake draft years (2010-2019)**: 1,273 draft entries showing pick positions
- **Auction draft years (2020-2024)**: 1,422 draft entries with costs and value analysis
- **Complete coverage**: No missing draft data - every player ever drafted is included

### Data Types
- **NBA Players**: Full stats + draft history (normal rows)
- **Yahoo-Only Players**: Draft history only, no NBA stats (gray italic rows)

---

*Updated: August 2025 • Complete Data: 2010-2024 NBA Seasons • 2,024 Total Players • 547 with Draft History*