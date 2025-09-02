# Sports Market Data Library

A unified Python library for accessing sports betting and prediction market data from multiple providers including Kalshi (prediction markets) and The Odds API (sportsbook aggregation).

## Features

- **Unified Interface**: Single API to access multiple sports data providers
- **Multi-Provider Support**: Kalshi prediction markets and The Odds API sportsbook data
- **Real-time Data**: Live odds, games, and market information
- **Arbitrage Detection**: Find pricing discrepancies between providers
- **Advanced Team Matching**: Fuzzy matching to align team names across providers
- **Error Resilience**: Continues operation even if some providers are unavailable
- **Rate Limiting**: Built-in rate limiting and retry logic
- **Async/Await**: Full asynchronous support for high performance

## Supported Sports

- **NFL** (American Football)
- **MLB** (Baseball)  
- **NBA** (Basketball)
- **NHL** (Hockey)

## Supported Providers

### Kalshi
- Prediction markets for sports outcomes
- Binary yes/no markets on game winners, season totals, etc.
- RSA-PSS authentication
- Real-time market prices

### The Odds API
- Aggregated sportsbook odds from 40+ bookmakers
- Moneyline, spread, and total markets
- American, decimal, and fractional odds formats
- Live and upcoming games

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd sports-market-data-library

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
import asyncio
from unified_client import create_unified_client
from market_data_core import Sport

async def main():
    # Configure providers
    client = create_unified_client(
        kalshi_config={
            'api_key': 'your_kalshi_api_key',
            'private_key': 'your_rsa_private_key_pem',
            'base_url': 'https://demo-api.kalshi.co/trade-api/v2'
        },
        odds_api_config={
            'api_key': 'your_odds_api_key',
            'base_url': 'https://api.the-odds-api.com/v4'
        }
    )
    
    # Authenticate with all providers
    auth_results = await client.authenticate_all()
    print(f"Authentication: {auth_results}")
    
    # Get unified NFL games from all providers
    nfl_games = await client.get_unified_games(Sport.NFL)
    print(f"Found {len(nfl_games)} NFL games")
    
    for game in nfl_games[:3]:
        sources = game.metadata.get('source_providers', [])
        print(f"{game.away_team.nickname} @ {game.home_team.nickname}")
        print(f"  Date: {game.game_date}")
        print(f"  Sources: {', '.join(sources)}")

asyncio.run(main())
```

### Arbitrage Detection

```python
# Find arbitrage opportunities
arbitrage_ops = await client.find_arbitrage_opportunities(
    Sport.NFL,
    min_edge=0.02  # 2% minimum edge
)

for opp in arbitrage_ops:
    print(f"{opp.game.away_team.nickname} @ {opp.game.home_team.nickname}")
    print(f"  Edge: {opp.total_edge:.2%}")
    print(f"  Providers: {', '.join(opp.providers_involved)}")
```

### Individual Provider Access

```python
from market_data_kalshi import KalshiClient
from market_data_odds import OddsAPIClient

# Direct Kalshi access
kalshi_client = KalshiClient({
    'api_key': 'your_kalshi_api_key',
    'private_key': 'your_rsa_private_key_pem'
})

# Direct Odds API access  
odds_client = OddsAPIClient({
    'api_key': 'your_odds_api_key'
})
```

## Configuration

### Environment Variables

Set up your API credentials:

```bash
# Kalshi credentials
export KALSHI_API_KEY='your_kalshi_api_key'
export KALSHI_PRIVATE_KEY='your_rsa_private_key_pem_content'

# Odds API credential
export ODDS_API_KEY='your_odds_api_key'
```

### API Keys

#### Kalshi
1. Sign up at [kalshi.com](https://kalshi.com)
2. Generate API keys in your account settings
3. Create RSA private key for authentication
4. Use demo environment URL for testing: `https://demo-api.kalshi.co/trade-api/v2`

#### The Odds API
1. Sign up at [the-odds-api.com](https://the-odds-api.com)
2. Get your API key from the dashboard
3. Free tier includes 500 requests/month

## Architecture

### Core Components

- **`market_data_core`**: Shared data models, utilities, and base classes
- **`market_data_kalshi`**: Kalshi prediction market integration
- **`market_data_odds`**: The Odds API sportsbook integration
- **`unified_client`**: Multi-provider client with unified interface

### Data Models

```python
from market_data_core import Sport, Team, Game, Market, Quote, Category

# Unified data models work across all providers
game = Game(
    game_id="nfl_kc_bal_2024_w1",
    home_team=Team(name="Baltimore Ravens", city="Baltimore", nickname="Ravens"),
    away_team=Team(name="Kansas City Chiefs", city="Kansas City", nickname="Chiefs"),
    sport=Sport.NFL,
    game_date=datetime(2024, 9, 5, 20, 20),
    season="2024",
    week=1
)
```

### Authentication

#### Kalshi RSA-PSS Authentication
```python
from market_data_kalshi import KalshiAuthenticator

auth = KalshiAuthenticator(
    api_key="your_api_key",
    private_key="-----BEGIN PRIVATE KEY-----\n...",
    base_url="https://demo-api.kalshi.co/trade-api/v2"
)
```

#### Odds API Key Authentication
```python
from market_data_odds import OddsAPIAuthenticator

auth = OddsAPIAuthenticator("your_odds_api_key")
```

## Testing

The library includes comprehensive test suites:

```bash
# Run all tests
python -m pytest tests/

# Run specific test phases
python tests/test_core/test_phase1_validation.py
python tests/test_kalshi/test_kalshi_integration.py
python tests/test_odds/test_odds_integration.py
python tests/test_integration/test_cross_provider.py
```

## Examples

See the `examples/` directory for detailed usage examples:

- `basic_usage.py` - Basic library usage and provider setup
- `advanced_usage.py` - Arbitrage detection, custom configurations, error handling

## API Reference

### Unified Client

```python
class UnifiedMarketDataClient:
    async def authenticate_all() -> Dict[ProviderType, bool]
    async def get_sports(provider_filter=None) -> Dict[ProviderType, ProviderResponse]
    async def get_games(sport, date_from=None, date_to=None) -> Dict[ProviderType, ProviderResponse]
    async def get_unified_games(sport, date_from=None, date_to=None) -> List[Game]
    async def find_arbitrage_opportunities(sport, min_edge=0.02) -> List[ArbitrageOpportunity]
    async def get_best_quotes(sport, market_type="moneyline") -> Dict[str, Dict]
    async def health_check() -> Dict[str, Any]
```

### Provider Clients

```python
class KalshiClient(BaseMarketDataClient):
    async def get_categories(sport) -> ProviderResponse
    async def get_games(sport, date_from=None, date_to=None) -> ProviderResponse
    async def get_markets(game) -> ProviderResponse
    
class OddsAPIClient(BaseMarketDataClient):
    async def get_categories(sport) -> ProviderResponse
    async def get_games(sport, date_from=None, date_to=None) -> ProviderResponse
    async def get_markets(game) -> ProviderResponse
```

## Rate Limits

- **Kalshi**: No explicit rate limits in demo environment
- **The Odds API**: 500 requests/month (free tier), 500 requests/minute

## Error Handling

The library is designed for resilience:

- Continues operating if some providers are unavailable
- Comprehensive error logging
- Graceful degradation of functionality
- Retry logic with exponential backoff

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite
5. Submit a pull request

## License

[MIT License](LICENSE)

## Support

For questions and support:
- Check the `examples/` directory for usage patterns
- Run the test suites to validate your setup
- Review provider documentation:
  - [Kalshi API Docs](https://kalshi-public-docs.s3.amazonaws.com/KalshiAPI_v1.2.pdf)
  - [The Odds API Docs](https://the-odds-api.com/liveapi/guides/v4/)

## Changelog

### v0.1.0 (Current)
- Initial release
- Kalshi and Odds API integration
- Unified multi-provider client
- NFL/MLB/NBA/NHL support
- Arbitrage detection framework
- Comprehensive test suite