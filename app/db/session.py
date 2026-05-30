# -*- coding: utf-8 -*-
"""
Created on Thu May 28 22:25:57 2026

@author: AUM
"""
from app.db.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = "postgresql+psycopg2://postgres:postgres123@localhost:5433/tennis_prediction"

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

