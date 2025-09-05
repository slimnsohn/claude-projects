"""
Core utilities for market data library
Includes configuration loading, rate limiting, and common helper functions.
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from threading import Lock
import asyncio


class ConfigLoader:
    """Loads and validates configuration from secrets.json"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader
        
        Args:
            config_path: Path to secrets.json file, defaults to config/secrets.json
        """
        if config_path is None:
            # Look for config relative to project root
            current_dir = Path(__file__).parent.parent
            config_path = current_dir / "config" / "secrets.json"
        
        self.config_path = Path(config_path)
        self._config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                self._config = json.load(f)
            self._validate_config()
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found at {self.config_path}. "
                f"Please copy secrets.json.template to secrets.json and fill in your API keys."
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _validate_config(self) -> None:
        """Validate configuration structure"""
        required_sections = ['kalshi', 'odds_api']
        for section in required_sections:
            if section not in self._config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate Kalshi config
        kalshi_required = ['api_key', 'base_url']
        for key in kalshi_required:
            if key not in self._config['kalshi']:
                raise ValueError(f"Missing required Kalshi config: {key}")
        
        # Validate Odds API config
        odds_required = ['api_key', 'base_url']
        for key in odds_required:
            if key not in self._config['odds_api']:
                raise ValueError(f"Missing required Odds API config: {key}")
    
    def get_kalshi_config(self) -> Dict[str, Any]:
        """Get Kalshi API configuration"""
        return self._config['kalshi'].copy()
    
    def get_odds_api_config(self) -> Dict[str, Any]:
        """Get Odds API configuration"""
        return self._config['odds_api'].copy()
    
    def get_rate_limits(self) -> Dict[str, int]:
        """Get rate limit configuration"""
        defaults = {
            'kalshi_requests_per_minute': 60,
            'odds_api_requests_per_minute': 500
        }
        return self._config.get('rate_limits', defaults)
    
    def get_timeouts(self) -> Dict[str, int]:
        """Get timeout configuration"""
        defaults = {
            'default_timeout': 30,
            'auth_timeout': 10
        }
        return self._config.get('timeouts', defaults)


class RateLimiter:
    """Rate limiter with exponential backoff"""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds (default 60s = 1 minute)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = Lock()
    
    def can_proceed(self) -> bool:
        """Check if request can proceed without rate limiting"""
        with self.lock:
            now = time.time()
            # Remove old requests outside time window
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            return len(self.requests) < self.max_requests
    
    def wait_if_needed(self) -> None:
        """Block until request can proceed"""
        with self.lock:
            now = time.time()
            # Remove old requests outside time window
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            if len(self.requests) >= self.max_requests:
                # Calculate wait time until oldest request expires
                oldest_request = min(self.requests)
                wait_time = self.time_window - (now - oldest_request)
                if wait_time > 0:
                    time.sleep(wait_time)
            
            # Record this request
            self.requests.append(time.time())
    
    async def async_wait_if_needed(self) -> None:
        """Async version of wait_if_needed"""
        with self.lock:
            now = time.time()
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            if len(self.requests) >= self.max_requests:
                oldest_request = min(self.requests)
                wait_time = self.time_window - (now - oldest_request)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
            
            self.requests.append(time.time())


class ExponentialBackoff:
    """Exponential backoff utility for retry logic"""
    
    def __init__(self, base_delay: float = 1.0, max_delay: float = 60.0, 
                 backoff_factor: float = 2.0, max_retries: int = 5):
        """
        Initialize exponential backoff
        
        Args:
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            backoff_factor: Multiplier for each retry
            max_retries: Maximum number of retries
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.max_retries = max_retries
        self.attempt = 0
    
    def reset(self) -> None:
        """Reset retry counter"""
        self.attempt = 0
    
    def should_retry(self) -> bool:
        """Check if should retry based on attempt count"""
        return self.attempt < self.max_retries
    
    def get_delay(self) -> float:
        """Get current delay and increment attempt counter"""
        if not self.should_retry():
            return 0
        
        delay = min(self.base_delay * (self.backoff_factor ** self.attempt), 
                   self.max_delay)
        self.attempt += 1
        return delay
    
    def wait(self) -> None:
        """Wait for current delay period"""
        delay = self.get_delay()
        if delay > 0:
            time.sleep(delay)
    
    async def async_wait(self) -> None:
        """Async version of wait"""
        delay = self.get_delay()
        if delay > 0:
            await asyncio.sleep(delay)


def setup_logging(name: str = "market_data", level: int = logging.INFO) -> logging.Logger:
    """Set up standardized logging configuration"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    
    return logger


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse various timestamp formats to datetime"""
    if not timestamp_str:
        return None
    
    # Common formats to try
    formats = [
        '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO with microseconds and Z
        '%Y-%m-%dT%H:%M:%SZ',     # ISO with Z
        '%Y-%m-%dT%H:%M:%S.%f',   # ISO with microseconds
        '%Y-%m-%dT%H:%M:%S',      # ISO basic
        '%Y-%m-%d %H:%M:%S',      # Space separated
        '%Y-%m-%d',               # Date only
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    return None


def calculate_implied_probability(american_odds: int) -> float:
    """Calculate implied probability from American odds"""
    if american_odds > 0:
        return 100 / (american_odds + 100)
    else:
        return abs(american_odds) / (abs(american_odds) + 100)


def american_to_decimal_odds(american_odds: int) -> float:
    """Convert American odds to decimal odds"""
    if american_odds > 0:
        return (american_odds / 100) + 1
    else:
        return (100 / abs(american_odds)) + 1