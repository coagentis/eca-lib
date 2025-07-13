# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class SemanticMemory:
    """Representa um fato ou regra na memória semântica."""
    id: str
    domain_id: str
    type: str
    text_content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EpisodicMemory:
    """Representa um episódio de conversa (um turno) na memória episódica."""
    user_id: str
    domain_id: str
    user_input: str
    assistant_output: str
    timestamp: str