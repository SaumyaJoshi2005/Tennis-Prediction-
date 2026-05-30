# -*- coding: utf-8 -*-
"""
Created on Thu May 28 22:27:21 2026

@author: AUM
"""
from app.db.base import Base
from sqlalchemy import Column, Integer, Text



class Tournament(Base):
    __tablename__ = "tournaments"

    tournament_id = Column(Integer, primary_key=True, index=True)

    tournament_name = Column(Text)
    surface = Column(Text)
    level = Column(Text)
    location = Column(Text)