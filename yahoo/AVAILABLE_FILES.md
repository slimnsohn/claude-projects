# 📁 Available Analysis Files - Yahoo Fantasy Basketball Project

## 🎯 MAIN ANALYSIS FILES (READY TO USE)

### 1. **`html_reports/simple_working.html`** ⭐ **RECOMMENDED**
**✅ FULLY WORKING** - Primary analysis tool
- **Purpose**: Complete player analysis for drafted players
- **Content**: 547 players who were actually drafted (2010-2024)
- **File Size**: 0.9 MB (loads instantly)
- **Features**:
  - 🔍 Real-time player search
  - 📊 Expandable player details with:
    - 📋 Complete draft history (year, team, cost, pick #)
    - 📈 Full season stats (GP, PPG, RPG, APG, FG%, FT%, 3PM, STL, BLK, TO)
    - 💰 Value analysis (times drafted, avg cost, value score)
  - 🎨 Color-coded value scores (green=high, orange=medium, red=low)
  - 📱 Mobile responsive design

### 2. **`html_reports/draft_results_standalone.html`** 
**✅ FULLY WORKING** - Draft results browser
- **Purpose**: View complete draft results by year
- **Content**: All 2,366 draft picks across 15 years (2010-2024)
- **File Size**: 0.6 MB
- **Features**:
  - 📅 Year-by-year navigation (click any year 2010-2024)
  - 💰 Picks sorted by cost (highest to lowest)
  - 👥 Fantasy team names for each pick
  - 📊 Draft statistics (total picks, spending, averages)
  - 🏀 Full player names for all picks

## 🧪 TEST/DEBUG FILES

### 3. **`html_reports/minimal_test.html`**
- **Purpose**: Minimal test with 3 players for debugging
- **Content**: Alex Abrines, Precious Achiuwa, Quincy Acy
- **Features**: Basic table with debug information

### 4. **`html_reports/debug_test.html`**
- **Purpose**: Single player test with expandable details
- **Content**: Steven Adams with complete data
- **Features**: Full expandable functionality test

## 📊 COMPLETE DATABASE FILES (LARGE - MAY HAVE LOADING ISSUES)

### 5. **`html_reports/standalone_complete.html`**
- **Purpose**: Complete player database with all 2,024 players
- **File Size**: 3.1 MB
- **Status**: ⚠️ May not load due to large embedded data

### 6. **`html_reports/standalone_final.html`**
- **Purpose**: Fixed version of complete database
- **File Size**: 3.1 MB
- **Status**: ⚠️ May not load due to large embedded data

### 7. **`html_reports/standalone_fixed.html`**
- **Purpose**: Alternative complete database version
- **File Size**: 3.1 MB
- **Status**: ⚠️ May not load due to large embedded data

## 📋 DATA SUMMARY FILES

### 8. **`summary.html`**
- **Purpose**: Project overview and data summary
- **Content**: High-level statistics and project description

### 9. **`README.md`**
- **Purpose**: Complete project documentation
- **Content**: Setup instructions, data structure, analysis opportunities

## 💾 RAW DATA DIRECTORIES

### **`league_data/`** - Complete Yahoo Fantasy Data
```
league_data/
├── 2010/ through 2024/          # 15 years of data
│   ├── processed_data/
│   │   ├── draft_analysis.json   # Draft picks with player names
│   │   ├── owners.json          # Team owners and standings
│   │   └── league_info.json     # League settings
│   └── raw_data/                # Original Yahoo API responses
├── master_data/                 # Cross-year reference files
│   ├── league_keys.json
│   ├── owners_master.json
│   └── players_master.json
```

### **`historical_nba_stats/`** - NBA Performance Data
```
historical_nba_stats/
├── 2010/ through 2024/          # NBA stats by year
│   ├── fantasy_relevant_stats.csv    # Key fantasy stats
│   └── nba_season_stats.csv         # Complete season stats
├── player_mappings/             # Yahoo-NBA player links
│   ├── nba_player_mapping.json
│   ├── yahoo_nba_mapping.json
│   └── yahoo_to_nba_lookup.json
```

### **`html_reports/data/`** - Web Interface Data
```
html_reports/data/
├── players.json                 # Complete player database (2,024 players)
├── insights.json               # Analysis insights and top performers
├── metadata.json               # Summary statistics
├── player_index.json           # Search index
└── drafted_players.json        # Filtered data (547 drafted players)
```

## 🔧 PYTHON SCRIPTS

### **`py_scripts/`** - Analysis and Data Processing
- **`comprehensive_data_extractor.py`** - Main extraction engine
- **`create_simple_working.py`** - Created the working analysis file
- **`fix_expandable_issue.py`** - Fixed expandable functionality
- **`debug_standalone.py`** - Created debug test files
- **`generate_complete_web_data.py`** - Generate web interface data

## 📊 DATA COVERAGE SUMMARY

| **Category** | **Count** | **Description** |
|--------------|-----------|-----------------|
| **Total Seasons** | 15 | 2010-2024 consecutive years |
| **Total Draft Picks** | 2,366 | All picks across 15 years |
| **Drafted Players** | 547 | Unique players drafted at least once |
| **NBA Players** | 2,024 | Total players with NBA stats |
| **Yahoo-NBA Mapping** | 96.3% | Successfully linked Yahoo→NBA |
| **Snake Draft Years** | 6 | 2010-2015 (944 picks) |
| **Auction Draft Years** | 9 | 2016-2024 (1,422 picks) |

## 🎯 RECOMMENDATION FOR USE

**Start with these two files:**
1. **`simple_working.html`** - For player analysis and value research
2. **`draft_results_standalone.html`** - For historical draft review

Both load instantly and provide complete functionality for fantasy basketball analysis!

---
**Last Updated**: August 2025  
**Data Coverage**: 2010-2024 (15 seasons)  
**League**: "The Best Time of Year" Yahoo Fantasy NBA