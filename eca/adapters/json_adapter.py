# -*- coding: utf-8 -*-

import json
from dataclasses import asdict 
from typing import List, Optional, Dict

from eca.models import Persona, PersonaConfig, Memory, CognitiveWorkspace
from eca.adapters.base import PersonaProvider, MemoryProvider, SessionProvider

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
        # Retorna a persona carregada do dicionário.
        return self.personas.get(persona_id)

    def detect_domain(self, user_input: str) -> str:
        # Lógica de detecção de domínio simples baseada em palavras-chave.
        # Em produção, isso vai usar a 'semantic_description' e embeddings.
        user_input_lower = user_input.lower()
        if any(kw in user_input_lower for kw in ["nota", "icms", "fiscal", "nfe"]):
            return "fiscal"
        if any(kw in user_input_lower for kw in ["produto", "cadastrar", "sku"]):
            return "product_catalog"
        return "default"

class JSONMemoryProvider(MemoryProvider):
    """Implementação de Provedor de Memória que lê de um arquivo JSON."""
    def __init__(self, file_path: str):
        self.memories: List[Memory] = []
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for m_data in data:
                self.memories.append(Memory(**m_data))

    def fetch_relevant_memories(self, user_input: str, domain_id: str, top_k: int = 3) -> List[Memory]:
        # Simulação de busca. Filtra por domínio e depois por keywords na entrada.
        # Em produção, aqui será a busca vetorial no embedding.
        domain_memories = [m for m in self.memories if m.domain_id == domain_id]
        # Lógica de relevância simplificada
        relevant = [m for m in domain_memories if any(word in m.text_content.lower() for word in user_input.lower().split())]
        return relevant[:top_k]

class JSONSessionProvider(SessionProvider):
    """Implementação de Provedor de Sessão que lê e escreve em um arquivo JSON."""
    def __init__(self, file_path: str):
        self.file_path = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.sessions = json.load(f)
        except FileNotFoundError:
            self.sessions = {}

    def get_workspace(self, user_id: str) -> Optional[CognitiveWorkspace]:
        # Carrega os dados da sessão do usuário se existirem.
        user_session_data = self.sessions.get(user_id)
        if user_session_data:
            # Recria o objeto a partir do dicionário
            return CognitiveWorkspace(**user_session_data)
        return None

    def save_workspace(self, workspace: CognitiveWorkspace):
        # Converte o objeto de volta para um dicionário para salvar no JSON.
        self.sessions[workspace.user_id] = asdict(workspace)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.sessions, f, indent=2, ensure_ascii=False)