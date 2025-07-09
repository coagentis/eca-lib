# -*- coding: utf-8 -*-

from eca.adapters.base import PersonaProvider, MemoryProvider, SessionProvider
from eca.workspace import CognitiveWorkspaceManager

class ECAOrchestrator:
    """O Orquestrador principal da arquitetura ECA."""

    def __init__(
        self,
        persona_provider: PersonaProvider,
        memory_provider: MemoryProvider,
        session_provider: SessionProvider
    ):
        """
        Inicializa o Orquestrador com os provedores de dados necessários (Injeção de Dependência).
        """
        self.persona_provider = persona_provider
        self.memory_provider = memory_provider
        self.session_provider = session_provider
        self.workspace_manager = CognitiveWorkspaceManager()

    def generate_dynamic_context(self, user_id: str, user_input: str) -> dict:
        """
        Processa uma entrada do usuário e gera o objeto de contexto dinâmico completo.
        Este é o método principal que encapsula a lógica da ECA.
        """
        # 1. Carrega ou cria a área de trabalho do usuário.
        workspace = self.workspace_manager.load_or_create(self.session_provider, user_id)

        # 2. Detecta o domínio da nova entrada.
        detected_domain = self.persona_provider.detect_domain(user_input)

        # 3. Gerencia o foco na área de trabalho.
        workspace = self.workspace_manager.switch_focus(workspace, detected_domain)
        active_domain_state = workspace.active_domains[detected_domain]

        # 4. Busca memórias relevantes para o domínio em foco.
        relevant_memories = self.memory_provider.fetch_relevant_memories(
            user_input=user_input,
            domain_id=detected_domain
        )
        active_domain_state.relevant_memories = relevant_memories
        
        # 5. Atualiza a tarefa ativa no estado do domínio.
        active_domain_state.active_task = f"Processing user input: '{user_input[:50]}...'"
        
        # 6. Salva o estado atualizado do workspace.
        self.session_provider.save_workspace(workspace)

        # 7. Retorna o estado completo como um dicionário.
        # Este é o objeto que será usado para montar o prompt final.
        return workspace.__dict__