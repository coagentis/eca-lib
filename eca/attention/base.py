# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Any, List, TypeVar

MemoryType = TypeVar('MemoryType')


class AttentionMechanism(ABC):
    """Define a interface para um Mecanismo de Atenção.

    Na arquitetura cognitiva, o Mecanismo de Atenção é responsável por
    determinar o foco do agente. Ele recebe uma lista de memórias (sejam
    semânticas ou episódicas) e as reordena ou filtra com base na sua
    relevância para a entrada atual do usuário.

    Implementações desta classe podem variar de simples buscas por
    palavras-chave a complexas buscas por similaridade de vetores.
    """
    @abstractmethod
    def rank(self, user_input: str, memories: List[MemoryType]) -> List[MemoryType]:
        """Reordena uma lista de memórias com base na relevância para a entrada.

        Args:
            user_input (str): O texto atual do usuário, que serve como
                contexto para o ranqueamento.
            memories (List[MemoryType]): A lista de objetos de memória
                (ex: `SemanticMemory`, `EpisodicMemory`) a ser ordenada.

        Returns:
            List[MemoryType]: A mesma lista de memórias, mas reordenada com
            os itens mais relevantes primeiro.
        """
        pass


class PassthroughAttention(AttentionMechanism):
    """Uma implementação de 'mecanismo de atenção' que não realiza operação.

    Esta classe serve como um "noop" (no-operation) ou um objeto nulo para o
    mecanismo de atenção. Ela cumpre o contrato da interface `AttentionMechanism`
    mas não altera a ordem das memórias.

    É útil como um comportamento padrão no Orquestrador quando nenhum
    mecanismo de atenção específico é necessário, ou para fins de teste.
    """
    def rank(self, user_input: str, memories: List[Any]) -> List[Any]:
        """Retorna a lista de memórias na mesma ordem em que foi recebida.

        Este método ignora a entrada do usuário e simplesmente repassa a lista
        de memórias original, sem qualquer tipo de ranqueamento.

        Args:
            user_input (str): A entrada do usuário (ignorada por esta
                implementação).
            memories (List[Any]): A lista de memórias a ser retornada.

        Returns:
            List[Any]: A lista de memórias original, sem alterações.
        """
        return memories