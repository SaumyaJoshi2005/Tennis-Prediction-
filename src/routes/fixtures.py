# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 01:55:15 2026

@author: AUM
"""

from fastapi import APIRouter

from app.db.session import SessionLocal

from app.db.models.fixture import Fixture
from app.db.models.player import Player
from src.utils.fixture_lifecycle import (
    active_fixture_filter,
    mark_stale_fixtures
)

router = APIRouter(
prefix="/fixtures",
tags=["Fixtures"]
)

@router.get("/")
def get_fixtures():


    db = SessionLocal()
    
    try:

        mark_stale_fixtures(db)
    
        fixtures = (
            db.query(Fixture)
            .filter(active_fixture_filter())
            .order_by(Fixture.match_date)
            .all()
        )
    
        results = []

        for fixture in fixtures:
            player_a = (
                db.query(Player)
                .filter(Player.player_id == fixture.player_a_id)
                .first()
            )

            player_b = (
                db.query(Player)
                .filter(Player.player_id == fixture.player_b_id)
                .first()
            )

            result_winner = None

            if fixture.status == "COMPLETED":
                if fixture.winner_predicted == "player_a" and player_a:
                    result_winner = player_a.player_name
                elif fixture.winner_predicted == "player_b" and player_b:
                    result_winner = player_b.player_name
                else:
                    result_winner = fixture.winner_predicted

            results.append({
                "fixture_id": fixture.fixture_id,
                "tournament": fixture.tournament,
                "round": fixture.round,
                "surface": fixture.surface,
                "match_date": fixture.match_date,
                "status": fixture.status,
                "player_a_id": fixture.player_a_id,
                "player_b_id": fixture.player_b_id,
                "player_a": player_a.player_name if player_a else None,
                "player_b": player_b.player_name if player_b else None,
                "winner_predicted": fixture.winner_predicted,
                "player_a_win_probability": fixture.player_a_win_probability,
                "result_winner": result_winner,
                "result_summary": "Completed" if fixture.status == "COMPLETED" else None
            })

        return results
    
    finally:
    
        db.close()

    
@router.get("/scheduled")
def get_scheduled_fixtures():
    

    db = SessionLocal()
    
    try:

        mark_stale_fixtures(db)
    
        fixtures = (
            db.query(Fixture)
            .filter(
                active_fixture_filter(),
                Fixture.status == "SCHEDULED"
            )
            .order_by(Fixture.match_date)
            .all()
        )
    
        return fixtures
    
    finally:
    
        db.close()

