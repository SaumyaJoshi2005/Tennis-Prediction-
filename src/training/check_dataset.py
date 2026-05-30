# -*- coding: utf-8 -*-
"""
Created on Fri May 29 02:08:49 2026

@author: AUM
"""

import pandas as pd


DATA_PATH = "data/training_dataset.csv"


def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():

    print("Loading training dataset...")

    df = pd.read_csv(DATA_PATH)

    print("\nDataset loaded successfully!")
    print(f"Shape: {df.shape}")

    # --------------------------------------------------
    # BASIC INFO
    # --------------------------------------------------

    print_section("BASIC DATASET INFO")

    print(df.info())

    # --------------------------------------------------
    # TARGET DISTRIBUTION
    # --------------------------------------------------

    print_section("TARGET DISTRIBUTION")

    target_counts = df["target"].value_counts()

    print(target_counts)

    print("\nTarget percentages:")

    print(
        (
            target_counts / len(df)
        ) * 100
    )

    # --------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------

    print_section("MISSING VALUES")

    missing = (
        df.isnull()
        .sum()
        .sort_values(ascending=False)
    )

    missing = missing[missing > 0]

    if len(missing) == 0:
        print("No missing values found.")

    else:
        print(missing)

    # --------------------------------------------------
    # DUPLICATES
    # --------------------------------------------------

    print_section("DUPLICATE ROWS")

    duplicates = df.duplicated().sum()

    print(f"Duplicate rows: {duplicates}")

    # --------------------------------------------------
    # DATE RANGE
    # --------------------------------------------------

    print_section("DATE RANGE")

    df["match_date"] = pd.to_datetime(
        df["match_date"]
    )

    print(
        f"Min date: {df['match_date'].min()}"
    )

    print(
        f"Max date: {df['match_date'].max()}"
    )

    # --------------------------------------------------
    # NUMERIC FEATURES
    # --------------------------------------------------

    print_section("NUMERIC FEATURE SUMMARY")

    numeric_cols = df.select_dtypes(
        include=["number"]
    ).columns

    print(
        df[numeric_cols]
        .describe()
        .T
    )

    # --------------------------------------------------
    # FEATURE CORRELATIONS
    # --------------------------------------------------

    print_section("FEATURE CORRELATIONS")

    corr = (
        df[numeric_cols]
        .corr()["target"]
        .sort_values(ascending=False)
    )

    print(corr)

    # --------------------------------------------------
    # CHECK FOR EXTREME VALUES
    # --------------------------------------------------

    print_section("EXTREME VALUE CHECK")

    for col in numeric_cols:

        if col == "target":
            continue

        max_val = df[col].max()
        min_val = df[col].min()

        print(
            f"{col}: "
            f"min={min_val}, "
            f"max={max_val}"
        )

    # --------------------------------------------------
    # LEAKAGE CHECK
    # --------------------------------------------------

    print_section("BASIC LEAKAGE CHECK")

    suspicious = []

    for col in numeric_cols:

        if col == "target":
            continue

        corr_value = abs(
            df[col].corr(df["target"])
        )

        if corr_value > 0.95:
            suspicious.append(
                (col, corr_value)
            )

    if len(suspicious) == 0:
        print(
            "No obvious leakage columns detected."
        )

    else:
        print(
            "Potential leakage features found:"
        )

        for col, val in suspicious:
            print(f"{col}: {val}")

    # --------------------------------------------------
    # SAMPLE ROWS
    # --------------------------------------------------

    print_section("SAMPLE ROWS")

    print(df.head())

    print("\nDataset check completed successfully!")


if __name__ == "__main__":
    main()