# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 00:40:05 2026

@author: AUM
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class PlayerDTO:

    name: str

    country: str | None = None

    ranking: int | None = None

    height_cm: int | None = None

    birth_date: date | None = None

    hand: str | None = None

    source: str | None = None

    source_player_id: str | None = None