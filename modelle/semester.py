"""Represent one semester of the fixed six-semester study plan."""


class Semester:
    """Represent one semester of the fixed six-semester study plan."""

    def __init__(self, nummer):
        if type(nummer) is not int or nummer not in {1, 2, 3, 4, 5, 6}:
            raise ValueError('Bitte eine Semesternummer von 1 bis 6 verwenden.')
        self.nummer = nummer
        self.geplante_ects = 30
