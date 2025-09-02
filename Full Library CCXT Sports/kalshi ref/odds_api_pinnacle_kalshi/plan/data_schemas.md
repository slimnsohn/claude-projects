# Data Schemas for Mispricing Detection System

## Normalized Odds Schema

### Core Game Data Structure
```python
{
    "game_id": str,              # Unique identifier for the game
    "game_date": str,            # ISO format date (YYYY-MM-DD)
    "game_time": str,            # ISO format datetime (YYYY-MM-DDTHH:MM:SSZ)
    "sport": str,                # "MLB" for this implementation
    "home_team": str,            # Standardized team name
    "away_team": str,            # Standardized team name
    "source": str,               # "pinnacle" or "kalshi"
    "home_odds": {
        "american": int,         # American odds format (+140, -110, etc.)
        "decimal": float,        # Decimal odds format (2.40, 1.91, etc.)
        "implied_probability": float  # Percentage (0.0-1.0)
    },
    "away_odds": {
        "american": int,
        "decimal": float,
        "implied_probability": float
    },
    "metadata": {
        "last_updated": str,     # ISO timestamp when data was fetched
        "bookmaker": str,        # "pinnacle" for OddsAPI data
        "market_type": str,      # "moneyline" for this implementation
        "raw_data": dict         # Original API response for debugging
    }
}
```

## Conversion Formulas

### American to Decimal Odds
```python
def american_to_decimal(american_odds):
    if american_odds > 0:
        return (american_odds / 100) + 1
    else:
        return (100 / abs(american_odds)) + 1
```

### Decimal to Implied Probability
```python
def decimal_to_probability(decimal_odds):
    return 1 / decimal_odds
```

### Kalshi Percentage to American Odds
```python
def kalshi_to_american(percentage, kalshi_fee=0.03):
    # Adjust for Kalshi's 3% fee structure
    adjusted_percentage = percentage * (1 - kalshi_fee)
    
    if adjusted_percentage >= 0.5:
        return int(-100 / (adjusted_percentage / (1 - adjusted_percentage)))
    else:
        return int(100 * ((1 - adjusted_percentage) / adjusted_percentage))
```

## Team Name Standardization

### MLB Team Mapping
```python
TEAM_MAPPINGS = {
    # Pinnacle variations -> Standard names
    "Los Angeles Angels": ["LAA", "Angels", "LA Angels"],
    "Houston Astros": ["HOU", "Astros"],
    "Oakland Athletics": ["OAK", "Athletics", "A's"],
    "Toronto Blue Jays": ["TOR", "Blue Jays", "Jays"],
    "Atlanta Braves": ["ATL", "Braves"],
    "Milwaukee Brewers": ["MIL", "Brewers"],
    "St. Louis Cardinals": ["STL", "Cardinals"],
    "Chicago Cubs": ["CHC", "Cubs"],
    "Arizona Diamondbacks": ["ARI", "Diamondbacks", "D-backs"],
    "Colorado Rockies": ["COL", "Rockies"],
    "Los Angeles Dodgers": ["LAD", "Dodgers"],
    "San Diego Padres": ["SD", "Padres"],
    "San Francisco Giants": ["SF", "Giants"],
    "Miami Marlins": ["MIA", "Marlins"],
    "New York Mets": ["NYM", "Mets"],
    "Philadelphia Phillies": ["PHI", "Phillies"],
    "Pittsburgh Pirates": ["PIT", "Pirates"],
    "Washington Nationals": ["WSH", "Nationals"],
    "Chicago White Sox": ["CWS", "White Sox"],
    "Cleveland Guardians": ["CLE", "Guardians"],
    "Detroit Tigers": ["DET", "Tigers"],
    "Kansas City Royals": ["KC", "Royals"],
    "Minnesota Twins": ["MIN", "Twins"],
    "New York Yankees": ["NYY", "Yankees"],
    "Baltimore Orioles": ["BAL", "Orioles"],
    "Boston Red Sox": ["BOS", "Red Sox"],
    "Tampa Bay Rays": ["TB", "Rays"],
    "Texas Rangers": ["TEX", "Rangers"],
    "Seattle Mariners": ["SEA", "Mariners"]
}
```

## Mispricing Detection Schema

### Opportunity Structure
```python
{
    "opportunity_id": str,       # Unique identifier for this opportunity
    "game_data": dict,           # Full normalized game data
    "pinnacle_odds": dict,       # Pinnacle odds data
    "kalshi_odds": dict,         # Kalshi odds data (converted)
    "discrepancy": {
        "home_team_diff": float, # Difference in implied probability
        "away_team_diff": float,
        "max_edge": float,       # Highest profitable edge found
        "recommended_side": str  # "home" or "away"
    },
    "profit_analysis": {
        "expected_value": float, # Expected value of the bet
        "kelly_fraction": float, # Kelly criterion bet sizing
        "confidence_score": float # 0.0-1.0 confidence in opportunity
    },
    "timestamp": str             # When opportunity was identified
}
```

## Validation Test Cases

### Odds Conversion Test Cases
```python
CONVERSION_TEST_CASES = [
    {"percentage": 0.40, "expected_american": 140},
    {"percentage": 0.45, "expected_american": 114},
    {"percentage": 0.50, "expected_american": -107},  # With fee adjustment
    {"percentage": 0.70, "expected_american": -262},
    {"percentage": 0.85, "expected_american": -606},
    {"percentage": 0.95, "expected_american": -2396}
]
```