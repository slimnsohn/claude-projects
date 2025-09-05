from enum import Enum

class Sport(Enum):
    NFL = "nfl"
    NBA = "nba"
    MLB = "mlb"
    NHL = "nhl"

class BetType(Enum):
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    TOTAL = "total"  # over/under

class Provider(Enum):
    ODDS_API = "odds_api"
    KALSHI = "kalshi"
    POLYMARKET = "polymarket"

# Mapping for different naming conventions
PROVIDER_SPORT_MAPPING = {
    Provider.ODDS_API: {
        Sport.NFL: "americanfootball_nfl",
        Sport.NBA: "basketball_nba",
        Sport.MLB: "baseball_mlb",
        Sport.NHL: "icehockey_nhl"
    },
    Provider.KALSHI: {
        Sport.NFL: "nfl",
        Sport.NBA: "nba",
        Sport.MLB: "mlb",
        Sport.NHL: "nhl"
    },
    Provider.POLYMARKET: {
        Sport.NFL: "NFL",
        Sport.NBA: "NBA", 
        Sport.MLB: "MLB",
        Sport.NHL: "NHL"
    }
}