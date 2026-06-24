# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 00:55:10 2026

@author: AUM
"""

# -*- coding: utf-8 -*-
"""
Player Resolver

Responsible only for:
- Normalizing player names
- Resolving player IDs from the database
- Returning Player ORM objects when needed

Does NOT:
- Create players
- Call external providers
- Modify database records
"""

from typing import Optional

from sqlalchemy import func

from app.db.session import (
    SessionLocal
)

from app.db.models.player import (
    Player
)


class PlayerResolver:

    def __init__(self):

        self.db = SessionLocal()

    def normalize_name(
        self,
        name: str
    ) -> str:

        if not name:
            return ""

        return (
            name
            .strip()
            .lower()
        )

    def get_player(
        self,
        player_name: str
    ) -> Optional[Player]:

        if not player_name:
            return None

        normalized = self.normalize_name(
            player_name
        )

        return (
            self.db.query(Player)
            .filter(
                func.lower(
                    Player.player_name
                ) == normalized
            )
            .first()
        )

    def resolve_player(
        self,
        player_name: str
    ) -> Optional[int]:

        player = self.get_player(
            player_name
        )

        if player is None:
            return None

        return player.player_id

    def player_exists(
        self,
        player_name: str
    ) -> bool:

        return (
            self.resolve_player(
                player_name
            )
            is not None
        )

    def resolve_players(
        self,
        player_names: list[str]
    ) -> dict[str, Optional[int]]:

        results = {}

        for name in player_names:

            results[name] = (
                self.resolve_player(
                    name
                )
            )

        return results

    def close(
        self
    ):

        self.db.close()