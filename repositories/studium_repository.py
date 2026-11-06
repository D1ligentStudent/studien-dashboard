"""Define the storage contract used by the dashboard controller."""

from abc import ABC, abstractmethod


class StudiumRepository(ABC):
    """Require each storage implementation to load and save a complete plan."""

    @abstractmethod
    def lade_studiendaten(self, studium):
        """Load persisted modules and results into the supplied study plan."""
        raise NotImplementedError

    @abstractmethod
    def speichere_studiendaten(self, studium):
        """Persist all modules and results from the supplied study plan."""
        raise NotImplementedError
