# -*- coding: utf-8 -*-
"""
Created on Thu May 28 22:27:35 2026

@author: AUM
"""

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Float,
    Date,
    ForeignKey,
    Text
)

from app.db.base import Base


class Match(Base):
    __tablename__ = "matches"

    match_id = Column(BigInteger, primary_key=True, index=True)

    tournament_id = Column(
        Integer,
        ForeignKey("tournaments.tournament_id")
    )

    match_date = Column(Date)

    round = Column(Text)
    best_of = Column(Integer)

    winner_id = Column(
        Integer,
        ForeignKey("players.player_id")
    )

    loser_id = Column(
        Integer,
        ForeignKey("players.player_id")
    )

    winner_rank = Column(Integer)
    loser_rank = Column(Integer)

    winner_elo = Column(Float)
    loser_elo = Column(Float)

    winner_surface_elo = Column(Float)
    loser_surface_elo = Column(Float)

    winner_recent_form = Column(Float)
    loser_recent_form = Column(Float)

    winner_surface_winrate = Column(Float)
    loser_surface_winrate = Column(Float)

    winner_fitness = Column(Float)
    loser_fitness = Column(Float)