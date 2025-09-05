"""
Odds API Response Handler
Converts Odds API responses to unified data models.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from market_data_core.models import (
    Game, Market, Quote, Team, Sport, MarketType, QuoteSide, Category
)
from market_data_core.team_matcher import TeamMatcher, MatchResult
from market_data_core.utils import parse_timestamp, setup_logging


class OddsAPIResponseHandler:
    """Handles conversion of Odds API responses to unified models"""
    
    # Sport mapping from our Sport enum to Odds API keys
    SPORT_MAP = {
        Sport.NFL: 'americanfootball_nfl',
        Sport.MLB: 'baseball_mlb',
        Sport.NBA: 'basketball_nba',
        Sport.NHL: 'icehockey_nhl',
        Sport.NCAAF: 'americanfootball_ncaaf',
        Sport.NCAAB: 'basketball_ncaab'
    }
    
    # Reverse mapping
    REVERSE_SPORT_MAP = {v: k for k, v in SPORT_MAP.items()}
    
    # Market type mapping
    MARKET_TYPE_MAP = {
        'h2h': MarketType.MONEYLINE,  # Head-to-head (moneyline)
        'spreads': MarketType.SPREAD,
        'totals': MarketType.TOTAL,
        'outrights': MarketType.FUTURES
    }
    
    def __init__(self):
        """Initialize response handler"""
        self.logger = setup_logging("odds_api_handler")
    
    async def odds_data_to_games(self, odds_data: List[Dict], sport: Sport,
                                team_matcher: TeamMatcher) -> List[Game]:
        """
        Convert Odds API data to Game objects
        
        Args:
            odds_data: Raw odds data from Odds API
            sport: Sport type
            team_matcher: Team matcher for resolving team names
            
        Returns:
            List of Game objects
        """
        games = []
        
        for game_data in odds_data:
            try:
                game = await self._create_game_from_odds_data(game_data, sport, team_matcher)
                if game:
                    games.append(game)
            except Exception as e:
                self.logger.error(f"Error creating game from odds data: {e}")
                continue
        
        self.logger.info(f"Converted {len(games)} games from {len(odds_data)} odds entries")
        return games
    
    async def _create_game_from_odds_data(self, game_data: Dict, sport: Sport,
                                        team_matcher: TeamMatcher) -> Optional[Game]:
        """Create Game object from Odds API game data"""
        try:
            # Extract basic game info
            game_id = game_data.get('id')
            if not game_id:
                self.logger.warning("Game data missing ID")
                return None
            
            # Extract team names
            home_team_name = game_data.get('home_team')
            away_team_name = game_data.get('away_team')
            
            if not home_team_name or not away_team_name:
                self.logger.warning(f"Game {game_id} missing team names")
                return None
            
            # Match teams using team matcher
            home_result = team_matcher.match_team(home_team_name)
            away_result = team_matcher.match_team(away_team_name)
            
            if not home_result.matched_team or not away_result.matched_team:
                self.logger.warning(f"Could not match teams: {home_team_name}, {away_team_name}")
                return None
            
            # Parse game date
            game_date = self._parse_game_date(game_data.get('commence_time'))
            if not game_date:
                self.logger.warning(f"Game {game_id} missing or invalid date")
                return None
            
            # Determine season from date
            season = str(game_date.year)
            
            # For NFL, determine week (simplified - could be enhanced)
            week = None
            if sport == Sport.NFL:
                # Simple week calculation based on date
                # NFL season typically starts first week of September
                import calendar
                september_first = datetime(game_date.year, 9, 1)
                days_diff = (game_date - september_first).days
                week = max(1, min(18, (days_diff // 7) + 1))
            
            # Extract sport key from data
            sport_key = game_data.get('sport_key', '')
            sport_title = game_data.get('sport_title', '')
            
            # Create Game object
            game = Game(
                game_id=game_id,
                home_team=home_result.matched_team,
                away_team=away_result.matched_team,
                sport=sport,
                game_date=game_date,
                season=season,
                week=week,
                status=self._determine_game_status(game_data),
                metadata={
                    'odds_api_id': game_id,
                    'odds_api_sport_key': sport_key,
                    'odds_api_sport_title': sport_title,
                    'original_home_team': home_team_name,
                    'original_away_team': away_team_name,
                    'team_match_confidence': {
                        'home': home_result.confidence,
                        'away': away_result.confidence
                    },
                    'bookmakers_data': game_data.get('bookmakers', []),
                    'commence_time': game_data.get('commence_time')
                }
            )
            
            return game
            
        except Exception as e:
            self.logger.error(f"Error creating game from odds data: {e}")
            return None
    
    def _parse_game_date(self, commence_time: Optional[str]) -> Optional[datetime]:
        """Parse game date from Odds API commence_time"""
        if not commence_time:
            return None
        
        try:
            # Odds API uses ISO format timestamps
            return parse_timestamp(commence_time)
        except Exception as e:
            self.logger.warning(f"Error parsing commence_time {commence_time}: {e}")
            return None
    
    def _determine_game_status(self, game_data: Dict) -> str:
        """Determine game status from Odds API data"""
        try:
            # Odds API doesn't provide explicit game status
            # Determine based on game time and current time
            commence_time = game_data.get('commence_time')
            if not commence_time:
                return 'unknown'
            
            game_date = self._parse_game_date(commence_time)
            if not game_date:
                return 'unknown'
            
            now = datetime.utcnow()
            
            # Simple status determination
            if game_date > now:
                return 'scheduled'
            elif game_date <= now and (now - game_date).total_seconds() < 10800:  # Within 3 hours
                return 'live'
            else:
                return 'final'  # Assume finished if more than 3 hours past start
                
        except Exception:
            return 'unknown'
    
    async def create_markets_from_bookmakers(self, game: Game) -> List[Market]:
        """Create Market objects from bookmaker data in game metadata"""
        markets = []
        
        try:
            bookmakers_data = game.metadata.get('bookmakers_data', [])
            
            for bookmaker_data in bookmakers_data:
                bookmaker_name = bookmaker_data.get('key', 'unknown')
                markets_data = bookmaker_data.get('markets', [])
                
                for market_data in markets_data:
                    market = await self._create_market_from_bookmaker_data(
                        market_data, game, bookmaker_name
                    )
                    if market:
                        markets.append(market)
            
        except Exception as e:
            self.logger.error(f"Error creating markets from bookmakers: {e}")
        
        return markets
    
    async def _create_market_from_bookmaker_data(self, market_data: Dict, game: Game,
                                               bookmaker_name: str) -> Optional[Market]:
        """Create Market object from bookmaker market data"""
        try:
            market_key = market_data.get('key')
            if not market_key:
                return None
            
            # Determine market type from key
            market_type = self.MARKET_TYPE_MAP.get(market_key, MarketType.MONEYLINE)
            
            # Create market ID
            market_id = f"{game.game_id}_{bookmaker_name}_{market_key}"
            
            # Extract market details
            last_update = market_data.get('last_update')
            outcomes = market_data.get('outcomes', [])
            
            # For spreads and totals, extract the line/point value
            spread_line = None
            total_line = None
            
            if market_type == MarketType.SPREAD and outcomes:
                # Spread outcomes typically have 'point' values
                for outcome in outcomes:
                    point = outcome.get('point')
                    if point is not None:
                        spread_line = float(point)
                        break
            
            elif market_type == MarketType.TOTAL and outcomes:
                # Total outcomes typically have 'point' values for the total
                for outcome in outcomes:
                    point = outcome.get('point')
                    if point is not None:
                        total_line = float(point)
                        break
            
            # Create Market object
            market = Market(
                market_id=market_id,
                game=game,
                market_type=market_type,
                name=f"{bookmaker_name.title()} {market_key.title()}",
                spread_line=spread_line,
                total_line=total_line,
                is_active=True,  # Assume active if in API response
                close_time=parse_timestamp(last_update) if last_update else None,
                metadata={
                    'odds_api_market_key': market_key,
                    'bookmaker': bookmaker_name,
                    'last_update': last_update,
                    'outcomes_count': len(outcomes),
                    'raw_market_data': market_data
                }
            )
            
            return market
            
        except Exception as e:
            self.logger.error(f"Error creating market from bookmaker data: {e}")
            return None
    
    async def create_quotes_from_outcomes(self, market: Market, outcomes: List[Dict]) -> List[Quote]:
        """Create Quote objects from market outcomes"""
        quotes = []
        
        try:
            for i, outcome in enumerate(outcomes):
                quote = await self._create_quote_from_outcome(outcome, market, i)
                if quote:
                    quotes.append(quote)
                    
        except Exception as e:
            self.logger.error(f"Error creating quotes from outcomes: {e}")
        
        return quotes
    
    async def _create_quote_from_outcome(self, outcome: Dict, market: Market,
                                       outcome_index: int) -> Optional[Quote]:
        """Create Quote object from single outcome"""
        try:
            # Extract outcome data
            name = outcome.get('name')
            price = outcome.get('price')  # American odds format
            point = outcome.get('point')  # For spreads/totals
            
            if not name or price is None:
                return None
            
            # Determine quote side based on market type and outcome
            quote_side = self._determine_quote_side(market, outcome, name)
            
            # Create quote ID
            quote_id = f"{market.market_id}_{outcome_index}_{name.replace(' ', '_')}"
            
            # Convert American odds to other formats
            american_odds = int(price) if isinstance(price, (int, float)) else None
            decimal_odds = None
            implied_probability = None
            
            if american_odds is not None:
                decimal_odds = self._american_to_decimal(american_odds)
                implied_probability = self._american_to_probability(american_odds)
            
            # Create Quote object
            quote = Quote(
                quote_id=quote_id,
                market=market,
                side=quote_side,
                provider="odds_api",
                bookmaker=market.metadata.get('bookmaker'),
                american_odds=american_odds,
                decimal_odds=decimal_odds,
                implied_probability=implied_probability,
                timestamp=datetime.utcnow(),
                metadata={
                    'outcome_name': name,
                    'point': point,
                    'raw_outcome': outcome
                }
            )
            
            return quote
            
        except Exception as e:
            self.logger.error(f"Error creating quote from outcome: {e}")
            return None
    
    def _determine_quote_side(self, market: Market, outcome: Dict, name: str) -> QuoteSide:
        """Determine quote side from market type and outcome"""
        name_upper = name.upper()
        
        if market.market_type == MarketType.MONEYLINE:
            # For moneyline, check if it's home or away team
            if market.game.home_team.matches(name) > 0.8:
                return QuoteSide.HOME
            elif market.game.away_team.matches(name) > 0.8:
                return QuoteSide.AWAY
            else:
                # Default based on name patterns
                return QuoteSide.HOME if 'HOME' in name_upper else QuoteSide.AWAY
        
        elif market.market_type == MarketType.TOTAL:
            return QuoteSide.OVER if 'OVER' in name_upper else QuoteSide.UNDER
        
        elif market.market_type == MarketType.SPREAD:
            # For spreads, determine based on point value or team name
            point = outcome.get('point')
            if point is not None:
                return QuoteSide.HOME if float(point) < 0 else QuoteSide.AWAY
            else:
                # Fallback to team matching
                if market.game.home_team.matches(name) > 0.8:
                    return QuoteSide.HOME
                else:
                    return QuoteSide.AWAY
        
        # Default fallback
        return QuoteSide.HOME
    
    @staticmethod
    def _american_to_decimal(american_odds: int) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    @staticmethod
    def _american_to_probability(american_odds: int) -> float:
        """Convert American odds to implied probability"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def get_sport_key_for_api(self, sport: Sport) -> Optional[str]:
        """Get Odds API sport key for our Sport enum"""
        return self.SPORT_MAP.get(sport)
    
    def get_sport_from_api_key(self, api_key: str) -> Optional[Sport]:
        """Get our Sport enum from Odds API key"""
        return self.REVERSE_SPORT_MAP.get(api_key)
    
    async def create_categories_for_sport(self, sport: Sport) -> List[Category]:
        """Create categories for a sport (Odds API organizes by bookmakers)"""
        categories = []
        
        # Create a general category for the sport
        main_category = Category(
            category_id=f"odds_api_{sport.value}",
            name=f"{sport.value.upper()} Markets",
            sport=sport,
            description=f"All {sport.value.upper()} markets from sportsbooks",
            metadata={'sport_key': self.SPORT_MAP.get(sport)}
        )
        categories.append(main_category)
        
        return categories