"""Distinguish compulsory modules from elective modules."""

from enum import Enum


class Modulart(Enum):
    PFLICHT = 'PFLICHT'
    WAHLPFLICHT = 'WAHLPFLICHT'
