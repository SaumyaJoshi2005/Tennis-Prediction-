# -*- coding: utf-8 -*-
"""
ATP Player Data Fetcher
Fetches player data from ATP API for unregistered players and updates PlayerState
Uses fuzzy matching to prevent duplicate player entries in database

Created on Jun 9, 2026
@author: AUM
"""

import requests
import logging
from difflib import SequenceMatcher
from typing import Optional, Dict, Tuple
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from app.db.session import SessionLocal
from app.db.models.player import Player
from app.db.models.player_state import PlayerState


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ATP_FETCHER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


ATP_API_BASE = "https://www.atptour.com/en/players"
FUZZY_MATCH_THRESHOLD = 0.80  # 80% similarity threshold


class ATPPlayerFetcher:
    """Fetch player data from ATP API and manage database upserts."""
    
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
    
    @staticmethod
    def fuzzy_match_ratio(s1: str, s2: str) -> float:
        """
        Calculate fuzzy match ratio between two strings.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Match ratio between 0 and 1
        """
        s1_normalized = s1.lower().strip()
        s2_normalized = s2.lower().strip()
        
        return SequenceMatcher(
            None,
            s1_normalized,
            s2_normalized
        ).ratio()
    
    def find_player_in_db(
        self,
        first_name: str,
        last_name: str
    ) -> Optional[Player]:
        """
        Find player in database using fuzzy matching.
        
        Args:
            first_name: Player first name
            last_name: Player last name
            
        Returns:
            Player object if found, None otherwise
        """
        search_name = f"{first_name} {last_name}"
        
        # Get all players from database
        all_players = self.db.query(Player).all()
        
        best_match = None
        best_score = FUZZY_MATCH_THRESHOLD
        
        for player in all_players:
            score = self.fuzzy_match_ratio(
                search_name,
                player.player_name
            )
            
            if score > best_score:
                best_score = score
                best_match = player
        
        if best_match:
            logger.info(
                f"Fuzzy match found: {search_name} -> "
                f"{best_match.player_name} (score: {best_score:.2f})"
            )
        
        return best_match
    
    def fetch_player_from_atp(
        self,
        first_name: str,
        last_name: str,
        country: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Fetch player data from ATP API.
        
        Args:
            first_name: Player first name
            last_name: Player last name
            country: Player country (optional)
            
        Returns:
            Dictionary with player data or None if not found
        """
        try:
            # Build search query
            search_query = f"{first_name} {last_name}"
            
            # ATP API search endpoint
            search_url = f"{ATP_API_BASE}/search"
            params = {
                'q': search_query,
                'pagesize': 1
            }
            
            response = self.session.get(
                search_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                player_info = data[0]
                
                logger.info(
                    f"ATP API found: {first_name} {last_name}"
                )
                
                return {
                    'first_name': player_info.get('firstName'),
                    'last_name': player_info.get('lastName'),
                    'country': player_info.get('country'),
                    'birth_date': player_info.get('birthDate'),
                    'height_cm': player_info.get('height'),
                    'hand': player_info.get('hand'),
                    'atp_id': player_info.get('id')
                }
            
            return None
            
        except requests.RequestException as e:
            logger.warning(
                f"ATP API error for {first_name} {last_name}: {str(e)}"
            )
            return None
    
    def register_player(
        self,
        first_name: str,
        last_name: str,
        atp_data: Optional[Dict] = None
    ) -> Optional[Player]:
        """
        Register a new player in database.
        
        Args:
            first_name: Player first name
            last_name: Player last name
            atp_data: ATP API data (optional)
            
        Returns:
            Player object if successful, None otherwise
        """
        try:
            player_name = f"{first_name} {last_name}"
            
            # Check if player already exists (exact match)
            existing = self.db.query(Player).filter(
                Player.player_name == player_name
            ).first()
            
            if existing:
                logger.info(f"Player already registered: {player_name}")
                return existing
            
            # Create new player
            new_player = Player(
                player_name=player_name,
                hand=atp_data.get('hand') if atp_data else None,
                country=atp_data.get('country') if atp_data else None,
                birth_date=atp_data.get('birth_date') if atp_data else None,
                height_cm=atp_data.get('height_cm') if atp_data else None
            )
            
            self.db.add(new_player)
            self.db.flush()  # Get the player_id
            
            # Initialize PlayerState for new player
            player_state = PlayerState(
                player_id=new_player.player_id,
                elo=1500.0,  # Default Elo rating
                clay_elo=1500.0,
                hard_elo=1500.0,
                grass_elo=1500.0,
                recent_form=0.5,
                clay_winrate=0.5,
                hard_winrate=0.5,
                grass_winrate=0.5,
                matches_last_7d=0,
                days_since_last_match=0,
                total_matches=0,
                last_match_date=None
            )
            
            self.db.add(player_state)
            self.db.commit()
            
            logger.info(f"New player registered: {player_name}")
            return new_player
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error registering player: {str(e)}")
            return None
    
    def update_player_state(
        self,
        player_id: int,
        atp_data: Dict
    ) -> bool:
        """
        Update PlayerState with ATP data.
        
        Args:
            player_id: Player ID in database
            atp_data: ATP API data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            player_state = self.db.query(PlayerState).filter(
                PlayerState.player_id == player_id
            ).first()
            
            if not player_state:
                logger.warning(
                    f"PlayerState not found for player_id: {player_id}"
                )
                return False
            
            # Update existing fields with ATP data if available
            if 'elo' in atp_data and atp_data['elo']:
                player_state.elo = atp_data['elo']
            
            if 'clay_elo' in atp_data and atp_data['clay_elo']:
                player_state.clay_elo = atp_data['clay_elo']
            
            if 'hard_elo' in atp_data and atp_data['hard_elo']:
                player_state.hard_elo = atp_data['hard_elo']
            
            if 'grass_elo' in atp_data and atp_data['grass_elo']:
                player_state.grass_elo = atp_data['grass_elo']
            
            if 'recent_form' in atp_data and atp_data['recent_form']:
                player_state.recent_form = atp_data['recent_form']
            
            if 'matches_last_7d' in atp_data and atp_data['matches_last_7d']:
                player_state.matches_last_7d = atp_data['matches_last_7d']
            
            if 'days_since_last_match' in atp_data and \
               atp_data['days_since_last_match']:
                player_state.days_since_last_match = \
                    atp_data['days_since_last_match']
            
            if 'total_matches' in atp_data and atp_data['total_matches']:
                player_state.total_matches = atp_data['total_matches']
            
            if 'last_match_date' in atp_data and atp_data['last_match_date']:
                player_state.last_match_date = atp_data['last_match_date']
            
            self.db.commit()
            
            logger.info(f"Updated PlayerState for player_id: {player_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Error updating PlayerState for player_id {player_id}: "
                f"{str(e)}"
            )
            return False
    
    def process_player(
        self,
        first_name: str,
        last_name: str
    ) -> Tuple[Optional[Player], bool]:
        """
        Process a player: check if exists, register if needed, update stats.
        
        Args:
            first_name: Player first name
            last_name: Player last name
            
        Returns:
            Tuple of (Player object, is_new_player)
        """
        # Try fuzzy match first
        existing_player = self.find_player_in_db(first_name, last_name)
        
        if existing_player:
            logger.info(
                f"Player found in database: {existing_player.player_name}"
            )
            
            # Fetch ATP data and update stats
            atp_data = self.fetch_player_from_atp(first_name, last_name)
            if atp_data:
                self.update_player_state(existing_player.player_id, atp_data)
            
            return existing_player, False
        
        # Player not in database, fetch from ATP and register
        logger.info(
            f"Player not found in database: {first_name} {last_name}"
        )
        
        atp_data = self.fetch_player_from_atp(first_name, last_name)
        
        if not atp_data:
            logger.warning(
                f"ATP API could not find: {first_name} {last_name}"
            )
            # Still register with basic info (ATP might have issues temporarily)
            new_player = self.register_player(first_name, last_name, None)
            return new_player, True
        
        # Register with ATP data
        new_player = self.register_player(first_name, last_name, atp_data)
        
        if new_player:
            self.update_player_state(new_player.player_id, atp_data)
            return new_player, True
        
        return None, False


def process_players_batch(
    player_names: list
) -> Dict[str, Tuple[Optional[Player], bool]]:
    """
    Process a batch of players.
    
    Args:
        player_names: List of player names (format: "FirstName LastName")
        
    Returns:
        Dictionary mapping player_name to (Player object, is_new)
    """
    fetcher = ATPPlayerFetcher()
    results = {}
    
    for player_name in player_names:
        try:
            parts = player_name.split(' ', 1)
            if len(parts) == 2:
                first_name, last_name = parts
                player, is_new = fetcher.process_player(first_name, last_name)
                results[player_name] = (player, is_new)
            else:
                logger.warning(f"Invalid player name format: {player_name}")
                results[player_name] = (None, False)
        except Exception as e:
            logger.error(f"Error processing {player_name}: {str(e)}")
            results[player_name] = (None, False)
    
    return results


if __name__ == "__main__":
    # Example usage
    test_players = ["Novak Djokovic", "Rafael Nadal", "Roger Federer"]
    results = process_players_batch(test_players)
    
    for name, (player, is_new) in results.items():
        status = "NEW" if is_new else "EXISTING"
        print(f"{name}: {status} - {player.player_name if player else 'FAILED'}")
