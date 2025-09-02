"""
Market Data Core - Base models and interfaces for sports betting APIs
Provides unified data models and abstract interfaces for market data providers.
"""

__version__ = "0.1.0"
__author__ = "Sports Betting Library"

from .base_client import BaseMarketDataClient
from .models import Team, Game, Market, Quote, Category, Sport
from .utils import RateLimiter, ConfigLoader
from .exceptions import (
    MarketDataError,
    AuthenticationError,
    RateLimitError,
    DataNotFoundError
)
from .data_manager import NFLDataManager, get_nfl_data_manager
from .team_matcher import TeamMatcher, MatchResult, get_team_matcher

__all__ = [
    'BaseMarketDataClient',
    'Team', 'Game', 'Market', 'Quote', 'Category', 'Sport',
    'RateLimiter', 'ConfigLoader',
    'MarketDataError', 'AuthenticationError', 'RateLimitError', 'DataNotFoundError',
    'NFLDataManager', 'get_nfl_data_manager',
    'TeamMatcher', 'MatchResult', 'get_team_matcher'
]