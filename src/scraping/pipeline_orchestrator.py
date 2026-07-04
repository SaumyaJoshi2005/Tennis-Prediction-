# -*- coding: utf-8 -*-
"""
Roland Garros Pipeline Orchestrator
Orchestrates the complete RG draw scraping and result updating pipeline
Coordinates: draw scraping -> player registration/update -> results collection

Created on Jun 9, 2026
@author: AUM
"""

import sys
import logging
import argparse
from typing import Dict, Tuple
from datetime import datetime
from pathlib import Path

# Ensure project root is in path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rg_draw_scraper import scrape_rg_draws
from match_results_updater import update_results
from atp_player_fetcher import process_players_batch


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ORCHESTRATOR - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rg_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RGPipelineOrchestrator:
    """Orchestrate complete RG scraping and injection pipeline."""
    
    def __init__(self, force: bool = False):
        """
        Initialize orchestrator.
        
        Args:
            force: Force execution even if within buffer windows
        """
        self.force = force
        self.stats = {
            'fixtures_created': 0,
            'fixtures_failed': 0,
            'results_updated': 0,
            'results_failed': 0,
            'players_new': 0,
            'players_updated': 0
        }
    
    def log_summary(self):
        """Log pipeline execution summary."""
        logger.info("="*60)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("="*60)
        logger.info(
            f"Fixtures Created: {self.stats['fixtures_created']}"
        )
        logger.info(
            f"Fixtures Failed:  {self.stats['fixtures_failed']}"
        )
        logger.info(
            f"Results Updated:  {self.stats['results_updated']}"
        )
        logger.info(
            f"Results Failed:   {self.stats['results_failed']}"
        )
        logger.info(
            f"New Players:      {self.stats['players_new']}"
        )
        logger.info(
            f"Updated Players:  {self.stats['players_updated']}"
        )
        logger.info("="*60)
    
    def run_complete_pipeline(self) -> Dict:
        """
        Run complete pipeline: scrape draws -> update results.
        
        Returns:
            Pipeline execution results
        """
        logger.info("Starting Complete RG Pipeline Execution")
        logger.info(f"Force mode: {self.force}")
        logger.info("-" * 60)
        
        try:
            # Step 1: Scrape draws
            logger.info("STEP 1: Scraping RG Draws")
            logger.info("-" * 60)
            draw_results = scrape_rg_draws(force=self.force)
            
            for round_name, (created, failed) in draw_results.items():
                self.stats['fixtures_created'] += created
                self.stats['fixtures_failed'] += failed
                logger.info(
                    f"  {round_name}: Created {created}, Failed {failed}"
                )
            
            logger.info("-" * 60)
            
            # Step 2: Update results
            logger.info("STEP 2: Updating Match Results")
            logger.info("-" * 60)
            result_results = update_results()
            
            for round_name, (updated, failed) in result_results.items():
                self.stats['results_updated'] += updated
                self.stats['results_failed'] += failed
                logger.info(
                    f"  {round_name}: Updated {updated}, Failed {failed}"
                )
            
            logger.info("-" * 60)
            
            # Log summary
            self.log_summary()
            
            logger.info("Pipeline execution completed successfully")
            
            return {
                'success': True,
                'stats': self.stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats,
                'timestamp': datetime.now().isoformat()
            }
    
    def run_scrape_only(self, round_name: str = None) -> Dict:
        """
        Run only draw scraping step.
        
        Args:
            round_name: Specific round to scrape (optional)
            
        Returns:
            Scrape results
        """
        logger.info("Starting Draw Scraping Only")
        logger.info(f"Target round: {round_name or 'All rounds'}")
        logger.info("-" * 60)
        
        try:
            draw_results = scrape_rg_draws(
                round_name=round_name,
                force=self.force
            )
            
            for rnd, (created, failed) in draw_results.items():
                self.stats['fixtures_created'] += created
                self.stats['fixtures_failed'] += failed
                logger.info(
                    f"  {rnd}: Created {created}, Failed {failed}"
                )
            
            self.log_summary()
            
            return {
                'success': True,
                'results': draw_results,
                'stats': self.stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats,
                'timestamp': datetime.now().isoformat()
            }
    
    def run_results_only(self, round_name: str = None) -> Dict:
        """
        Run only results update step.
        
        Args:
            round_name: Specific round to update (optional)
            
        Returns:
            Results update results
        """
        logger.info("Starting Results Update Only")
        logger.info(f"Target round: {round_name or 'All rounds'}")
        logger.info("-" * 60)
        
        try:
            result_results = update_results(round_name=round_name)
            
            for rnd, (updated, failed) in result_results.items():
                self.stats['results_updated'] += updated
                self.stats['results_failed'] += failed
                logger.info(
                    f"  {rnd}: Updated {updated}, Failed {failed}"
                )
            
            self.log_summary()
            
            return {
                'success': True,
                'results': result_results,
                'stats': self.stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Results update failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats,
                'timestamp': datetime.now().isoformat()
            }


def main():
    """Main entry point with CLI argument support."""
    
    parser = argparse.ArgumentParser(
        description='Roland Garros Scraping and Injection Pipeline'
    )
    
    parser.add_argument(
        '--mode',
        choices=['full', 'scrape', 'results'],
        default='full',
        help='Pipeline execution mode (default: full)'
    )
    
    parser.add_argument(
        '--round',
        type=str,
        default=None,
        help='Specific round to process (optional)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force execution even if within 24hr buffer'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    for handler in logger.handlers:
        handler.setLevel(getattr(logging, args.log_level))
    
    # Create orchestrator
    orchestrator = RGPipelineOrchestrator(force=args.force)
    
    # Run appropriate mode
    if args.mode == 'full':
        result = orchestrator.run_complete_pipeline()
    elif args.mode == 'scrape':
        result = orchestrator.run_scrape_only(round_name=args.round)
    elif args.mode == 'results':
        result = orchestrator.run_results_only(round_name=args.round)
    
    # Exit with appropriate code
    exit_code = 0 if result['success'] else 1
    logger.info(f"Pipeline exit code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    exit(main())
