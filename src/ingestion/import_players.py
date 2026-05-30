# -*- coding: utf-8 -*-
"""
Created on Thu May 28 22:47:55 2026

@author: AUM
"""

import pandas as pd

from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.db.models.player import Player


CSV_PATH = "data/all_combined_engineered_symmetric_org.csv"


def extract_players(df: pd.DataFrame):
    player1 = []

    if "winner_name" in df.columns:
        player1 = df["winner_name"].dropna().astype(str).tolist()

    player2 = []

    if "loser_name" in df.columns:
        player2 = df["loser_name"].dropna().astype(str).tolist()

    all_players = player1 + player2

    unique_players = sorted(set(all_players))

    return unique_players

def main():
    print("Loading dataset...")
    df = pd.read_csv(CSV_PATH)

    unique_players = extract_players(df)

    print(f"Unique players found: {len(unique_players)}")

    db = SessionLocal()

    inserted = 0
    skipped = 0

    try:
        existing_players = {
            row[0]
            for row in db.query(Player.player_name).all()
        }

        new_players = []

        for name in unique_players:
            if name in existing_players:
                skipped += 1
                continue

            player = Player(
                player_name=name
            )

            new_players.append(player)

        db.bulk_save_objects(new_players)

        db.commit()

        inserted = len(new_players)

    except IntegrityError:
        db.rollback()
        print("Integrity error occurred.")

    finally:
        db.close()

    print("\nImport completed.")
    print(f"Inserted players : {inserted}")
    print(f"Skipped players  : {skipped}")


if __name__ == "__main__":
    main()