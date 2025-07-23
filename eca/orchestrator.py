# eca/orchestrator.py
import json
import os
from datetime import datetime
from typing import Any, Callable, Dict, Optional
import importlib.resources  

from .adapters.base import PersonaProvider, MemoryProvider, SessionProvider
from .workspace import CognitiveWorkspaceManager
from .models import CognitiveWorkspace
from .attention import AttentionMechanism, PassthroughAttention


class ECAOrchestrator:
    """O orquestrador principal da arquitetura ECA "Engenharia de Contexto Aumentada (Augmented Context Engineering)".

    Esta classe é o ponto central que integra todos os componentes da
    arquitetura: provedores de dados, mecanismos de atenção e gerenciamento
    de estado. Sua principal responsabilidade é processar a entrada de um
    usuário, construir um contexto rico e dinâmico, e gerar um prompt final
    otimizado para ser enviado a um Modelo de Linguagem Grande (LLM).

    Attributes:
        persona_provider (PersonaProvider): Provedor para carregar personas.
        memory_provider (MemoryProvider): Provedor para acesso às memórias.
        session_provider (SessionProvider): Provedor para persistir o estado.
        semantic_attention (AttentionMechanism): Mecanismo para rankear
            memórias semânticas.
        episodic_attention (AttentionMechanism): Mecanismo para rankear
            memórias episódicas.
        workspace_manager (CognitiveWorkspaceManager): Gerenciador do estado
            da área de trabalho cognitiva.
        knowledge_base_path (str): Caminho para a base de dados externa.
        data_handlers (Dict[str, Callable]): Funções para processar dados de
            tarefas específicas.
        meta_prompt_template (str): O template mestre do prompt.
    """

    def __init__(
        self,
        persona_provider: PersonaProvider,
        memory_provider: MemoryProvider,
        session_provider: SessionProvider,
        knowledge_base_path: str,
        prompt_language: str = "pt_br",
        meta_prompt_path_override: Optional[str] = None,
        semantic_attention: Optional[AttentionMechanism] = None,
        episodic_attention: Optional[AttentionMechanism] = None,
        data_handlers: Optional[Dict[str, Callable[[Dict], Any]]] = None
    ):
        """Inicializa o Orquestrador com todas as suas dependências.

        Args:
            persona_provider (PersonaProvider): Instância de um provedor de persona.
            memory_provider (MemoryProvider): Instância de um provedor de memória.
            session_provider (SessionProvider): Instância de um provedor de sessão.
            knowledge_base_path (str): Caminho para o diretório da base de conhecimento.
            prompt_language (str, optional): O idioma do template de prompt padrão
                a ser carregado de dentro do pacote. Padrão é "pt_BR".
            meta_prompt_path_override (Optional[str], optional): O caminho completo para
                um arquivo de template customizado. Se fornecido, ele ignora o
                `prompt_language`. Padrão é `None`.
            semantic_attention (Optional[AttentionMechanism], optional): Mecanismo para
                rankear memórias semânticas. Padrão é `PassthroughAttention`.
            episodic_attention (Optional[AttentionMechanism], optional): Mecanismo para
                rankear memórias episódicas. Padrão é `PassthroughAttention`.
            data_handlers (Optional[Dict[str, Callable[[Dict], Any]]], optional): Funções
                para pré-processar dados de tarefas. Padrão é `None`.
        """
        self.persona_provider = persona_provider
        self.memory_provider = memory_provider
        self.session_provider = session_provider
        self.semantic_attention = semantic_attention or PassthroughAttention()
        self.episodic_attention = episodic_attention or PassthroughAttention()
        self.workspace_manager = CognitiveWorkspaceManager()
        self.knowledge_base_path = knowledge_base_path
        self.data_handlers = data_handlers if data_handlers else {}

        if meta_prompt_path_override:
            # Se um caminho customizado for fornecido, use-o.
            with open(meta_prompt_path_override, 'r', encoding='utf-8') as f:
                self.meta_prompt_template = f.read()
        else:
            # Caso contrário, carregue o prompt padrão com base no idioma.
            try:
                filename = f"meta_prompt_template_{prompt_language}.txt"
                # Usa importlib.resources para encontrar o arquivo DENTRO do pacote instalado
                prompt_ref = importlib.resources.files('eca').joinpath('prompts', filename)
                with prompt_ref.open('r', encoding='utf-8') as f:
                    self.meta_prompt_template = f.read()
            except FileNotFoundError:
                raise ValueError(
                    f"O template de prompt padrão para o idioma '{prompt_language}' não foi encontrado. "
                    "Verifique se o arquivo 'meta_prompt_template_{prompt_language}.txt' existe na pasta 'eca/prompts'."
                )

    def generate_context_object(self, user_id: str, user_input: str) -> CognitiveWorkspace:
        """Processa uma entrada e retorna o objeto `CognitiveWorkspace` completo.

        Este método de baixo nível executa todo o pipeline de construção de
        contexto: carrega a sessão, detecta o domínio, gerencia o foco, busca
        e rankeia memórias, e carrega dados externos. O objeto retornado
        contém o estado completo e atualizado da sessão do usuário.

        É útil para depuração, logging ou para usuários avançados que queiram
        construir seus próprios prompts a partir do estado bruto.

        Args:
            user_id (str): O identificador único do usuário.
            user_input (str): O texto fornecido pelo usuário.

        Returns:
            CognitiveWorkspace: O objeto de área de trabalho cognitiva,
            preenchido e atualizado com o contexto mais recente.
        """
        workspace = self.workspace_manager.load_or_create(self.session_provider, user_id)
        detected_domain = self.persona_provider.detect_domain(user_input)
        workspace = self.workspace_manager.switch_focus(workspace, detected_domain)
        
        active_domain_state = workspace.active_domains[detected_domain]
        active_domain_state.active_task = f"Analisando a solicitação '{user_input[:50]}...' para o domínio '{detected_domain}'."
        
        all_semantic_memories = self.memory_provider.fetch_semantic_memories(
            user_input=user_input, 
            domain_id=detected_domain
        )
        all_episodic_memories = self.memory_provider.fetch_episodic_memories(
            user_id=user_id, 
            domain_id=detected_domain
        )

        ranked_semantic = self.semantic_attention.rank(user_input, all_semantic_memories)
        ranked_episodic = self.episodic_attention.rank(user_input, all_episodic_memories)

        active_domain_state.semantic_memories = ranked_semantic[:3]
        active_domain_state.episodic_memories = ranked_episodic[:5]
        active_domain_state.task_data = self._load_task_data(user_input)

        self.session_provider.save_workspace(workspace)
        
        return workspace

    def generate_final_prompt(self, user_id: str, user_input: str) -> str:
        """Orquestra o fluxo completo e retorna o prompt final para o LLM.

        Este é o principal método de conveniência da classe. Ele abstrai toda
        a complexidade da construção de contexto e retorna uma string única,
        formatada e pronta para ser enviada a um modelo de linguagem.

        Args:
            user_id (str): O identificador único do usuário.
            user_input (str): O texto fornecido pelo usuário.

        Returns:
            str: O prompt final, formatado e contextualizado.
        """
        context_object = self.generate_context_object(user_id, user_input)
        dynamic_context_str = self._flatten_context_to_string(context_object, user_input)
        final_prompt = self.meta_prompt_template.replace("{{DYNAMIC_CONTEXT}}", dynamic_context_str)
        
        return final_prompt

    def _flatten_context_to_string(self, workspace: CognitiveWorkspace, user_input: str) -> str:
        """Converte o objeto `CognitiveWorkspace` em uma string de contexto.

        Este método "achata" o estado estruturado da área de trabalho em uma
        string formatada com tags especiais (ex: `[IDENTITY:...]`), que será
        injetada no template mestre do prompt.

        Args:
            workspace (CognitiveWorkspace): O objeto de estado da sessão.
            user_input (str): A entrada original do usuário.

        Returns:
            str: Uma string única representando todo o contexto dinâmico.
        """
        context_str = ""
        active_domain_id = workspace.current_focus
        active_domain_state = workspace.active_domains.get(active_domain_id)
        persona = self.persona_provider.get_persona_by_id(active_domain_id)
        
        if not persona:
            return f"[ERROR: Persona com id '{active_domain_id}' não encontrada.]"

        config = persona.config
        user_details = workspace.user_id

        context_str += f"[TIMESTAMP:{datetime.now().isoformat()}]\n"
        context_str += f"[IDENTITY:{persona.name}|{persona.id.upper()}]\n"
        context_str += f"[OBJECTIVE:{config.objective}]\n"
        
        if config.golden_rules:
            rules_str = "\\n".join([f"- {rule}" for rule in config.golden_rules])
            context_str += f"[GOLDEN_RULES:\\n{rules_str}]\n"
        
        context_str += f"[USER:{user_details}]\n"
        
        if active_domain_state and active_domain_state.episodic_memories:
            history_str = "\\n".join(
                [f"User: {mem.user_input}\\nAssistant: {mem.assistant_output}" for mem in active_domain_state.episodic_memories]
            )
            context_str += f"[RECENT_HISTORY:\\n{history_str}]\\n"
        
        if active_domain_state:
            context_str += f"[CURRENT_SESSION:{active_domain_state.session_summary or 'Initiating new task.'}]\n"
            context_str += f"[ACTIVE_TASK:{active_domain_state.active_task}]\n"

            for i, mem in enumerate(active_domain_state.semantic_memories):
                context_str += f"[RELEVANT_MEMORY_{i+1}:{mem.text_content}]\n"

            if active_domain_state.task_data:
                handler = self.data_handlers.get(active_domain_id)
                if handler:
                    task_data_summary = handler(active_domain_state.task_data)
                else:
                    task_data_summary = active_domain_state.task_data
                context_str += f"[INPUT_DATA: {json.dumps(task_data_summary, ensure_ascii=False)}]\n"

        context_str += f"[USER_INPUT: \"{user_input}\"]"
        
        return context_str
        
    def _load_task_data(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Busca dados externos com base em palavras-chave na entrada.

        Nota:
            Esta é uma simulação para fins de exemplo. Uma implementação real
            teria uma lógica mais robusta para identificar e carregar dados
            relevantes a partir de fontes externas.

        Args:
            user_input (str): O texto do usuário.

        Returns:
            Optional[Dict[str, Any]]: Um dicionário com os dados carregados ou
            `None` se nenhum dado for encontrado.
        """
        if "78910" in user_input:
            file_path = os.path.join(self.knowledge_base_path, 'nfe_78910.json')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except FileNotFoundError:
                return {"error": "NF-e 78910 não encontrada."}
        return None