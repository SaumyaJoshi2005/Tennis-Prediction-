
# -*- coding: utf-8 -*-
"""
Fixture Loader

Responsibilities:
- Resolve players from DTOs
- Automatically acquire missing players
- Prevent duplicate fixtures
- Insert fixtures into database
"""

from typing import Iterable

from app.db.session import (
    SessionLocal
)

from app.db.models.fixture import (
    Fixture
)

from src.acquisition.models.fixtures_dto import (
    FixtureDTO
)

from src.acquisition.player_resolver import (
    PlayerResolver
)

from src.acquisition.player_aquisition_service import (
    PlayerAcquisitionService
)


class FixtureLoader:

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

    def fixture_exists(
        self,
        player_a_id: int,
        player_b_id: int,
        tournament: str,
        round_name: str
    ) -> bool:

        existing = (
            self.db.query(Fixture)
            .filter(
                Fixture.player_a_id == player_a_id,
                Fixture.player_b_id == player_b_id,
                Fixture.tournament == tournament,
                Fixture.round == round_name
            )
            .first()
        )

        return existing is not None

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

    def load_fixture(
        self,
        fixture: FixtureDTO
    ) -> bool:

        if (
            not fixture.player_a
            or
            not fixture.player_b
        ):
            return False

        if (
            fixture.player_a == "TBD"
            or
            fixture.player_b == "TBD"
        ):
            return False

        player_a_id = (
            self._resolve_or_acquire(
                fixture.player_a
            )
        )

        player_b_id = (
            self._resolve_or_acquire(
                fixture.player_b
            )
        )

        if player_a_id is None:

            print(
                f"A_NOT_FOUND: "
                f"{fixture.player_a}"
            )

            return False

        if player_b_id is None:

            print(
                f"B_NOT_FOUND: "
                f"{fixture.player_b}"
            )

            return False

        if (
            self.fixture_exists(
                player_a_id,
                player_b_id,
                fixture.tournament,
                fixture.round
            )
        ):
            return False

        db_fixture = Fixture(

            player_a_id=player_a_id,

            player_b_id=player_b_id,

            tournament=fixture.tournament,

            round=fixture.round,

            surface=fixture.surface,

            match_date=(
                fixture.match_time.date()
                if fixture.match_time
                else None
            ),

            prediction=None,

            winner_predicted=None,

            player_a_win_probability=None,

            status="SCHEDULED"
        )

        self.db.add(
            db_fixture
        )

        return True

    def load_fixtures(
    self,
    fixtures: Iterable[
        FixtureDTO
    ]
):

        inserted = 0
    
        duplicate_count = 0
    
        tbd_count = 0
    
        player_not_found_count = 0
    
        exception_count = 0
    
        try:
    
            for fixture in fixtures:
    
                try:
    
                    # TBD CHECK
    
                    if (
                        not fixture.player_a
                        or
                        not fixture.player_b
                        or
                        fixture.player_a == "TBD"
                        or
                        fixture.player_b == "TBD"
                    ):
    
                        tbd_count += 1
    
                        print(
                            f"TBD: "
                            f"{fixture.player_a} "
                            f"vs "
                            f"{fixture.player_b}"
                        )
    
                        continue
    
                    # RESOLVE PLAYERS
    
                    player_a_id = (
                        self._resolve_or_acquire(
                            fixture.player_a
                        )
                    )
    
                    player_b_id = (
                        self._resolve_or_acquire(
                            fixture.player_b
                        )
                    )
    
                    if player_a_id is None:
    
                        player_not_found_count += 1
    
                        print(
                            f"A_NOT_FOUND: "
                            f"{fixture.player_a}"
                        )
    
                        continue
    
                    if player_b_id is None:
    
                        player_not_found_count += 1
    
                        print(
                            f"B_NOT_FOUND: "
                            f"{fixture.player_b}"
                        )
    
                        continue
    
                    # DUPLICATE CHECK
    
                    if (
                        self.fixture_exists(
                            player_a_id,
                            player_b_id,
                            fixture.tournament,
                            fixture.round
                        )
                    ):
    
                        duplicate_count += 1
    
                        print(
                            f"DUPLICATE: "
                            f"{fixture.player_a} "
                            f"vs "
                            f"{fixture.player_b}"
                        )
    
                        continue
    
                    # INSERT FIXTURE
    
                    db_fixture = Fixture(
    
                        player_a_id=player_a_id,
    
                        player_b_id=player_b_id,
    
                        tournament=fixture.tournament,
    
                        round=fixture.round,
    
                        surface=fixture.surface,
    
                        match_date=(
                            fixture.match_time.date()
                            if fixture.match_time
                            else None
                        ),
    
                        prediction=None,
    
                        winner_predicted=None,
    
                        player_a_win_probability=None,
    
                        status="SCHEDULED"
                    )
    
                    self.db.add(
                        db_fixture
                    )
    
                    inserted += 1
    
                    print(
                        f"INSERTED: "
                        f"{fixture.player_a} "
                        f"vs "
                        f"{fixture.player_b}"
                    )
    
                except Exception as e:
    
                    exception_count += 1
    
                    print(
                        f"EXCEPTION: "
                        f"{fixture.player_a} "
                        f"vs "
                        f"{fixture.player_b}"
                    )
    
                    print(
                        f"Reason: {e}"
                    )
    
            self.db.commit()
    
        except Exception:
    
            self.db.rollback()
    
            raise
    
        print("\n========== SUMMARY ==========")
    
        print(
            f"INSERTED: {inserted}"
        )
    
        print(
            f"DUPLICATES: {duplicate_count}"
        )
    
        print(
            f"TBD: {tbd_count}"
        )
    
        print(
            f"PLAYER_NOT_FOUND: "
            f"{player_not_found_count}"
        )
    
        print(
            f"EXCEPTIONS: "
            f"{exception_count}"
        )
    
        print("=============================")

    def close(
        self
    ):

        self.player_resolver.close()

        self.player_acquisition.close()

        self.db.close()

