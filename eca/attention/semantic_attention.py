# -*- coding: utf-8 -*-
import difflib
from typing import List
from eca.memory.types import SemanticMemory
from .base import AttentionMechanism


class SimpleSemanticAttention(AttentionMechanism):
    """Um mecanismo de atenção que usa similaridade de texto literal.

    Esta é uma implementação concreta de `AttentionMechanism` que não requer
    nenhuma dependência de modelos de machine learning ou bibliotecas de
    vetorização. Ela utiliza o `difflib` da biblioteca padrão do Python
    para calcular a similaridade entre a entrada do usuário e o conteúdo
    textual das memórias.

    É uma opção leve e funcional para casos onde uma busca semântica
    completa (baseada em vetores) é desnecessária ou computacionalmente cara.
    """
    def rank(self, user_input: str, memories: List[SemanticMemory]) -> List[SemanticMemory]:
        """Ordena memórias com base na similaridade de texto usando `difflib`.

        O método calcula um "ratio" de similaridade para cada memória comparada
        à entrada do usuário e retorna a lista ordenada em ordem decrescente
        dessa pontuação.

        Args:
            user_input (str): O texto do usuário, que será a base para a
                comparação.
            memories (List[SemanticMemory]): Uma lista de objetos
                `SemanticMemory` a serem ranqueados.

        Returns:
            List[SemanticMemory]: A lista de memórias ordenada pela
            similaridade com a entrada do usuário.
        """
        def _calculate_similarity(memory: SemanticMemory) -> float:
            """Calcula a pontuação de similaridade entre a memória e a entrada."""
            return difflib.SequenceMatcher(
                None,
                user_input.lower(),
                memory.text_content.lower()
            ).ratio()
        
        return sorted(memories, key=_calculate_similarity, reverse=True)