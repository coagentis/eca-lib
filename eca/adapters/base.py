# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import List, Optional
from eca.models import Persona, CognitiveWorkspace
from eca.memory import SemanticMemory, EpisodicMemory

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
    """
    Interface abstrata para provedores de memória, agora separando
    as responsabilidades de memória Semântica e Episódica.
    """

    @abstractmethod
    def fetch_semantic_memories(self, user_input: str, domain_id: str, top_k: int = 3) -> List[SemanticMemory]:
        """Busca os fatos e regras (memória semântica) mais relevantes."""
        pass

    @abstractmethod
    def fetch_episodic_memories(self, user_id: str, domain_id: str, last_n: int = 5) -> List[EpisodicMemory]:
        """Busca os últimos N episódios (histórico da conversa) de um usuário."""
        pass

    @abstractmethod
    def log_interaction(self, interaction: EpisodicMemory):
        """Salva um novo episódio (interação) no histórico."""
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