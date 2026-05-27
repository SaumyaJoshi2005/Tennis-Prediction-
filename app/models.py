"""
models.py — SQLAlchemy ORM table definitions
=============================================
BUG FIXED: This file was an exact copy of cache.py (Redis code).
It should define database tables. Replaced entirely.

Tables
------
  Player         — stores player stats fetched/uploaded by users
  PredictionLog  — audit log of every prediction made via the API
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, func
from database import Base


class Player(Base):
    """
    One row per player. Holds all features the predictor needs.
    Populated via the /upload or /players routes.
    """
    __tablename__ = "players"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String(100), unique=True, index=True, nullable=False)

    # Ranking & physical
    rank            = Column(Integer,   nullable=False)
    age             = Column(Float,     nullable=True)
    height          = Column(Float,     nullable=True)   # cm; nullable — we fill with median

    # Fitness (rolling minutes played recently)
    fitness         = Column(Float,     nullable=True)

    # ELO scores
    elo             = Column(Float,     nullable=False, default=1500.0)
    surface_elo     = Column(Float,     nullable=False, default=1500.0)

    # Recent form
    recent_form     = Column(Float,     nullable=True)   # rolling win-rate last N matches
    surface_winrate = Column(Float,     nullable=True)   # win-rate on specific surface

    created_at      = Column(DateTime, server_default=func.now())
    updated_at      = Column(DateTime, server_default=func.now(), onupdate=func.now())


class PredictionLog(Base):
    """
    Audit log — every prediction request stored here.
    Useful for monitoring model drift over time.
    """
    __tablename__ = "prediction_logs"

    id                   = Column(Integer, primary_key=True, index=True)
    player1_name         = Column(String(100), nullable=False)
    player2_name         = Column(String(100), nullable=False)
    surface              = Column(String(20),  nullable=False)
    tourney_level        = Column(String(5),   nullable=False)
    best_of              = Column(Integer,     nullable=False)
    model_used           = Column(String(20),  nullable=False)
    player1_probability  = Column(Float,       nullable=False)
    player2_probability  = Column(Float,       nullable=False)
    estimated_error      = Column(Float,       nullable=False)
    created_at           = Column(DateTime,    server_default=func.now())
