# -*- coding: utf-8 -*-
"""
Created on Sun May 31 18:19:51 2026

@author: AUM
"""

from sqlalchemy.orm import Session

from app.db.models.player import Player
from app.db.models.player_state import PlayerState


def get_player_snapshot(
    db: Session,
    player_name: str
):
    player = (
        db.query(Player)
        .filter(
            Player.player_name == player_name
        )
        .first()
    )

    if player is None:
        raise ValueError(
            f"Player not found: {player_name}"
        )

    state = (
        db.query(PlayerState)
        .filter(
            PlayerState.player_id
            == player.player_id
        )
        .first()
    )

    if state is None:
        raise ValueError(
            f"No state found for {player_name}"
        )

    return state
def get_player_snapshot_by_id(
    db,
    player_id
):

    state = (
        db.query(PlayerState)
        .filter(
            PlayerState.player_id == player_id
        )
        .first()
    )

    if state is None:
        raise ValueError(
            f"No state found for player {player_id}"
        )

    return state