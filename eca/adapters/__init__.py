# eca/adapters/__init__.py
"""
Adapters for different data sources and services.

This module exposes the available data provider implementations.
Production-ready adapters like Redis or PostgreSQL are only available if their
corresponding extras are installed (e.g., `pip install eca-lib[redis]`).
"""

# Adaptadores baseados em JSON, sempre disponíveis pois não têm dependências externas
from .json_adapter import (
    JSONMemoryProvider,
    JSONPersonaProvider,
    JSONSessionProvider,
)

# Lista para exportação pública, começamos com os adaptadores padrão
__all__ = [
    "JSONMemoryProvider",
    "JSONPersonaProvider",
    "JSONSessionProvider",
]

# Tenta importar o adaptador Redis. Se falhar, é porque o 'redis' extra não foi instalado.
try:
    from .redis_adapter import RedisSessionProvider
    __all__.append("RedisSessionProvider")
except ImportError:
    pass 

# Tenta importar os adaptadores PostgreSQL. Se falhar, o 'postgres' extra não foi instalado.
try:
    from .postgres_adapter import PostgresPersonaProvider, PostgresMemoryProvider
    __all__.extend(["PostgresPersonaProvider", "PostgresMemoryProvider"])
except ImportError:
    pass  