# -*- coding: utf-8 -*-
"""
Created on Sun May 31 02:20:16 2026

@author: AUM
"""

import pandas as pd

from sqlalchemy import text

from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    log_loss
)

from app.db.session import engine


QUERY = """
SELECT * FROM training_view
"""


FEATURES = [
    "elo_diff",
    "surface_elo_diff",
    "recent_form_diff",
    "surface_winrate_diff",
    #"matches_last_7d_diff",
    #"days_since_last_match_diff",
    "h2h_diff"
]

TARGET = "target"


def main():

    print("Loading dataset...")

    with engine.connect() as conn:
        df = pd.read_sql(
            text(QUERY),
            conn
        )

    df["match_date"] = pd.to_datetime(
        df["match_date"]
    )

    df = df.sort_values(
        "match_date"
    )

    unique_matches = (
        df[["match_id", "match_date"]]
        .drop_duplicates()
        .sort_values("match_date")
    )

    split_idx = int(
        len(unique_matches) * 0.8
    )

    train_match_ids = set(
        unique_matches.iloc[:split_idx]["match_id"]
    )

    test_match_ids = set(
        unique_matches.iloc[split_idx:]["match_id"]
    )

    train_df = df[
        df["match_id"].isin(
            train_match_ids
        )
    ]

    test_df = df[
        df["match_id"].isin(
            test_match_ids
        )
    ]

    X_train = train_df[
        FEATURES
    ].fillna(0)

    y_train = train_df[
        TARGET
    ]

    X_test = test_df[
        FEATURES
    ].fillna(0)

    y_test = test_df[
        TARGET
    ]

    print(
        f"Train rows: {len(X_train)}"
    )

    print(
        f"Test rows: {len(X_test)}"
    )

    print(
        "\nTraining XGBoost..."
    )

    model = XGBClassifier(
        objective="binary:logistic",

        n_estimators=200,

        learning_rate=0.05,

        max_depth=4,

        subsample=0.8,

        colsample_bytree=0.8,

        random_state=42,

        eval_metric="logloss"
    )

    model.fit(
        X_train,
        y_train
    )
    
    import os
    import joblib

    os.makedirs("models", exist_ok=True)

    joblib.dump(
        model,
        "models/xgb_model.pkl"
    )

    joblib.dump(
        FEATURES,
        "models/features.pkl"
    )

    print("Model saved successfully.")
    
    pred_probs = model.predict_proba(
        X_test
    )[:, 1]

    preds = (
        pred_probs >= 0.5
    ).astype(int)

    accuracy = accuracy_score(
        y_test,
        preds
    )

    auc = roc_auc_score(
        y_test,
        pred_probs
    )

    loss = log_loss(
        y_test,
        pred_probs
    )

    print("\n" + "-" * 60)
    print("FINAL RESULTS")
    print("-" * 60)

    print(
        f"Accuracy : {accuracy:.4f}"
    )

    print(
        f"ROC AUC : {auc:.4f}"
    )

    print(
        f"LOG LOSS : {loss:.4f}"
    )

    print("\n" + "-" * 60)
    print("FEATURE IMPORTANCE")
    print("-" * 60)

    feature_importance = sorted(
        zip(
            FEATURES,
            model.feature_importances_
        ),
        key=lambda x: x[1],
        reverse=True
    )

    for feature, importance in feature_importance:

        print(
            f"{feature}: "
            f"{importance:.4f}"
        )


if __name__ == "__main__":
    main()
    
# %%
    
