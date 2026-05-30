# -*- coding: utf-8 -*-
"""
Created on Thu May 28 23:06:39 2026

@author: AUM
"""


from collections import defaultdict

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.match import Match

from app.db.models.player import Player
from app.db.models.tournament import Tournament

INITIAL_ELO = 1500
K_FACTOR = 32


def expected_score(rating_a, rating_b):
    return 1 / (1 + (10 ** ((rating_b - rating_a) / 400)))


def update_elo(winner_elo, loser_elo):
    expected_winner = expected_score(winner_elo, loser_elo)
    expected_loser = expected_score(loser_elo, winner_elo)

    new_winner_elo = winner_elo + K_FACTOR * (1 - expected_winner)
    new_loser_elo = loser_elo + K_FACTOR * (0 - expected_loser)

    return new_winner_elo, new_loser_elo


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

        updated = 0

        for match in matches:

            winner_id = match.winner_id
            loser_id = match.loser_id

            if winner_id is None or loser_id is None:
                continue

            current_winner_elo = player_elo[winner_id]
            current_loser_elo = player_elo[loser_id]

            # Store PRE-match ratings
            match.winner_elo = round(current_winner_elo, 2)
            match.loser_elo = round(current_loser_elo, 2)

            # Calculate updated ratings
            new_winner_elo, new_loser_elo = update_elo(
                current_winner_elo,
                current_loser_elo
            )

            # Update in-memory ratings
            player_elo[winner_id] = new_winner_elo
            player_elo[loser_id] = new_loser_elo

            updated += 1

            if updated % 5000 == 0:
                print(f"Processed: {updated}")

        print("Saving updated Elo ratings...")

        db.commit()

        print("\nElo generation completed successfully!")
        print(f"Matches updated: {updated}")

    except Exception as e:
        db.rollback()
        print("Error occurred:")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    main()