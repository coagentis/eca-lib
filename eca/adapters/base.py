# eca/adapters/base.py
"""Abstract base classes for adapters."""

from abc import ABC, abstractmethod

class MemoryAdapter(ABC):
    """Abstract base class for memory adapters."""

    @abstractmethod
    def load(self, source: str):
        """Load memory from a source."""
        pass

    @abstractmethod
    def save(self, data, destination: str):
        """Save memory to a destination."""
        pass