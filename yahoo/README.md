# Yahoo Fantasy Basketball - 15 Year Analysis Project

## 🏀 Project Overview

This project contains a comprehensive analysis of **15 consecutive years** (2010-2024) of Yahoo Fantasy Basketball league data for "The Best Time of Year" league. The data enables three types of analysis:

1. **Player-Level Analysis** - Identify under/over-valued players year over year
2. **Owner Analysis** - Understand draft patterns and tendencies of current participants  
3. **Draft Strategy Analysis** - Correlate draft strategies with success

## 📊 Data Summary

- **15 consecutive seasons** of complete data (2010-2024)
- **2,366 total draft picks** (944 snake, 1,422 auction)
- **165 total teams** across all seasons
- **Complete owner tracking** with email-based unique IDs
- **Full playoff/standings results** for strategy analysis
- **1,708 NBA players** with historical performance data (2010-2024)
- **96.3% Yahoo-NBA player mapping** success rate

## 📁 Project Structure

```
yahoo/
├── README.md                    # This file
├── summary.html                 # Visual overview of all data
├── jsons/                       # OAuth credentials (keep secure)
│   ├── oauth2.json
│   ├── teams.json
│   └── 2020_ranks_pre.csv
├── py_scripts/                  # All Python extraction/processing scripts
│   ├── comprehensive_data_extractor.py    # Main data extraction system
│   ├── data_structure_design.py          # Creates organized folder structure
│   ├── extract_working_years.py          # Extract recent years (2020-2024)
│   ├── extract_remaining_years.py        # Extract older years (2010-2019)
│   ├── process_nba_historical_data.py    # Process NBA player stats by season
│   ├── create_yahoo_nba_player_mapping.py # Map Yahoo IDs to NBA players
│   ├── robust_test_extraction.py         # Test API connectivity
│   └── [other analysis scripts...]
├── league_data/                 # **MAIN DATA REPOSITORY**
│   ├── master_data/            # Cross-year reference files
│   │   ├── league_keys.json
│   │   ├── stat_categories.json
│   │   ├── owners_master.json
│   │   └── players_master.json
│   ├── 2010/                   # Each year contains:
│   │   ├── raw_data/          #   - Raw Yahoo API responses
│   │   ├── processed_data/    #   - Organized draft/owner data
│   │   └── external_data/     #   - NBA stats (future)
│   ├── 2011/
│   │   └── ... (same structure)
│   └── ... (through 2024)
├── historical_nba_stats/        # **NBA REFERENCE DATA**
│   ├── README.md               # NBA stats documentation
│   ├── 2010/ through 2024/     # NBA player stats by season
│   │   ├── fantasy_relevant_stats.csv  # Key stats in fantasy format
│   │   ├── nba_season_stats.csv        # Comprehensive season stats
│   │   └── year_summary.json           # Season metadata
│   ├── player_mappings/        # Yahoo-NBA player ID mappings
│   │   ├── nba_player_mapping.json     # NBA ID to name mapping
│   │   ├── yahoo_nba_mapping.json      # Detailed mapping results
│   │   └── yahoo_to_nba_lookup.json    # Quick lookup table
│   └── raw_downloads/          # Original NBA dataset
└── html_reports/               # **WEB-BASED ANALYSIS INTERFACE**
    ├── index.html              # Main analysis dashboard
    ├── css/style.css           # Interface styling
    ├── js/app.js               # Interactive functionality
    └── data/                   # Generated web data files
        ├── players.json        # Player database
        ├── insights.json       # Analysis insights
        ├── metadata.json       # Summary statistics
        └── player_index.json   # Search index
```

## 🎯 Data Available by Year

| Year | Teams | Picks | Budget | Status | Notes |
|------|-------|-------|---------|---------|-------|
| 2024 | 10    | 150   | $2,000  | ✅ Complete | Current season |
| 2023 | 10    | 150   | $2,000  | ✅ Complete | |
| 2022 | 10    | 150   | $2,000  | ✅ Complete | |
| 2021 | 10    | 150   | $2,000  | ✅ Complete | |
| 2020 | 10    | 150   | $2,000  | ✅ Complete | Original data source |
| 2019 | 10    | 160   | $2,000  | ✅ Complete | |
| 2018 | 10    | 160   | $2,000  | ✅ Complete | |
| 2017 | 12    | 192   | $2,400  | ✅ Complete | 12-team season |
| 2016 | 10    | 160   | $2,000  | ✅ Complete | |
| 2015 | 10    | 160   | $2,000  | ✅ Complete | |
| 2014 | 10    | 140   | $2,000  | ✅ Complete | |
| 2013 | 12    | 168   | $2,400  | ✅ Complete | 12-team season |
| 2012 | 12    | 168   | $2,400  | ✅ Complete | 12-team season |
| 2011 | 12    | 168   | $2,400  | ✅ Complete | 12-team season |
| 2010 | 10    | 140   | $2,000  | ✅ Complete | First year |

**Total: 2,366 draft picks across 15 seasons**
- **Snake Draft Years:** 2010-2015 (944 picks)
- **Auction Draft Years:** 2016-2024 (1,422 picks)

## 📈 Statistical Categories

The league uses 9 statistical categories plus games played:

1. **Field Goal %** (higher better)
2. **Free Throw %** (higher better) 
3. **3-Pointers Made** (higher better, averages)
4. **Points** (higher better, averages)
5. **Rebounds** (higher better, averages)
6. **Assists** (higher better, averages)
7. **Steals** (higher better, averages)
8. **Blocks** (higher better, averages)
9. **Turnovers** (lower better, averages)
10. **Games Played** (counting stat for analysis)

## 🔧 Key Scripts

### Data Extraction
- `comprehensive_data_extractor.py` - Main extraction engine for all 15 years
- `data_structure_design.py` - Sets up the organized folder structure

### Analysis Ready Scripts  
- `extract_working_years.py` - Quick extraction of recent years (2020-2024)
- `extract_remaining_years.py` - Extraction of older years (2010-2019)
- `robust_test_extraction.py` - Test API connectivity before full extraction

### Historical Research (Completed)
- `league_chain_explorer.py` - Discovered the 15-year league chain
- `pre_2010_explorer.py` - Confirmed 2010 as the starting year

## 🚀 Getting Started

### Prerequisites
```bash
pip install yahoo_oauth yahoo_fantasy_api pandas
```

### Quick Start - Analysis Files Ready to Use

**🎯 MAIN ANALYSIS FILES:**
1. **`html_reports/simple_working.html`** - ✅ **RECOMMENDED** - 547 drafted players with full stats
2. **`html_reports/draft_results_standalone.html`** - ✅ Draft results by year (2010-2024)
3. **`html_reports/minimal_test.html`** - ✅ Test file (3 players) for debugging
4. **`html_reports/debug_test.html`** - ✅ Single player test with Steven Adams

**📁 Other Files:**
- **Data Overview**: Open `summary.html` for project summary
- **Raw Data**: Check `league_data/[year]/processed_data/` folders
- **Re-extract Data**: Run `py_scripts/extract_working_years.py` if needed

> **⚠️ Note**: The full `standalone.html` with all 2,024 players may not load due to large data size. Use `simple_working.html` instead.

### For New Analysis
1. Use data in `league_data/` folders - already organized and ready
2. Player IDs are consistent - use them to link across years
3. Owner emails are unique identifiers for tracking across seasons

## 📋 Data Structure Details

### Draft Data (`draft_analysis.json`)
```json
{
  "season": "2024",
  "total_picks": 150,
  "total_spending": 2000,
  "picks": [
    {
      "pick_number": 1,
      "player_id": "6355",
      "fantasy_team": "Team Name",
      "draft_cost": 54,
      "raw_data": {...}
    }
  ]
}
```

### Owner Data (`owners.json`)
```json
{
  "season": "2024",
  "owners": {
    "email@example.com": {
      "team_name": "Fantasy Team",
      "manager_info": {...},
      "standings": {...}
    }
  }
}
```

## 🏀 NBA Performance Data Integration

The project now includes comprehensive NBA player performance data for all 15 seasons:

- **Data Source**: [NocturneBear/NBA-Data-2010-2024](https://github.com/NocturneBear/NBA-Data-2010-2024) 
- **Coverage**: 1,708 unique NBA players across 15 seasons
- **Yahoo Mapping**: 96.3% success rate linking Yahoo player IDs to NBA data
- **Fantasy Categories**: All 9 league categories plus games played as averages
- **Structure**: Organized by year with fantasy-focused CSV files

### Key Features
- **Season-wide aggregates**: Per-game averages for all fantasy categories
- **Player mapping system**: Direct links between Yahoo draft picks and NBA performance
- **Clean data structure**: Each year self-contained for easy analysis
- **Reference data**: Static per season, updated only when new seasons available

### Usage Example
```python
# Load Yahoo draft data and NBA performance data
yahoo_draft = pd.read_json('league_data/2024/processed_data/draft_analysis.json')
nba_stats = pd.read_csv('historical_nba_stats/2024/fantasy_relevant_stats.csv')

# Load player mapping
with open('historical_nba_stats/player_mappings/yahoo_to_nba_lookup.json') as f:
    mapping = json.load(f)

# Merge data for value analysis
merged_data = merge_yahoo_nba_data(yahoo_draft, nba_stats, mapping)
```

## 🎯 Analysis Opportunities

### 1. Player Value Analysis
- Compare draft costs to actual performance across years
- Identify consistently under/over-valued players
- Track positional value trends (centers vs. guards)

### 2. Owner Pattern Analysis
- Draft strategy identification (stars & scrubs vs. balanced)
- Success correlation with spending patterns
- Historical performance tracking

### 3. Strategy Optimization
- Winning team characteristics
- Optimal budget allocation by position
- Draft timing advantages (early vs. late picks)

## 🔐 Security Notes

- `jsons/oauth2.json` contains API credentials - keep secure
- OAuth tokens refresh automatically
- All data extraction respects Yahoo's rate limits

## 🌐 Interactive Web Analysis Files

The project includes multiple web-based analysis interfaces:

### 🎯 Primary Analysis Tool: `simple_working.html`
**✅ FULLY WORKING** - Focus on drafted players (547 players, loads instantly)

**Features:**
- **🔍 Player Search**: Instant search through all drafted players
- **📊 Expandable Details**: Click any player row to see:
  - **📋 Complete Draft History**: Every draft with year, team, cost, pick number
  - **📈 Full Season Stats**: All 10 fantasy categories (GP, PPG, RPG, APG, FG%, FT%, 3PM, STL, BLK, TO)
  - **💰 Value Analysis**: Times drafted, average cost, value score, cost range
- **🎨 Color-Coded Values**: Green (high value), orange (medium), red (low value)
- **📱 Responsive Design**: Works on desktop, tablet, and mobile

### 📋 Draft Results Tool: `draft_results_standalone.html`
**✅ FULLY WORKING** - View all draft results by year

**Features:**
- **📅 Year Navigation**: Click any year (2010-2024) to see complete draft
- **💰 Cost Sorting**: All picks sorted by draft cost (highest to lowest)
- **👥 Team Information**: See which fantasy team drafted each player
- **📊 Draft Statistics**: Total picks, total spending, average cost per year
- **🏀 Player Names**: Full player names for all 2,366 draft picks across 15 years

### 📊 Complete Player Database (Large Files)
**⚠️ May have loading issues due to size** - All 2,024 players

- `standalone_complete.html` - Full features but large (3.1MB)
- `standalone_final.html` - Fixed version but still large
- `standalone_fixed.html` - Alternative version

### Database Content
- **547 Drafted Players**: Complete stats and draft history for all players ever drafted
- **1,477 NBA-Only Players**: Season stats without draft history 
- **15-Year Coverage**: Data from 2010-2024 seasons
- **Value Scoring Formula**: (PPG + RPG + APG - TO) / Average Cost × 10
- **Comprehensive Stats**: All 9 fantasy categories plus games played

## 📊 Next Steps

1. **✅ External NBA Stats Integration** - Complete with 96.3% mapping success
2. **✅ HTML Dashboard** - Interactive web-based player database complete
3. **Master Owner Database** - Build cross-year owner tracking system
4. **Advanced Analytics** - Implement machine learning models for player predictions
5. **Mobile Optimization** - Enhance responsive design for mobile draft use

## 📞 Support

This is a complete, self-contained fantasy basketball analysis system with 15 years of historical data ready for comprehensive analysis.

---
**Data Extracted**: August 2025  
**League**: "The Best Time of Year" (Yahoo Fantasy NBA)  
**Timespan**: 2010-2024 (15 consecutive seasons)