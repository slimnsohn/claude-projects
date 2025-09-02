"""
Market Data Kalshi - Kalshi prediction markets integration
Provides access to Kalshi sports betting markets and real-time pricing data.
"""

__version__ = "0.1.0"
__author__ = "Sports Betting Library"

from .client import KalshiClient
from .handler import KalshiResponseHandler
from .auth import KalshiAuthenticator

__all__ = ['KalshiClient', 'KalshiResponseHandler', 'KalshiAuthenticator']