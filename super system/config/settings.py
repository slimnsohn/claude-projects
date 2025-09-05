import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_key_from_file(key_file_path):
    """Load API key from a file, handling various formats"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, key_file_path)
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read().strip()
                # Handle format: api_key = 'value' or api_key = "value"
                if "'" in content:
                    return content.split("'")[1]
                elif '"' in content:
                    return content.split('"')[1]
                else:
                    return content
    except Exception:
        pass
    return None

# API Keys - Try to load from files first, then environment variables
ODDS_API_KEY = load_key_from_file('odds_api_key.txt') or os.getenv('ODDS_API_KEY')
KALSHI_API_KEY = load_key_from_file('kalshi_credentials.txt') or os.getenv('KALSHI_API_KEY')
KALSHI_API_SECRET = os.getenv('KALSHI_API_SECRET')
POLYMARKET_API_KEY = os.getenv('POLYMARKET_API_KEY')

# API Base URLs
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
KALSHI_API_BASE_URL = "https://api.kalshi.com"
POLYMARKET_API_BASE_URL = "https://api.polymarket.com"

# Database settings (if needed)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///sports_analytics.db')

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Cache settings
CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', '300'))  # 5 minutes default

# Rate limiting
REQUESTS_PER_MINUTE = int(os.getenv('REQUESTS_PER_MINUTE', '60'))

# UI settings
UI_HOST = os.getenv('UI_HOST', '0.0.0.0')
UI_PORT = int(os.getenv('UI_PORT', '5000'))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'