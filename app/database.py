"""
database.py — SQLAlchemy engine & session factory
==================================================
BUGS FIXED
----------
1. Credentials hardcoded as root/password — these should never be in
   source code. Replaced with os.getenv() calls.

2. Password mismatch: docker-compose.yml set MYSQL_ROOT_PASSWORD=123
   but this file had 'password' — the two containers could never connect.
   Fixed: both now read from the same DB_PASSWORD environment variable.
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# FIX 1 + 2: All credentials from environment variables.
# Set these in docker-compose.yml under the 'api' service environment block,
# matching the values given to the mysql service.
DB_USER     = os.getenv("DB_USER",     "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tennis123")   # must match docker-compose MYSQL_ROOT_PASSWORD
DB_HOST     = os.getenv("DB_HOST",     "mysql")       # Docker service name, not localhost
DB_PORT     = os.getenv("DB_PORT",     "3306")
DB_NAME     = os.getenv("DB_NAME",     "tennis_db")

DATABASE_URL = (
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # re-validates connections before use (handles MySQL 8hr timeout)
    pool_recycle=3600,    # recycle connections every hour
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session, always closes on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
