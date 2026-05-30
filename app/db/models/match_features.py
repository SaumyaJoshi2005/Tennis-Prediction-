# -*- coding: utf-8 -*-
"""
Created on Thu May 28 23:21:41 2026

@author: AUM
"""

from sqlalchemy import (
    Column,
    BigInteger,
    Float,
    Integer,
    ForeignKey
)

from app.db.base import Base
from app.db.models.match import Match

class MatchFeatures(Base):
    __tablename__ = "match_features"

    match_id = Column(
        BigInteger,
        ForeignKey("matches.match_id"),
        primary_key=True
    )

    winner_pre_elo = Column(Float)
    loser_pre_elo = Column(Float)

    winner_surface_elo = Column(Float)
    loser_surface_elo = Column(Float)

    winner_recent_form_5 = Column(Float)
    loser_recent_form_5 = Column(Float)

    winner_surface_winrate = Column(Float)
    loser_surface_winrate = Column(Float)

    winner_matches_last_7d = Column(Integer)
    loser_matches_last_7d = Column(Integer)

    winner_minutes_last_14d = Column(Float)
    loser_minutes_last_14d = Column(Float)

    winner_days_since_last_match = Column(Integer)
    loser_days_since_last_match = Column(Integer)

    winner_h2h = Column(Float)
    loser_h2h = Column(Float)