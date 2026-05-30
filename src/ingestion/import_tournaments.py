import pandas as pd

from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.db.models.tournament import Tournament


CSV_PATH = "data/all_combined_engineered_symmetric_org.csv"


def extract_tournaments(df: pd.DataFrame):
    required_cols = [
        "tourney_name",
        "surface",
        "tourney_level"
    ]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    tournaments = (
        df[
            ["tourney_name", "surface", "tourney_level"]
        ]
        .dropna(subset=["tourney_name"])
        .drop_duplicates()
    )

    return tournaments


def main():
    print("Loading dataset...")
    df = pd.read_csv(CSV_PATH)

    tournaments_df = extract_tournaments(df)

    print(f"Unique tournaments found: {len(tournaments_df)}")

    db = SessionLocal()

    inserted = 0
    skipped = 0

    try:
        existing_tournaments = {
            (
                row[0],
                row[1],
                row[2]
            )
            for row in db.query(
                Tournament.tournament_name,
                Tournament.surface,
                Tournament.level
            ).all()
        }

        new_tournaments = []

        for _, row in tournaments_df.iterrows():

            key = (
                row["tourney_name"],
                row["surface"],
                row["tourney_level"]
            )

            if key in existing_tournaments:
                skipped += 1
                continue

            tournament = Tournament(
                tournament_name=row["tourney_name"],
                surface=row["surface"],
                level=row["tourney_level"]
            )

            new_tournaments.append(tournament)

        db.bulk_save_objects(new_tournaments)

        db.commit()

        inserted = len(new_tournaments)

    except IntegrityError:
        db.rollback()
        print("Integrity error occurred.")

    finally:
        db.close()

    print("\nImport completed.")
    print(f"Inserted tournaments : {inserted}")
    print(f"Skipped tournaments  : {skipped}")


if __name__ == "__main__":
    main()