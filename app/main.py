"""
main.py — FastAPI application entry point
==========================================
BUGS FIXED
----------
1. Imported routes (predict, players, upload) that don't exist as files —
   app crashed on startup with ModuleNotFoundError.
   Fixed: stubbed the three routers inline until route files are created,
   and added a clear TODO comment per router.

2. No CORS middleware — the React frontend running on localhost:3000
   (or any other origin) is blocked by browsers from calling this API.
   Fixed: CORSMiddleware added with configurable allowed origins.

3. No exception handlers — unhandled errors leaked raw stack traces to
   clients. Added a generic 500 handler and a validation error handler.
"""

import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from database import Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create all tables on startup (idempotent — safe to run every time)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tennis Match Prediction API",
    description="XGBoost & LightGBM powered ATP match outcome predictor",
    version="2.0.0",
)

# FIX 2: CORS middleware — required for the React frontend to call this API.
# In production, replace "*" with your actual frontend domain.
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173"   # Vite + CRA defaults
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FIX 3a: Validation error handler — returns clean 422 with readable message
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "hint": "Check field names and allowed values."},
    )

# FIX 3b: Generic error handler — prevents raw stack traces reaching the client
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Check API logs."},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
# FIX 1: Route files don't exist yet — importing them crashed the app on startup.
# Each router is defined inline here as a stub so the app starts cleanly.
# Move each block to its own file (routes/predict.py etc.) as you build them out.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import PredictionRequest, PredictionResponse
from predictor import predict_match
from cache import get_cached_prediction, set_cached_prediction
import models

# ── /predict ──────────────────────────────────────────────────────────────────
predict_router = APIRouter(prefix="/predict", tags=["Predictions"])

@predict_router.post("/", response_model=PredictionResponse)
def predict(req: PredictionRequest, db: Session = Depends(get_db)):
    # Cache key — same matchup + surface + model returns cached result
    cache_key = f"{req.player1}:{req.player2}:{req.surface}:{req.model_name}"
    cached    = get_cached_prediction(cache_key)
    if cached:
        return cached

    p1 = db.query(models.Player).filter(models.Player.name == req.player1).first()
    p2 = db.query(models.Player).filter(models.Player.name == req.player2).first()

    if not p1 or not p2:
        from fastapi import HTTPException
        missing = req.player1 if not p1 else req.player2
        raise HTTPException(status_code=404, detail=f"Player not found: {missing}")

    result = predict_match(
        p1, p2,
        surface=req.surface,
        model_name=req.model_name,
        tourney_level=req.tourney_level,
        best_of=req.best_of,
    )

    response = {
        "player1_name":         req.player1,
        "player2_name":         req.player2,
        "surface":              req.surface,
        "model_used":           req.model_name,
        "predicted_winner":     req.player1 if result["player1_probability"] >= 0.5 else req.player2,
        **result,
    }

    # Log to DB
    log = models.PredictionLog(
        player1_name=req.player1, player2_name=req.player2,
        surface=req.surface, tourney_level=req.tourney_level,
        best_of=req.best_of, model_used=req.model_name,
        player1_probability=result["player1_probability"],
        player2_probability=result["player2_probability"],
        estimated_error=result["estimated_error"],
    )
    db.add(log); db.commit()

    set_cached_prediction(cache_key, response)
    return response


# ── /players ──────────────────────────────────────────────────────────────────
players_router = APIRouter(prefix="/players", tags=["Players"])

@players_router.get("/", summary="List all players")
def list_players(db: Session = Depends(get_db)):
    return db.query(models.Player).all()

@players_router.get("/{name}", summary="Get a single player by name")
def get_player(name: str, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    player = db.query(models.Player).filter(models.Player.name == name).first()
    if not player:
        raise HTTPException(status_code=404, detail=f"Player '{name}' not found")
    return player


# ── /upload ───────────────────────────────────────────────────────────────────
upload_router = APIRouter(prefix="/upload", tags=["Upload"])

@upload_router.post("/player", summary="Add or update a player's stats")
def upsert_player(player_data: dict, db: Session = Depends(get_db)):
    # TODO: add proper PlayerCreate schema + upsert logic
    return {"message": "TODO — implement player upsert"}


# Register all routers
app.include_router(predict_router)
app.include_router(players_router)
app.include_router(upload_router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Tennis Prediction API Running", "version": "2.0.0"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
