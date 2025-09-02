"""
Custom exceptions for market data library
Provides specific exception types for different error scenarios.
"""

from typing import Optional, Dict, Any


class MarketDataError(Exception):
    """Base exception for all market data errors"""
    
    def __init__(self, message: str, provider: Optional[str] = None, 
                 error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize market data error
        
        Args:
            message: Error message
            provider: Name of the provider that caused the error
            error_code: Provider-specific error code
            details: Additional error details
        """
        super().__init__(message)
        self.provider = provider
        self.error_code = error_code
        self.details = details or {}
        
    def __str__(self) -> str:
        parts = [super().__str__()]
        if self.provider:
            parts.append(f"Provider: {self.provider}")
        if self.error_code:
            parts.append(f"Code: {self.error_code}")
        return " | ".join(parts)


class AuthenticationError(MarketDataError):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, **kwargs)


class RateLimitError(MarketDataError):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class DataNotFoundError(MarketDataError):
    """Raised when requested data is not found"""
    
    def __init__(self, message: str = "Data not found", 
                 requested_data: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.requested_data = requested_data


class InvalidDataError(MarketDataError):
    """Raised when data format is invalid or corrupted"""
    
    def __init__(self, message: str = "Invalid data format", 
                 expected_format: Optional[str] = None, 
                 actual_format: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.expected_format = expected_format
        self.actual_format = actual_format


class NetworkError(MarketDataError):
    """Raised when network requests fail"""
    
    def __init__(self, message: str = "Network request failed", 
                 status_code: Optional[int] = None, 
                 response_text: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_text = response_text


class ConfigurationError(MarketDataError):
    """Raised when configuration is invalid or missing"""
    
    def __init__(self, message: str = "Configuration error", 
                 config_key: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.config_key = config_key


class TeamMatchingError(MarketDataError):
    """Raised when team matching fails"""
    
    def __init__(self, message: str = "Team matching failed", 
                 home_team: Optional[str] = None, 
                 away_team: Optional[str] = None, 
                 confidence: Optional[float] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.home_team = home_team
        self.away_team = away_team
        self.confidence = confidence


class MarketNotAvailableError(MarketDataError):
    """Raised when a market is not available from provider"""
    
    def __init__(self, message: str = "Market not available", 
                 market_type: Optional[str] = None, 
                 sport: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.market_type = market_type
        self.sport = sport


class QuoteStaleError(MarketDataError):
    """Raised when quote data is too old to be reliable"""
    
    def __init__(self, message: str = "Quote data is stale", 
                 quote_age_seconds: Optional[int] = None, 
                 max_age_seconds: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.quote_age_seconds = quote_age_seconds
        self.max_age_seconds = max_age_seconds


class ValidationError(MarketDataError):
    """Raised when data validation fails"""
    
    def __init__(self, message: str = "Validation failed", 
                 field_name: Optional[str] = None, 
                 field_value: Optional[Any] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.field_name = field_name
        self.field_value = field_value


# Provider-specific exceptions

class KalshiError(MarketDataError):
    """Base class for Kalshi-specific errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, provider="kalshi", **kwargs)


class KalshiAuthenticationError(AuthenticationError):
    """Kalshi authentication error"""
    
    def __init__(self, message: str = "Kalshi authentication failed", **kwargs):
        super().__init__(message, provider="kalshi", **kwargs)


class KalshiSignatureError(KalshiError):
    """Raised when RSA-PSS signature generation/validation fails"""
    
    def __init__(self, message: str = "RSA signature error", **kwargs):
        super().__init__(message, **kwargs)


class OddsAPIError(MarketDataError):
    """Base class for Odds API specific errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, provider="odds_api", **kwargs)


class OddsAPIQuotaExceededError(RateLimitError):
    """Raised when Odds API quota is exceeded"""
    
    def __init__(self, message: str = "Odds API quota exceeded", 
                 remaining_requests: Optional[int] = None, **kwargs):
        super().__init__(message, provider="odds_api", **kwargs)
        self.remaining_requests = remaining_requests