# -*- coding: utf-8 -*-
"""
Created on Thu May 28 23:14:32 2026

@author: AUM
"""

from collections import defaultdict
from datetime import timedelta

from sqlalchemy.orm import Session
import numpy as np
from app.db.session import SessionLocal
from app.db.models.match import Match
from app.db.models.player import Player
from app.db.models.tournament import Tournament
from app.db.models.match_features import MatchFeatures


INITIAL_ELO = 1500
K_FACTOR = 32


def expected_score(rating_a, rating_b):
    return 1 / (1 + (10 ** ((rating_b - rating_a) / 400)))


def update_elo(rating_a, rating_b, score_a):
    expected_a = expected_score(rating_a, rating_b)

    return rating_a + K_FACTOR * (score_a - expected_a)


def compute_recent_form(history, n=5):
    if len(history) == 0:
        return 0.5

    recent = history[-n:]

    wins = sum(result for _, result, _, _ in recent)

    return wins / len(recent)
def compute_surface_winrate(history, surface):
    filtered = [
        result
        for s, result in history
        if s == surface
    ]

    if len(filtered) == 0:
        return 0.5

    return sum(filtered) / len(filtered)


def compute_matches_last_7d(history, current_date):
    threshold = current_date - timedelta(days=7)

    return sum(
        1
        for date, _, _, _ in history
        if date >= threshold
    )


def compute_minutes_last_14d(history, current_date):
    threshold = current_date - timedelta(days=14)

    total_minutes = 0

    for date, _, _, minutes in history:
        if date >= threshold:
            if minutes is not None:
                total_minutes += minutes

    return total_minutes


def compute_days_since_last_match(history, current_date):
    if len(history) == 0:
        return None

    days = (current_date - history[-1][0]).days

    return min(365,days)


def main():
    db: Session = SessionLocal()

    try:
        print("Loading matches chronologically...")

        matches = (
            db.query(Match)
            .order_by(Match.match_date.asc())
            .all()
        )

        print(f"Matches loaded: {len(matches)}")

        player_elo = defaultdict(lambda: INITIAL_ELO)

        surface_elo = defaultdict(
            lambda: defaultdict(lambda: INITIAL_ELO)
        )

        recent_results = defaultdict(list)

        surface_results = defaultdict(list)

        h2h = defaultdict(int)

        feature_rows = []

        processed = 0

        for match in matches:

            if (
                match.winner_id is None
                or match.loser_id is None
                or match.match_date is None
            ):
                continue

            winner_id = match.winner_id
            loser_id = match.loser_id

            current_date = match.match_date

            tournament = (
                db.query(Tournament)
                .filter(
                    Tournament.tournament_id
                    == match.tournament_id
                )
                .first()
            )

            surface = None

            if tournament:
                surface = tournament.surface

            # --------------------------------------------------
            # PRE-MATCH FEATURES
            # --------------------------------------------------

            winner_pre_elo = player_elo[winner_id]
            loser_pre_elo = player_elo[loser_id]

            winner_surface_elo = (
                surface_elo[winner_id][surface]
            )

            loser_surface_elo = (
                surface_elo[loser_id][surface]
            )

            winner_recent_form = compute_recent_form(
                recent_results[winner_id]
            )

            loser_recent_form = compute_recent_form(
                recent_results[loser_id]
            )

            winner_surface_winrate = (
                compute_surface_winrate(
                    surface_results[winner_id],
                    surface
                )
            )

            loser_surface_winrate = (
                compute_surface_winrate(
                    surface_results[loser_id],
                    surface
                )
            )

            winner_matches_last_7d = (
                compute_matches_last_7d(
                    recent_results[winner_id],
                    current_date
                )
            )

            loser_matches_last_7d = (
                compute_matches_last_7d(
                    recent_results[loser_id],
                    current_date
                )
            )

            winner_minutes_last_14d = (
                compute_minutes_last_14d(
                    recent_results[winner_id],
                    current_date
                )
            )

            loser_minutes_last_14d = (
                compute_minutes_last_14d(
                    recent_results[loser_id],
                    current_date
                )
            )

            winner_days_since_last_match = (
                compute_days_since_last_match(
                    recent_results[winner_id],
                    current_date
                )
            )

            loser_days_since_last_match = (
                compute_days_since_last_match(
                    recent_results[loser_id],
                    current_date
                )
            )

            """pair = tuple(sorted([winner_id, loser_id]))

            winner_h2h = h2h[pair]["a"]
            loser_h2h = h2h[pair]["b"]
            """
            ##h2h fix:-winner h2h->no of wins of W vs L
            winner_h2h = h2h[
                (winner_id, loser_id)
            ]

            loser_h2h = h2h[
                (loser_id, winner_id)
            ]
            # --------------------------------------------------
            # STORE FEATURES
            # --------------------------------------------------

            feature_row = MatchFeatures(
                match_id=match.match_id,

                winner_pre_elo=winner_pre_elo,
                loser_pre_elo=loser_pre_elo,

                winner_surface_elo=winner_surface_elo,
                loser_surface_elo=loser_surface_elo,

                winner_recent_form_5=winner_recent_form,
                loser_recent_form_5=loser_recent_form,

                winner_surface_winrate=winner_surface_winrate,
                loser_surface_winrate=loser_surface_winrate,

                winner_matches_last_7d=winner_matches_last_7d,
                loser_matches_last_7d=loser_matches_last_7d,

                winner_minutes_last_14d=winner_minutes_last_14d,
                loser_minutes_last_14d=loser_minutes_last_14d,

                winner_days_since_last_match=winner_days_since_last_match,
                loser_days_since_last_match=loser_days_since_last_match,

                winner_h2h=winner_h2h,
                loser_h2h=loser_h2h
            )

            feature_rows.append(feature_row)

            # --------------------------------------------------
            # POST-MATCH STATE UPDATE
            # --------------------------------------------------

            new_winner_elo = update_elo(
                winner_pre_elo,
                loser_pre_elo,
                1
            )

            new_loser_elo = update_elo(
                loser_pre_elo,
                winner_pre_elo,
                0
            )

            player_elo[winner_id] = new_winner_elo
            player_elo[loser_id] = new_loser_elo

            new_winner_surface_elo = update_elo(
                winner_surface_elo,
                loser_surface_elo,
                1
            )

            new_loser_surface_elo = update_elo(
                loser_surface_elo,
                winner_surface_elo,
                0
            )

            surface_elo[winner_id][surface] = (
                new_winner_surface_elo
            )

            surface_elo[loser_id][surface] = (
                new_loser_surface_elo
            )
            if processed < 20:
                print("minutes =", getattr(match, "minutes", "NO_ATTR"))
            minutes = None

            if hasattr(match, "minutes"):
                minutes = match.minutes
            if processed < 20:
                print(
                current_date,
                winner_id,
                loser_id,
                minutes
            )
            if processed >= 20:
                break
            recent_results[winner_id].append(
                (current_date, 1, surface, minutes)
            )

            recent_results[loser_id].append(
                (current_date, 0, surface, minutes)
            )

            surface_results[winner_id].append(
                (surface, 1)
            )

            surface_results[loser_id].append(
                (surface, 0)
            )

            h2h[
                (winner_id,loser_id)
            ] += 1

            processed += 1

            if processed % 5000 == 0:
                print(f"Processed: {processed}")

        print("Saving feature rows...")

        db.bulk_save_objects(feature_rows)

        db.commit()

        print("\nFeature generation completed!")
        print(f"Rows inserted: {len(feature_rows)}")

    except Exception as e:
        db.rollback()

        print("\nError occurred:")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    main()