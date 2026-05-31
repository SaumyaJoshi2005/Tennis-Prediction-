# -*- coding: utf-8 -*-
"""
Created on Sun May 31 18:06:18 2026

@author: AUM
"""

from sqlalchemy import (
    Column,
    Integer,
    Float,
    Date,
    ForeignKey
)

from app.db.base import Base


class PlayerState(Base):
    __tablename__ = "player_state"

    player_id = Column(
        Integer,
        ForeignKey("players.player_id"),
        primary_key=True
    )

    elo = Column(Float)

    clay_elo = Column(Float)
    hard_elo = Column(Float)
    grass_elo = Column(Float)

    recent_form = Column(Float)

    clay_winrate = Column(Float)
    hard_winrate = Column(Float)
    grass_winrate = Column(Float)

    matches_last_7d = Column(Integer)

    days_since_last_match = Column(Integer)

    total_matches = Column(Integer)

    last_match_date = Column(Date)