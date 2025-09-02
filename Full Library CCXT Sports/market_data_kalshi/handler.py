"""
Kalshi Response Handler
Converts Kalshi API responses to unified data models.
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from market_data_core.models import (
    Game, Market, Quote, Team, Sport, MarketType, QuoteSide, Category
)
from market_data_core.team_matcher import TeamMatcher, MatchResult
from market_data_core.utils import parse_timestamp, setup_logging


class KalshiResponseHandler:
    """Handles conversion of Kalshi API responses to unified models"""
    
    def __init__(self):
        """Initialize response handler"""
        self.logger = setup_logging("kalshi_handler")
        
        # Market type patterns for Kalshi tickers
        self.market_type_patterns = {
            MarketType.MONEYLINE: [
                r'-WIN$',  # Team win markets (e.g., KXNFLGAME-KC-BAL-24-WIN)
                r'-W$'     # Shortened win markets
            ]
        }
    
    async def markets_to_games(self, markets_data: List[Dict], sport: Sport, 
                             team_matcher: TeamMatcher) -> List[Game]:
        """
        Convert Kalshi markets data to Game objects
        
        Args:
            markets_data: Raw market data from Kalshi API
            sport: Sport type
            team_matcher: Team matcher for resolving team names
            
        Returns:
            List of Game objects
        """
        games = []
        games_by_id = {}  # Group markets by game
        
        for market_data in markets_data:
            try:
                # Parse game info from market ticker
                game_info = self._parse_game_from_ticker(market_data.get('ticker', ''), sport)
                if not game_info:
                    continue
                
                game_id = game_info['game_id']
                
                # Group markets by game
                if game_id not in games_by_id:
                    games_by_id[game_id] = {
                        'game_info': game_info,
                        'markets': []
                    }
                
                games_by_id[game_id]['markets'].append(market_data)
                
            except Exception as e:
                self.logger.warning(f"Error parsing market {market_data.get('ticker', 'unknown')}: {e}")
                continue
        
        # Create Game objects
        for game_id, game_group in games_by_id.items():
            try:
                game = await self._create_game_from_group(game_group, sport, team_matcher)
                if game:
                    games.append(game)
            except Exception as e:
                self.logger.error(f"Error creating game {game_id}: {e}")
                continue
        
        self.logger.info(f"Converted {len(games)} games from {len(markets_data)} markets")
        return games
    
    def _parse_game_from_ticker(self, ticker: str, sport: Sport) -> Optional[Dict]:
        """
        Parse game information from Kalshi market ticker
        
        Example ticker: KXNFLGAME-KC-BAL-24W1-WIN
        Format: SERIES-TEAM1-TEAM2-SEASON+WEEK-MARKET
        """
        if not ticker:
            return None
        
        try:
            # Basic pattern for NFL games
            if sport == Sport.NFL:
                # Pattern: KXNFLGAME-TEAM1-TEAM2-SEASON+WEEK-MARKET
                match = re.match(r'KXNFLGAME-([A-Z]+)-([A-Z]+)-(\d{2})W(\d+)-([A-Z]+)', ticker)
                if match:
                    team1, team2, season_short, week, market_type = match.groups()
                    
                    # Determine season from short format (24 -> 2024)
                    season = f"20{season_short}"
                    
                    return {
                        'game_id': f"nfl_{season}_week{week}_{team1.lower()}_{team2.lower()}",
                        'team1': team1,
                        'team2': team2,
                        'season': season,
                        'week': int(week),
                        'sport': sport
                    }
            
            # Pattern for other sports (MLB, NBA, etc.)
            # KXMLBGAME-LAD-SD-24-WIN
            elif sport in [Sport.MLB, Sport.NBA, Sport.NHL]:
                sport_code = {
                    Sport.MLB: 'KXMLBGAME',
                    Sport.NBA: 'KXNBAGAME', 
                    Sport.NHL: 'KXNHLGAME'
                }[sport]
                
                match = re.match(rf'{sport_code}-([A-Z]+)-([A-Z]+)-(\d{{2}})-([A-Z]+)', ticker)
                if match:
                    team1, team2, season_short, market_type = match.groups()
                    season = f"20{season_short}"
                    
                    return {
                        'game_id': f"{sport.value}_{season}_{team1.lower()}_{team2.lower()}",
                        'team1': team1,
                        'team2': team2,
                        'season': season,
                        'week': None,
                        'sport': sport
                    }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error parsing ticker {ticker}: {e}")
            return None
    
    async def _create_game_from_group(self, game_group: Dict, sport: Sport,
                                    team_matcher: TeamMatcher) -> Optional[Game]:
        """Create Game object from grouped market data"""
        try:
            game_info = game_group['game_info']
            markets = game_group['markets']
            
            if not markets:
                return None
            
            # Use first market for common game data
            first_market = markets[0]
            
            # Match teams using team matcher
            team1_result = team_matcher.match_team(game_info['team1'])
            team2_result = team_matcher.match_team(game_info['team2'])
            
            if not team1_result.matched_team or not team2_result.matched_team:
                self.logger.warning(f"Could not match teams: {game_info['team1']}, {game_info['team2']}")
                return None
            
            # Determine home/away (Kalshi doesn't specify, so we'll use alphabetical order)
            if team1_result.matched_team.city < team2_result.matched_team.city:
                home_team = team2_result.matched_team
                away_team = team1_result.matched_team
            else:
                home_team = team1_result.matched_team
                away_team = team2_result.matched_team
            
            # Parse game date from market data
            event_ticker = first_market.get('event_ticker', '')
            game_date = self._parse_game_date_from_market(first_market)
            
            if not game_date:
                # Default to a reasonable date if we can't parse it
                game_date = datetime.utcnow()
            
            # Create Game object
            game = Game(
                game_id=game_info['game_id'],
                home_team=home_team,
                away_team=away_team,
                sport=sport,
                game_date=game_date,
                season=game_info['season'],
                week=game_info.get('week'),
                status=self._determine_game_status(markets),
                metadata={
                    'kalshi_markets': markets,
                    'kalshi_event_ticker': event_ticker,
                    'original_team1': game_info['team1'],
                    'original_team2': game_info['team2'],
                    'team_match_confidence': {
                        'team1': team1_result.confidence,
                        'team2': team2_result.confidence
                    }
                }
            )
            
            return game
            
        except Exception as e:
            self.logger.error(f"Error creating game from group: {e}")
            return None
    
    def _parse_game_date_from_market(self, market_data: Dict) -> Optional[datetime]:
        """Parse game date from market data"""
        try:
            # Try various date fields
            date_fields = [
                'open_time',
                'close_time', 
                'event_time',
                'created_time'
            ]
            
            for field in date_fields:
                if field in market_data:
                    date_str = market_data[field]
                    parsed_date = parse_timestamp(date_str)
                    if parsed_date:
                        return parsed_date
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error parsing game date: {e}")
            return None
    
    def _determine_game_status(self, markets: List[Dict]) -> str:
        """Determine game status from market data"""
        try:
            # Check status of markets
            statuses = set()
            for market in markets:
                status = market.get('status', 'unknown')
                statuses.add(status)
            
            # Map Kalshi statuses to our standard statuses
            if 'open' in statuses:
                return 'scheduled'
            elif 'closed' in statuses:
                return 'live'
            elif 'settled' in statuses or 'resolved' in statuses:
                return 'final'
            else:
                return 'unknown'
                
        except Exception:
            return 'unknown'
    
    async def create_markets_from_data(self, markets_data: List[Dict], game: Game) -> List[Market]:
        """Create Market objects from market data for a specific game"""
        markets = []
        
        for market_data in markets_data:
            market = await self.create_market_from_data(market_data, game)
            if market:
                markets.append(market)
        
        return markets
    
    async def create_market_from_data(self, market_data: Dict, game: Game) -> Optional[Market]:
        """Create Market object from single market data"""
        try:
            ticker = market_data.get('ticker', '')
            if not ticker:
                return None
            
            # Determine market type from ticker
            market_type = self._determine_market_type(ticker)
            
            # Parse market name and description
            title = market_data.get('title', ticker)
            
            # Create Market object
            market = Market(
                market_id=ticker,
                game=game,
                market_type=market_type,
                name=title,
                is_active=market_data.get('status') == 'open',
                close_time=parse_timestamp(market_data.get('close_time')),
                metadata={
                    'kalshi_ticker': ticker,
                    'kalshi_status': market_data.get('status'),
                    'kalshi_event_ticker': market_data.get('event_ticker'),
                    'raw_market_data': market_data
                }
            )
            
            return market
            
        except Exception as e:
            self.logger.error(f"Error creating market from data: {e}")
            return None
    
    def _determine_market_type(self, ticker: str) -> MarketType:
        """Determine market type from Kalshi ticker"""
        ticker_upper = ticker.upper()
        
        # Check patterns for market types
        for market_type, patterns in self.market_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, ticker_upper):
                    return market_type
        
        # Default to moneyline if we can't determine
        return MarketType.MONEYLINE
    
    def is_market_for_game(self, market_data: Dict, game: Game) -> bool:
        """Check if a market is for a specific game"""
        try:
            ticker = market_data.get('ticker', '')
            if not ticker:
                return False
            
            # Parse game info from ticker
            game_info = self._parse_game_from_ticker(ticker, game.sport)
            if not game_info:
                return False
            
            # Check if the parsed game matches our game
            return game_info['game_id'] == game.game_id
            
        except Exception:
            return False
    
    async def create_quotes_from_market(self, market_data: Dict, market: Market) -> List[Quote]:
        """Create Quote objects from market data"""
        quotes = []
        
        try:
            # Kalshi markets are binary (YES/NO)
            yes_price = market_data.get('yes_bid')  # Price for YES outcome
            no_price = market_data.get('no_bid')    # Price for NO outcome
            
            ticker = market_data.get('ticker', '')
            
            # Create YES quote
            if yes_price is not None:
                yes_quote = Quote(
                    quote_id=f"{ticker}_YES",
                    market=market,
                    side=QuoteSide.YES,
                    provider="kalshi",
                    price=float(yes_price) / 100.0,  # Kalshi prices are in cents
                    decimal_odds=100.0 / float(yes_price) if yes_price > 0 else None,
                    implied_probability=float(yes_price) / 100.0,
                    timestamp=datetime.utcnow(),
                    metadata={
                        'kalshi_ticker': ticker,
                        'side': 'yes',
                        'raw_price': yes_price
                    }
                )
                quotes.append(yes_quote)
            
            # Create NO quote
            if no_price is not None:
                no_quote = Quote(
                    quote_id=f"{ticker}_NO",
                    market=market,
                    side=QuoteSide.NO,
                    provider="kalshi",
                    price=float(no_price) / 100.0,  # Kalshi prices are in cents
                    decimal_odds=100.0 / float(no_price) if no_price > 0 else None,
                    implied_probability=float(no_price) / 100.0,
                    timestamp=datetime.utcnow(),
                    metadata={
                        'kalshi_ticker': ticker,
                        'side': 'no',
                        'raw_price': no_price
                    }
                )
                quotes.append(no_quote)
            
        except Exception as e:
            self.logger.error(f"Error creating quotes from market data: {e}")
        
        return quotes