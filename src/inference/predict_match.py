# -*- coding: utf-8 -*-
"""
Created on Sun May 31 17:21:52 2026

@author: AUM
"""

import joblib
import pandas as pd

model = joblib.load(
    "models/xgb_model.pkl"
)

FEATURES = joblib.load(
    "models/features.pkl"
)

sample = pd.DataFrame([
    {
        "elo_diff": 100,
        "surface_elo_diff": 80,
        "recent_form_diff": 0.2,
        "surface_winrate_diff": 0.1,
        "matches_last_7d_diff": 1,
        "days_since_last_match_diff": -2,
        "h2h_diff": 1
    }
])

sample = sample[FEATURES]

prob = model.predict_proba(sample)[0][1]

print(
    f"Player 1 Win Probability: {prob:.4f}"
)