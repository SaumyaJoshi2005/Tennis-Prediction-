# -*- coding: utf-8 -*-
"""
Match Results Updater
Fetches Roland Garros match results and updates fixtures with outcomes
Also updates MatchFeatures with result data

Created on Jun 9, 2026
@author: AUM
"""

import re
import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dateutil import parser as date_parser

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.fixture import Fixture
from app.db.models.player import Player
from app.db.models.match_features import MatchFeatures


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - RESULTS_UPDATER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


RG_BASE_URL = "https://www.rolandgarros.com/en-us/results/SM"
RG_RESULT_URLS = {
    'first': f"{RG_BASE_URL}?round=1",
    'second': f"{RG_BASE_URL}?round=2",
    'third': f"{RG_BASE_URL}?round=3",
    'fourth': f"{RG_BASE_URL}?round=4",
    'quarterfinals': f"{RG_BASE_URL}?round=5",
    'semifinals': f"{RG_BASE_URL}?round=6",
    'final': f"{RG_BASE_URL}?round=7",
}


class MatchResultsUpdater:
    """Fetch and update match results from Roland Garros."""
    
    def __init__(self):
        self.db = SessionLocal()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })
    
    def __del__(self):
        """Cleanup database session."""
        if self.db:
            self.db.close()
    
    def fetch_results_html(self, round_name: str) -> Optional[str]:
        """
        Fetch results HTML from RG website.
        
        Args:
            round_name: Round identifier
            
        Returns:
            HTML content or None
        """
        try:
            url = RG_RESULT_URLS.get(round_name, RG_BASE_URL)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Fetched results HTML for round: {round_name}")
            return response.text
            
        except requests.RequestException as e:
            logger.error(
                f"Error fetching results for {round_name}: {str(e)}"
            )
            return None
    
    def extract_results(self, html: str) -> List[Dict]:
        """
        Extract match results from HTML.
        
        Args:
            html: HTML content
            
        Returns:
            List of result dictionaries
        """
        results = []
        
        try:
            # Look for roundResults in HTML
            start_idx = html.find("roundResults:[")
            
            if start_idx == -1:
                logger.warning("roundResults not found in HTML")
                return results
            
            # Extract section containing results
            html_section = html[start_idx:start_idx + 500000]
            
            # Regex pattern to extract result details
            pattern = (
                r'id:"(SM\d+)".*?'
                r'firstName:"([^"]+)".*?'
                r'lastName:"([^"]+)".*?'
                r'teamB:\{players:\[\{.*?'
                r'firstName:"([^"]+)".*?'
                r'lastName:"([^"]+)".*?'
                r'status:"([^"]+)".*?'
                r'(?:winner|score).*?'
                r'(\d+)[,\-\s]+(\d+)'
            )
            
            found_results = re.findall(pattern, html_section, re.DOTALL)
            
            for match_data in found_results:
                try:
                    match_id, p1_first, p1_last, p2_first, p2_last, \
                        status, set1, set2 = match_data
                    
                    results.append({
                        'match_id': match_id,
                        'player_a_name': f"{p1_first} {p1_last}",
                        'player_b_name': f"{p2_first} {p2_last}",
                        'status': status,
                        'set1_score': int(set1),
                        'set2_score': int(set2)
                    })
                except (ValueError, IndexError) as e:
                    logger.debug(f"Could not parse result: {str(e)}")
                    continue
            
            logger.info(f"Extracted {len(results)} results from HTML")
            return results
            
        except Exception as e:
            logger.error(f"Error extracting results: {str(e)}")
            return []
    
    def find_fixture_by_players(
        self,
        player_a_name: str,
        player_b_name: str,
        round_name: str
    ) -> Optional[Fixture]:
        """
        Find fixture by player names and round.
        
        Args:
            player_a_name: Player A name
            player_b_name: Player B name
            round_name: Round name
            
        Returns:
            Fixture object or None
        """
        try:
            # Get players
            player_a = self.db.query(Player).filter(
                Player.player_name == player_a_name
            ).first()
            
            player_b = self.db.query(Player).filter(
                Player.player_name == player_b_name
            ).first()
            
            if not player_a or not player_b:
                logger.debug(
                    f"Could not find players: {player_a_name}, {player_b_name}"
                )
                return None
            
            # Find fixture
            fixture = self.db.query(Fixture).filter(
                Fixture.round == round_name,
                Fixture.tournament == "Roland Garros",
                Fixture.status.in_(["UPCOMING", "IN_PROGRESS"])
            ).filter(
                ((Fixture.player_a_id == player_a.player_id) & 
                 (Fixture.player_b_id == player_b.player_id)) |
                ((Fixture.player_a_id == player_b.player_id) & 
                 (Fixture.player_b_id == player_a.player_id))
            ).first()
            
            return fixture
            
        except Exception as e:
            logger.error(
                f"Error finding fixture: {str(e)}"
            )
            return None
    
    def update_fixture_with_result(
        self,
        fixture: Fixture,
        result: Dict,
        winner_id: int
    ) -> bool:
        """
        Update fixture with match result.
        
        Args:
            fixture: Fixture object
            result: Result dictionary
            winner_id: Player ID of winner
            
        Returns:
            True if successful
        """
        try:
            # Determine winner_predicted
            winner_predicted = "player_a" if winner_id == fixture.player_a_id \
                else "player_b"
            
            # Update fixture
            fixture.status = "COMPLETED"
            fixture.winner_predicted = winner_predicted
            
            self.db.commit()
            
            logger.info(
                f"Updated fixture {fixture.fixture_id} with result"
            )
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating fixture: {str(e)}")
            return False
    
    def update_round_results(
        self,
        round_name: str
    ) -> Tuple[int, int]:
        """
        Update all results for a round.
        
        Args:
            round_name: Round identifier
            
        Returns:
            Tuple of (updated_count, failed_count)
        """
        logger.info(f"Starting results update for round: {round_name}")
        
        # Fetch results
        html = self.fetch_results_html(round_name)
        if not html:
            return 0, 0
        
        # Extract results
        results = self.extract_results(html)
        if not results:
            logger.warning(f"No results found for {round_name}")
            return 0, 0
        
        # Process results
        updated = 0
        failed = 0
        
        for result in results:
            try:
                # Find fixture
                fixture = self.find_fixture_by_players(
                    result['player_a_name'],
                    result['player_b_name'],
                    round_name
                )
                
                if not fixture:
                    logger.debug(
                        f"Fixture not found for result: "
                        f"{result['player_a_name']} vs {result['player_b_name']}"
                    )
                    failed += 1
                    continue
                
                # Determine winner (simplified logic - would need actual score parsing)
                # In a real scenario, parse the score to determine winner
                # For now, assume status indicates winner
                if "won" in result.get('status', '').lower():
                    winner_id = fixture.player_a_id
                else:
                    winner_id = fixture.player_b_id
                
                # Update fixture
                if self.update_fixture_with_result(fixture, result, winner_id):
                    updated += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Error processing result: {str(e)}")
                failed += 1
        
        logger.info(
            f"Round {round_name}: Updated {updated} fixtures, "
            f"Failed {failed}"
        )
        
        return updated, failed
    
    def update_all_rounds(self) -> Dict[str, Tuple[int, int]]:
        """
        Update results for all rounds.
        
        Returns:
            Dictionary mapping round_name to (updated, failed)
        """
        results = {}
        
        for round_name in RG_RESULT_URLS.keys():
            updated, failed = self.update_round_results(round_name)
            results[round_name] = (updated, failed)
        
        return results
    
    def update_match_features(
        self,
        fixture_id: int,
        features_data: Dict
    ) -> bool:
        """
        Update MatchFeatures for a fixture (for completed matches).
        
        Args:
            fixture_id: Fixture ID
            features_data: Features dictionary
            
        Returns:
            True if successful
        """
        try:
            # Check if MatchFeatures already exists
            match_feature = self.db.query(MatchFeatures).filter(
                MatchFeatures.match_id == fixture_id
            ).first()
            
            if match_feature:
                # Update existing
                for key, value in features_data.items():
                    if hasattr(match_feature, key):
                        setattr(match_feature, key, value)
            else:
                # Create new
                match_feature = MatchFeatures(
                    match_id=fixture_id,
                    **features_data
                )
                self.db.add(match_feature)
            
            self.db.commit()
            logger.info(f"Updated MatchFeatures for match_id: {fixture_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating MatchFeatures: {str(e)}")
            return False


def update_results(
    round_name: Optional[str] = None
) -> Dict[str, Tuple[int, int]]:
    """
    Main entry point to update match results.
    
    Args:
        round_name: Specific round to update (default: all rounds)
        
    Returns:
        Results dictionary
    """
    updater = MatchResultsUpdater()
    
    if round_name:
        results = {round_name: updater.update_round_results(round_name)}
    else:
        results = updater.update_all_rounds()
    
    return results


if __name__ == "__main__":
    # Example: Update all results
    results = update_results()
    
    for round_name, (updated, failed) in results.items():
        print(f"{round_name}: Updated {updated}, Failed {failed}")
