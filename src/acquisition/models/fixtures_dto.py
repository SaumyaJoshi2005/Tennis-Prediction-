# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 00:39:42 2026

@author: AUM
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class FixtureDTO:

    player_a: str

    player_b: str

    tournament: str

    round: str

    surface: str | None = None

    match_time: datetime | None = None

    source: str | None = None

    source_id: str | None = None