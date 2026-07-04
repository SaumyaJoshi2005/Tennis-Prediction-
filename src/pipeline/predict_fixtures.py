# -*- coding: utf-8 -*-
"""
Created on Sun May 31 18:47:41 2026

@author: AUM
"""

from app.db.session import SessionLocal

from app.db.models.fixture import Fixture
from app.db.models.player import Player

from src.inference.predict_players import (
    predict_players
)
from src.utils.fixture_lifecycle import (
    mark_stale_fixtures,
    prediction_candidate_filter
)


def main():

    db = SessionLocal()

    try:

        stale_count = mark_stale_fixtures(db)

        fixtures = (
            db.query(Fixture)
            .filter(prediction_candidate_filter())
            .all()
        )

        print(
            f"Fixtures found: {len(fixtures)}"
        )
        print(
            f"Stale fixtures marked: {stale_count}"
        )

        for fixture in fixtures:

            player_a = (
                db.query(Player)
                .filter(
                    Player.player_id
                    == fixture.player_a_id
                )
                .first()
            )

            player_b = (
                db.query(Player)
                .filter(
                    Player.player_id
                    == fixture.player_b_id
                )
                .first()
            )

            probability = predict_players(
                player_a.player_name,
                player_b.player_name,
                fixture.surface
            )

            fixture.player_a_win_probability = float(
                probability
            )

            fixture.winner_predicted = (
                player_a.player_name
                if probability >= 0.5
                else player_b.player_name
            )

            fixture.status = "PREDICTED"

        db.commit()

        print(
            "Predictions completed."
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()
