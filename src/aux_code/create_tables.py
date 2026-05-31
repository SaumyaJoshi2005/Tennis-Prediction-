# -*- coding: utf-8 -*-
"""
Created on Thu May 28 22:29:03 2026

@author: AUM
"""

from app.db.session import engine, Base

from app.db.models.player import Player
from app.db.models.tournament import Tournament
from app.db.models.match import Match
from app.db.models.match_features import MatchFeatures
from app.db.models.player_state import PlayerState
from app.db.models.fixture import Fixture

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")