# -*- coding: utf-8 -*-
"""
Created on Thu May 28 22:10:29 2026

@author: AUM
"""

from sqlalchemy import create_engine

DB_URL = "postgresql+psycopg2://postgres:postgres123@localhost:5433/tennis_prediction"

engine = create_engine(DB_URL)

with engine.connect() as conn:
    print("PostgreSQL connected successfully!")