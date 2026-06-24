# -*- coding: utf-8 -*-

from app.db.session import (
    SessionLocal
)

from app.db.models.player import (
    Player
)

from app.db.models.player_state import (
    PlayerState
)

from src.acquisition.player_resolver import (
    PlayerResolver
)


class PlayerAcquisitionService:

    def __init__(
        self,
        provider
    ):

        self.db = SessionLocal()

        self.provider = provider

        self.player_resolver = (
            PlayerResolver()
        )

    def acquire_player(
        self,
        player_name: str
    ):

        existing_player_id = (
            self.player_resolver
            .resolve_player(
                player_name
            )
        )

        if existing_player_id:

            return existing_player_id

        player_dto = (
            self.provider
            .get_player(
                player_name
            )
        )

        if player_dto is None:

            print(
                f"Unable to acquire: "
                f"{player_name}"
            )

            return None

        try:

            player = Player(

                player_name=player_dto.name,

                hand=player_dto.hand,

                country=player_dto.country,

                birth_date=player_dto.birth_date,

                height_cm=player_dto.height_cm
            )

            self.db.add(
                player
            )

            self.db.flush()

            player_state = PlayerState(

                player_id=player.player_id,

                elo=1500,

                clay_elo=1500,

                hard_elo=1500,

                grass_elo=1500,

                recent_form=0.5,

                clay_winrate=0.5,

                hard_winrate=0.5,

                grass_winrate=0.5,

                matches_last_7d=0,

                days_since_last_match=None,

                total_matches=0,

                last_match_date=None
            )

            self.db.add(
                player_state
            )

            self.db.commit()

            print(
                f"Created player: "
                f"{player.player_name}"
            )

            return player.player_id

        except Exception as e:

            self.db.rollback()

            print(
                f"Failed acquiring "
                f"{player_name}: {e}"
            )

            return None

    def close(
        self
    ):

        self.player_resolver.close()

        self.db.close()