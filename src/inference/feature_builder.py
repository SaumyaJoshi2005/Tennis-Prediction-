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

        a_surface_winrate = (
            a.clay_winrate or 0
        )

        b_surface_winrate = (
            b.clay_winrate or 0
        )

    elif surface == "Grass":

        a_surface_elo = a.grass_elo
        b_surface_elo = b.grass_elo

        a_surface_winrate = (
            a.grass_winrate or 0
        )

        b_surface_winrate = (
            b.grass_winrate or 0
        )

    else:

        a_surface_elo = a.hard_elo
        b_surface_elo = b.hard_elo

        a_surface_winrate = (
            a.hard_winrate or 0
        )

        b_surface_winrate = (
            b.hard_winrate or 0
        )

    return {

        "elo_diff":
            (a.elo or 0)
            - (b.elo or 0),

        "surface_elo_diff":
            (a_surface_elo or 0)
            - (b_surface_elo or 0),

        "recent_form_diff":
            (a.recent_form or 0)
            - (b.recent_form or 0),

        "surface_winrate_diff":
            a_surface_winrate
            - b_surface_winrate,

        "matches_last_7d_diff":
            (a.matches_last_7d or 0)
            - (b.matches_last_7d or 0),

        "days_since_last_match_diff":
            (a.days_since_last_match or 0)
            - (b.days_since_last_match or 0),

        "h2h_diff":
            0
    }