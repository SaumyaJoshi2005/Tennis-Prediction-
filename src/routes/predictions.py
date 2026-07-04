# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 01:54:27 2026

@author: AUM
"""

from fastapi import APIRouter

from app.db.session import SessionLocal

from app.db.models.fixture import Fixture
from app.db.models.player import Player
from src.utils.fixture_lifecycle import (
    mark_stale_fixtures,
    prediction_output_filter
)

router = APIRouter(
prefix="/predictions",
tags=["Predictions"]
)

@router.get("/today")
def get_today_predictions():


    db = SessionLocal()
    
    try:

        mark_stale_fixtures(db)
    
        fixtures = (
            db.query(Fixture)
            .filter(prediction_output_filter())
            .order_by(Fixture.match_date)
            .all()
        )
    
        results = []
    
        for fixture in fixtures:
    
            player_a = (
                db.query(Player)
                .filter(
                    Player.player_id
                    == fixture.player_a_id
                )
                .first()
            )
    
            player_b = (
                db.query(Player)
                .filter(
                    Player.player_id
                    == fixture.player_b_id
                )
                .first()
            )
    
            results.append({
    
                "fixture_id":
                    fixture.fixture_id,
    
                "tournament":
                    fixture.tournament,
    
                "round":
                    fixture.round,
    
                "surface":
                    fixture.surface,
    
                "match_date":
                    fixture.match_date,
    
                "player_a":
                    player_a.player_name,
    
                "player_b":
                    player_b.player_name,
    
                "winner_predicted":
                    fixture.winner_predicted,
    
                "player_a_win_probability":
                    fixture.player_a_win_probability
            })
    
        return results
    
    finally:
    
        db.close()

