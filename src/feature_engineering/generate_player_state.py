# -*- coding: utf-8 -*-
"""
Created on Sun May 31 18:09:46 2026

@author: AUM
"""

from collections import defaultdict

from sqlalchemy.orm import Session

from app.db.session import SessionLocal

from app.db.models.match import Match
from app.db.models.tournament import Tournament
from app.db.models.player_state import (
    PlayerState
)

from src.feature_engineering.feature_utils import (
    INITIAL_ELO,
    update_elo,
    compute_recent_form,
    compute_surface_winrate,
    compute_matches_last_7d,
    compute_days_since_last_match
)


def main():

    db: Session = SessionLocal()

    try:

        print(
            "Loading matches chronologically..."
        )

        matches = (
            db.query(Match)
            .order_by(
                Match.match_date.asc()
            )
            .all()
        )

        print(
            f"Matches loaded: {len(matches)}"
        )

        player_elo = defaultdict(
            lambda: INITIAL_ELO
        )

        surface_elo = defaultdict(
            lambda: defaultdict(
                lambda: INITIAL_ELO
            )
        )

        recent_results = defaultdict(list)

        surface_results = defaultdict(list)

        for match in matches:

            if (
                match.winner_id is None
                or match.loser_id is None
                or match.match_date is None
            ):
                continue

            winner_id = match.winner_id
            loser_id = match.loser_id

            current_date = (
                match.match_date
            )

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
                surface = (
                    tournament.surface
                )

            winner_pre_elo = (
                player_elo[winner_id]
            )

            loser_pre_elo = (
                player_elo[loser_id]
            )

            winner_surface_elo = (
                surface_elo[winner_id][surface]
            )

            loser_surface_elo = (
                surface_elo[loser_id][surface]
            )

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

            player_elo[winner_id] = (
                new_winner_elo
            )

            player_elo[loser_id] = (
                new_loser_elo
            )

            new_winner_surface_elo = (
                update_elo(
                    winner_surface_elo,
                    loser_surface_elo,
                    1
                )
            )

            new_loser_surface_elo = (
                update_elo(
                    loser_surface_elo,
                    winner_surface_elo,
                    0
                )
            )

            surface_elo[winner_id][surface] = (
                new_winner_surface_elo
            )

            surface_elo[loser_id][surface] = (
                new_loser_surface_elo
            )

            recent_results[winner_id].append(
                (
                    current_date,
                    1,
                    surface,
                    None
                )
            )

            recent_results[loser_id].append(
                (
                    current_date,
                    0,
                    surface,
                    None
                )
            )

            surface_results[winner_id].append(
                (
                    surface,
                    1
                )
            )

            surface_results[loser_id].append(
                (
                    surface,
                    0
                )
            )

        print(
            "Clearing old player states..."
        )

        db.query(PlayerState).delete()

        db.commit()

        rows = []

        for player_id in player_elo:

            history = (
                recent_results[player_id]
            )

            if len(history) == 0:
                continue

            last_match_date = (
                history[-1][0]
            )

            rows.append(
                PlayerState(
                    player_id=player_id,

                    elo=player_elo[player_id],

                    clay_elo=surface_elo[
                        player_id
                    ]["Clay"],

                    hard_elo=surface_elo[
                        player_id
                    ]["Hard"],

                    grass_elo=surface_elo[
                        player_id
                    ]["Grass"],

                    recent_form=
                    compute_recent_form(
                        history
                    ),

                    clay_winrate=
                    compute_surface_winrate(
                        surface_results[
                            player_id
                        ],
                        "Clay"
                    ),

                    hard_winrate=
                    compute_surface_winrate(
                        surface_results[
                            player_id
                        ],
                        "Hard"
                    ),

                    grass_winrate=
                    compute_surface_winrate(
                        surface_results[
                            player_id
                        ],
                        "Grass"
                    ),

                    matches_last_7d=
                    compute_matches_last_7d(
                        history,
                        last_match_date
                    ),

                    days_since_last_match=
                    compute_days_since_last_match(
                        history,
                        last_match_date
                    ),

                    total_matches=
                    len(history),

                    last_match_date=
                    last_match_date
                )
            )

        print(
            f"Saving {len(rows)} "
            "player states..."
        )

        db.bulk_save_objects(rows)

        db.commit()

        print(
            "\nPlayer state generation completed!"
        )

    except Exception as e:

        db.rollback()

        print(
            "\nError occurred:"
        )

        print(e)

    finally:

        db.close()


if __name__ == "__main__":
    main()