# -*- coding: utf-8 -*-
"""
Created on Sun May 31 18:46:54 2026

@author: AUM
"""

from app.db.session import SessionLocal
from app.db.models.fixture import Fixture
from app.db.models.player import Player


def insert_fixture(
    player_a_name,
    player_b_name,
    surface,
    tournament,
    round_name
):
    db = SessionLocal()

    try:

        player_a = (
            db.query(Player)
            .filter(
                Player.player_name
                == player_a_name
            )
            .first()
        )

        player_b = (
            db.query(Player)
            .filter(
                Player.player_name
                == player_b_name
            )
            .first()
        )

        if not player_a or not player_b:
            raise ValueError(
                "Player not found"
            )

        fixture = Fixture(
            player_a_id=player_a.player_id,
            player_b_id=player_b.player_id,
            surface=surface,
            tournament=tournament,
            round=round_name,
            status="PENDING"
        )

        db.add(fixture)

        db.commit()

        print("Fixture inserted")

    finally:

        db.close()