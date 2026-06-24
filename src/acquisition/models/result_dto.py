# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 00:40:17 2026

@author: AUM
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class ResultDTO:

    winner: str

    loser: str

    tournament: str

    round: str

    score: str | None = None

    match_date: date | None = None

    source: str | None = None

    source_id: str | None = None