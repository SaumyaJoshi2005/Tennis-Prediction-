# -*- coding: utf-8 -*-
"""
Created on Sun May 31 18:12:20 2026

@author: AUM
"""

from datetime import timedelta

INITIAL_ELO = 1500
K_FACTOR = 32


def expected_score(rating_a, rating_b):
    return 1 / (
        1 + (10 ** ((rating_b - rating_a) / 400))
    )


def update_elo(rating_a, rating_b, score_a):
    expected_a = expected_score(
        rating_a,
        rating_b
    )

    return (
        rating_a
        + K_FACTOR * (score_a - expected_a)
    )


def compute_recent_form(history, n=5):
    if len(history) == 0:
        return 0.5

    recent = history[-n:]

    wins = sum(
        result
        for _, result, _, _ in recent
    )

    return wins / len(recent)


def compute_surface_winrate(
    history,
    surface
):
    filtered = [
        result
        for s, result in history
        if s == surface
    ]

    if len(filtered) == 0:
        return 0.5

    return sum(filtered) / len(filtered)


def compute_matches_last_7d(
    history,
    current_date
):
    threshold = (
        current_date
        - timedelta(days=7)
    )

    return sum(
        1
        for date, _, _, _
        in history
        if date >= threshold
    )


def compute_days_since_last_match(
    history,
    current_date
):
    if len(history) == 0:
        return None

    days = (
        current_date
        - history[-1][0]
    ).days

    return min(365, days)