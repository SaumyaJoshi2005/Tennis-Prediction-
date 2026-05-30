# Tennis Match Prediction System

## Overview

A machine learning system for predicting professional tennis match outcomes using ATP historical match data, player ratings, activity metrics, and engineered performance features.

The project includes:

* PostgreSQL database design
* Automated data ingestion pipeline
* Elo and Surface Elo rating generation
* Feature engineering framework
* Custom Gradient Boosting implementation
* sklearn Gradient Boosting benchmark
* XGBoost benchmark
* Model comparison and evaluation

---

## Engineered Features

The current model uses:

* Elo Difference
* Surface Elo Difference
* Recent Form Difference
* Surface Win Rate Difference
* Matches Played Last 7 Days Difference
* Days Since Last Match Difference
* Head-to-Head Difference

---

## Model Comparison

| Model             | Accuracy | ROC AUC | Log Loss |
| ----------------- | -------: | ------: | -------: |
| Manual Boosting   |   0.7603 |  0.8343 |   0.5816 |
| Gradient Boosting |   0.7706 |  0.8436 |   0.5006 |
| XGBoost           |   0.7750 |  0.8523 |   0.4787 |

---

## Project Pipeline

Raw ATP Match Data

↓

PostgreSQL Database

↓

Feature Engineering

↓

Training Dataset

↓

Model Training

↓

Prediction Service

---

## Technologies

* Python
* PostgreSQL
* SQLAlchemy
* Pandas
* NumPy
* Scikit-Learn
* XGBoost

---

## Current Status

Completed:

* Database schema
* Data ingestion pipeline
* Feature engineering pipeline
* Manual Gradient Boosting implementation
* Gradient Boosting benchmark
* XGBoost benchmark

Planned:

* Model serialization
* FastAPI backend
* React frontend
* Deployment
