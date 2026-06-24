# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 16:17:43 2026

@author: AUM
"""

K_FACTOR = 32


def expected_score(
    player_elo: float,
    opponent_elo: float
) -> float:

    return 1 / (
        1 +
        10 ** (
            (opponent_elo - player_elo)
            / 400
        )
    )


def update_elo(
    winner_elo: float,
    loser_elo: float
):

    expected_winner = (
        expected_score(
            winner_elo,
            loser_elo
        )
    )

    expected_loser = (
        expected_score(
            loser_elo,
            winner_elo
        )
    )

    new_winner_elo = (
        winner_elo
        + K_FACTOR
        * (
            1 - expected_winner
        )
    )

    new_loser_elo = (
        loser_elo
        + K_FACTOR
        * (
            0 - expected_loser
        )
    )

    return (
        round(
            new_winner_elo,
            2
        ),
        round(
            new_loser_elo,
            2
        )
    )