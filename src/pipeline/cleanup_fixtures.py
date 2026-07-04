from app.db.session import SessionLocal
from src.utils.fixture_lifecycle import mark_stale_fixtures


def cleanup_fixtures():
    db = SessionLocal()

    try:
        stale_count = mark_stale_fixtures(db)
        db.commit()
        print(f"Stale fixtures marked: {stale_count}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    cleanup_fixtures()
