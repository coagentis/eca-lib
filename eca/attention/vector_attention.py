# -*- coding: utf-8 -*-
import math
from typing import List, Callable

from eca.memory.types import SemanticMemory
from .base import AttentionMechanism


class VectorizedSemanticAttention(AttentionMechanism):
    """Usa embeddings vetoriais para rankear memórias por proximidade semântica.

    Esta implementação de `AttentionMechanism` realiza uma busca semântica
    genuína, comparando o "significado" da entrada do usuário com o conteúdo
    das memórias através de vetores numéricos (embeddings).

    A classe é projetada para ser flexível, permitindo que o usuário injete
    qualquer função de embedding compatível (ex: de bibliotecas como
    `sentence-transformers`, `transformers`, ou APIs como OpenAI).
    Notavelmente, o cálculo de similaridade é feito com a biblioteca `math`
    padrão do Python, evitando dependências pesadas como NumPy ou SciPy.

    Attributes:
        embed (Callable[[str], List[float]]): A função que converte uma string
            de texto em um vetor de embedding (uma lista de floats).
    """
    def __init__(self, embedding_function: Callable[[str], List[float]]):
        """Inicializa o mecanismo com uma função de embedding.

        Args:
            embedding_function (Callable[[str], List[float]]): Uma função que
                aceita uma string como entrada e retorna seu embedding vetorial
                como uma lista de números de ponto flutuante.

        Raises:
            TypeError: Se o argumento `embedding_function` não for uma função
                (callable).
        """
        if not callable(embedding_function):
            raise TypeError("O argumento 'embedding_function' deve ser uma função.")
        self.embed = embedding_function

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calcula a similaridade de cossenos entre dois vetores.

        Esta é uma implementação em Python puro que não depende de bibliotecas
        externas de algebra linear. A similaridade de cossenos mede o cosseno
        do ângulo entre dois vetores, resultando em um valor que representa
        a similaridade de direção entre eles.

        Args:
            vec_a (List[float]): O primeiro vetor.
            vec_b (List[float]): O segundo vetor.

        Returns:
            float: Um valor de similaridade, tipicamente entre 0.0 e 1.0 para
            embeddings de texto, onde 1.0 significa identidade de direção.
            Retorna 0.0 se os vetores tiverem comprimentos diferentes ou se
            um deles tiver norma zero.
        """
        if len(vec_a) != len(vec_b):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a**2 for a in vec_a))
        norm_b = math.sqrt(sum(b**2 for b in vec_b))

        # Evita divisão por zero se um dos vetores for nulo
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)

    def rank(self, user_input: str, memories: List[SemanticMemory]) -> List[SemanticMemory]:
        """Rankeia memórias pela similaridade de cossenos de seus embeddings.

        O processo consiste em:
        1. Gerar o embedding vetorial para a entrada do usuário.
        2. Para cada memória na lista, calcular a similaridade de cossenos
           entre o embedding da entrada e o embedding pré-existente da memória.
        3. Ordenar a lista de memórias com base na pontuação de similaridade,
           da mais alta para a mais baixa.

        Args:
            user_input (str): O texto do usuário a ser usado como consulta.
            memories (List[SemanticMemory]): A lista de memórias a ser
                ranqueada. Cada memória deve conter um atributo `embedding`
                que seja uma lista de floats.

        Returns:
            List[SemanticMemory]: A lista de memórias ordenada por relevância
            semântica. Se ocorrer um erro ou a lista de entrada estiver vazia,
            a lista original pode ser retornada sem ordenação.
        """
        if not memories:
            return []

        # Gera o embedding para a entrada do usuário e valida o resultado
        try:
            input_embedding = self.embed(user_input)
            if not isinstance(input_embedding, list):
                print("Aviso: A função de embedding não retornou uma lista de floats.")
                return memories # Retorna a lista original sem rankear
        except Exception as e:
            print(f"Aviso: Erro ao executar a embedding_function: {e}")
            return memories

        scored_memories = []
        for mem in memories:
            # Valida se a memória possui um embedding compatível
            if (isinstance(mem.embedding, list) and 
                len(mem.embedding) == len(input_embedding)):
                
                score = self._cosine_similarity(input_embedding, mem.embedding)
                scored_memories.append((mem, score))

        # Ordena a lista de tuplas (memória, pontuação) pela pontuação
        sorted_by_score = sorted(
            scored_memories,
            key=lambda x: x[1],
            reverse=True
        )

        # Extrai apenas as memórias da lista ordenada
        return [mem for mem, score in sorted_by_score]