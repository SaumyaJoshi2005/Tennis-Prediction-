# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 16:26:39 2026

@author: AUM
"""

from typing import Iterable

from app.db.session import (
    SessionLocal
)

from app.db.models.match import (
    Match
)

from src.acquisition.models.result_dto import (
    ResultDTO
)

from src.acquisition.player_resolver import (
    PlayerResolver
)

from src.acquisition.player_aquisition_service import (
    PlayerAcquisitionService
)
from src.acquisition.tournament_resolver import (
    TournamentResolver
)

class ResultLoader:

    def __init__(
        self,
        player_provider
    ):

        self.db = SessionLocal()

        self.player_resolver = (
            PlayerResolver()
        )

        self.player_acquisition = (
            PlayerAcquisitionService(
                player_provider
            )
        )
        self.tournament_resolver = (
            TournamentResolver()
            )

    def _resolve_or_acquire(
        self,
        player_name: str
    ):

        player_id = (
            self.player_resolver
            .resolve_player(
                player_name
            )
        )

        if player_id is not None:
            return player_id

        print(
            f"Acquiring player: "
            f"{player_name}"
        )

        return (
            self.player_acquisition
            .acquire_player(
                player_name
            )
        )

    def match_exists(
        self,
        winner_id: int,
        loser_id: int,
        match_date,
        round_name: str
    ) -> bool:

        existing = (
            self.db.query(Match)
            .filter(
                Match.winner_id == winner_id,
                Match.loser_id == loser_id,
                Match.match_date == match_date,
                Match.round == round_name
            )
            .first()
        )

        return existing is not None

    def load_result(
        self,
        result: ResultDTO
    ) -> bool:

        if (
            not result.winner
            or
            not result.loser
        ):
            return False

        winner_id = (
            self._resolve_or_acquire(
                result.winner
            )
        )

        loser_id = (
            self._resolve_or_acquire(
                result.loser
            )
        )

        if winner_id is None:

            print(
                f"WINNER_NOT_FOUND: "
                f"{result.winner}"
            )

            return False

        if loser_id is None:

            print(
                f"LOSER_NOT_FOUND: "
                f"{result.loser}"
            )

            return False

        if (
            self.match_exists(
                winner_id,
                loser_id,
                result.match_date,
                result.round
            )
        ):

            return False
        tournament_id = (
    self.tournament_resolver
    .resolve_or_create(
        result.tournament
    )
)
        db_match = Match(

            tournament_id=tournament_id,

            match_date=result.match_date,

            round=result.round,

            best_of=None,

            winner_id=winner_id,

            loser_id=loser_id,

            winner_rank=None,

            loser_rank=None,

            winner_elo=None,

            loser_elo=None,

            winner_surface_elo=None,

            loser_surface_elo=None,

            winner_recent_form=None,

            loser_recent_form=None,

            winner_surface_winrate=None,

            loser_surface_winrate=None,

            winner_fitness=None,

            loser_fitness=None
        )

        self.db.add(
            db_match
        )

        return True

    def load_results(
        self,
        results: Iterable[
            ResultDTO
        ]
    ):

        inserted = 0

        duplicates = 0

        failed = 0

        try:

            for result in results:

                success = (
                    self.load_result(
                        result
                    )
                )

                if success:

                    inserted += 1

                else:

                    failed += 1

            self.db.commit()

        except Exception as e:

            self.db.rollback()

            raise e

        print(
            f"Inserted: {inserted}"
        )

        print(
            f"Failed: {failed}"
        )

    def close(
        self
    ):

        self.player_resolver.close()

        self.player_acquisition.close()

        self.db.close()
        self.tournament_resolver.close()
        
