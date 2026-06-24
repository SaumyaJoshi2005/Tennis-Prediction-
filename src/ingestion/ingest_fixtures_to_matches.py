# -*- coding: utf-8 -*-
"""
Ingest COMPLETED fixtures into Match table.

Purpose:
    Transform scraped Fixture data (scheduled/upcoming events) into Match table
    (historical truth for completed matches).

Architecture:
    Fixture (status=COMPLETED) → Match → Feature Builder → Model Training

    Note: MatchFeatures are generated separately via Feature Builder pipeline.
    This script only populates Match table with base historical data.

Usage:
    python ingest_fixtures_to_matches.py
    python ingest_fixtures_to_matches.py --validate  # Dry run
    python ingest_fixtures_to_matches.py --log-level DEBUG
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

from sqlalchemy.exc import IntegrityError

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.db.session import SessionLocal
from app.db.models.match import Match
from app.db.models.fixture import Fixture
from app.db.models.player import Player
from app.db.models.player_state import PlayerState
from app.db.models.tournament import Tournament


# Configure logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class FixtureIngestionStats:
    """Track ingestion statistics."""
    
    def __init__(self):
        self.fixtures_examined = 0
        self.matches_created = 0
        self.already_ingested = 0
        self.missing_players = 0
        self.missing_tournaments = 0
        self.failed_records = 0
    
    def report(self):
        """Print statistics summary."""
        logger.info("=" * 60)
        logger.info("Ingestion Summary:")
        logger.info(f"  Fixtures examined: {self.fixtures_examined}")
        logger.info(f"  Matches created: {self.matches_created}")
        logger.info(f"  Already ingested: {self.already_ingested}")
        logger.info(f"  Missing players: {self.missing_players}")
        logger.info(f"  Missing tournaments: {self.missing_tournaments}")
        logger.info(f"  Failed records: {self.failed_records}")
        logger.info("=" * 60)


def load_lookup_tables(db) -> Tuple[Dict, Dict, Dict]:
    """
    Load Player, PlayerState, and Tournament lookup tables.
    
    Returns:
        Tuple of (player_lookup, player_state_lookup, tournament_lookup)
        where:
        - player_lookup: {player_id: player_obj}
        - player_state_lookup: {player_id: player_state_obj}
        - tournament_lookup: {tournament_name: tournament_id}
    """
    logger.info("Loading lookup tables...")
    
    # Load players
    players = db.query(Player).all()
    player_lookup = {player.player_id: player for player in players}
    
    # Load player states
    player_states = db.query(PlayerState).all()
    player_state_lookup = {ps.player_id: ps for ps in player_states}
    
    # Load tournaments (by name)
    tournaments = db.query(Tournament).all()
    tournament_lookup = {t.tournament_name: t.tournament_id for t in tournaments}
    
    logger.info(f"  Players: {len(player_lookup)}")
    logger.info(f"  Player States: {len(player_state_lookup)}")
    logger.info(f"  Tournaments: {len(tournament_lookup)}")
    
    return player_lookup, player_state_lookup, tournament_lookup


def get_player_stats(
    player_id: int,
    player_state_lookup: Dict,
    surface: str = 'Clay'
) -> Dict:
    """
    Extract player statistics from PlayerState.
    
    Args:
        player_id: Player ID to lookup
        player_state_lookup: PlayerState lookup dict
        surface: Match surface (Clay, Hard, Grass) for surface-specific stats
    
    If PlayerState missing, returns dict with None values.
    (Future: Add ATP API fallback here)
    """
    if player_id not in player_state_lookup:
        # Future: ATP API fallback could be implemented here
        return {
            'rank': None,
            'elo': None,
            'surface_elo': None,
            'recent_form': None,
            'surface_winrate': None,
            'fitness': None,
        }
    
    ps = player_state_lookup[player_id]
    
    # Map surface to surface-specific fields
    surface_elo_field = f"{surface.lower()}_elo"
    surface_winrate_field = f"{surface.lower()}_winrate"
    
    # Safe attribute access with fallback
    surface_elo = getattr(ps, surface_elo_field, None)
    surface_winrate = getattr(ps, surface_winrate_field, None)
    
    return {
        'rank': None,  # PlayerState doesn't track rank; Match rank can be None
        'elo': ps.elo,
        'surface_elo': surface_elo,
        'recent_form': ps.recent_form,
        'surface_winrate': surface_winrate,
        'fitness': ps.matches_last_7d,
    }


def ingest_fixtures_to_matches(
    db,
    validate_only: bool = False
) -> FixtureIngestionStats:
    """
    Main ingestion logic: Transform completed fixtures into matches.
    
    Args:
        db: SQLAlchemy session
        validate_only: If True, perform dry run without commits
    
    Returns:
        FixtureIngestionStats object with ingestion metrics
    """
    stats = FixtureIngestionStats()
    
    logger.info("Starting fixture ingestion...")
    logger.info(f"Validate only: {validate_only}")
    
    # Load lookups
    player_lookup, player_state_lookup, tournament_lookup = load_lookup_tables(db)
    
    # Query completed fixtures
    completed_fixtures = db.query(Fixture).filter(
        Fixture.status == 'COMPLETED'
    ).all()
    
    logger.info(f"Found {len(completed_fixtures)} completed fixtures")
    
    matches_to_insert = []
    
    for fixture in completed_fixtures:
        stats.fixtures_examined += 1
        
        # Skip if match already exists
        existing_match = db.query(Match).filter(
            Match.match_id == fixture.fixture_id
        ).first()
        
        if existing_match:
            stats.already_ingested += 1
            logger.debug(f"Match {fixture.fixture_id} already ingested, skipping")
            continue
        
        # Validate players exist
        if fixture.player_a_id not in player_lookup:
            stats.missing_players += 1
            logger.warning(
                f"Fixture {fixture.fixture_id}: player_a_id "
                f"{fixture.player_a_id} not found in database"
            )
            continue
        
        if fixture.player_b_id not in player_lookup:
            stats.missing_players += 1
            logger.warning(
                f"Fixture {fixture.fixture_id}: player_b_id "
                f"{fixture.player_b_id} not found in database"
            )
            continue
        
        # Determine winner and loser based on fixture.winner_predicted
        if fixture.winner_predicted == 'player_a':
            winner_id = fixture.player_a_id
            loser_id = fixture.player_b_id
        elif fixture.winner_predicted == 'player_b':
            winner_id = fixture.player_b_id
            loser_id = fixture.player_a_id
        else:
            stats.failed_records += 1
            logger.error(
                f"Fixture {fixture.fixture_id}: invalid winner_predicted "
                f"value '{fixture.winner_predicted}'"
            )
            continue
        
        # Lookup tournament_id
        tournament_id = tournament_lookup.get(fixture.tournament)
        if tournament_id is None:
            stats.missing_tournaments += 1
            logger.warning(
                f"Fixture {fixture.fixture_id}: tournament '{fixture.tournament}' "
                f"not found in database"
            )
            continue
        
        # Get player stats from PlayerState
        winner_stats = get_player_stats(winner_id, player_state_lookup, fixture.surface)
        loser_stats = get_player_stats(loser_id, player_state_lookup, fixture.surface)
        
        # Create Match record
        try:
            match = Match(
                match_id=fixture.fixture_id,
                tournament_id=tournament_id,
                match_date=fixture.match_date,
                round=fixture.round,
                best_of=3,  # Tennis standard
                
                winner_id=winner_id,
                loser_id=loser_id,
                
                winner_rank=winner_stats['rank'],
                loser_rank=loser_stats['rank'],
                
                winner_elo=winner_stats['elo'],
                loser_elo=loser_stats['elo'],
                
                winner_surface_elo=winner_stats['surface_elo'],
                loser_surface_elo=loser_stats['surface_elo'],
                
                winner_recent_form=winner_stats['recent_form'],
                loser_recent_form=loser_stats['recent_form'],
                
                winner_surface_winrate=winner_stats['surface_winrate'],
                loser_surface_winrate=loser_stats['surface_winrate'],
                
                winner_fitness=winner_stats['fitness'],
                loser_fitness=loser_stats['fitness'],
            )
            
            matches_to_insert.append(match)
            
        except Exception as e:
            stats.failed_records += 1
            logger.error(f"Fixture {fixture.fixture_id}: Failed to create Match - {e}")
            continue
    
    # Bulk insert matches
    if matches_to_insert:
        logger.info(f"Inserting {len(matches_to_insert)} matches...")
        
        if not validate_only:
            try:
                db.bulk_save_objects(matches_to_insert)
                db.commit()
                stats.matches_created = len(matches_to_insert)
                logger.info(f"Successfully inserted {len(matches_to_insert)} matches")
            except IntegrityError as e:
                db.rollback()
                stats.failed_records += len(matches_to_insert)
                logger.error(f"Bulk insert failed: {e}")
            except Exception as e:
                db.rollback()
                stats.failed_records += len(matches_to_insert)
                logger.error(f"Unexpected error during bulk insert: {e}")
        else:
            stats.matches_created = len(matches_to_insert)
            logger.info(f"[DRY RUN] Would insert {len(matches_to_insert)} matches")
    else:
        logger.info("No matches to insert")
    
    return stats


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Ingest completed fixtures into Match table',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ingest_fixtures_to_matches.py                # Full ingestion
  python ingest_fixtures_to_matches.py --validate     # Dry run
  python ingest_fixtures_to_matches.py --log-level DEBUG
        """
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Dry run: validate without committing'
    )
    
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Set log level
    logger.setLevel(getattr(logging, args.log_level))
    
    # Connect to database
    db = SessionLocal()
    
    try:
        stats = ingest_fixtures_to_matches(db, validate_only=args.validate)
        stats.report()
    
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == '__main__':
    main()
