# -*- coding: utf-8 -*-
"""
Created on Fri May 29 02:16:36 2026

@author: AUM
"""

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import (
    accuracy_score,
    log_loss,
    roc_auc_score
)
from sqlalchemy import text
from app.db.session import engine

QUERY = """
SELECT * FROM training_view
"""



FEATURES=[
    "elo_diff",
    "surface_elo_diff",
    "recent_form_diff",
    "surface_winrate_diff",
    "matches_last_7d_diff",
    ##"minutes_last_14d_diff",-> no data available ie all values are 0 ...
    "days_since_last_match_diff",
    "h2h_diff"
]

TARGET="target"

N_ESTIMATORS=50
LEARNING_RATE=0.05
MAX_DEPTH=3

def sigmoid(x):
    x = np.clip(x, -500, 500)
    return 1 / (1 + np.exp(-x))


def main():
    print("Loading dataset...")
    
    with engine.connect() as conn:
        df=pd.read_sql(text(QUERY),conn)
    """for col in FEATURES:
        print("\n", col)
        print(df[col].describe())
    print(
        df["days_since_last_match_diff"]
        .abs()
        .gt(1000)
        .sum()
    )
    features = [
    "elo_diff",
    "surface_elo_diff",
    "recent_form_diff",
    "surface_winrate_diff",
    "matches_last_7d_diff",
    "days_since_last_match_diff",
    "h2h_diff"
    ]

    print(df[features].corr())
    print(df["days_since_last_match_diff"].describe())
    """
    df["match_date"]=pd.to_datetime(df["match_date"])
    df=df.sort_values("match_date")
    unique_matches = (
    df[["match_id", "match_date"]]
    .drop_duplicates()
    .sort_values("match_date")
)
####Chronological split ie train for -t and test for +t
    
    split_idx=int(len(unique_matches)*0.8)
    
    train_match_ids = set(
    unique_matches.iloc[:split_idx]["match_id"]
    )

    test_match_ids = set(
    unique_matches.iloc[split_idx:]["match_id"]
    )
    
    train_df = df[
        df["match_id"].isin(train_match_ids)
    ]

    test_df = df[
        df["match_id"].isin(test_match_ids)
    ]
    
    
    X_train=train_df[FEATURES].fillna(0)
    y_train=train_df[TARGET]
    
    X_test=test_df[FEATURES].fillna(0)
    y_test=test_df[TARGET]
    
    
    print(f"Unique train matches: {len(train_match_ids)}")
    print(f"Unique test matches: {len(test_match_ids)}")

    print(f"Train rows: {len(X_train)}")
    print(f"Test rows: {len(X_test)}")
    
####Initial pred..
    
    base_predtion=np.log(y_train.mean()/(1- y_train.mean()))
    
    train_score=np.full(len(X_train),base_predtion)
    
    test_score=np.full(len(X_test),base_predtion)
    trees=[]
    
####Boosting loop..

    print("\n Training Boosting model ...\n")
    
    for i in range(N_ESTIMATORS):
        
        train_probs=sigmoid(train_score)
        
        residuals=y_train -train_probs
        
        tree=DecisionTreeRegressor(max_depth=MAX_DEPTH,random_state=42)
        
        tree.fit(X_train,residuals)
        
        train_update=tree.predict(X_train)
        test_update=tree.predict(X_test)
        
        train_score+=(LEARNING_RATE * train_update)
        test_score+=(LEARNING_RATE * test_update)


        trees.append(tree)
        
        train_pred_prob=sigmoid(train_score)
        test_pred_prob=sigmoid(test_score)
        
        train_loss=log_loss(y_train,train_pred_prob)
        test_loss=log_loss(y_test,test_pred_prob)
        
        print(
            f"Tree {i+1:02d} | "
            f"Train LogLoss: {train_loss:.4f} | "
            f"Test LogLoss: {test_loss:.4f}"
            )
        
####Final Eval ...

    final_probs=sigmoid(test_score)
    final_pred=(final_probs>=0.5).astype(int)
    
    accuracy=accuracy_score(y_test,final_pred)
    auc=roc_auc_score(y_test,final_probs)
    loss=log_loss(y_test,final_probs)
###Feature Imp ...
    print("\n"+ "-"*60)
    print("FINAL RESULTS")
    print("-"*60)
    
    print(f"Accuracy : {accuracy:.04f}")
    print(f"ROC AUC : {auc:.04f}")
    print(f"LOG LOSS : {loss:.04f}")
    
    print("\n" + "-" * 60)
    print("FEATURE IMPORTANCE")
    print("-" * 60)

    importance = np.zeros(len(FEATURES))

    for tree in trees:
        importance += tree.feature_importances_

    importance /= len(trees)

    for feat, imp in sorted(
            zip(FEATURES, importance),
            key=lambda x: x[1],
            reverse=True
    ):
        print(f"{feat}: {imp:.4f}")
    
if __name__ == "__main__":
    main()

# %%

   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    