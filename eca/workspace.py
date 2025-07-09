# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Dict

from eca.models import CognitiveWorkspace, DomainState

class CognitiveWorkspaceManager:
    """Gerencia o ciclo de vida e o estado da Área de Trabalho Cognitiva."""

    def load_or_create(self, session_provider, user_id: str) -> CognitiveWorkspace:
        """Carrega um workspace existente ou cria um novo para o usuário."""
        workspace = session_provider.get_workspace(user_id)
        if not workspace:
            workspace = CognitiveWorkspace(user_id=user_id)
        return workspace

    def switch_focus(self, workspace: CognitiveWorkspace, new_domain_id: str) -> CognitiveWorkspace:
        """Muda o foco para um novo domínio, pausando o anterior."""
        
        # Pausa o domínio que estava ativo anteriormente
        if workspace.current_focus in workspace.active_domains:
            workspace.active_domains[workspace.current_focus].status = "paused"
            
        # Define o novo foco
        workspace.current_focus = new_domain_id
        
        # Cria ou ativa o estado do novo domínio
        if new_domain_id not in workspace.active_domains:
            workspace.active_domains[new_domain_id] = DomainState()
        
        workspace.active_domains[new_domain_id].status = "active"
        
        return workspace