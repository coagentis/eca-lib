# -*- coding: utf-8 -*-
"""ECA-LIB: A Python library for Augmented Context Engineering."""

__version__ = "0.1.0"

# Expõe as classes principais da arquitetura
from .orchestrator import ECAOrchestrator
from .models import CognitiveWorkspace, Persona
from .memory.types import SemanticMemory, EpisodicMemory

# Expõe os adaptadores padrão
from .adapters.base import PersonaProvider, MemoryProvider, SessionProvider
from .adapters.json_adapter import JSONPersonaProvider, JSONMemoryProvider, JSONSessionProvider

# Expõe os mecanismos de atenção
from .attention import AttentionMechanism, PassthroughAttention, SimpleSemanticAttention, VectorizedSemanticAttention