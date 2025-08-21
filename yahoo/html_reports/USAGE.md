# How to Use the Fantasy Basketball Analysis Interface

## 🚀 Quick Start Options

### Option 1: Standalone File (Easiest)
1. **Open the standalone file**: Double-click `standalone.html` 
2. **Browser opens automatically** with full functionality
3. **Works offline** - no internet or server required

### Option 2: Local Server (If standalone has issues)
1. **Run the server**: Open command prompt in this folder and run:
   ```bash
   python serve.py
   ```
2. **Browser opens automatically** at http://localhost:8080
3. **Press Ctrl+C** to stop the server when done

## 📊 Using the Interface

### Player Database Tab
- **Search**: Type player names in the search box
- **Filter**: Click filter chips to narrow results:
  - **All Players**: All 1,708 NBA players (2010-2024)  
  - **Drafted in League**: Only players drafted in your league
  - **High Value**: Players with value scores > 1.5
  - **Long Career**: Players with 5+ seasons
  - **Recent Players**: Active in 2022+ seasons

- **Table View**: Browse 20+ players per screen in compact table format
- **Sort Columns**: Click any column header to sort (name, seasons, value, stats)
- **Expand Details**: Click any row to see:
  - Complete draft history with costs and teams
  - Season-by-season stats for all categories
  - Career averages and totals

### Analysis & Insights Tab
- **Summary Cards**: Overview of data coverage
- **Best Values**: Top value players based on production vs. cost
- **Most Consistent**: Players with reliable, low-variance production
- **Strategic Insights**: Draft recommendations and patterns

## 🎯 Understanding Value Scores

**Formula**: `(Points + Rebounds + Assists - Turnovers) / Average Cost × 10`

**Interpretation**:
- **> 1.5**: Excellent value (target these players)
- **0.8-1.5**: Fair value (reasonable picks)
- **< 0.8**: Poor value (overpaid or avoid)

## 📱 Tips for Draft Preparation

1. **Sort by Value**: Click "Value" column header to see best values first
2. **Target High Values**: Look for players with consistently high value scores
3. **Check Consistency**: Prefer players with low variance in key stats
4. **Recent Form**: Filter by recent players to focus on currently active ones
5. **Draft History**: See what you've paid historically vs. production received
6. **Compare Stats**: Use sortable columns to compare players across categories
7. **Games Played**: Factor in availability - great stats mean nothing if they don't play

## 🔧 Troubleshooting

**"0 players found"**:
- Use `standalone.html` instead of `index.html`
- Or run `python serve.py` from this folder

**Slow loading**:
- The standalone file is large (2.7MB) due to embedded data
- Server version loads faster but requires Python

**Search not working**:
- Clear browser cache and refresh
- Try typing full player names

**Player rows not expanding**:
- Click anywhere on the table row
- Only one row expands at a time
- Look for the down arrow in the last column

## 📁 File Sizes
- `standalone.html`: 2.7MB (includes all data)
- `index.html`: 8KB (requires server + data files)

---

*For technical support, check the main project README.md*