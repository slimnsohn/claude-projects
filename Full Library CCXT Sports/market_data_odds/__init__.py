"""
Market Data Odds - The Odds API integration
Provides access to multiple sportsbook odds via The Odds API aggregation service.
"""

__version__ = "0.1.0"
__author__ = "Sports Betting Library"

from .client import OddsAPIClient
from .handler import OddsAPIResponseHandler
from .auth import OddsAPIAuthenticator

__all__ = ['OddsAPIClient', 'OddsAPIResponseHandler', 'OddsAPIAuthenticator']