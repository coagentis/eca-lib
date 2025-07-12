# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

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
class Memory:
    """Representa um único fragmento de conhecimento na memória de longo prazo."""
    # Identificador único da memória.
    id: str
    # O domínio ao qual esta memória pertence primariamente.
    domain_id: str
    # O conteúdo da memória em texto legível.
    text_content: str
    # O vetor de embedding para busca semântica (simulado ou real).
    embedding: Optional[List[float]] = None
    # Metadados adicionais em formato JSON.
    metadata: Dict[str, Any] = field(default_factory=dict)

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
    relevant_memories: List[Memory] = field(default_factory=list)
    # Dados brutos necessários para a tarefa (ex: JSON de uma NF-e).
    task_data: Optional[Dict[str, Any]] = None

@dataclass
class CognitiveWorkspace:
    """Representa a "Área de Trabalho Cognitiva" completa de um usuário."""
    # Identificador único do usuário.
    user_id: str
    # O ID do domínio que está em foco no momento.
    current_focus: str = "default"
    # Um dicionário que armazena o estado de todos os domínios ativos ou pausados.
    # A chave é o domain_id.
    active_domains: Dict[str, DomainState] = field(default_factory=dict)

    def __post_init__(self):
        """
        Este método é chamado automaticamente após a inicialização do objeto.
        Ele verifica se os domínios ativos são dicionários (vindos de um JSON)
        e os converte (hidrata) de volta para objetos DomainState.
        """
        # Verifica se active_domains não está vazio e se o primeiro item é um dicionário
        if self.active_domains and isinstance(next(iter(self.active_domains.values())), dict):
            # Recria o dicionário, transformando cada valor de dicionário em um objeto DomainState
            self.active_domains = {
                domain_id: DomainState(**domain_data)
                for domain_id, domain_data in self.active_domains.items()
            }