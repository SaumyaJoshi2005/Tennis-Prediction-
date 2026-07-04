# -*- coding: utf-8 -*-
"""
Roland Garros Draw Scraper
Scrapes RG draws from website, applies 24hr buffer, and injects fixtures into database
Uses local cache file for buffer management

Created on Jun 9, 2026
@author: AUM
"""

import re
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from sqlalchemy.exc import IntegrityError
from app.db.session import SessionLocal
from app.db.models.fixture import Fixture
from app.db.models.player import Player
from app.db.models.tournament import Tournament
from atp_player_fetcher import ATPPlayerFetcher


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - RG_SCRAPER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Cache file for 24hr buffer metadata
CACHE_FILE = Path(__file__).parent / "scrape_metadata.json"

# RG API endpoints
RG_BASE_URL = "https://www.rolandgarros.com/en-us/results/SM"
RG_ROUND_URLS = {
    'first': RG_BASE_URL,
    'second': f"{RG_BASE_URL}?round=2",
    'third': f"{RG_BASE_URL}?round=3",
    'fourth': f"{RG_BASE_URL}?round=4",
    'quarterfinals': f"{RG_BASE_URL}?round=5",
    'semifinals': f"{RG_BASE_URL}?round=6",
    'final': f"{RG_BASE_URL}?round=7",
}


class RGDrawScraper:
    """Scrape Roland Garros draws with 24hr buffer logic."""
    
    def __init__(self):
        self.db = SessionLocal()
        self.atp_fetcher = ATPPlayerFetcher()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })
        self.cache = self._load_cache()
    
    def __del__(self):
        """Cleanup resources."""
        if self.db:
            self.db.close()
    
    def _load_cache(self) -> Dict:
        """Load scrape metadata cache."""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("Cache file corrupted, reinitializing")
                return {}
        return {}
    
    def _save_cache(self):
        """Save scrape metadata cache."""
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump(self.cache, f, indent=2, default=str)
            logger.info("Cache saved")
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")
    
    def should_scrape(self, round_name: str) -> bool:
        """
        Check if 24hr buffer has passed for a round.
        
        Args:
            round_name: Round identifier
            
        Returns:
            True if should scrape, False if within 24hr buffer
        """
        if round_name not in self.cache:
            return True
        
        # Handle None values from initial cache
        last_scraped_str = self.cache[round_name]['last_scraped']
        if last_scraped_str is None:
            return True
        
        last_scraped = datetime.fromisoformat(last_scraped_str)
        
        time_elapsed = datetime.now() - last_scraped
        buffer_time = timedelta(hours=24)
        
        if time_elapsed >= buffer_time:
            logger.info(
                f"24hr buffer expired for {round_name}, "
                f"scraping allowed"
            )
            return True
        
        logger.info(
            f"24hr buffer active for {round_name}, "
            f"skipping scrape ({buffer_time - time_elapsed} remaining)"
        )
        return False
    
    def _update_cache(self, round_name: str, count: int):
        """Update cache with latest scrape timestamp."""
        self.cache[round_name] = {
            'last_scraped': datetime.now().isoformat(),
            'fixture_count': count
        }
        self._save_cache()
    
    def fetch_html(self, round_name: str) -> Optional[str]:
        """
        Fetch HTML from RG website for a specific round.
        
        Args:
            round_name: Round identifier
            
        Returns:
            HTML content or None if request fails
        """
        try:
            url = RG_ROUND_URLS.get(round_name, RG_BASE_URL)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Fetched HTML for round: {round_name}")
            return response.text
            
        except requests.RequestException as e:
            logger.error(
                f"Error fetching RG data for {round_name}: {str(e)}"
            )
            return None
    
    def extract_matches(self, html: str) -> List[Dict]:
        """
        Extract matches from RG HTML.
        
        Args:
            html: HTML content
            
        Returns:
            List of match dictionaries
        """
        matches = []
        
        try:
            # Regex pattern to extract match details
            pattern = (
                r'id:"(SM\d+)".*?'
                r'firstName:"([^"]+)".*?'
                r'lastName:"([^"]+)".*?'
                r'teamB:\{players:\[\{.*?'
                r'firstName:"([^"]+)".*?'
                r'lastName:"([^"]+)"'
            )
            
            found_matches = re.findall(
                pattern,
                html,
                re.DOTALL
            )
            
            for (
                match_id,
                p1_first,
                p1_last,
                p2_first,
                p2_last
            ) in found_matches:
                
                matches.append({
                    'match_id': match_id,
                    'player_a_name': f"{p1_first} {p1_last}",
                    'player_b_name': f"{p2_first} {p2_last}"
                })
            
            logger.info(f"Extracted {len(matches)} matches from HTML")
            return matches
            
        except Exception as e:
            logger.error(f"Error extracting matches: {str(e)}")
            return []
    
    def normalize_tournament_name(self) -> str:
        """
        Get normalized tournament name for Roland Garros.
        
        Returns:
            Tournament name string
        """
        return "Roland Garros"
    
    def get_or_create_player(
        self,
        player_name: str
    ) -> Optional[int]:
        """
        Get player_id or create player if doesn't exist.
        
        Args:
            player_name: Full player name
            
        Returns:
            Player ID or None
        """
        try:
            player, _ = self.atp_fetcher.process_player(
                *player_name.split(' ', 1)
            )
            
            if player:
                return player.player_id
            
            return None
            
        except Exception as e:
            logger.error(
                f"Error processing player {player_name}: {str(e)}"
            )
            return None
    
    def create_fixture(
        self,
        player_a_id: int,
        player_b_id: int,
        round_name: str,
        match_date: Optional[str] = None
    ) -> Optional[Fixture]:
        """
        Create a fixture in database.
        
        Args:
            player_a_id: Player A ID
            player_b_id: Player B ID
            round_name: Round name
            match_date: Match date (optional)
            
        Returns:
            Fixture object if successful, None otherwise
        """
        try:
            fixture = Fixture(
                player_a_id=player_a_id,
                player_b_id=player_b_id,
                tournament=self.normalize_tournament_name(),
                round=round_name,
                surface="Clay",  # RG is always clay
                match_date=match_date,
                prediction=None,
                winner_predicted=None,
                player_a_win_probability=None,
                status="UPCOMING"
            )
            
            self.db.add(fixture)
            self.db.flush()
            
            logger.info(
                f"Created fixture {fixture.fixture_id}: "
                f"{player_a_id} vs {player_b_id}"
            )
            
            return fixture
            
        except IntegrityError as e:
            self.db.rollback()
            logger.warning(f"Duplicate fixture (likely already exists): {str(e)}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating fixture: {str(e)}")
            return None
    
    def scrape_round(
        self,
        round_name: str,
        force: bool = False
    ) -> Tuple[int, int]:
        """
        Scrape a specific round with 24hr buffer check.
        
        Args:
            round_name: Round identifier
            force: Force scrape even if within buffer (default: False)
            
        Returns:
            Tuple of (fixtures_created, fixtures_failed)
        """
        logger.info(f"Starting scrape for round: {round_name}")
        
        # Check 24hr buffer
        if not force and not self.should_scrape(round_name):
            logger.info(f"Skipping {round_name} due to 24hr buffer")
            return 0, 0
        
        # Fetch HTML
        html = self.fetch_html(round_name)
        if not html:
            return 0, 0
        
        # Extract matches
        matches = self.extract_matches(html)
        if not matches:
            logger.warning(f"No matches found for {round_name}")
            return 0, 0
        
        # Process matches and create fixtures
        created = 0
        failed = 0
        
        for match in matches:
            try:
                # Get or create players
                player_a_id = self.get_or_create_player(
                    match['player_a_name']
                )
                player_b_id = self.get_or_create_player(
                    match['player_b_name']
                )
                
                if not player_a_id or not player_b_id:
                    logger.warning(
                        f"Could not find/create players for match: "
                        f"{match['player_a_name']} vs {match['player_b_name']}"
                    )
                    failed += 1
                    continue
                
                # Create fixture
                fixture = self.create_fixture(
                    player_a_id,
                    player_b_id,
                    round_name
                )
                
                if fixture:
                    created += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(
                    f"Error processing match: {str(e)}"
                )
                failed += 1
        
        # Commit all changes
        try:
            self.db.commit()
            logger.info(
                f"Round {round_name}: Created {created} fixtures, "
                f"Failed {failed}"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Commit failed: {str(e)}")
        
        # Update cache
        self._update_cache(round_name, created)
        
        return created, failed
    
    def scrape_all_rounds(self, force: bool = False) -> Dict[str, Tuple[int, int]]:
        """
        Scrape all rounds.
        
        Args:
            force: Force scrape even if within buffer
            
        Returns:
            Dictionary mapping round_name to (created, failed)
        """
        results = {}
        
        for round_name in RG_ROUND_URLS.keys():
            created, failed = self.scrape_round(round_name, force)
            results[round_name] = (created, failed)
        
        return results


def scrape_rg_draws(
    round_name: Optional[str] = None,
    force: bool = False
) -> Dict[str, Tuple[int, int]]:
    """
    Main entry point to scrape RG draws.
    
    Args:
        round_name: Specific round to scrape (default: all rounds)
        force: Force scrape (default: False)
        
    Returns:
        Results dictionary
    """
    scraper = RGDrawScraper()
    
    if round_name:
        results = {round_name: scraper.scrape_round(round_name, force)}
    else:
        results = scraper.scrape_all_rounds(force)
    
    return results


if __name__ == "__main__":
    # Example: Scrape all rounds
    results = scrape_rg_draws()
    
    for round_name, (created, failed) in results.items():
        print(f"{round_name}: Created {created}, Failed {failed}")
