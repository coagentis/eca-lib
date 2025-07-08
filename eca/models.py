# eca/models.py
"""Data models for the ECA library."""

from dataclasses import dataclass

@dataclass
class Persona:
    """Represents the agent's identity."""
    name: str
    role: str
    instructions: str

@dataclass
class Memoria:
    """Represents the agent's memory."""
    # This will be expanded later
    pass

@dataclass
class CognitiveWorkspace:
    """Represents the dynamic reasoning space."""
    # This will be expanded later
    pass