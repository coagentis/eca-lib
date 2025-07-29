# -*- coding: utf-8 -*-
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
import importlib.resources

from .adapters.base import (
    PersonaProvider, MemoryProvider, SessionProvider, Tool, DataFormatter
)
from .workspace import CognitiveWorkspaceManager
from .models import CognitiveWorkspace, PersonaConfig # Importar PersonaConfig para type hints
from .attention import AttentionMechanism, PassthroughAttention


class ECAOrchestrator:
    """
    O orquestrador principal da arquitetura ECA (Engenharia de Contexto Aumentada).

    Esta classe é o ponto central que integra todos os componentes da
    arquitetura. Sua principal responsabilidade é processar a entrada de um
    usuário (texto e/ou anexos), construir um contexto rico e dinâmico usando
    memória, personas e ferramentas externas, e gerar um prompt final
    otimizado para ser enviado a um Modelo de Linguagem Grande (LLM).
    
    Attributes:
        persona_provider (PersonaProvider): Provedor para carregar e detectar personas.
        memory_provider (MemoryProvider): Provedor para acesso às memórias semântica e episódica.
        session_provider (SessionProvider): Provedor para persistir o estado da sessão.
        semantic_attention (AttentionMechanism): Mecanismo para rankear memórias semânticas.
        episodic_attention (AttentionMechanism): Mecanismo para rankear memórias episódicas.
        workspace_manager (CognitiveWorkspaceManager): Gerenciador do estado da área de trabalho.
        tools (List[Tool]): Lista de ferramentas externas disponíveis para carregar dados.
        data_formatters (Dict[str, DataFormatter]): Mapeamento de formatadores para
            processar os dados retornados pelas ferramentas.
        meta_prompt_template (str): O template mestre do prompt.
    """

    def __init__(
        self,
        persona_provider: PersonaProvider,
        memory_provider: MemoryProvider,
        session_provider: SessionProvider,
        prompt_language: str = "pt_br",
        meta_prompt_path_override: Optional[str] = None,
        semantic_attention: Optional[AttentionMechanism] = None,
        episodic_attention: Optional[AttentionMechanism] = None,
        tools: Optional[List[Tool]] = None,
        data_formatters: Optional[Dict[str, DataFormatter]] = None,
    ):
        """Inicializa o Orquestrador com todas as suas dependências."""
        self.persona_provider = persona_provider
        self.memory_provider = memory_provider
        self.session_provider = session_provider
        self.semantic_attention = semantic_attention or PassthroughAttention()
        self.episodic_attention = episodic_attention or PassthroughAttention()
        self.workspace_manager = CognitiveWorkspaceManager()
        self.tools = tools if tools else []
        self.data_formatters = data_formatters if data_formatters else {}

        if meta_prompt_path_override:
            with open(meta_prompt_path_override, 'r', encoding='utf-8') as f:
                self.meta_prompt_template = f.read()
        else:
            try:
                filename = f"meta_prompt_template_{prompt_language}.txt"
                prompt_ref = importlib.resources.files('eca').joinpath('prompts', filename)
                with prompt_ref.open('r', encoding='utf-8') as f:
                    self.meta_prompt_template = f.read()
            except FileNotFoundError:
                raise ValueError(
                    f"O template de prompt padrão para o idioma '{prompt_language}' não foi encontrado."
                )

    def generate_context_object(
        self,
        user_id: str,
        user_input: str,
        attachment: Optional[Any] = None,
        tool_execution_mode: str = 'first_match'
    ) -> CognitiveWorkspace:
        """Processa uma entrada e retorna o objeto `CognitiveWorkspace` completo."""
        workspace = self.workspace_manager.load_or_create(self.session_provider, user_id)
        detected_domain = self.persona_provider.detect_domain(user_input)
        workspace = self.workspace_manager.switch_focus(workspace, detected_domain)

        active_domain_state = workspace.active_domains[detected_domain]
        active_domain_state.active_task = f"Analisando a solicitação '{user_input[:50]}...' para o domínio '{detected_domain}'."

        all_semantic_memories = self.memory_provider.fetch_semantic_memories(user_input, domain_id=detected_domain)
        all_episodic_memories = self.memory_provider.fetch_episodic_memories(user_id, domain_id=detected_domain)

        ranked_semantic = self.semantic_attention.rank(user_input, all_semantic_memories)
        ranked_episodic = self.episodic_attention.rank(user_input, all_episodic_memories)

        active_domain_state.semantic_memories = ranked_semantic[:3]
        active_domain_state.episodic_memories = ranked_episodic[:5]
        active_domain_state.task_data = self._run_tool(user_input, attachment, mode=tool_execution_mode)

        self.session_provider.save_workspace(workspace)
        return workspace

    def generate_final_prompt(
        self,
        user_id: str,
        user_input: str,
        attachment: Optional[Any] = None,
        tool_execution_mode: str = 'first_match'
    ) -> str:
        """Orquestra o fluxo completo e retorna o prompt final para o LLM."""
        context_object = self.generate_context_object(user_id, user_input, attachment, tool_execution_mode)
        dynamic_context_str = self._flatten_context_to_string(context_object, user_input)
        final_prompt = self.meta_prompt_template.replace("{{DYNAMIC_CONTEXT}}", dynamic_context_str)
        return final_prompt

    def _flatten_context_to_string(self, workspace: CognitiveWorkspace, user_input: str) -> str:
        """Converte o objeto `CognitiveWorkspace` em uma string de contexto formatada."""
        active_domain_id = workspace.current_focus
        active_domain_state = workspace.active_domains.get(active_domain_id)
        persona = self.persona_provider.get_persona_by_id(active_domain_id)

        if not persona:
            return f"[ERROR: Persona com id '{active_domain_id}' não encontrada.]"

        context_parts = []
        # Adicionamos um type hint para o config para facilitar o acesso aos novos campos
        config: PersonaConfig = persona.config 

        # --- CONSTRUÇÃO DO PROMPT  ---
        context_parts.append(f"[TIMESTAMP:{datetime.now().isoformat()}]")
        context_parts.append(f"[IDENTITY:{persona.name}|{persona.id.upper()}|OBJECTIVE:{config.objective}]")
        
        if config.tone_of_voice:
            context_parts.append(f"[TONE_OF_VOICE:{', '.join(config.tone_of_voice)}]")
        
        if config.verbosity and config.verbosity != "normal":
             context_parts.append(f"[VERBOSITY:{config.verbosity}]")

        if config.output_format:
            context_parts.append(f"[OUTPUT_FORMAT:{config.output_format}]")
            
        if config.forbidden_topics:
            context_parts.append(f"[FORBIDDEN_TOPICS:{', '.join(config.forbidden_topics)}]")

        if config.golden_rules:
            rules_str = "\n".join([f"- {rule}" for rule in config.golden_rules])
            context_parts.append(f"[GOLDEN_RULES:\n{rules_str}]")

        context_parts.append(f"[USER:{workspace.user_id}]")

        if active_domain_state and active_domain_state.episodic_memories:
            history_str = "\n".join(
                [f"User: {mem.user_input}\nAssistant: {mem.assistant_output}" for mem in active_domain_state.episodic_memories]
            )
            context_parts.append(f"[RECENT_HISTORY:\n{history_str}]")

        if active_domain_state:
            context_parts.append(f"[CURRENT_SESSION:{active_domain_state.session_summary or 'Iniciando nova tarefa.'}]")
            context_parts.append(f"[ACTIVE_TASK:{active_domain_state.active_task}]")

            for i, mem in enumerate(active_domain_state.semantic_memories):
                context_parts.append(f"[RELEVANT_MEMORY_{i+1}:{mem.text_content}]")

            if active_domain_state.task_data:
                task_data = active_domain_state.task_data
                
                if isinstance(task_data, list):
                    for tool_result in task_data:
                        tool_name = tool_result.get("source_tool", "data")
                        data_to_format = tool_result.get("data", {})
                        
                        formatter = self.data_formatters.get(active_domain_id)
                        data_summary = formatter(data_to_format) if formatter else data_to_format
                        context_parts.append(f"[INPUT_DATA_{tool_name.upper()}:{json.dumps(data_summary, ensure_ascii=False)}]")

                elif isinstance(task_data, dict):
                    # No modo 'first_match', a tag não precisa do nome da ferramenta para ser mais limpa
                    formatter = self.data_formatters.get(active_domain_id)
                    task_data_summary = formatter(task_data) if formatter else task_data
                    context_parts.append(f"[INPUT_DATA:{json.dumps(task_data_summary, ensure_ascii=False)}]")

        context_parts.append(f"[USER_INPUT:\"{user_input}\"]")
        return "\n".join(context_parts)

    def _run_tool(self, user_input: str, attachment: Optional[Any] = None, mode: str = 'first_match') -> Optional[Any]:
        """Busca e executa ferramentas compatíveis com base no modo de execução."""
        if mode == 'first_match':
            for tool in self.tools:
                if tool.can_handle(user_input, attachment):
                    return tool.load(user_input, attachment)
            return None

        elif mode == 'all_matches':
            executed_results = []
            for tool in self.tools:
                if tool.can_handle(user_input, attachment):
                    result = tool.load(user_input, attachment)
                    if result:
                        tool_name = getattr(tool, 'name', tool.__class__.__name__)
                        executed_results.append({"source_tool": tool_name, "data": result})
            
            return executed_results if executed_results else None
        
        raise ValueError(f"Modo de execução de ferramenta desconhecido: '{mode}'")