# -*- coding: utf-8 -*-
"""
Created on Thu May 28 23:03:32 2026

@author: AUM
"""

import pandas as pd

from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.db.models.match import Match
from app.db.models.player import Player
from app.db.models.tournament import Tournament


CSV_PATH = "data/all_combined_engineered_symmetric_org.csv"


def load_lookup_tables(db):
    players = db.query(Player).all()

    player_lookup = {
        player.player_name: player.player_id
        for player in players
    }

    tournaments = db.query(Tournament).all()

    tournament_lookup = {
        (
            tournament.tournament_name,
            tournament.surface,
            tournament.level
        ): tournament.tournament_id
        for tournament in tournaments
    }

    return player_lookup, tournament_lookup


def safe_int(value):
    if pd.isna(value):
        return None

    try:
        return int(value)
    except:
        return None


def safe_float(value):
    if pd.isna(value):
        return None

    try:
        return float(value)
    except:
        return None


def main():
    print("Loading dataset...")
    df = pd.read_csv(CSV_PATH)

    print(f"Rows found: {len(df)}")

    db = SessionLocal()

    inserted = 0
    skipped = 0

    try:
        player_lookup, tournament_lookup = load_lookup_tables(db)

        matches_to_insert = []

        for _, row in df.iterrows():

            winner_name = row.get("winner_name")
            loser_name = row.get("loser_name")

            if pd.isna(winner_name) or pd.isna(loser_name):
                skipped += 1
                continue

            winner_id = player_lookup.get(winner_name)
            loser_id = player_lookup.get(loser_name)

            if winner_id is None or loser_id is None:
                skipped += 1
                continue

            tournament_key = (
                row.get("tourney_name"),
                row.get("surface"),
                row.get("tourney_level")
            )

            tournament_id = tournament_lookup.get(tournament_key)

            if tournament_id is None:
                skipped += 1
                continue

            match = Match(
                tournament_id=tournament_id,

                match_date=row.get("tourney_date"),

                round=row.get("round"),

                best_of=safe_int(row.get("best_of")),

                winner_id=winner_id,
                loser_id=loser_id,

                winner_rank=safe_int(row.get("winner_rank")),
                loser_rank=safe_int(row.get("loser_rank")),

                winner_elo=safe_float(row.get("winner_elo")),
                loser_elo=safe_float(row.get("loser_elo")),

                winner_surface_elo=safe_float(
                    row.get("winner_surface_elo")
                ),

                loser_surface_elo=safe_float(
                    row.get("loser_surface_elo")
                ),

                winner_recent_form=safe_float(
                    row.get("winner_recent_form")
                ),

                loser_recent_form=safe_float(
                    row.get("loser_recent_form")
                ),

                winner_surface_winrate=safe_float(
                    row.get("winner_surface_winrate")
                ),

                loser_surface_winrate=safe_float(
                    row.get("loser_surface_winrate")
                ),

                winner_fitness=safe_float(
                    row.get("winner_fitness")
                ),

                loser_fitness=safe_float(
                    row.get("loser_fitness")
                )
            )

            matches_to_insert.append(match)

        print(f"Prepared matches: {len(matches_to_insert)}")

        db.bulk_save_objects(matches_to_insert)

        db.commit()

        inserted = len(matches_to_insert)

    except IntegrityError:
        db.rollback()
        print("Integrity error occurred.")

    finally:
        db.close()

    print("\nImport completed.")
    print(f"Inserted matches : {inserted}")
    print(f"Skipped matches  : {skipped}")


if __name__ == "__main__":
    main()