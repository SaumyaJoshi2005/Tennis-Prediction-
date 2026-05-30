# -*- coding: utf-8 -*-
"""
Created on Fri May 29 02:06:02 2026

@author: AUM
"""

import pandas as pd

from sqlalchemy import text

from app.db.session import engine


OUTPUT_CSV = "data/training_dataset.csv"


QUERY = """
SELECT
    m.match_id,
    m.match_date,
    t.surface,
    t.level,
    m.best_of,
    m.round,

    wp.player_name AS winner_name,
    lp.player_name AS loser_name,

    mf.winner_pre_elo,
    mf.loser_pre_elo,

    mf.winner_surface_elo,
    mf.loser_surface_elo,

    mf.winner_recent_form_5,
    mf.loser_recent_form_5,

    mf.winner_surface_winrate,
    mf.loser_surface_winrate,

    mf.winner_matches_last_7d,
    mf.loser_matches_last_7d,

    mf.winner_minutes_last_14d,
    mf.loser_minutes_last_14d,

    mf.winner_days_since_last_match,
    mf.loser_days_since_last_match,

    mf.winner_h2h,
    mf.loser_h2h

FROM matches m

JOIN match_features mf
ON m.match_id = mf.match_id

JOIN players wp
ON m.winner_id = wp.player_id

JOIN players lp
ON m.loser_id = lp.player_id

JOIN tournaments t
ON m.tournament_id = t.tournament_id

ORDER BY m.match_date ASC
"""


def build_symmetric_rows(df: pd.DataFrame):

    rows = []

    for _, row in df.iterrows():

        # --------------------------------------------------
        # ORIGINAL ROW
        # winner -> player1
        # loser  -> player2
        # target = 1
        # --------------------------------------------------

        row1 = {
            "match_id": row["match_id"],
            "match_date": row["match_date"],

            "surface": row["surface"],
            "level": row["level"],
            "best_of": row["best_of"],
            "round": row["round"],

            "player1_name": row["winner_name"],
            "player2_name": row["loser_name"],

            "player1_elo": row["winner_pre_elo"],
            "player2_elo": row["loser_pre_elo"],

            "player1_surface_elo": row["winner_surface_elo"],
            "player2_surface_elo": row["loser_surface_elo"],

            "player1_recent_form": row["winner_recent_form_5"],
            "player2_recent_form": row["loser_recent_form_5"],

            "player1_surface_winrate": (
                row["winner_surface_winrate"]
            ),

            "player2_surface_winrate": (
                row["loser_surface_winrate"]
            ),

            "player1_matches_last_7d": (
                row["winner_matches_last_7d"]
            ),

            "player2_matches_last_7d": (
                row["loser_matches_last_7d"]
            ),

            "player1_minutes_last_14d": (
                row["winner_minutes_last_14d"]
            ),

            "player2_minutes_last_14d": (
                row["loser_minutes_last_14d"]
            ),

            "player1_days_since_last_match": (
                row["winner_days_since_last_match"]
            ),

            "player2_days_since_last_match": (
                row["loser_days_since_last_match"]
            ),

            "player1_h2h": row["winner_h2h"],
            "player2_h2h": row["loser_h2h"],

            "target": 1
        }

        rows.append(row1)

        # --------------------------------------------------
        # MIRRORED ROW
        # loser  -> player1
        # winner -> player2
        # target = 0
        # --------------------------------------------------

        row2 = {
            "match_id": row["match_id"],
            "match_date": row["match_date"],

            "surface": row["surface"],
            "level": row["level"],
            "best_of": row["best_of"],
            "round": row["round"],

            "player1_name": row["loser_name"],
            "player2_name": row["winner_name"],

            "player1_elo": row["loser_pre_elo"],
            "player2_elo": row["winner_pre_elo"],

            "player1_surface_elo": row["loser_surface_elo"],
            "player2_surface_elo": row["winner_surface_elo"],

            "player1_recent_form": row["loser_recent_form_5"],
            "player2_recent_form": row["winner_recent_form_5"],

            "player1_surface_winrate": (
                row["loser_surface_winrate"]
            ),

            "player2_surface_winrate": (
                row["winner_surface_winrate"]
            ),

            "player1_matches_last_7d": (
                row["loser_matches_last_7d"]
            ),

            "player2_matches_last_7d": (
                row["winner_matches_last_7d"]
            ),

            "player1_minutes_last_14d": (
                row["loser_minutes_last_14d"]
            ),

            "player2_minutes_last_14d": (
                row["winner_minutes_last_14d"]
            ),

            "player1_days_since_last_match": (
                row["loser_days_since_last_match"]
            ),

            "player2_days_since_last_match": (
                row["winner_days_since_last_match"]
            ),

            "player1_h2h": row["loser_h2h"],
            "player2_h2h": row["winner_h2h"],

            "target": 0
        }

        rows.append(row2)

    return pd.DataFrame(rows)


def create_diff_features(df: pd.DataFrame):

    df["elo_diff"] = (
        df["player1_elo"]
        - df["player2_elo"]
    )

    df["surface_elo_diff"] = (
        df["player1_surface_elo"]
        - df["player2_surface_elo"]
    )

    df["recent_form_diff"] = (
        df["player1_recent_form"]
        - df["player2_recent_form"]
    )

    df["surface_winrate_diff"] = (
        df["player1_surface_winrate"]
        - df["player2_surface_winrate"]
    )

    df["matches_last_7d_diff"] = (
        df["player1_matches_last_7d"]
        - df["player2_matches_last_7d"]
    )

    df["minutes_last_14d_diff"] = (
        df["player1_minutes_last_14d"]
        - df["player2_minutes_last_14d"]
    )

    df["days_since_last_match_diff"] = (
        df["player1_days_since_last_match"]
        - df["player2_days_since_last_match"]
    )

    df["h2h_diff"] = (
        df["player1_h2h"]
        - df["player2_h2h"]
    )

    return df


def main():

    print("Loading relational training data...")

    with engine.connect() as conn:
        df = pd.read_sql(
            text(QUERY),
            conn
        )

    print(f"Rows loaded: {len(df)}")

    print("Building symmetric rows...")

    symmetric_df = build_symmetric_rows(df)

    print(f"Symmetric rows: {len(symmetric_df)}")

    print("Generating diff features...")

    symmetric_df = create_diff_features(
        symmetric_df
    )

    print("Saving training dataset...")

    symmetric_df.to_csv(
        OUTPUT_CSV,
        index=False
    )

    print("\nTraining dataset built successfully!")
    print(f"Saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()