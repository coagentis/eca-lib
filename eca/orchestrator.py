import json
import os
from datetime import datetime
from typing import Any, Callable, Dict, Optional
from .adapters.base import PersonaProvider, MemoryProvider, SessionProvider
from .workspace import CognitiveWorkspaceManager
from .models import CognitiveWorkspace

class ECAOrchestrator:
    """O Orquestrador principal da arquitetura ECA."""

    def __init__(
        self,
        persona_provider: PersonaProvider,
        memory_provider: MemoryProvider,
        session_provider: SessionProvider,
        meta_prompt_template_path: str,
        knowledge_base_path: str,
        data_handlers: Optional[Dict[str, Callable[[Dict], Any]]] = None
    ):
        """
        Inicializa o Orquestrador com os provedores de dados e o template mestre.
        """
        self.persona_provider = persona_provider
        self.memory_provider = memory_provider
        self.session_provider = session_provider
        self.workspace_manager = CognitiveWorkspaceManager()
        self.knowledge_base_path = knowledge_base_path
        self.data_handlers = data_handlers if data_handlers else {}
        with open(meta_prompt_template_path, 'r', encoding='utf-8') as f:
            self.meta_prompt_template = f.read()

    def generate_context_object(self, user_id: str, user_input: str) -> CognitiveWorkspace:
        """
        Processa uma entrada e retorna o objeto CognitiveWorkspace completo.
        Útil para debugging, logging ou para usuários avançados que queiram
        construir seus próprios prompts.
        """
        # Etapa 1: Carrega ou cria a área de trabalho do usuário.
        workspace = self.workspace_manager.load_or_create(self.session_provider, user_id)

        # Etapa 2: Detecta o domínio e gerencia o foco na área de trabalho.
        detected_domain = self.persona_provider.detect_domain(user_input)
        workspace = self.workspace_manager.switch_focus(workspace, detected_domain)
        
        active_domain_state = workspace.active_domains[detected_domain]
        
        # Etapa 3: Busca memórias e dados externos relevantes.
        active_domain_state.relevant_memories = self.memory_provider.fetch_relevant_memories(
            user_input=user_input,
            domain_id=detected_domain
        )
        active_domain_state.active_task = f"Analisando a solicitação '{user_input[:50]}...'"
        active_domain_state.task_data = self._load_task_data(user_input)

        # Etapa 4: Salva o novo estado da sessão.
        self.session_provider.save_workspace(workspace)
        
        return workspace

    def generate_final_prompt(self, user_id: str, user_input: str) -> str:
        """
        Método de conveniência que orquestra todo o fluxo e retorna o prompt
        final, formatado e pronto para ser enviado a um LLM.
        """
        # Etapa 1: Usa o método de baixo nível para obter o objeto de contexto.
        context_object = self.generate_context_object(user_id, user_input)
        
        # Etapa 2: "Achata" o objeto em uma string otimizada.
        dynamic_context_str = self._flatten_context_to_string(context_object, user_input)
        
        # Etapa 3: Injeta a string de contexto no template mestre.
        final_prompt = self.meta_prompt_template.replace("{{DYNAMIC_CONTEXT}}", dynamic_context_str)
        
        return final_prompt

    # --- Métodos Internos (Helpers) ---
    def _flatten_context_to_string(self, workspace: CognitiveWorkspace, user_input: str) -> str:
        """
        Pega o objeto de workspace e o "achata" em uma string de contexto otimizada.
        """
        context_str = ""
        active_domain_id = workspace.current_focus
        active_domain_state = workspace.active_domains.get(active_domain_id)
        persona = self.persona_provider.get_persona_by_id(active_domain_id)
        
        # Se a persona não for encontrada por algum motivo, retorna um erro claro.
        if not persona:
            return f"[ERROR: Persona com id '{active_domain_id}' não encontrada.]"

        # --- A LÓGICA REATORADA, COMO VOCÊ SUGERIU ---
        # 1. Pegamos o objeto de configuração para facilitar o acesso.
        config = persona.config
        user_details = workspace.user_id

        # 2. Montamos os tokens usando o 'config' para as informações da persona.
        context_str += f"[TIMESTAMP:{datetime.now().isoformat()}]\n"
        context_str += f"[IDENTITY:{persona.name}|{persona.id.upper()}]\n"
        context_str += f"[OBJECTIVE:{config.objective}]\n"
        
        if config.golden_rules:
            rules_str = "\\n".join([f"- {rule}" for rule in config.golden_rules])
            context_str += f"[GOLDEN_RULES:\\n{rules_str}]\n"
        # ---------------------------------------------
        
        context_str += f"[USER:{user_details}]\n"
        context_str += f"[CURRENT_SESSION:{active_domain_state.session_summary or 'Initiating new task.'}]\n"
        context_str += f"[ACTIVE_TASK:{active_domain_state.active_task}]\n"

        for i, mem in enumerate(active_domain_state.relevant_memories):
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
        
    def _load_task_data(self, user_input: str) -> dict | None:
        """Simula a busca por dados externos."""
        if "78910" in user_input:
            file_path = os.path.join(self.knowledge_base_path, 'nfe_78910.json')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except FileNotFoundError:
                return {"error": "NF-e 78910 não encontrada."}
        return None