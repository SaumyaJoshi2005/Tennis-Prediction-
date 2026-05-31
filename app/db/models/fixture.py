# -*- coding: utf-8 -*-
"""
Created on Sun May 31 18:44:59 2026

@author: AUM
"""

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Text,
    Date,
    Float,
    ForeignKey
)

from app.db.base import Base


class Fixture(Base):
    __tablename__ = "fixtures"

    fixture_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    player_a_id = Column(
        Integer,
        ForeignKey("players.player_id")
    )

    player_b_id = Column(
        Integer,
        ForeignKey("players.player_id")
    )

    tournament = Column(Text)

    round = Column(Text)

    surface = Column(Text)

    match_date = Column(Date)

    prediction = Column(Float)

    winner_predicted = Column(Text)
    
    player_a_win_probability = Column(Float)
    
    status = Column(Text)