# Sports Analytics Platform

A comprehensive Python platform for aggregating sports odds from multiple providers, comparing prices, and identifying arbitrage opportunities.

## Features

- **Multi-Provider Data Aggregation**: Supports Odds API, Kalshi, and Polymarket
- **Normalized Data Models**: Common format for games, odds, and orders across all providers
- **Arbitrage Detection**: Automatically find profitable betting opportunities
- **Best Odds Finder**: Compare odds across providers to find the best prices
- **Extensible Architecture**: Easy to add new sports, bet types, and providers

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Basic Demo**
   ```bash
   python main.py
   ```

4. **Run Tests**
   ```bash
   python tests/test_basic.py
   python tests/test_models.py
   python tests/test_aggregator.py
   ```

## Project Structure

```
sports_analytics_platform/
├── config/                 # Configuration and constants
│   ├── constants.py       # Sports, bet types, provider mappings
│   ├── settings.py        # Environment variables and settings
│   └── __init__.py
│
├── market_data/           # Data providers and aggregation
│   ├── base.py           # Abstract base class for providers
│   ├── aggregator.py     # Central data aggregation logic
│   │
│   ├── odds_api/         # The Odds API integration
│   │   └── production/
│   │       └── client.py
│   │
│   ├── kalshi/           # Kalshi integration (placeholder)
│   │   └── production/
│   │       └── client.py
│   │
│   └── polymarket/       # Polymarket integration (placeholder)
│       └── production/
│           └── client.py
│
├── models/               # Data models
│   ├── game.py          # Normalized game representation
│   ├── odds.py          # Normalized odds representation
│   └── order.py         # Order and position models
│
├── utils/               # Utility functions
├── tests/              # Test files
│   ├── test_basic.py   # Integration tests
│   ├── test_models.py  # Model unit tests
│   └── test_aggregator.py # Aggregator tests
│
├── main.py             # Main demo application
├── requirements.txt    # Python dependencies
└── .env.example       # Environment variables template
```

## Core Components

### Data Models

- **Game**: Normalized representation of a sports game with metadata
- **Odds**: Normalized odds data with conversion utilities
- **Order**: Order management for tracking bets
- **Position**: Position tracking for portfolio management

### Market Data Aggregation

- **DataProvider**: Abstract base class for all data providers
- **MarketDataAggregator**: Central orchestrator for data from multiple sources
- **Client Implementations**: Provider-specific API clients

### Key Features

#### Game Deduplication
Games from different providers are automatically deduplicated based on teams and start time:

```python
from market_data.aggregator import MarketDataAggregator
from config.constants import Sport

aggregator = MarketDataAggregator()
games = aggregator.get_all_games(Sport.NFL)
```

#### Best Odds Finding
Find the best odds across all providers:

```python
best_odds = aggregator.get_best_odds(game, BetType.MONEYLINE)
print(f"Best home odds: {best_odds['home'].home_ml}")
```

#### Arbitrage Detection
Automatically detect arbitrage opportunities:

```python
arb = aggregator.find_arbitrage_opportunities(game, BetType.MONEYLINE)
if arb:
    print(f"Profit margin: {arb['profit_margin']:.2%}")
```

## API Keys Required

1. **The Odds API**: Get your key from [the-odds-api.com](https://the-odds-api.com/)
2. **Kalshi API**: Get credentials from [kalshi.com](https://kalshi.com/) (optional)
3. **Polymarket API**: Get key from [polymarket.com](https://polymarket.com/) (optional)

## Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
ODDS_API_KEY=your_odds_api_key_here
KALSHI_API_KEY=your_kalshi_api_key_here
KALSHI_API_SECRET=your_kalshi_api_secret_here
POLYMARKET_API_KEY=your_polymarket_api_key_here
```

## Usage Examples

### Basic Usage

```python
from market_data.aggregator import MarketDataAggregator
from config.constants import Sport, BetType

# Initialize aggregator
aggregator = MarketDataAggregator()

# Get all NFL games
games = aggregator.get_all_games(Sport.NFL)

for game in games:
    print(f"{game.away_team} @ {game.home_team}")
    
    # Get best moneyline odds
    best_ml = aggregator.get_best_odds(game, BetType.MONEYLINE)
    if best_ml:
        print(f"Home: {best_ml['home'].home_ml} ({best_ml['home'].provider.value})")
        print(f"Away: {best_ml['away'].away_ml} ({best_ml['away'].provider.value})")
```

### Single Provider

```python
# Fetch from specific provider only
odds_api_games = aggregator.get_games_by_provider(Sport.NFL, Provider.ODDS_API)
```

### Arbitrage Detection

```python
for game in games:
    arb = aggregator.find_arbitrage_opportunities(game, BetType.MONEYLINE)
    if arb:
        print(f"Arbitrage found! Profit: {arb['profit_margin']:.2%}")
        print(f"Bet {arb['home_bet']['stake_percentage']:.1%} on home")
        print(f"Bet {arb['away_bet']['stake_percentage']:.1%} on away")
```

## Testing

The platform includes comprehensive tests:

```bash
# Run integration tests
python tests/test_basic.py

# Run model tests  
python tests/test_models.py

# Run aggregator tests
python tests/test_aggregator.py
```

## Architecture Principles

1. **Modularity**: Each provider is completely independent
2. **Normalization**: All data converted to common models
3. **Extensibility**: Easy to add new sports, bet types, providers
4. **Error Handling**: Graceful degradation when providers fail
5. **Testing**: Comprehensive test coverage

## Adding New Providers

1. Create new directory under `market_data/`
2. Implement `DataProvider` base class
3. Add provider to `config/constants.py`
4. Update aggregator initialization

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions, please create an issue in the repository.