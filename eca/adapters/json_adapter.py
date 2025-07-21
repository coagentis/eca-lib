# -*- coding: utf-8 -*-
import json
from dataclasses import asdict
from typing import List, Optional, Dict, Any, Type

# Importa os modelos e as interfaces base
from eca.models import Persona, PersonaConfig, CognitiveWorkspace
from eca.memory import SemanticMemory, EpisodicMemory
from eca.adapters.base import PersonaProvider, MemoryProvider, SessionProvider


class JSONPersonaProvider(PersonaProvider):
    """Implementação de `PersonaProvider` que lê dados de um arquivo JSON.

    Esta classe oferece uma maneira simples de carregar múltiplas personas
    a partir de um único arquivo JSON no início. É ideal para prototipagem,
    testes ou aplicações onde as personas são estáticas.

    Attributes:
        personas (Dict[str, Persona]): Um dicionário que armazena as instâncias
            de `Persona` em memória, usando o ID da persona como chave.
    """
    def __init__(self, file_path: str):
        """Inicializa o provedor carregando as personas do arquivo especificado.

        Args:
            file_path (str): O caminho para o arquivo JSON contendo a lista
                de definições de persona.
        """
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
        """Recupera uma persona da memória pelo seu ID.

        Args:
            persona_id (str): O ID da persona a ser buscada.

        Returns:
            Optional[Persona]: O objeto `Persona` correspondente, ou `None` se
            o ID não for encontrado.
        """
        return self.personas.get(persona_id)

    def detect_domain(self, user_input: str) -> str:
        """Detecta um domínio com base em palavras-chave na entrada do usuário.

        Esta é uma implementação simples e baseada em regras para roteamento.
        Para aplicações mais robustas, um modelo de classificação de texto
        seria mais apropriado.

        Args:
            user_input (str): O texto a ser analisado.

        Returns:
            str: O ID do domínio detectado ('fiscal', 'product_catalog' ou
            'default').
        """
        user_input_lower = user_input.lower()
        if any(kw in user_input_lower for kw in ["nota", "icms", "fiscal", "nfe", "nf-e"]):
            return "fiscal"
        if any(kw in user_input_lower for kw in ["produto", "cadastrar", "sku", "item"]):
            return "product_catalog"
        return "default"


class JSONMemoryProvider(MemoryProvider):
    """Gerencia memórias Semântica e Episódica usando arquivos JSON.

    Esta implementação de `MemoryProvider` persiste o conhecimento de longo
    prazo (semântico) e o histórico de conversas (episódico) em arquivos
    JSON separados. É adequada para testes e aplicações de pequena escala.

    Attributes:
        semantic_memories (List[SemanticMemory]): Lista de memórias semânticas
            carregadas em memória.
        episodic_log (List[EpisodicMemory]): Lista de interações de conversa
            carregadas em memória.
        episodic_path (str): Caminho para o arquivo de log episódico, usado
            para salvar novas interações.
    """
    def __init__(self, semantic_path: str, episodic_path: str):
        """Inicializa o provedor de memória carregando os arquivos JSON.

        Args:
            semantic_path (str): Caminho para o arquivo JSON de memória semântica.
            episodic_path (str): Caminho para o arquivo JSON de memória episódica.
        """
        self.semantic_memories: List[SemanticMemory] = self._load_json(semantic_path, SemanticMemory)
        self.episodic_log: List[EpisodicMemory] = self._load_json(episodic_path, EpisodicMemory)
        self.episodic_path = episodic_path

    def _load_json(self, file_path: str, model_class: Type) -> List[Any]:
        """Carrega e desserializa um arquivo JSON para uma lista de objetos.

        Args:
            file_path (str): O caminho do arquivo a ser lido.
            model_class (Type): A classe de modelo (ex: `SemanticMemory`) a ser
                instanciada para cada item no JSON.

        Returns:
            List[Any]: Uma lista de instâncias de `model_class`, ou uma lista
            vazia se o arquivo não for encontrado ou estiver malformado.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content:
                    return []
                data = json.loads(content)
                return [model_class(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def fetch_semantic_memories(self, user_input: str, domain_id: str, top_k: int = 3) -> List[SemanticMemory]:
        """Simula uma busca por memórias semânticas filtrando por domínio.

        Nota:
            Esta é uma simulação simplificada. Uma implementação de produção
            usaria técnicas de busca por similaridade de vetores (embeddings)
            em vez de apenas retornar os primeiros K itens.

        Args:
            user_input (str): A entrada do usuário (não utilizada nesta
                implementação simples).
            domain_id (str): O domínio para filtrar as memórias.
            top_k (int): O número máximo de memórias a retornar.

        Returns:
            List[SemanticMemory]: Uma lista de memórias filtradas.
        """
        domain_memories = [m for m in self.semantic_memories if m.domain_id == domain_id]
        return domain_memories[:top_k]

    def fetch_episodic_memories(self, user_id: str, domain_id: str, last_n: int = 5) -> List[EpisodicMemory]:
        """Recupera as últimas N interações de um usuário em um domínio.

        Args:
            user_id (str): O ID do usuário para filtrar o histórico.
            domain_id (str): O ID do domínio para filtrar o histórico.
            last_n (int): O número máximo de interações a retornar.

        Returns:
            List[EpisodicMemory]: O histórico de conversa filtrado.
        """
        user_domain_interactions = [
            inter for inter in self.episodic_log
            if inter.user_id == user_id and inter.domain_id == domain_id
        ]
        return user_domain_interactions[-last_n:]

    def log_interaction(self, interaction: EpisodicMemory):
        """Adiciona uma nova interação ao log e reescreve o arquivo JSON.

        Nota:
            Reescrever o arquivo inteiro a cada interação não é performático
            para logs grandes. Em produção, seria preferível um formato de
            append (JSON Lines) ou um banco de dados.

        Args:
            interaction (EpisodicMemory): A interação a ser salva.
        """
        self.episodic_log.append(interaction)
        data_to_save = [asdict(inter) for inter in self.episodic_log]
        with open(self.episodic_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)


class JSONSessionProvider(SessionProvider):
    """Implementação de `SessionProvider` que usa um arquivo JSON.

    Gerencia o `CognitiveWorkspace` de múltiplos usuários, armazenando
    todos eles em um único arquivo JSON, onde cada chave é um `user_id`.

    Attributes:
        file_path (str): O caminho para o arquivo JSON de sessões.
        sessions (Dict[str, Any]): Um dicionário em memória com os dados
            das sessões de todos os usuários.
    """
    def __init__(self, file_path: str):
        """Inicializa o provedor de sessão carregando o arquivo de sessões.

        Args:
            file_path (str): O caminho para o arquivo JSON de sessões.
        """
        self.file_path = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.sessions = json.loads(content) if content else {}
        except (FileNotFoundError, json.JSONDecodeError):
            self.sessions = {}

    def get_workspace(self, user_id: str) -> Optional[CognitiveWorkspace]:
        """Carrega a área de trabalho de um usuário a partir do cache em memória.

        Args:
            user_id (str): O ID do usuário cuja sessão será recuperada.

        Returns:
            Optional[CognitiveWorkspace]: O objeto `CognitiveWorkspace` se
            uma sessão existir, caso contrário, `None`.
        """
        user_session_data = self.sessions.get(user_id)
        if user_session_data:
            return CognitiveWorkspace(**user_session_data)
        return None

    def save_workspace(self, workspace: CognitiveWorkspace):
        """Salva a área de trabalho e reescreve o arquivo JSON de sessões.

        Nota:
            Assim como no `JSONMemoryProvider`, reescrever o arquivo inteiro
            pode não ser ideal para um número muito grande de usuários/sessões.

        Args:
            workspace (CognitiveWorkspace): O objeto de área de trabalho
                a ser salvo.
        """
        self.sessions[workspace.user_id] = asdict(workspace)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.sessions, f, indent=2, ensure_ascii=False)