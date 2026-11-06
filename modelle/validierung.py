"""Validate values received from terminal input, configuration, or storage."""

from datetime import date


def _positive_ganzzahl(wert, name):
    """Reject fractions and booleans even though True behaves like the number 1."""
    if type(wert) is not int or wert <= 0:
        raise ValueError(f'{name}: Bitte eine positive ganze Zahl eingeben.')
    return wert


def _note(wert, maximum=5.0):
    """Accept zero for a missing result, or a grade within the given limits."""
    if type(wert) not in {int, float}:
        raise ValueError(f'Bitte 0 oder eine Note von 1 bis {maximum:g} eingeben.')
    if wert == 0:
        return 0.0
    if 1 <= wert <= maximum:
        return float(wert)
    raise ValueError(f'Bitte 0 oder eine Note von 1 bis {maximum:g} eingeben.')


def _datum(wert, name):
    """Require a calendar date, without accepting datetime values or strings."""
    if type(wert) is not date:
        raise ValueError(f'{name}: Bitte ein gültiges Datum eingeben.')
    return wert


def _text(wert, name):
    """Require non-empty text and remove surrounding spaces."""
    if type(wert) is not str or not wert.strip():
        raise ValueError(f'{name}: Bitte einen Text eingeben.')
    return wert.strip()
