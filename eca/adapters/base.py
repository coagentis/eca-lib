# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import List, Optional
from eca.models import Persona, CognitiveWorkspace
from eca.memory import SemanticMemory, EpisodicMemory


class PersonaProvider(ABC):
    """Define a interface para um provedor de personas do agente.

    Esta classe abstrata estabelece o contrato que um provedor de
    personalidade deve seguir. As implementações desta classe são responsáveis
    por carregar perfis de persona e por determinar o domínio de
    conhecimento relevante com base na entrada do usuário, atuando como um
    roteador inicial para o orquestrador.
    """
    @abstractmethod
    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        """Busca e retorna uma persona específica pelo seu identificador.

        Args:
            persona_id (str): O ID único da persona a ser carregada.

        Returns:
            Optional[Persona]: Um objeto `Persona` preenchido com os dados
            encontrados, ou `None` se nenhuma persona com o ID fornecido
            for localizada.
        """
        pass

    @abstractmethod
    def detect_domain(self, user_input: str) -> str:
        """Detecta o domínio de conhecimento mais provável para uma dada entrada.

        Esta função atua como um roteador, analisando o texto do usuário para
        determinar a qual área de especialização do agente a pergunta pertence
        (ex: 'vendas', 'suporte', 'financeiro').

        Args:
            user_input (str): O texto fornecido pelo usuário.

        Returns:
            str: O identificador (ID) do domínio detectado.
        """
        pass


class MemoryProvider(ABC):
    """Define a interface para um provedor de memória do agente.

    Esta classe abstrata estabelece o contrato para a gestão das memórias
    semântica (conhecimento de longo prazo) e episódica (histórico de
    conversas). Implementações desta classe são o coração da capacidade
    de aprendizado e contextualização do agente.
    """

    @abstractmethod
    def fetch_semantic_memories(self, user_input: str, domain_id: str, top_k: int = 3) -> List[SemanticMemory]:
        """Busca fatos e regras (memória semântica) relevantes para a entrada.

        Args:
            user_input (str): O texto do usuário, usado para a busca de
                similaridade na base de conhecimento.
            domain_id (str): O ID do domínio para filtrar a busca.
            top_k (int, optional): O número máximo de memórias a serem
                retornadas. Padrão é 3.

        Returns:
            List[SemanticMemory]: Uma lista de objetos `SemanticMemory`
            relevantes, ou uma lista vazia se nada for encontrado.
        """
        pass

    @abstractmethod
    def fetch_episodic_memories(self, user_id: str, domain_id: str, last_n: int = 5) -> List[EpisodicMemory]:
        """Busca os últimos N episódios de conversa de um usuário em um domínio.

        Args:
            user_id (str): O ID único do usuário cujo histórico está sendo
                buscado.
            domain_id (str): O ID do domínio da conversa para filtrar o
                histórico.
            last_n (int, optional): O número de interações passadas a serem
                retornadas. Padrão é 5.

        Returns:
            List[EpisodicMemory]: Uma lista de objetos `EpisodicMemory`
            representando o histórico da conversa.
        """
        pass

    @abstractmethod
    def log_interaction(self, interaction: EpisodicMemory):
        """Salva um novo episódio (interação) no histórico de conversas.

        Esta função é chamada para persistir cada turno da conversa, garantindo
        que o agente se lembre de interações futuras.

        Args:
            interaction (EpisodicMemory): O objeto de interação contendo os
                detalhes do turno da conversa a ser salvo.
        
        Returns:
            None: Esta função não retorna valor.
        """
        pass


class SessionProvider(ABC):
    """Define a interface para provedores de sessão (Área de Trabalho Cognitiva).

    Esta classe gerencia o estado de curto prazo do agente para um usuário
    específico, conhecido como "Área de Trabalho Cognitiva". Ela é responsável
    por carregar e salvar o contexto atual da tarefa do usuário.
    """
    @abstractmethod
    def get_workspace(self, user_id: str) -> Optional[CognitiveWorkspace]:
        """Carrega a área de trabalho cognitiva de um usuário.

        Este método recupera o estado da sessão de um usuário, permitindo que
        o agente continue uma tarefa de onde parou.

        Args:
            user_id (str): O ID único do usuário.

        Returns:
            Optional[CognitiveWorkspace]: Um objeto `CognitiveWorkspace` com o
            estado da sessão, ou `None` se não houver sessão ativa para o
            usuário.
        """
        pass
    
    @abstractmethod
    def save_workspace(self, workspace: CognitiveWorkspace):
        """Salva o estado atual da área de trabalho cognitiva de um usuário.

        Args:
            workspace (CognitiveWorkspace): O objeto de área de trabalho
                contendo o estado atual a ser persistido.
        
        Returns:
            None: Esta função não retorna valor.
        """
        pass