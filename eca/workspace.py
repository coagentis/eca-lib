# -*- coding: utf-8 -*-
from .adapters.base import SessionProvider
from .models import CognitiveWorkspace, DomainState


class CognitiveWorkspaceManager:
    """Gerencia o ciclo de vida e as transições de estado da Área de Trabalho Cognitiva.

    Esta classe encapsula a lógica de negócios para manipular o objeto
    `CognitiveWorkspace`. Suas responsabilidades incluem criar ou carregar
    uma área de trabalho e gerenciar a troca de foco (atenção) entre
    diferentes domínios de conhecimento durante uma sessão de usuário.
    """

    def load_or_create(self, session_provider: SessionProvider, user_id: str) -> CognitiveWorkspace:
        """Carrega um workspace existente ou cria um novo para o usuário.

        Este método utiliza um `session_provider` para tentar recuperar a
        sessão de um usuário. Se nenhuma sessão for encontrada, uma nova e
        vazia `CognitiveWorkspace` é instanciada.

        Args:
            session_provider (SessionProvider): O provedor de dados responsável
                por carregar a sessão.
            user_id (str): O identificador único do usuário.

        Returns:
            CognitiveWorkspace: A área de trabalho cognitiva, seja ela
            carregada ou recém-criada.
        """
        workspace = session_provider.get_workspace(user_id)
        if not workspace:
            workspace = CognitiveWorkspace(user_id=user_id)
        return workspace

    def switch_focus(self, workspace: CognitiveWorkspace, new_domain_id: str) -> CognitiveWorkspace:
        """Muda o foco de atenção para um novo domínio, pausando o anterior.

        Esta função gerencia a transição de estado ao mudar de um domínio para
        outro. Ela garante que o domínio anteriormente ativo seja marcado como
        'paused' e que o novo domínio de foco seja criado (se não existir) e
        marcado como 'active'.

        Args:
            workspace (CognitiveWorkspace): A área de trabalho a ser modificada.
            new_domain_id (str): O identificador do novo domínio que receberá o
                foco.

        Returns:
            CognitiveWorkspace: A mesma instância da área de trabalho, agora com
            o foco e os estados dos domínios atualizados.
        """
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