# NFL Odds Comparison System

A stripped-down system focused on comparing NFL odds between Pinnacle (sportsbook) and Kalshi (prediction market).

## What This System Does

1. **View Pinnacle NFL Games** - Get current NFL games and odds from Pinnacle sportsbook
2. **View Kalshi NFL Markets** - Get NFL prediction markets from Kalshi
3. **View Aligned Games** - See games that have lines on both platforms and identify mispricing opportunities

## Quick Start

### 1. View Pinnacle NFL Games
```bash
python view_nfl_pinnacle.py
```

### 2. View Kalshi NFL Markets  
```bash
python view_nfl_kalshi.py
```

### 3. View Games with Both Lines
```bash
python view_nfl_aligned.py
```

### 4. Run Complete Demo
```bash
python simple_nfl_demo.py
```

## File Structure

```
├── keys/
│   ├── odds_api_key.txt         # Your Odds API key
│   └── kalshi_credentials.txt   # Your Kalshi credentials
├── prod_ready/
│   ├── core/
│   │   ├── main_system.py       # Main orchestration
│   │   ├── pinnacle_client.py   # Pinnacle API client
│   │   ├── kalshi_client.py     # Kalshi API client
│   │   ├── data_aligner.py      # Game matching logic
│   │   └── odds_converter.py    # Odds conversion utilities
│   ├── config/
│   │   └── sports_config.py     # NFL configuration
│   └── utils/
│       └── timestamp_utils.py   # Time handling utilities
├── view_nfl_pinnacle.py         # View Pinnacle NFL games
├── view_nfl_kalshi.py           # View Kalshi NFL markets
├── view_nfl_aligned.py          # View aligned games
└── simple_nfl_demo.py           # Complete demo script
```

## Setup Required

1. **Odds API Key**: Get from https://the-odds-api.com and put in `keys/odds_api_key.txt`
2. **Kalshi Credentials**: Get from https://kalshi.com and put in `keys/kalshi_credentials.txt`

## What Was Removed

This system was stripped from a larger multi-sport mispricing detection system. Removed:
- All MLB, NBA, NHL, WNBA, UFC functionality  
- Debug and test files (60+ files)
- Complex analysis and strategy modules
- Documentation and planning files

Now focused purely on NFL odds comparison between Pinnacle and Kalshi.

## Folder: prod_ready/