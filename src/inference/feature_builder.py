# -*- coding: utf-8 -*-
"""
Created on Sun May 31 18:22:54 2026

@author: AUM
"""

from src.inference.player_snapshot import (
    get_player_snapshot
)


def build_features(
    db,
    player_a_name,
    player_b_name,
    surface
):

    a = get_player_snapshot(
        db,
        player_a_name
    )

    b = get_player_snapshot(
        db,
        player_b_name
    )

    if surface == "Clay":

        a_surface_elo = a.clay_elo
        b_surface_elo = b.clay_elo

    elif surface == "Grass":

        a_surface_elo = a.grass_elo
        b_surface_elo = b.grass_elo

    else:

        a_surface_elo = a.hard_elo
        b_surface_elo = b.hard_elo

    return {

        "elo_diff":
            a.elo - b.elo,

        "surface_elo_diff":
            a_surface_elo - b_surface_elo,

        "recent_form_diff":
            a.recent_form - b.recent_form,

        "surface_winrate_diff":
            0,

        "matches_last_7d_diff":
            0,

        "days_since_last_match_diff":
            0,

        "h2h_diff":
            0
    }
        
