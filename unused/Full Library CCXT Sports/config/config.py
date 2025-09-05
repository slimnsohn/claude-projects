#!/usr/bin/env python3
"""
Configuration Management for Sports Market Data Library
Loads API credentials and configuration from environment variables.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def _fix_private_key_format(private_key_str: Optional[str]) -> Optional[str]:
    """
    Fix private key format by converting escaped newlines to actual newlines
    
    Args:
        private_key_str: Private key string from environment
        
    Returns:
        Properly formatted private key string
    """
    if not private_key_str:
        return None
    
    # Replace escaped newlines with actual newlines
    fixed_key = private_key_str.replace('\\n', '\n')
    
    # Remove any surrounding quotes
    fixed_key = fixed_key.strip('"\'')
    
    return fixed_key


def load_environment_config(env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from environment variables
    
    Args:
        env_file: Path to .env file (optional)
        
    Returns:
        Dictionary with configuration values
    """
    # Load from .env file if specified or found in config directory
    if env_file:
        load_dotenv(env_file)
    else:
        # Look for .env in config directory
        config_dir = Path(__file__).parent
        env_path = config_dir / '.env'
        if env_path.exists():
            load_dotenv(env_path)
    
    # Extract configuration
    config = {
        # Kalshi Configuration
        'kalshi': {
            'api_key': os.getenv('KALSHI_API_KEY'),
            'private_key': _fix_private_key_format(os.getenv('KALSHI_PRIVATE_KEY')),
            'base_url': os.getenv('KALSHI_BASE_URL', 'https://demo-api.kalshi.co/trade-api/v2'),
            'environment': os.getenv('ENVIRONMENT', 'demo')
        },
        
        # Odds API Configuration
        'odds_api': {
            'api_key': os.getenv('ODDS_API_KEY'),
            'base_url': os.getenv('ODDS_API_BASE_URL', 'https://api.the-odds-api.com/v4')
        },
        
        # General Configuration
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'environment': os.getenv('ENVIRONMENT', 'demo')
    }
    
    return config


def validate_config(config: Dict[str, Any]) -> Dict[str, bool]:
    """
    Validate configuration completeness
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary with validation results
    """
    results = {
        'kalshi_complete': bool(
            config.get('kalshi', {}).get('api_key') and 
            config.get('kalshi', {}).get('private_key')
        ),
        'odds_api_complete': bool(
            config.get('odds_api', {}).get('api_key')
        )
    }
    
    results['overall_valid'] = results['kalshi_complete'] or results['odds_api_complete']
    
    return results


def get_kalshi_config() -> Dict[str, Any]:
    """Get Kalshi configuration"""
    config = load_environment_config()
    return config.get('kalshi', {})


def get_odds_api_config() -> Dict[str, Any]:
    """Get Odds API configuration"""
    config = load_environment_config()
    return config.get('odds_api', {})


def get_unified_client_config() -> Dict[str, Any]:
    """
    Get configuration for unified client with both providers
    
    Returns:
        Dictionary with kalshi_config and odds_api_config
    """
    config = load_environment_config()
    validation = validate_config(config)
    
    result = {}
    
    if validation['kalshi_complete']:
        result['kalshi_config'] = config['kalshi']
    
    if validation['odds_api_complete']:
        result['odds_api_config'] = config['odds_api']
    
    return result


def print_config_status():
    """Print configuration status for debugging"""
    config = load_environment_config()
    validation = validate_config(config)
    
    print("=== CONFIGURATION STATUS ===")
    print(f"Environment: {config.get('environment', 'unknown')}")
    print(f"Log Level: {config.get('log_level', 'unknown')}")
    print()
    
    print("Kalshi Configuration:")
    kalshi = config.get('kalshi', {})
    print(f"  API Key: {'OK' if kalshi.get('api_key') else 'X'} {'(' + kalshi.get('api_key')[:8] + '...)' if kalshi.get('api_key') else ''}")
    print(f"  Private Key: {'OK' if kalshi.get('private_key') else 'X'} {'(' + str(len(kalshi.get('private_key', ''))) + ' chars)' if kalshi.get('private_key') else ''}")
    print(f"  Base URL: {kalshi.get('base_url', 'Not set')}")
    print(f"  Complete: {'OK' if validation['kalshi_complete'] else 'X'}")
    print()
    
    print("Odds API Configuration:")
    odds = config.get('odds_api', {})
    print(f"  API Key: {'OK' if odds.get('api_key') else 'X'} {'(' + odds.get('api_key')[:8] + '...)' if odds.get('api_key') else ''}")
    print(f"  Base URL: {odds.get('base_url', 'Not set')}")
    print(f"  Complete: {'OK' if validation['odds_api_complete'] else 'X'}")
    print()
    
    print(f"Overall Status: {'OK Ready' if validation['overall_valid'] else 'X Incomplete'}")


if __name__ == "__main__":
    print_config_status()