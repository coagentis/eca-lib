# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from eca.memory.types import EpisodicMemory, SemanticMemory

@dataclass
class PersonaConfig:
    """Armazena a configuração detalhada de uma persona."""
    # Descreve a personalidade e o papel da IA.
    persona: str
    # O objetivo principal que guia as ações da IA.
    objective: str
    # Uma lista de regras que a IA nunca deve quebrar.
    golden_rules: List[str] = field(default_factory=list)

@dataclass
class Persona:
    """Representa uma identidade ou domínio completo que a IA pode assumir."""
    # Identificador único do domínio (ex: 'fiscal', 'product_catalog').
    id: str
    # Nome amigável da persona (ex: 'ÁBACO', 'CATÁLOGO').
    name: str
    # Descrição rica para busca semântica, explicando o que este domínio cobre.
    semantic_description: str
    # O objeto com a configuração detalhada da persona.
    config: PersonaConfig

@dataclass
class DomainState:
    """Armazena o estado de um único domínio dentro da área de trabalho."""
    # Status atual do domínio ('active' ou 'paused').
    status: str = "paused"
    # Resumo da interação neste domínio para economizar tokens.
    session_summary: str = ""
    # A tarefa específica que estava sendo executada.
    active_task: str = ""
    # Lista das memórias mais relevantes recuperadas para a tarefa atual.
    semantic_memories: List[SemanticMemory] = field(default_factory=list)
    episodic_memories: List[EpisodicMemory] = field(default_factory=list)
    # Dados brutos necessários para a tarefa (ex: JSON de uma NF-e).
    task_data: Optional[Dict[str, Any]] = None

@dataclass
class CognitiveWorkspace:
    """Representa a "Área de Trabalho Cognitiva" completa de um usuário."""
    user_id: str
    current_focus: str = "default"
    active_domains: Dict[str, DomainState] = field(default_factory=dict)

    def __post_init__(self):
        """
        Hidratação em múltiplos níveis. Este método garante que todos os objetos
        aninhados (DomainState, SemanticMemory, etc.) sejam recriados
        corretamente a partir dos dicionários lidos do JSON.
        """
        # Verifica se o primeiro item em active_domains é um dicionário
        if self.active_domains and isinstance(next(iter(self.active_domains.values())), dict):
            rehydrated_domains = {}
            for domain_id, domain_data in self.active_domains.items():
                
                # Hidrata as listas de memórias primeiro
                semantic_mem_list = [SemanticMemory(**mem) for mem in domain_data.get('semantic_memories', [])]
                episodic_mem_list = [EpisodicMemory(**mem) for mem in domain_data.get('episodic_memories', [])]

                # Atualiza o dicionário de dados com as listas de objetos
                domain_data['semantic_memories'] = semantic_mem_list
                domain_data['episodic_memories'] = episodic_mem_list

                # Agora, cria o objeto DomainState com os dados já tratados
                rehydrated_domains[domain_id] = DomainState(**domain_data)
            
            self.active_domains = rehydrated_domains