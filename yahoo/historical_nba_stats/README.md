# Historical NBA Player Statistics (2010-2024)

## 📊 Overview

This folder contains comprehensive NBA player statistics for seasons 2010-2024, organized to support fantasy basketball analysis. The data includes season-wide aggregated stats for all NBA players, with emphasis on the 9 categories used in your Yahoo Fantasy league.

## 📁 Structure

```
historical_nba_stats/
├── README.md                    # This file
├── 2010/ through 2024/          # Individual season folders
│   ├── fantasy_relevant_stats.csv    # Key stats in fantasy format
│   ├── nba_season_stats.csv         # Comprehensive season stats
│   └── year_summary.json            # Season metadata
├── player_mappings/             # Player ID mapping files
│   ├── nba_player_mapping.json      # NBA player ID to name mapping
│   ├── yahoo_nba_mapping.json       # Detailed Yahoo-NBA mapping
│   └── yahoo_to_nba_lookup.json     # Quick lookup for Yahoo IDs
└── raw_downloads/               # Original source data
    └── NBA-Data-2010-2024/      # Raw NBA dataset from GitHub
```

## 📈 Data Coverage

- **Years**: 2010-2024 (15 seasons)
- **Players**: 1,708 unique NBA players
- **Yahoo Mapping**: 96.3% success rate (233/242 players matched)
- **Games**: 351,409+ individual game performances processed

## 🎯 Fantasy-Relevant Stats

Each year folder contains `fantasy_relevant_stats.csv` with these key columns:

### Player Identification
- `personId`: NBA player ID
- `personName`: Player's full name
- `games_played`: Games played that season
- `teamTricode`: Team(s) played for

### Fantasy Categories (Per-Game Averages)
1. `field_goal_percentage`: FG% (higher better)
2. `free_throw_percentage`: FT% (higher better) 
3. `threepointers_per_game`: 3PM per game (higher better)
4. `points_per_game`: Points per game (higher better)
5. `rebounds_per_game`: Rebounds per game (higher better)
6. `assists_per_game`: Assists per game (higher better)
7. `steals_per_game`: Steals per game (higher better)
8. `blocks_per_game`: Blocks per game (higher better)
9. `turnovers_per_game`: Turnovers per game (lower better)

## 🔄 Player Mapping System

### Yahoo-to-NBA Mapping
The `player_mappings/yahoo_to_nba_lookup.json` file provides direct mapping:

```json
{
  "yahoo_player_id": {
    "nba_id": "nba_player_id",
    "player_name": "Player Name",
    "match_confidence": "exact|high"
  }
}
```

### Usage Example
```python
import json

# Load mapping
with open('historical_nba_stats/player_mappings/yahoo_to_nba_lookup.json') as f:
    yahoo_to_nba = json.load(f)

# Get NBA stats for Yahoo player
yahoo_id = "6355"  # Example Yahoo player ID
if yahoo_id in yahoo_to_nba:
    nba_id = yahoo_to_nba[yahoo_id]['nba_id']
    player_name = yahoo_to_nba[yahoo_id]['player_name']
    # Now look up NBA stats using nba_id
```

## 📋 Data Quality

### Coverage by Season
| Season | NBA Players | Yahoo Matched | Match Rate |
|--------|-------------|---------------|------------|
| 2024   | 572         | Active        | 96.3%      |
| 2023   | 539         | Active        | 96.3%      |
| 2022   | 605         | Limited       | -          |
| 2021   | 540         | Limited       | -          |
| 2020   | 529         | Active        | 96.3%      |

*Note: Yahoo mapping limited to recent seasons due to API access*

### Data Validation
- ✅ All percentages calculated from makes/attempts
- ✅ Per-game stats calculated from totals/games_played
- ✅ Players with <1 game filtered out
- ✅ DNP (Did Not Play) entries excluded
- ✅ Name-based matching with 96.3% success rate

## 🚀 Usage for Analysis

### 1. Player Value Analysis
Compare Yahoo draft costs to actual NBA performance:
```python
# Load Yahoo draft data
yahoo_draft = pd.read_csv('league_data/2024/processed_data/draft_analysis.json')

# Load NBA performance
nba_stats = pd.read_csv('historical_nba_stats/2024/fantasy_relevant_stats.csv')

# Merge using player mapping
merged = merge_yahoo_nba_data(yahoo_draft, nba_stats, yahoo_to_nba)
```

### 2. Year-over-Year Trends
Track how players' values change:
```python
# Load multiple years
years = range(2020, 2025)
player_trends = {}

for year in years:
    nba_data = pd.read_csv(f'historical_nba_stats/{year}/fantasy_relevant_stats.csv')
    # Analyze trends for specific players
```

### 3. Position Analysis
Identify positional value patterns:
```python
# Analyze performance by position
position_values = nba_stats.groupby('position').agg({
    'points_per_game': 'mean',
    'rebounds_per_game': 'mean',
    'assists_per_game': 'mean'
})
```

## 🔧 Maintenance

### Adding New Seasons
When new NBA seasons become available:

1. **Update source data**: Re-clone the NBA-Data repository
2. **Reprocess data**: Run `process_nba_historical_data.py`
3. **Update mappings**: Run `create_yahoo_nba_player_mapping.py` 
4. **Validate**: Check new season folders and mapping success rates

### Manual Updates
For players with poor name matches, manually edit:
- `player_mappings/yahoo_nba_mapping.json`
- Add entries to `possible_matches` section after verification

## 📞 Data Sources

- **NBA Statistics**: [NocturneBear/NBA-Data-2010-2024](https://github.com/NocturneBear/NBA-Data-2010-2024)
- **Yahoo Player Data**: Yahoo Fantasy Sports API
- **Processing**: Custom aggregation from game-by-game box scores

## 💡 Key Insights

1. **Reference Data**: This data is static per season and doesn't change year-to-year
2. **Clean Structure**: Each season is self-contained for easy yearly analysis
3. **Fantasy Focus**: All stats converted to per-game averages matching your league format
4. **High Match Rate**: 96.3% of Yahoo players successfully mapped to NBA data
5. **Comprehensive Coverage**: 15 years of data supporting trend analysis

---

*Last Updated: August 2025*  
*Data Coverage: NBA Seasons 2010-11 through 2023-24*