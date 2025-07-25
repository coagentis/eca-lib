# eca/database/schema.py
"""
Define o schema do banco de dados para os adaptadores PostgreSQL usando SQLAlchemy ORM.
"""

from sqlalchemy import Column, String, Text, Integer, JSON, TIMESTAMP
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

# O Base é a classe fundamental da qual todos os modelos ORM herdarão.
Base = declarative_base()

def get_schema_models(vector_dimension: int):
    """
    Gera e retorna as classes de modelo SQLAlchemy com uma dimensão de vetor customizada.

    Args:
        vector_dimension (int): A dimensão dos vetores de embedding a ser usada.

    Returns:
        tuple: Uma tupla contendo as classes (Base, PersonaModel, EpisodicMemoryModel, SemanticMemoryModel).
    """

    class PersonaModel(Base):
        __tablename__ = 'personas'
        id = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)
        semantic_description = Column(Text, nullable=False)
        config = Column(JSON, nullable=False)
        embedding = Column(Vector(vector_dimension))

    class EpisodicMemoryModel(Base):
        __tablename__ = 'episodic_memories'
        interaction_id = Column(Integer, primary_key=True, autoincrement=True)
        user_id = Column(String(255), nullable=False, index=True)
        domain_id = Column(String(255), nullable=False)
        user_input = Column(Text, nullable=False)
        assistant_output = Column(Text, nullable=False)
        timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    class SemanticMemoryModel(Base):
        __tablename__ = 'semantic_memories'
        id = Column(String(255), primary_key=True)
        domain_id = Column(String(255), nullable=False, index=True)
        type = Column(String(255))
        text_content = Column(Text, nullable=False)
        embedding = Column(Vector(vector_dimension))
        metadata = Column(JSON)

    return Base, PersonaModel, EpisodicMemoryModel, SemanticMemoryModel