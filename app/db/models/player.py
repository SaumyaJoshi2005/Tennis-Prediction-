# -*- coding: utf-8 -*-
"""
Created on Thu May 28 22:27:04 2026

@author: AUM
"""

from sqlalchemy import Column, Integer, Text, Date
from app.db.base import Base


class Player(Base):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key=True, index=True)
    player_name = Column(Text, unique=True, nullable=False)

    hand = Column(Text)
    country = Column(Text)
    birth_date = Column(Date)
    height_cm = Column(Integer)