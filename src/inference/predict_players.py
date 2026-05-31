# -*- coding: utf-8 -*-
"""
Created on Sun May 31 18:24:40 2026

@author: AUM
"""

import joblib
import pandas as pd

from app.db.session import SessionLocal

from src.inference.feature_builder import (
    build_features
)

model = joblib.load(
    "models/xgb_model.pkl"
)

FEATURES = joblib.load(
    "models/features.pkl"
)


def predict_players(
    player_a,
    player_b,
    surface
):

    db = SessionLocal()

    try:

        features = build_features(
            db,
            player_a,
            player_b,
            surface
        )

        df = pd.DataFrame(
            [features]
        )

        df = df[FEATURES]

        probability = (
            model
            .predict_proba(df)[0][1]
        )

        return float(probability)

    finally:

        db.close()
