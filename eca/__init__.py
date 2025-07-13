# -*- coding: utf-8 -*-
"""ECA-LIB: A Python library for Augmented Context Engineering."""

__version__ = "0.1.0"

from .orchestrator import ECAOrchestrator
from .models import CognitiveWorkspace, Persona
from .memory import SemanticMemory, EpisodicMemory
from .adapters.base import PersonaProvider, MemoryProvider, SessionProvider
from .adapters.json_adapter import JSONPersonaProvider, JSONMemoryProvider, JSONSessionProvider