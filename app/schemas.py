"""
schemas.py — Pydantic request/response models
==============================================
BUGS FIXED
----------
1. PlayerResponse was missing surface_elo, surface_winrate, height —
   predictor.py accesses all three; omitting them caused AttributeError.

2. PredictionRequest was missing best_of and tourney_level —
   predictor was silently hardcoding best_of=5 for every match,
   which is only correct for Grand Slams.

3. No surface validation — any garbage string passed as surface
   would KeyError inside SURFACE_MAP in predictor.py.
"""

from typing import Literal
from pydantic import BaseModel, Field


# ── Incoming requests ─────────────────────────────────────────────────────────

class PredictionRequest(BaseModel):
    player1:       str
    player2:       str

    # FIX 3: Literal enum so FastAPI rejects invalid surfaces at the schema layer
    # before it ever reaches predictor.py — no more KeyError in SURFACE_MAP
    surface:       Literal["Clay", "Hard", "Grass", "Carpet"]

    # FIX 2: Added best_of and tourney_level so predictor stops hardcoding
    # best_of=5 for every single match (only Grand Slams are best-of-5)
    best_of:       Literal[3, 5] = 3
    tourney_level: Literal["G", "M", "A", "D"] = "A"   # G=GrandSlam M=Masters A=ATP D=Davis

    model_name:    Literal["XGBoost", "LightGBM"] = "XGBoost"


# ── Outgoing responses ────────────────────────────────────────────────────────

class PlayerResponse(BaseModel):
    name:   str
    rank:   int

    # FIX 1: Added the four fields predictor.py was already accessing
    # via p1.height, p1.surface_elo, p1.surface_winrate, p1.recent_form
    age:             float
    height:          float = Field(default=185.0, description="Height in cm")
    fitness:         float

    elo:             float = Field(default=1500.0)
    surface_elo:     float = Field(default=1500.0)
    recent_form:     float = Field(default=0.5,   description="Rolling win-rate, last N matches")
    surface_winrate: float = Field(default=0.5,   description="Win-rate on requested surface")


class PredictionResponse(BaseModel):
    player1_name:        str
    player2_name:        str
    surface:             str
    model_used:          str
    player1_probability: float
    player2_probability: float
    estimated_error:     float
    predicted_winner:    str
