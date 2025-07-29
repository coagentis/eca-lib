# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from eca.memory.types import EpisodicMemory, SemanticMemory


@dataclass
class PersonaConfig:
    """Armazena a configuração detalhada da personalidade de um agente.

    Esta classe funciona como um contêiner para as diretrizes e regras que
    moldam o comportamento, o tom e os objetivos de uma persona específica
    da IA.

    Attributes:
        persona (str): Uma descrição em linguagem natural da personalidade e
            do papel que a IA deve assumir (ex: "um assistente prestativo e
            especialista em finanças").
        objective (str): O objetivo principal que guia todas as ações e
            respostas da IA dentro desta persona.
        golden_rules (List[str]): Uma lista de regras invioláveis que a IA
            nunca deve quebrar, garantindo segurança e conformidade.
        tone_of_voice (List[str]): Lista de adjetivos ou diretrizes que definem
            o tom da comunicação da persona. Ex: ["Formal", "Didático"].
        output_format (Optional[str]): Instrução explícita sobre o formato
            da saída, útil para integrações. Ex: "json", "markdown".
        forbidden_topics (List[str]): Lista de tópicos que a persona deve
            evitar discutir. Ex: ["Opiniões pessoais", "Conselhos de investimento"].
        verbosity (str): Controla o quão detalhada a resposta deve ser.
            Valores sugeridos: "concise", "normal", "detailed".
    """
    persona: str
    objective: str
    golden_rules: List[str] = field(default_factory=list)
    tone_of_voice: List[str] = field(default_factory=list)
    output_format: Optional[str] = None
    forbidden_topics: List[str] = field(default_factory=list)
    verbosity: str = "normal"


@dataclass
class Persona:
    """Representa uma identidade completa que a IA pode assumir.

    Este objeto agrega todas as informações de um domínio ou persona,
    combinando sua identidade, descrição semântica e configuração de
    comportamento.

    Attributes:
        id (str): O identificador único para o domínio ou persona (ex:
            'fiscal', 'product_catalog').
        name (str): Um nome amigável e legível para a persona (ex: 'ÁBACO',
            'Assistente de Catálogo').
        semantic_description (str): Uma descrição rica em palavras-chave,
            usada para busca semântica, que explica o escopo e as
            capacidades deste domínio.
        config (PersonaConfig): O objeto de configuração que detalha o
            comportamento desta persona.
    """
    id: str
    name: str
    semantic_description: str
    config: PersonaConfig

    # BÔNUS: Adicionado __post_init__ para robustez na desserialização.
    def __post_init__(self):
        """Garante que 'config' seja sempre um objeto PersonaConfig."""
        if isinstance(self.config, dict):
            self.config = PersonaConfig(**self.config)


@dataclass
class DomainState:
    """Armazena o estado de um único domínio na área de trabalho do usuário.

    Esta classe encapsula todo o contexto de uma tarefa ou domínio específico
    durante uma sessão, como o histórico de conversa relevante, os fatos
    recuperados e os dados necessários para a tarefa atual.

    Attributes:
        status (str): O estado atual do domínio, que pode ser 'active'
            (em foco) ou 'paused' (em segundo plano). O padrão é 'paused'.
        session_summary (str): Um resumo da interação neste domínio, útil para
            economizar tokens ao reativar o contexto.
        active_task (str): A tarefa específica que o usuário estava
            executando dentro deste domínio.
        semantic_memories (List[SemanticMemory]): Lista das memórias semânticas
            mais relevantes recuperadas para a tarefa atual.
        episodic_memories (List[EpisodicMemory]): Lista das últimas interações
            (memórias episódicas) relevantes para este domínio.
        task_data (Optional[Dict[str, Any]]): Dados brutos ou estruturados
            necessários para a tarefa atual (ex: o JSON de uma NF-e).
    """
    status: str = "paused"
    session_summary: str = ""
    active_task: str = ""
    semantic_memories: List[SemanticMemory] = field(default_factory=list)
    episodic_memories: List[EpisodicMemory] = field(default_factory=list)
    task_data: Optional[Dict[str, Any]] = None


@dataclass
class CognitiveWorkspace:
    """Representa a "Área de Trabalho Cognitiva" completa de um usuário.

    Este é o objeto de mais alto nível para o estado da sessão. Ele gerencia
    o foco atual do usuário e mantém um dicionário de todos os domínios com
    os quais o usuário interagiu, cada um com seu próprio estado.

    Attributes:
        user_id (str): O identificador único do usuário.
        current_focus (str): O ID do domínio que está atualmente em foco.
            O padrão é 'default'.
        active_domains (Dict[str, DomainState]): Um dicionário onde as chaves
            são os IDs dos domínios e os valores são os objetos `DomainState`
            correspondentes.
    """
    user_id: str
    current_focus: str = "default"
    active_domains: Dict[str, DomainState] = field(default_factory=dict)

    def __post_init__(self):
        """Executa a "reidratação" de objetos aninhados após a inicialização.

        Quando um `CognitiveWorkspace` é criado a partir de dados desserializados
        (como um JSON), os objetos aninhados (como `DomainState` e as memórias)
        são inicialmente criados como dicionários. Este método percorre a
        estrutura de dados e converte esses dicionários de volta em instâncias
        plenamente funcionais das suas respectivas classes.
        """
        # Verifica se active_domains existe e se seus valores são dicionários
        if self.active_domains and isinstance(next(iter(self.active_domains.values())), dict):
            rehydrated_domains = {}
            for domain_id, domain_data in self.active_domains.items():
                
                # Reidrata as listas de memórias primeiro
                semantic_mem_list = [SemanticMemory(**mem) for mem in domain_data.get('semantic_memories', [])]
                episodic_mem_list = [EpisodicMemory(**mem) for mem in domain_data.get('episodic_memories', [])]

                # Atualiza o dicionário de dados com as listas de objetos
                domain_data['semantic_memories'] = semantic_mem_list
                domain_data['episodic_memories'] = episodic_mem_list

                # Agora, cria o objeto DomainState com os dados já tratados
                rehydrated_domains[domain_id] = DomainState(**domain_data)
            
            self.active_domains = rehydrated_domains