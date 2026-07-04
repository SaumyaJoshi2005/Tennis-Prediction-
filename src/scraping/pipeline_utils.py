# -*- coding: utf-8 -*-
"""
Scraping Pipeline Utilities and Helpers
Provides common utilities for the RG scraping pipeline

Created on Jun 9, 2026
@author: AUM
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class BufferManager:
    """Manages 24-hour buffer logic for round scraping."""
    
    def __init__(self, cache_file: Path):
        """
        Initialize buffer manager.
        
        Args:
            cache_file: Path to cache JSON file
        """
        self.cache_file = cache_file
        self.cache = self._load()
    
    def _load(self) -> Dict:
        """Load cache from file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Cache corrupted: {self.cache_file}")
                return {}
        return {}
    
    def _save(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Failed to save cache: {e}")
    
    def is_buffer_active(
        self,
        key: str,
        buffer_hours: int = 24
    ) -> bool:
        """
        Check if buffer is still active.
        
        Args:
            key: Cache key
            buffer_hours: Buffer duration in hours
            
        Returns:
            True if buffer is active (skip), False if expired
        """
        if key not in self.cache:
            return False
        
        try:
            last_time = datetime.fromisoformat(
                self.cache[key].get('last_scraped')
            )
            elapsed = datetime.now() - last_time
            buffer = timedelta(hours=buffer_hours)
            
            return elapsed < buffer
            
        except (ValueError, TypeError):
            return False
    
    def update(self, key: str, data: Dict):
        """
        Update cache entry.
        
        Args:
            key: Cache key
            data: Data to store
        """
        if key not in self.cache:
            self.cache[key] = {}
        
        self.cache[key].update({
            'last_scraped': datetime.now().isoformat(),
            **data
        })
        
        self._save()


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Max requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
    
    def can_request(self) -> bool:
        """Check if request is allowed."""
        now = datetime.now()
        
        # Remove old requests outside window
        self.requests = [
            req_time for req_time in self.requests
            if now - req_time < timedelta(seconds=self.window_seconds)
        ]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        return False
    
    def wait_if_needed(self):
        """Wait if rate limit reached."""
        import time
        
        while not self.can_request():
            logger.info("Rate limit reached, waiting...")
            time.sleep(1)
        
        self.can_request()


class ErrorHandler:
    """Centralized error handling and recovery."""
    
    @staticmethod
    def handle_network_error(error: Exception, context: str) -> bool:
        """
        Handle network errors.
        
        Args:
            error: Exception object
            context: Context description
            
        Returns:
            True if recoverable, False otherwise
        """
        error_str = str(error).lower()
        
        # Timeout errors are recoverable
        if 'timeout' in error_str:
            logger.warning(f"{context}: Network timeout (recoverable)")
            return True
        
        # Connection errors are recoverable
        if 'connection' in error_str:
            logger.warning(f"{context}: Connection error (recoverable)")
            return True
        
        # Other errors may not be
        logger.error(f"{context}: {error}")
        return False
    
    @staticmethod
    def handle_database_error(error: Exception, context: str) -> bool:
        """
        Handle database errors.
        
        Args:
            error: Exception object
            context: Context description
            
        Returns:
            True if recoverable, False otherwise
        """
        error_str = str(error).lower()
        
        # Integrity errors indicate duplicate (recoverable)
        if 'integrity' in error_str:
            logger.info(f"{context}: Duplicate entry (skipping)")
            return True
        
        # Connection errors are recoverable
        if 'connection' in error_str:
            logger.warning(f"{context}: DB connection error (recoverable)")
            return True
        
        # Other errors are critical
        logger.error(f"{context}: {error}")
        return False


class DataValidator:
    """Validate scraped data."""
    
    @staticmethod
    def validate_player_name(name: str) -> bool:
        """
        Validate player name format.
        
        Args:
            name: Player name
            
        Returns:
            True if valid
        """
        if not name or not isinstance(name, str):
            return False
        
        parts = name.strip().split()
        
        # Must have at least first and last name
        return len(parts) >= 2
    
    @staticmethod
    def validate_round_name(round_name: str) -> bool:
        """
        Validate round name.
        
        Args:
            round_name: Round name
            
        Returns:
            True if valid
        """
        valid_rounds = [
            'first', 'second', 'third', 'fourth',
            'quarterfinals', 'semifinals', 'final'
        ]
        
        return round_name.lower() in valid_rounds
    
    @staticmethod
    def validate_match_data(match: Dict) -> bool:
        """
        Validate match data.
        
        Args:
            match: Match dictionary
            
        Returns:
            True if valid
        """
        required_keys = ['match_id', 'player_a_name', 'player_b_name']
        
        for key in required_keys:
            if key not in match or not match[key]:
                return False
        
        # Validate player names
        if not DataValidator.validate_player_name(match['player_a_name']):
            return False
        
        if not DataValidator.validate_player_name(match['player_b_name']):
            return False
        
        return True


class StatisticsCollector:
    """Collect pipeline statistics."""
    
    def __init__(self):
        """Initialize collector."""
        self.stats = {
            'total_matches_scraped': 0,
            'fixtures_created': 0,
            'fixtures_failed': 0,
            'players_new': 0,
            'players_updated': 0,
            'results_updated': 0,
            'errors': []
        }
    
    def record_match(self):
        """Record scraped match."""
        self.stats['total_matches_scraped'] += 1
    
    def record_fixture_created(self):
        """Record successful fixture creation."""
        self.stats['fixtures_created'] += 1
    
    def record_fixture_failed(self):
        """Record failed fixture creation."""
        self.stats['fixtures_failed'] += 1
    
    def record_player_new(self):
        """Record new player registration."""
        self.stats['players_new'] += 1
    
    def record_player_updated(self):
        """Record player update."""
        self.stats['players_updated'] += 1
    
    def record_result_updated(self):
        """Record result update."""
        self.stats['results_updated'] += 1
    
    def record_error(self, error_msg: str):
        """Record error."""
        self.stats['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'message': error_msg
        })
    
    def get_summary(self) -> Dict:
        """
        Get statistics summary.
        
        Returns:
            Statistics dictionary
        """
        return self.stats.copy()


if __name__ == "__main__":
    # Example usage
    from pathlib import Path
    
    cache_file = Path("scrape_metadata.json")
    buffer = BufferManager(cache_file)
    
    # Check if we should scrape
    if not buffer.is_buffer_active("first_round"):
        print("Can scrape first round")
        buffer.update("first_round", {"count": 128})
    else:
        print("Buffer still active, wait before scraping again")
