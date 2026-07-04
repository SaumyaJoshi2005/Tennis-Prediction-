# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 01:56:05 2026

@author: AUM
"""

from fastapi import APIRouter

from app.db.session import SessionLocal

from app.db.models.player import Player
from app.db.models.player_state import PlayerState

router = APIRouter(
prefix="/players",
tags=["Players"]
)

@router.get("/")
def get_players():

    db = SessionLocal()
    
    try:
    
        players = (
            db.query(Player)
            .all()
        )
    
        return players
    
    finally:
    
        db.close()

@router.get("/states")
def get_player_states():


    db = SessionLocal()
    
    try:
    
        states = (
            db.query(PlayerState)
            .all()
        )
    
        return states
    
    finally:
    
        db.close()

