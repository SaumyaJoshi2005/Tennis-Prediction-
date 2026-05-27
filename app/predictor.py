"""
predictor.py — Feature building & model inference
==================================================
BUGS FIXED
----------
1. Feature name 'rank_diff'    → 'rank_diff_fixed'
   Feature name 'fitness_diff' → 'fitness_diff_fixed'
   These mismatches caused silent wrong predictions because the FEATURES
   list from training used the _fixed suffix — X[FEATURES] would either
   KeyError or silently fill with NaN depending on pandas version.

2. Surface OHE keys were capitalised: 'surface_Clay', 'surface_Hard'
   Training pipeline produces lowercase: 'surface_clay', 'surface_hard'
   This would KeyError at runtime on any prediction request.

3. Models loaded at module level — if .pkl files are missing at import
   time, the entire FastAPI app fails to start with no helpful message.
   Fixed with lazy loading + clear FileNotFoundError on first call.

4. Cold-start ELO flags hardcoded to 0 — should be computed from
   actual ELO values so the model can discount uncertain predictions.

5. best_of and draw_size hardcoded to 5/128 — only correct for Grand
   Slams. Now passed in from PredictionRequest via predict_match().
"""

import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# ── Model paths ───────────────────────────────────────────────────────────────
MODEL_DIR = Path(os.getenv("MODEL_DIR", "app/ml_models"))

# FIX 3: Lazy-loaded globals — models loaded on first call, not at import time.
# Prevents the entire app from crashing if pkl files aren't present yet.
_xgb_model   = None
_lgbm_model  = None
_features    = None


def _load_models():
    """Load models from disk once, cache in module globals."""
    global _xgb_model, _lgbm_model, _features

    if _xgb_model is not None:
        return  # already loaded

    xgb_path  = MODEL_DIR / "xgb_model.pkl"
    lgbm_path = MODEL_DIR / "lgbm_model.pkl"
    feat_path = MODEL_DIR / "features.pkl"

    for path in (xgb_path, lgbm_path, feat_path):
        if not path.exists():
            raise FileNotFoundError(
                f"Model file not found: {path}\n"
                f"Run the training pipeline first to generate .pkl artifacts."
            )

    _xgb_model  = joblib.load(xgb_path)
    _lgbm_model = joblib.load(lgbm_path)
    _features   = joblib.load(feat_path)


# ── Surface map ───────────────────────────────────────────────────────────────
# FIX 2: Keys match training pipeline lowercase convention
SURFACE_MAP = {
    "Clay":   {"surface_clay": 1, "surface_hard": 0, "surface_grass": 0, "surface_carpet": 0},
    "Hard":   {"surface_clay": 0, "surface_hard": 1, "surface_grass": 0, "surface_carpet": 0},
    "Grass":  {"surface_clay": 0, "surface_hard": 0, "surface_grass": 1, "surface_carpet": 0},
    "Carpet": {"surface_clay": 0, "surface_hard": 0, "surface_grass": 0, "surface_carpet": 1},
}

LEVEL_MAP = {
    "G": {"level_grandslam": 1, "level_masters": 0, "level_atp": 0},
    "M": {"level_grandslam": 0, "level_masters": 1, "level_atp": 0},
    "A": {"level_grandslam": 0, "level_masters": 0, "level_atp": 1},
    "D": {"level_grandslam": 0, "level_masters": 0, "level_atp": 0},
}

# Default height used when player height is null (median from training data)
DEFAULT_HEIGHT = 185.0


def build_feature_vector(p1, p2, surface: str,
                          tourney_level: str = "A",
                          best_of: int = 3,
                          draw_size: int = 64) -> pd.DataFrame:
    """
    Build the exact feature vector the trained models expect.
    p1, p2 must be PlayerResponse (or any object with matching attributes).
    """
    h1 = p1.height if p1.height else DEFAULT_HEIGHT
    h2 = p2.height if p2.height else DEFAULT_HEIGHT

    row = {
        # ── Rank ──────────────────────────────────────────────────────────────
        "player1_rank":    p1.rank,
        "player2_rank":    p2.rank,
        # FIX 1a: was 'rank_diff', must match training feature name
        "rank_diff_fixed": p2.rank - p1.rank,

        # ── Fitness ───────────────────────────────────────────────────────────
        # FIX 1b: was 'fitness_diff', must match training feature name
        "fitness_diff_fixed": p1.fitness - p2.fitness,

        # ── ELO ───────────────────────────────────────────────────────────────
        "elo_diff":         p1.elo         - p2.elo,
        "surface_elo_diff": p1.surface_elo - p2.surface_elo,

        # ── Form ─────────────────────────────────────────────────────────────
        "recent_form_diff":     p1.recent_form     - p2.recent_form,
        "surface_winrate_diff": p1.surface_winrate - p2.surface_winrate,

        # ── Physical ─────────────────────────────────────────────────────────
        "player1_age":  p1.age,
        "player2_age":  p2.age,
        "age_diff":     p2.age - p1.age,
        "player1_height": h1,
        "player2_height": h2,
        "height_diff":  h1 - h2,

        # ── Context ───────────────────────────────────────────────────────────
        # FIX 5: best_of and draw_size now passed in, not hardcoded
        "best_of":   best_of,
        "draw_size": draw_size,
        "is_clay":   int(surface == "Clay"),

        # FIX 4: Cold-start flags computed from actual ELO, not hardcoded 0
        "player1_elo_coldstart": int(p1.elo == 1500),
        "player2_elo_coldstart": int(p2.elo == 1500),
    }

    # FIX 2: Surface OHE — lowercase keys matching training pipeline
    row.update(SURFACE_MAP[surface])

    # Tournament level OHE
    row.update(LEVEL_MAP.get(tourney_level, LEVEL_MAP["A"]))

    _load_models()  # no-op if already loaded
    X = pd.DataFrame([row])
    return X[_features]   # enforce exact column order from training


def predict_match(p1, p2, surface: str,
                  model_name: str = "XGBoost",
                  tourney_level: str = "A",
                  best_of: int = 3,
                  draw_size: int = 64) -> dict:
    """
    Run inference and return probabilities + confidence estimate.

    Confidence estimate logic
    -------------------------
    When prob is near 0.5 the model is uncertain — error is ~18%.
    When prob is near 0 or 1 the model is confident — error floors at 3%.
    Formula: error = max(0.03, (1 - |prob - 0.5| * 2) * 0.18)
    """
    _load_models()

    X   = build_feature_vector(p1, p2, surface, tourney_level, best_of, draw_size)
    mdl = _lgbm_model if model_name == "LightGBM" else _xgb_model
    prob = float(mdl.predict_proba(X)[0][1])

    error = max(0.03, (1 - abs(prob - 0.5) * 2) * 0.18)

    return {
        "player1_probability": round(prob,       4),
        "player2_probability": round(1 - prob,   4),
        "estimated_error":     round(error,      4),
        "predicted_winner":    "player1" if prob >= 0.5 else "player2",
    }
