# How to Add New Leagues/Sports

The mispricing detection system has been redesigned with an easy hook for adding new leagues. All sport-specific configurations are centralized in `sports_config.py`.

## Quick Start - Adding a New Sport

### 1. Update sports_config.py

Add your new sport to the `SPORTS_CONFIG` dictionary in `sports_config.py`:

```python
'tennis': SportConfig(
    name='Tennis',
    pinnacle_key='tennis_wta',  # OddsAPI sport key
    kalshi_keywords=[
        'tennis', 'wta', 'atp', 'wimbledon', 'us open', 
        'french open', 'australian open', 'djokovic', 
        'nadal', 'federer', 'serena', 'swiatek'
    ],
    kalshi_tickers=['kxtennis', 'kxwta'],
    team_aliases={
        # Player/tournament mappings if needed
        'DJOKOVIC': ['Novak Djokovic', 'Djokovic'],
        'NADAL': ['Rafael Nadal', 'Nadal', 'Rafa']
    },
    match_confidence_threshold=0.6,  # Adjust based on sport complexity
    time_threshold_hours=4.0,        # Adjust for typical scheduling
    min_edge_threshold=0.035,        # Adjust for market efficiency
    season_months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]  # Year-round
)
```

### 2. Test Your Configuration

Run the test script to verify everything works:

```bash
cd prod_ready
python test_multi_sport.py
```

### 3. Run Analysis

Your new sport is automatically available:

```python
from main_system import MispricingSystem

system = MispricingSystem()
results = system.run_analysis('tennis')  # Use your sport key
```

That's it! No other code changes needed.

## Configuration Parameters Explained

### Required Fields

- **name**: Human-readable sport name
- **pinnacle_key**: OddsAPI sport identifier (see [OddsAPI docs](https://the-odds-api.com/liveapi/guides/v4/))
- **kalshi_keywords**: List of keywords to search for in Kalshi market titles
- **kalshi_tickers**: Known ticker patterns for this sport on Kalshi
- **team_aliases**: Mapping of standard team names to variations
- **match_confidence_threshold**: Minimum confidence for game alignment (0.0-1.0)
- **time_threshold_hours**: Maximum time difference for matching games
- **min_edge_threshold**: Minimum edge percentage to consider opportunity
- **season_months**: List of months when sport is active (1-12)

### Finding the Right Values

#### Pinnacle Key
Check [OddsAPI documentation](https://the-odds-api.com/liveapi/guides/v4/) for available sports:
- `tennis_wta` - Women's Tennis
- `soccer_epl` - English Premier League
- `mma_mixed_martial_arts` - MMA

#### Kalshi Keywords
Search Kalshi markets manually or run:
```python
from kalshi_client import KalshiClientUpdated
client = KalshiClientUpdated('../keys/kalshi_credentials.txt')
markets = client.get_all_markets()
# Review market titles to identify patterns
```

#### Threshold Tuning
- **Complex sports** (many teams/players): Higher confidence threshold (0.6+)
- **Simple sports** (fewer participants): Lower confidence threshold (0.4+)
- **Efficient markets**: Higher edge threshold (0.04+)
- **Less efficient markets**: Lower edge threshold (0.02+)

## Advanced Configuration

### Custom Team Aliases

For sports with complex naming:

```python
team_aliases={
    'GSW': ['Golden State Warriors', 'Warriors', 'Dubs'],
    'LAL': ['Los Angeles Lakers', 'Lakers', 'LA Lakers'],
    # Add alternate spellings, abbreviations, nicknames
}
```

### Seasonal Sports

Set active months for seasonal sports:

```python
season_months=[9, 10, 11, 12, 1, 2]  # September through February (NFL)
season_months=[3, 4, 5, 6, 7, 8, 9, 10]  # March through October (MLB)
```

### Multiple Tickers

If a sport has multiple ticker patterns:

```python
kalshi_tickers=['kxnflgame', 'kxsuperbowl', 'kxnflplayoffs']
```

## System Features

### Automatic Sport Detection
The system automatically:
- ✅ Loads your sport configurations
- ✅ Validates sport parameters
- ✅ Uses sport-specific thresholds
- ✅ Applies sport-specific team matching
- ✅ Handles seasonal availability

### Multi-Sport Analysis
Run analysis across multiple sports:

```python
# Analyze all available sports
results = system.run_multi_sport_analysis()

# Analyze specific sports
results = system.run_multi_sport_analysis(['mlb', 'nfl', 'tennis'])

# Analyze only current season sports
from sports_config import get_current_season_sports
current_sports = get_current_season_sports()
results = system.run_multi_sport_analysis(current_sports)
```

### Configuration Utilities

```python
from sports_config import (
    get_sport_config,
    get_available_sports, 
    is_sport_in_season,
    create_new_sport_template
)

# Get configuration for a sport
config = get_sport_config('mlb')

# Check if sport is in season
in_season = is_sport_in_season('nfl')  # Current month
in_season = is_sport_in_season('nfl', 12)  # December

# Generate template for new sport
template = create_new_sport_template('Soccer')
print(template)
```

## Example: Adding Soccer

Here's a complete example of adding English Premier League:

```python
'epl': SportConfig(
    name='English Premier League',
    pinnacle_key='soccer_epl',
    kalshi_keywords=[
        'soccer', 'football', 'epl', 'premier league', 'manchester', 
        'liverpool', 'chelsea', 'arsenal', 'tottenham', 'city',
        'united', 'spurs', 'gunners', 'blues', 'reds'
    ],
    kalshi_tickers=['kxepl', 'kxsoccer'],
    team_aliases={
        'MAN CITY': ['Manchester City', 'City', 'MCFC'],
        'MAN UTD': ['Manchester United', 'United', 'MUFC'],
        'LIVERPOOL': ['Liverpool', 'LFC', 'Reds'],
        'ARSENAL': ['Arsenal', 'Gunners', 'AFC'],
        'CHELSEA': ['Chelsea', 'Blues', 'CFC'],
        'TOTTENHAM': ['Tottenham', 'Spurs', 'THFC']
    },
    match_confidence_threshold=0.5,
    time_threshold_hours=6.0,
    min_edge_threshold=0.03,
    season_months=[8, 9, 10, 11, 12, 1, 2, 3, 4, 5]  # August to May
)
```

## Testing New Sports

Always test new configurations:

1. **Configuration Test**: `python sports_config.py`
2. **System Test**: `python test_multi_sport.py`  
3. **Live Analysis**: `python main_system.py` (edit to use your sport)

## Troubleshooting

### Common Issues

**Sport not found**: Check spelling in `SPORTS_CONFIG` key
**No matches found**: Review `kalshi_keywords` - search Kalshi manually
**Low confidence scores**: Adjust `team_aliases` or lower `match_confidence_threshold`
**Too many false positives**: Increase `match_confidence_threshold` or `min_edge_threshold`

### Debug Mode

Enable detailed logging:

```python
# In main_system.py run_analysis method, add:
print(f"Sport config loaded: {sport_config}")
print(f"Search patterns: {sport_patterns}")
```

## Current Supported Sports

✅ **MLB** - Full team mappings, optimized thresholds  
✅ **NFL** - Full team mappings, game-specific timing  
✅ **NBA** - Full team mappings, frequent games  
✅ **NHL** - Full team mappings, optimized for hockey  
🔧 **College Football** - Basic setup, needs team mappings  
🔧 **College Basketball** - Basic setup, needs team mappings  

## Next Steps

1. Add your sport using this guide
2. Test thoroughly with recent data
3. Monitor results and tune thresholds
4. Consider adding more sophisticated team/player mappings
5. Share successful configurations with the team

The system is designed to make adding new leagues as simple as updating a single configuration file!