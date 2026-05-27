"""
seed_players.py — Populate MySQL with player data from CSV
===========================================================
Run this ONCE after docker-compose up to seed the players table.
The /predict endpoint needs players in the DB to work.

Usage
-----
  python seed_players.py
  python seed_players.py --csv "C:/path/to/other.csv"
  python seed_players.py --limit 500   # seed top 500 players by rank only
"""

import os
import argparse
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# ── Config ────────────────────────────────────────────────────────────────────
CSV_PATH = r"C:\Users\AUM\Desktop\Tennis_data\all_combined_engineered_symmetric.csv"

# Reads same env vars as the API — override if running outside Docker
DB_USER     = os.getenv("DB_USER",     "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tennis123")
DB_HOST     = os.getenv("DB_HOST",     "127.0.0.1")   # localhost when running on Windows
DB_PORT     = os.getenv("DB_PORT",     "3307")         # change to 3307 if you remapped the port
DB_NAME     = os.getenv("DB_NAME",     "tennis_db")


# ── Build player table from CSV ───────────────────────────────────────────────
def build_player_table(csv_path: str) -> pd.DataFrame:
    """
    Extract one row per player with their most recent stats.
    Uses both winner and loser appearances to cover all players.
    """
    print(f"  Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    df['date_parsed'] = pd.to_datetime(df['tourney_date'], errors='coerce')
    df = df.sort_values('date_parsed')

    # Winner rows — player1 columns hold winner stats in symmetric dataset
    w = df[['winner_name', 'winner_rank', 'winner_age', 'winner_ht',
            'winner_fitness', 'player1_elo', 'player1_surface_elo',
            'player1_recent_winrate', 'player1_surface_winrate']].copy()
    w.columns = ['name', 'rank', 'age', 'height', 'fitness',
                 'elo', 'surface_elo', 'recent_form', 'surface_winrate']

    # Loser rows — player2 columns hold loser stats
    l = df[['loser_name', 'loser_rank', 'loser_age', 'loser_ht',
            'loser_fitness', 'player2_elo', 'player2_surface_elo',
            'player2_recent_winrate', 'player2_surface_winrate']].copy()
    l.columns = ['name', 'rank', 'age', 'height', 'fitness',
                 'elo', 'surface_elo', 'recent_form', 'surface_winrate']

    # Combine — take the most recent row per player (CSV is sorted by date)
    players = pd.concat([w, l]).groupby('name').last().reset_index()

    # Fill any remaining nulls with safe defaults
    players['rank']           = players['rank'].fillna(999).astype(int)
    players['age']            = players['age'].fillna(25.0).round(1)
    players['height']         = players['height'].fillna(185.0)
    players['fitness']        = players['fitness'].fillna(0.5)
    players['elo']            = players['elo'].fillna(1500.0).round(4)
    players['surface_elo']    = players['surface_elo'].fillna(1500.0).round(4)
    players['recent_form']    = players['recent_form'].fillna(0.5).round(4)
    players['surface_winrate']= players['surface_winrate'].fillna(0.5).round(4)

    print(f"  Players extracted: {len(players):,}")
    return players


# ── Seed database ─────────────────────────────────────────────────────────────
def seed(csv_path: str, limit: int = None):
    players = build_player_table(csv_path)

    # Optionally limit to top N players by rank (useful for testing)
    if limit:
        players = players.nsmallest(limit, 'rank')
        print(f"  Limiting to top {limit} players by rank")

    # Connect to MySQL
    db_url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(f"\n  Connecting to: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("  ✔ Connected to MySQL")
    except Exception as e:
        print(f"  ✘ Connection failed: {e}")
        print("\n  Troubleshooting:")
        print("  1. Is docker-compose up and running?")
        print("  2. Did you remap MySQL to port 3307? Set DB_PORT=3307")
        print("     e.g.  DB_PORT=3307 python seed_players.py")
        return

    # Upsert — insert new players, update existing ones
    # Uses pandas to_sql with replace logic via temp table approach
    print(f"\n  Seeding {len(players):,} players …")

    inserted = 0
    updated  = 0
    errors   = 0

    with engine.connect() as conn:
        for _, row in players.iterrows():
            try:
                # Check if player exists
                exists = conn.execute(
                    text("SELECT id FROM players WHERE name = :name"),
                    {"name": row['name']}
                ).fetchone()

                if exists:
                    conn.execute(text("""
                        UPDATE players SET
                            `rank`           = :rank,
                            age            = :age,
                            height         = :height,
                            fitness        = :fitness,
                            elo            = :elo,
                            surface_elo    = :surface_elo,
                            recent_form    = :recent_form,
                            surface_winrate= :surface_winrate
                        WHERE name = :name
                    """), row.to_dict())
                    updated += 1
                else:
                    conn.execute(text("""
                        INSERT INTO players
                            (name, `rank`, age, height, fitness,
                             elo, surface_elo, recent_form, surface_winrate)
                        VALUES
                            (:name, :rank, :age, :height, :fitness,
                             :elo, :surface_elo, :recent_form, :surface_winrate)
                    """), row.to_dict())
                    inserted += 1

                # Commit every 100 rows
                if (inserted + updated) % 100 == 0:
                    conn.commit()
                    print(f"    … {inserted + updated:,} / {len(players):,}", end='\r')

            except Exception as e:
                errors += 1
                if errors <= 3:   # only print first 3 errors
                    print(f"\n  Warning on '{row['name']}': {e}")

        conn.commit()  # final commit

    print(f"\n  ✔ Done.")
    print(f"    Inserted : {inserted:,}")
    print(f"    Updated  : {updated:,}")
    print(f"    Errors   : {errors}")

    # Quick verification
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM players")).scalar()
        sample = conn.execute(
            text("SELECT name, `rank`, elo FROM players ORDER BY `rank` LIMIT 5")
        ).fetchall()

    print(f"\n  Total players in DB : {total:,}")
    print("  Top 5 by rank:")
    for row in sample:
        print(f"    {row[0]:<30} `rank`={row[1]}  elo={row[2]:.1f}")


# ── Main ──────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="Seed MySQL players table from CSV")
    p.add_argument("--csv",   default=CSV_PATH, help="Path to engineered symmetric CSV")
    p.add_argument("--limit", default=None, type=int,
                   help="Only seed top N players by rank (useful for testing)")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print("━" * 50)
    print("  TENNIS DB SEEDER")
    print("━" * 50)
    seed(args.csv, args.limit)
    print("━" * 50)
