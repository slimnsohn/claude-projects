from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

class DataProvider(ABC):
    """Abstract base class for all data providers"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.logger = self._setup_logger()
    
    @abstractmethod
    def fetch_games(self, sport: str, date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch raw game data from provider"""
        pass
    
    @abstractmethod
    def parse_games(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse raw data into intermediate format"""
        pass
    
    @abstractmethod
    def normalize_games(self, parsed_data: List[Dict[str, Any]]) -> List['Game']:
        """Normalize parsed data into common Game objects"""
        pass
    
    def get_games(self, sport: str, date: Optional[datetime] = None) -> List['Game']:
        """Main method to get normalized games"""
        try:
            self.logger.info(f"Fetching {sport} games from {self.provider_name}")
            raw_data = self.fetch_games(sport, date)
            
            self.logger.info(f"Parsing {len(raw_data)} raw games")
            parsed_data = self.parse_games(raw_data)
            
            self.logger.info(f"Normalizing {len(parsed_data)} parsed games")
            normalized_games = self.normalize_games(parsed_data)
            
            self.logger.info(f"Successfully processed {len(normalized_games)} games")
            return normalized_games
            
        except Exception as e:
            self.logger.error(f"Error processing games from {self.provider_name}: {e}")
            raise
    
    def _setup_logger(self):
        """Setup logger for the provider"""
        logger = logging.getLogger(f"{self.provider_name}_provider")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger