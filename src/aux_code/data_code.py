# -*- coding: utf-8 -*-
"""
Created on Thu May 28 00:38:14 2026

@author: AUM
"""

# %%

import pandas as pd
import numpy as np

INPUT_CSV = r"C:\Users\AUM\Desktop\Proj\prediction_model\Data\all_combined_engineered_symmetric_org.csv"
OUTPUT_CSV = r"C:\Users\AUM\Desktop\Proj\prediction_model\Data\all_combined_engineered_symmetric.csv"


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    print("Initial shape:", df.shape)

    # --------------------------------------------------
    # Remove accidental index columns
    # --------------------------------------------------
    drop_cols = [c for c in df.columns if "unnamed" in c.lower() or c.lower() == "index"]
    df.drop(columns=drop_cols, inplace=True, errors="ignore")

    # --------------------------------------------------
    # Standardize surface labels
    # --------------------------------------------------
    if "surface" in df.columns:
        df["surface"] = (
            df["surface"]
            .astype(str)
            .str.strip()
            .str.lower()
            .replace({
                "hardcourt": "hard",
                "hard court": "hard",
                "clay court": "clay",
                "grass court": "grass"
            })
        )

    # --------------------------------------------------
    # Parse dates
    # --------------------------------------------------
    if "tourney_date" in df.columns:
        df["tourney_date"] = pd.to_datetime(df["tourney_date"], errors="coerce")

    # --------------------------------------------------
    # Remove duplicate matches
    # --------------------------------------------------
    #duplicate_subset = [
    #   c for c in [
    #        "tourney_date",
    #        "player1_name",
    #        "player2_name",
    #        "surface"
    #    ] if c in df.columns
    #]

    #if duplicate_subset:
    #   before = len(df)
    #    df.drop_duplicates(subset=duplicate_subset, inplace=True)
    #    after = len(df)
    #    print(f"Removed duplicates: {before - after}")

    # --------------------------------------------------
    # Replace fake zeros with NaN
    # --------------------------------------------------
    fake_zero_cols = [
        "minutes",
        "minutes_last_14d",
        "player1_minutes_last_14d",
        "player2_minutes_last_14d"
    ]

    for col in fake_zero_cols:
        if col in df.columns:
            df.loc[df[col] == 0, col] = np.nan

    # --------------------------------------------------
    # Remove impossible values
    # --------------------------------------------------
    checks = {
        "player1_age": (14, 50),
        "player2_age": (14, 50),
        "player1_height": (140, 230),
        "player2_height": (140, 230),
        "player1_rank": (1, 5000),
        "player2_rank": (1, 5000),
        "player1_elo": (500, 3000),
        "player2_elo": (500, 3000),
        "player1_fitness": (0, 100),
        "player2_fitness": (0, 100)
    }

    for col, (low, high) in checks.items():
        if col in df.columns:
            df.loc[(df[col] < low) | (df[col] > high), col] = np.nan

    # --------------------------------------------------
    # Create diff features consistently
    # diff = player1 - player2
    # --------------------------------------------------
    feature_pairs = [
        ("rank", "rank_diff"),
        ("age", "age_diff"),
        ("height", "height_diff"),
        ("elo", "elo_diff"),
        ("surface_elo", "surface_elo_diff"),
        ("fitness", "fitness_diff"),
        ("recent_form", "recent_form_diff"),
        ("surface_winrate", "surface_winrate_diff")
    ]

    for base, diff_col in feature_pairs:
        p1 = f"player1_{base}"
        p2 = f"player2_{base}"

        if p1 in df.columns and p2 in df.columns:
            df[diff_col] = df[p1] - df[p2]

    # --------------------------------------------------
    # Surface one-hot encoding
    # --------------------------------------------------
    if "surface" in df.columns:
        surfaces = ["clay", "hard", "grass", "carpet"]

        for s in surfaces:
            df[f"is_{s}"] = (df["surface"] == s).astype(int)

    # --------------------------------------------------
    # Tournament level encoding
    # --------------------------------------------------
    if "tourney_level" in df.columns:
        level_map = {
            "G": 5,
            "M": 4,
            "A": 3,
            "B": 2,
            "C": 1
        }

        df["tourney_importance"] = df["tourney_level"].map(level_map)

    # --------------------------------------------------
    # Round encoding
    # --------------------------------------------------
    if "round" in df.columns:
        round_map = {
            "R128": 1,
            "R64": 2,
            "R32": 3,
            "R16": 4,
            "QF": 5,
            "SF": 6,
            "F": 7
        }

        df["round_weight"] = df["round"].map(round_map)

    # --------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------
    if "tourney_date" in df.columns:
        df.sort_values("tourney_date", inplace=True)

    # --------------------------------------------------
    # Optional: remove raw winner/loser columns
    # --------------------------------------------------
    remove_raw_cols = [
        c for c in df.columns
        if c.startswith("winner_") or c.startswith("loser_")
    ]

    df.drop(columns=remove_raw_cols, inplace=True, errors="ignore")

    # --------------------------------------------------
    # Reset index
    # --------------------------------------------------
    df.reset_index(drop=True, inplace=True)

    print("Final shape:", df.shape)

    return df


def main():
    print("Loading dataset...")
    df = pd.read_csv(INPUT_CSV)

    cleaned = clean_dataset(df)

    print("Saving cleaned dataset...")
    cleaned.to_csv(OUTPUT_CSV, index=False)

    print(f"Saved cleaned dataset to: {OUTPUT_CSV}")

    print("\nMissing values summary:")
    print(cleaned.isnull().sum().sort_values(ascending=False).head(20))


if __name__ == "__main__":
    main()
