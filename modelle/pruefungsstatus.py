"""Exam states derived from the curent result."""

from enum import Enum


class Pruefungsstatus(Enum):
    UNBENOTET = 'UNBENOTET'
    BESTANDEN = 'BESTANDEN'
    NICHT_BESTANDEN = 'NICHT_BESTANDEN'
