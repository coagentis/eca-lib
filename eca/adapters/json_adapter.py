# -*- coding: utf-8 -*-

import json
from dataclasses import asdict
from typing import List, Optional, Dict, Any, Type

# Importa os modelos e as interfaces base
from eca.models import Persona, PersonaConfig, CognitiveWorkspace
from eca.memory import SemanticMemory, EpisodicMemory
from eca.adapters.base import PersonaProvider, MemoryProvider, SessionProvider

# A classe JSONPersonaProvider permanece a mesma de antes.
class JSONPersonaProvider(PersonaProvider):
    """Implementação de Provedor de Persona que lê de um arquivo JSON."""
    def __init__(self, file_path: str):
        self.personas: Dict[str, Persona] = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for p_data in data:
                config = PersonaConfig(**p_data['persona_config'])
                self.personas[p_data['id']] = Persona(
                    id=p_data['id'],
                    name=p_data['name'],
                    semantic_description=p_data['semantic_description'],
                    config=config
                )

    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        return self.personas.get(persona_id)

    def detect_domain(self, user_input: str) -> str:
        user_input_lower = user_input.lower()
        if any(kw in user_input_lower for kw in ["nota", "icms", "fiscal", "nfe", "nf-e"]):
            return "fiscal"
        if any(kw in user_input_lower for kw in ["produto", "cadastrar", "sku", "item"]):
            return "product_catalog"
        return "default"

class JSONMemoryProvider(MemoryProvider):
    """
    Implementação que gerencia memória Semântica e Episódica 
    em arquivos JSON separados.
    """
    def __init__(self, semantic_path: str, episodic_path: str):
        # Carrega as memórias semânticas (fatos, regras)
        self.semantic_memories: List[SemanticMemory] = self._load_json(semantic_path, SemanticMemory)
        
        # Carrega as memórias episódicas (histórico de conversas)
        self.episodic_log: List[EpisodicMemory] = self._load_json(episodic_path, EpisodicMemory)
        self.episodic_path = episodic_path

    def _load_json(self, file_path: str, model_class: Type) -> List[Any]:
        """Função auxiliar para carregar um arquivo JSON e converter em objetos."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Garante que o arquivo não esteja vazio
                content = f.read()
                if not content:
                    return []
                data = json.loads(content)
                return [model_class(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def fetch_semantic_memories(self, user_input: str, domain_id: str, top_k: int = 3) -> List[SemanticMemory]:
        # Simulação de busca. Em produção, usaria embeddings para similaridade.
        domain_memories = [m for m in self.semantic_memories if m.domain_id == domain_id]
        return domain_memories[:top_k] # Retorna as primeiras K para o exemplo

    def fetch_episodic_memories(self, user_id: str, domain_id: str, last_n: int = 5) -> List[EpisodicMemory]:
        # Filtra o log para o usuário E para o domínio específico.
        user_domain_interactions = [
            inter for inter in self.episodic_log 
            if inter.user_id == user_id and inter.domain_id == domain_id
        ]
        
        # Pega as últimas N interações desse histórico filtrado.
        return user_domain_interactions[-last_n:]

    def log_interaction(self, interaction: EpisodicMemory):
        # Adiciona a nova interação ao log em memória
        self.episodic_log.append(interaction)
        # Converte a lista completa de objetos de volta para uma lista de dicionários
        data_to_save = [asdict(inter) for inter in self.episodic_log]
        # Salva o arquivo JSON completo
        with open(self.episodic_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)

class JSONSessionProvider(SessionProvider):
    """Implementação de Provedor de Sessão que lê e escreve em um arquivo JSON."""
    def __init__(self, file_path: str):
        self.file_path = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.sessions = json.loads(content) if content else {}
        except (FileNotFoundError, json.JSONDecodeError):
            self.sessions = {}

    def get_workspace(self, user_id: str) -> Optional[CognitiveWorkspace]:
        user_session_data = self.sessions.get(user_id)
        if user_session_data:
            return CognitiveWorkspace(**user_session_data)
        return None

    def save_workspace(self, workspace: CognitiveWorkspace):
        self.sessions[workspace.user_id] = asdict(workspace)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.sessions, f, indent=2, ensure_ascii=False)