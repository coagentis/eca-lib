# -*- coding: utf-8 -*-
"""
Adaptadores de produção para a eca-lib que utilizam PostgreSQL e SQLAlchemy ORM.

Este módulo fornece implementações concretas das interfaces base de provedores,
utilizando um banco de dados PostgreSQL para persistência de dados. Inclui
suporte para a extensão `pgvector` para buscas semânticas de alta performance.
"""

from typing import List, Optional, Callable

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from pgvector.sqlalchemy import Vector
except ImportError:
    raise ImportError(
        "Pacotes para suporte a SQLAlchemy/PostgreSQL não encontrados. "
        "Por favor, instale a eca-lib com o extra para PostgreSQL: pip install 'eca-lib[postgres]'"
    )

from ..database.schema import get_schema_models
from ..models import Persona, PersonaConfig
from ..memory import SemanticMemory, EpisodicMemory
from .base import PersonaProvider, MemoryProvider


class PostgresPersonaProvider(PersonaProvider):
    """
    Implementação de `PersonaProvider` que usa SQLAlchemy ORM para o PostgreSQL.
    Gerencia as identidades (personas) do agente a partir de uma tabela
    relacional, permitindo um controle robusto e dinâmico sobre os perfis
    que a IA pode assumir.
    """
    def __init__(self, dsn: str, embedding_function: Callable[[str], List[float]], vector_dimension: int, auto_setup: bool = False):
        """
        Inicializa o provedor, a conexão com o banco e, opcionalmente, o schema.

        Args:
            dsn (str): A string de conexão do banco de dados (DSN).
                Ex: "postgresql://user:password@host:port/database"
            embedding_function (Callable): Função que converte texto em um vetor.
            vector_dimension (int): A dimensão dos vetores de embedding (ex: 384, 1536).
            auto_setup (bool, optional): Se True, cria as tabelas da ECA no
                banco de dados se elas não existirem. Útil para desenvolvimento
                e testes. Em produção, recomenda-se gerenciar o schema com
                ferramentas de migração como Alembic. Padrão é False.
        """
        self.engine = create_engine(dsn)
        self.Session = sessionmaker(bind=self.engine)
        self.embed = embedding_function
        
        Base, self.PersonaModel, _, _ = get_schema_models(vector_dimension)

        if auto_setup:
            print("ECA-Lib [PersonaProvider]: Verificando e criando tabelas...")
            Base.metadata.create_all(self.engine)
            print("ECA-Lib [PersonaProvider]: Setup do banco de dados concluído.")

    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        """Busca uma persona no PostgreSQL pelo seu ID usando o ORM."""
        with self.Session() as session:
            persona_db = session.get(self.PersonaModel, persona_id)
            
            if persona_db:
                # O adaptador atua como um "tradutor" entre o modelo de banco
                # de dados (SQLAlchemy) e o modelo de domínio da aplicação (dataclass).
                return Persona(
                    id=persona_db.id,
                    name=persona_db.name,
                    semantic_description=persona_db.semantic_description,
                    config=PersonaConfig(**persona_db.config)
                )
            return None

    def detect_domain(self, user_input: str) -> str:
        """Detecta o domínio mais relevante usando busca vetorial com o ORM.
        
        Converte a entrada do usuário em um vetor e busca a persona cuja
        `semantic_description` (representada pela coluna `embedding`) tenha
        a menor distância vetorial (maior similaridade).
        """
        query_embedding = self.embed(user_input)
        with self.Session() as session:
            best_match = session.query(self.PersonaModel).order_by(
                self.PersonaModel.embedding.l2_distance(query_embedding)
            ).first()

            return best_match.id if best_match else "default"


class PostgresMemoryProvider(MemoryProvider):
    """
    Implementação de `MemoryProvider` para PostgreSQL com SQLAlchemy e `pgvector`.
    
    Gerencia a memória episódica (histórico) e a memória semântica (conhecimento)
    em tabelas PostgreSQL, oferecendo uma solução de memória unificada e performática.
    """
    def __init__(self, dsn: str, embedding_function: Callable[[str], List[float]], vector_dimension: int, auto_setup: bool = False):
        """
        Inicializa o provedor de memória.

        Args:
            dsn (str): A string de conexão do PostgreSQL.
            embedding_function (Callable): Função que converte texto em um vetor.
            vector_dimension (int): A dimensão dos vetores de embedding.
            auto_setup (bool, optional): Se True, cria as tabelas no banco. Padrão False.
        """
        self.engine = create_engine(dsn)
        self.Session = sessionmaker(bind=self.engine)
        self.embed = embedding_function

        Base, _, self.EpisodicMemoryModel, self.SemanticMemoryModel = get_schema_models(vector_dimension)

        if auto_setup:
            print("ECA-Lib [MemoryProvider]: Verificando e criando tabelas...")
            Base.metadata.create_all(self.engine)
            print("ECA-Lib [MemoryProvider]: Setup do banco de dados concluído.")

    def fetch_semantic_memories(self, user_input: str, domain_id: str, top_k: int = 3) -> List[SemanticMemory]:
        """Busca memórias semânticas usando busca vetorial com o ORM."""
        query_embedding = self.embed(user_input)
        
        with self.Session() as session:
            results_db = session.query(self.SemanticMemoryModel).filter_by(
                domain_id=domain_id
            ).order_by(
                self.SemanticMemoryModel.embedding.l2_distance(query_embedding)
            ).limit(top_k).all()
            
            return [
                SemanticMemory(
                    id=mem.id, domain_id=mem.domain_id, type=mem.type,
                    text_content=mem.text_content, embedding=mem.embedding,
                    metadata=mem.metadata
                ) for mem in results_db
            ]

    def fetch_episodic_memories(self, user_id: str, domain_id: str, last_n: int = 5) -> List[EpisodicMemory]:
        """Busca o histórico de conversas de um usuário usando o ORM."""
        with self.Session() as session:
            results_db = session.query(self.EpisodicMemoryModel).filter_by(
                user_id=user_id,
                domain_id=domain_id
            ).order_by(
                self.EpisodicMemoryModel.timestamp.desc()
            ).limit(last_n).all()
            
            results_db.reverse()
            
            return [
                EpisodicMemory(
                    user_id=mem.user_id, domain_id=mem.domain_id,
                    user_input=mem.user_input, assistant_output=mem.assistant_output,
                    timestamp=mem.timestamp.isoformat()
                ) for mem in results_db
            ]

    def log_interaction(self, interaction: EpisodicMemory):
        """Salva uma nova interação no banco de dados usando o ORM."""
        with self.Session() as session:
            new_interaction_db = self.EpisodicMemoryModel(
                user_id=interaction.user_id,
                domain_id=interaction.domain_id,
                user_input=interaction.user_input,
                assistant_output=interaction.assistant_output,
                timestamp=interaction.timestamp
            )
            session.add(new_interaction_db)
            session.commit()