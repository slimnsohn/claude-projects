# Pinnacle-Kalshi Mispricing Detection System

Clean, organized production-ready system for finding mispricing opportunities between Pinnacle and Kalshi.

## 🚀 Quick Start

**Main Scripts (All You Need):**

```bash
# Run mispricing analysis
python run_analysis.py                  # MLB analysis (default)
python run_analysis.py --sport nfl      # NFL analysis
python run_analysis.py --all-sports     # All sports

# View odds data  
python view_odds.py                     # View MLB odds
python view_odds.py --sport nba --export # NBA odds + export to CSV
```

## 📁 Organized Structure

```
prod_ready/
├── run_analysis.py         # 🎯 MAIN: Run mispricing analysis
├── view_odds.py            # 📊 MAIN: View/export odds data
├── README.md               # This file
├── core/                   # Core system modules
│   ├── main_system.py      # Main analysis engine
│   ├── pinnacle_client.py  # Pinnacle API client
│   ├── kalshi_client.py    # Kalshi API client
│   ├── data_aligner.py     # Game matching logic
│   └── odds_converter.py   # Odds conversion utilities
├── config/                 # Configuration
│   └── sports_config.py    # Sports definitions & settings
├── utils/                  # Utility scripts
│   ├── timestamp_utils.py  # Time handling utilities
│   ├── quick_odds_dump.py  # Quick odds export
│   └── dump_odds_data.py   # Detailed odds export
├── tests/                  # Test & debug scripts
│   ├── test_multi_sport.py # Test sports configuration
│   ├── test_live_game_filtering.py # Test filtering
│   └── debug_baltimore_houston.py # Debug specific games
├── docs/                   # Documentation
│   └── HOW_TO_ADD_NEW_LEAGUES.md # Guide for adding sports
└── output/                 # Generated files
    └── *.csv               # Exported data files
```

## 🎯 Main Scripts Usage

### Analysis Script (`run_analysis.py`)

Find mispricing opportunities:

```bash
# Basic usage
python run_analysis.py                    # MLB (default)
python run_analysis.py --sport nfl        # NFL
python run_analysis.py --sport nba        # NBA

# Advanced options
python run_analysis.py --all-sports       # All available sports
python run_analysis.py --current-season   # Only sports in season
python run_analysis.py --max-opportunities 5  # Show max 5 opportunities
python run_analysis.py --verbose          # Detailed output + save results
```

### Odds Viewer (`view_odds.py`)

View and export odds data:

```bash
# Basic viewing
python view_odds.py                       # MLB odds
python view_odds.py --sport nfl           # NFL odds

# Export options
python view_odds.py --export              # Export to CSV
python view_odds.py --format detailed     # Comprehensive view
python view_odds.py --pinnacle-only       # Only Pinnacle data
```

## 🏆 Features

✅ **Multi-Sport Support**: MLB, NFL, NBA, NHL, College Football, College Basketball  
✅ **Live Game Filtering**: Automatically excludes live/started games  
✅ **Easy League Expansion**: Add new sports in `config/sports_config.py`  
✅ **Clean Output**: Your preferred format with fav/dog identification  
✅ **Export Ready**: CSV export with timestamps  
✅ **Organized Codebase**: Clean separation of concerns  

## 🔧 Configuration

Sports settings are centralized in `config/sports_config.py`:
- Team aliases and mappings
- Confidence thresholds per sport
- Edge thresholds per sport
- Season months
- Search keywords for Kalshi

## 📈 Output Format

The system outputs odds in your preferred format:

```
     book                teams fav_team dog_team  fav_odds  dog_odds league bet_type  game_time game_date
0 pinnacle              [COL, PIT]      PIT      COL      -182       163    mlb       ml  FRI_22:41  20250822
1    kalshi              [HOU, BAL]      BAL      HOU      -120       105    mlb       ml  FRI_23:06  20250822
```

## 🚨 Important Notes

- **API Keys Required**: Place your keys in `../keys/` folder
- **Live Filtering**: System automatically filters out live games
- **Path Updates**: All import paths have been updated for the new structure
- **Clean Interface**: Only use the two main scripts for daily operations

## 🛠️ For Developers

- **Core modules**: Main system logic in `core/`
- **Add sports**: Update `config/sports_config.py`
- **Tests**: Run tests from `tests/` folder
- **Debug**: Use scripts in `tests/` for troubleshooting

The organized structure keeps your main folder clean while providing all the power of the underlying system!