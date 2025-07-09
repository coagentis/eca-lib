# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import List, Optional

from eca.models import Persona, Memory, CognitiveWorkspace

class PersonaProvider(ABC):
    """Interface abstrata para provedores de personas."""

    @abstractmethod
    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        """Busca uma persona pelo seu ID."""
        pass

    @abstractmethod
    def detect_domain(self, user_input: str) -> str:
        """Detecta o domínio mais provável com base na entrada do usuário."""
        pass

class MemoryProvider(ABC):
    """Interface abstrata para provedores de memória."""

    @abstractmethod
    def fetch_relevant_memories(self, user_input: str, domain_id: str, top_k: int = 3) -> List[Memory]:
        """Busca as memórias mais relevantes para uma dada entrada e domínio."""
        pass

class SessionProvider(ABC):
    """Interface abstrata para provedores de sessão (Área de Trabalho Cognitiva)."""

    @abstractmethod
    def get_workspace(self, user_id: str) -> Optional[CognitiveWorkspace]:
        """Carrega a área de trabalho de um usuário."""
        pass
    
    @abstractmethod
    def save_workspace(self, workspace: CognitiveWorkspace):
        """Salva o estado atual da área de trabalho de um usuário."""
        pass