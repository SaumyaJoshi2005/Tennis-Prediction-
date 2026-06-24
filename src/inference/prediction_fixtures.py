# -*- coding: utf-8 -*-

from app.db.session import SessionLocal

from app.db.models.fixture import (
    Fixture
)

from app.db.models.player import (
    Player
)

from src.inference.predict_players import (
    predict_players
)


def predict_all_fixtures():

    db = SessionLocal()

    predicted = 0
    failed = 0

    try:

        fixtures = (
            db.query(Fixture)
            .filter(
                Fixture.status == "SCHEDULED"
            )
            .all()
        )

        print(
            f"Fixtures found: "
            f"{len(fixtures)}"
        )

        for fixture in fixtures:

            try:

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

                if (
                    player_a is None
                    or
                    player_b is None
                ):
                    failed += 1
                    continue

                surface = (
                    fixture.surface
                    or "Hard"
                )

                probability = (
                    predict_players(
                        player_a.player_name,
                        player_b.player_name,
                        surface
                    )
                )

                fixture.player_a_win_probability = (
                    probability
                )

                fixture.winner_predicted = (
                    player_a.player_name
                    if probability >= 0.5
                    else player_b.player_name
                )

                fixture.status = (
                    "PREDICTED"
                )

                predicted += 1

            except Exception as e:

                print(
                    f"FAILED: "
                    f"{fixture.fixture_id}"
                )

                print(e)

                failed += 1

        db.commit()

        print()
        print("========== SUMMARY ==========")
        print(
            f"PREDICTED: {predicted}"
        )
        print(
            f"FAILED: {failed}"
        )
        print("=============================")

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":

    predict_all_fixtures()