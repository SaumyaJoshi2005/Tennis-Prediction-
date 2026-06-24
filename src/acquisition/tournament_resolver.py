# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 16:51:23 2026

@author: AUM
"""
"""
Tournament Resolver

Responsible for:

- Finding tournaments in DB
- Creating tournaments if missing
- Returning tournament_id

Does NOT:

- Scrape tournaments
- Call external APIs
- Update tournament metadata
"""

from typing import Optional

from sqlalchemy import func

from app.db.session import (
    SessionLocal
)

from app.db.models.tournament import (
    Tournament
)


class TournamentResolver:

    def __init__(self):

        self.db = SessionLocal()

    def normalize_name(
        self,
        tournament_name: str
    ) -> str:

        if not tournament_name:
            return ""

        return (
            tournament_name
            .strip()
            .lower()
        )

    def get_tournament(
        self,
        tournament_name: str
    ) -> Optional[Tournament]:

        normalized = (
            self.normalize_name(
                tournament_name
            )
        )

        return (
            self.db.query(Tournament)
            .filter(
                func.lower(
                    Tournament.tournament_name
                ) == normalized
            )
            .first()
        )

    def resolve_tournament(
        self,
        tournament_name: str
    ) -> Optional[int]:

        tournament = (
            self.get_tournament(
                tournament_name
            )
        )

        if tournament is None:
            return None

        return tournament.tournament_id

    def create_tournament(
        self,
        tournament_name: str,
        surface: str | None = None,
        level: str | None = None,
        location: str | None = None
    ) -> int:

        existing = (
            self.get_tournament(
                tournament_name
            )
        )

        if existing is not None:

            return (
                existing.tournament_id
            )

        tournament = Tournament(

            tournament_name=
            tournament_name,

            surface=surface,

            level=level,

            location=location
        )

        self.db.add(
            tournament
        )

        self.db.commit()

        self.db.refresh(
            tournament
        )

        print(
            f"Created tournament: "
            f"{tournament_name}"
        )

        return (
            tournament.tournament_id
        )

    def resolve_or_create(
        self,
        tournament_name: str,
        surface: str | None = None,
        level: str | None = None,
        location: str | None = None
    ) -> int:

        tournament_id = (
            self.resolve_tournament(
                tournament_name
            )
        )

        if tournament_id is not None:

            return tournament_id

        return (
            self.create_tournament(
                tournament_name,
                surface,
                level,
                location
            )
        )

    def close(
        self
    ):

        self.db.close()
        
    