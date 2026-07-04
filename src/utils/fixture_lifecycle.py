from datetime import date, timedelta

from sqlalchemy import and_, or_

from app.db.models.fixture import Fixture


ACTIVE_FIXTURE_STATUSES = (
    "PENDING",
    "SCHEDULED",
    "UPCOMING",
    "IN_PROGRESS",
    "LIVE",
    "PREDICTED",
)

RECENT_COMPLETED_STATUSES = (
    "COMPLETED",
)


def active_fixture_filter(reference_date=None):
    today = reference_date or date.today()
    recently_completed_cutoff = today - timedelta(days=1)

    return and_(
        or_(
            and_(
                Fixture.status.in_(ACTIVE_FIXTURE_STATUSES),
                Fixture.match_date >= today,
            ),
            and_(
                Fixture.status.in_(RECENT_COMPLETED_STATUSES),
                Fixture.match_date >= recently_completed_cutoff,
            ),
        ),
        Fixture.match_date.isnot(None),
        Fixture.player_a_id.isnot(None),
        Fixture.player_b_id.isnot(None),
        Fixture.tournament.isnot(None),
        Fixture.round.isnot(None),
        Fixture.surface.isnot(None),
    )


def prediction_candidate_filter(reference_date=None):
    today = reference_date or date.today()

    return and_(
        Fixture.status.in_(("PENDING", "SCHEDULED")),
        Fixture.match_date.isnot(None),
        Fixture.match_date >= today,
        Fixture.player_a_id.isnot(None),
        Fixture.player_b_id.isnot(None),
        Fixture.tournament.isnot(None),
        Fixture.round.isnot(None),
        Fixture.surface.isnot(None),
    )


def prediction_output_filter(reference_date=None):
    today = reference_date or date.today()

    return and_(
        Fixture.status == "PREDICTED",
        Fixture.match_date.isnot(None),
        Fixture.match_date >= today,
        Fixture.player_a_id.isnot(None),
        Fixture.player_b_id.isnot(None),
        Fixture.tournament.isnot(None),
        Fixture.round.isnot(None),
        Fixture.surface.isnot(None),
        Fixture.winner_predicted.isnot(None),
        Fixture.player_a_win_probability.isnot(None),
    )


def mark_stale_fixtures(db, reference_date=None):
    today = reference_date or date.today()

    stale_fixtures = (
        db.query(Fixture)
        .filter(
            Fixture.status.in_(ACTIVE_FIXTURE_STATUSES),
            Fixture.match_date.isnot(None),
            Fixture.match_date < today,
        )
        .all()
    )

    for fixture in stale_fixtures:
        fixture.status = "STALE"

    return len(stale_fixtures)
