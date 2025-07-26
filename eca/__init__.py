# eca/__init__.py
"""ECA-Lib: Um framework Python para Engenharia de Contexto Aumentada."""

__version__ = "0.1.3"

# --- Componentes Principais (Sempre disponíveis) ---
from .orchestrator import ECAOrchestrator
from .models import Persona, PersonaConfig, DomainState, CognitiveWorkspace
from .memory.types import SemanticMemory, EpisodicMemory

# --- Interfaces Base (Sempre disponíveis) ---
from .adapters.base import PersonaProvider, MemoryProvider, SessionProvider

# --- Adaptadores Padrão (Sempre disponíveis) ---
from .adapters.json_adapter import JSONPersonaProvider, JSONMemoryProvider, JSONSessionProvider

# --- Mecanismos de Atenção ---
from .attention import AttentionMechanism, PassthroughAttention, SimpleSemanticAttention

# Lista para exportação pública, com os componentes principais
__all__ = [
    "ECAOrchestrator",
    "Persona", "PersonaConfig", "DomainState", "CognitiveWorkspace",
    "SemanticMemory", "EpisodicMemory",
    "PersonaProvider", "MemoryProvider", "SessionProvider",
    "JSONPersonaProvider", "JSONMemoryProvider", "JSONSessionProvider",
    "AttentionMechanism", "PassthroughAttention", "SimpleSemanticAttention"
]

# --- Componentes Opcionais (Disponíveis apenas se os extras forem instalados) ---

# Tenta importar o adaptador Redis
try:
    from .adapters.redis_adapter import RedisSessionProvider
    __all__.append("RedisSessionProvider")
except ImportError:
    pass

# Tenta importar os adaptadores PostgreSQL
try:
    from .adapters.postgres_adapter import PostgresPersonaProvider, PostgresMemoryProvider
    __all__.extend(["PostgresPersonaProvider", "PostgresMemoryProvider"])
except ImportError:
    pass

# Tenta importar o mecanismo de atenção vetorial
try:
    from .attention import VectorizedSemanticAttention
    __all__.append("VectorizedSemanticAttention")
except ImportError:
    pass