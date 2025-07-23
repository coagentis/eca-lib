# -*- coding: utf-8 -*-
import json
from dataclasses import asdict
from typing import Optional

try:
    import redis
except ImportError:
    raise ImportError(
        "O pacote 'redis' não está instalado. "
        "Por favor, instale a eca-lib com o suporte a Redis: pip install eca-lib[redis]"
    )

from .base import SessionProvider
from ..models import CognitiveWorkspace


class RedisSessionProvider(SessionProvider):
    """
    Uma implementação de `SessionProvider` de alta performance para produção.

    Utiliza o Redis, um banco de dados em memória, para armazenar e recuperar
    o estado da `CognitiveWorkspace` de forma extremamente rápida. Esta abordagem
    é ideal para aplicações escaláveis e sem estado (stateless), garantindo
    que o gerenciamento de sessão não se torne um gargalo de performance.

    Cada workspace é serializado para JSON e armazenado em uma chave Redis
    com um tempo de vida (TTL) configurável, permitindo que sessões inativas
    expirem e liberem memória automaticamente.

    Attributes:
        redis_client (redis.Redis): A instância do cliente de conexão com o Redis.
        key_prefix (str): Um namespace para as chaves de sessão, evitando
            colisões com outras aplicações no mesmo Redis.
        ttl_seconds (int): O tempo de vida (TTL) em segundos para as chaves
            de sessão. Um valor de 0 desativa a expiração.
    """
    def __init__(self, host: str = 'localhost', port: int = 6379, password: Optional[str] = None, db: int = 0, ttl_seconds: int = 3600):
        """
        Inicializa o provedor de sessão com os detalhes da conexão Redis.

        Args:
            host (str, optional): O host do servidor Redis. Padrão 'localhost'.
            port (int, optional): A porta do servidor Redis. Padrão 6379.
            password (Optional[str], optional): A senha para o servidor Redis. Padrão None.
            db (int, optional): O número do banco de dados Redis. Padrão 0.
            ttl_seconds (int, optional): O tempo em segundos para a sessão
                expirar. Padrão 1 hora (3600s). Use 0 para desativar.
        """
        # decode_responses=True garante que os valores lidos do Redis venham como strings
        self.redis_client = redis.Redis(host=host, port=port, password=password, db=db, decode_responses=True)
        self.key_prefix = "eca:session:"
        self.ttl_seconds = ttl_seconds

    def get_workspace(self, user_id: str) -> Optional[CognitiveWorkspace]:
        """Carrega a área de trabalho de um usuário a partir do Redis.

        O método busca a string JSON no Redis, a converte de volta para um
        dicionário e então reconstrói o objeto `CognitiveWorkspace`. A
        reidratação dos objetos aninhados (como `DomainState`) é feita
        automaticamente pelo método `__post_init__` da classe `CognitiveWorkspace`.

        Args:
            user_id (str): O ID único do usuário.

        Returns:
            Optional[CognitiveWorkspace]: O objeto `CognitiveWorkspace`
            reconstruído, ou `None` se a sessão não for encontrada.
        """
        key = f"{self.key_prefix}{user_id}"
        workspace_json = self.redis_client.get(key)
        
        if workspace_json:
            workspace_data = json.loads(workspace_json)
            return CognitiveWorkspace(**workspace_data)
        
        return None
    
    def save_workspace(self, workspace: CognitiveWorkspace):
        """Salva o estado da área de trabalho de um usuário no Redis.

        Utiliza `dataclasses.asdict` para converter recursivamente o objeto
        `CognitiveWorkspace` e todos os seus objetos aninhados em um
        dicionário, que é então serializado para uma string JSON e salvo no Redis.

        Args:
            workspace (CognitiveWorkspace): O objeto `CognitiveWorkspace` a ser salvo.
        """
        key = f"{self.key_prefix}{workspace.user_id}"
        
        # Correção: Usamos asdict para garantir a conversão correta de
        # dataclasses aninhados em um dicionário.
        workspace_data = asdict(workspace)
        
        # A função `default=str` é um truque para lidar com tipos que o JSON
        # não conhece, como objetos datetime, convertendo-os para string.
        workspace_json = json.dumps(workspace_data, default=str)
        
        # Salva no Redis com o tempo de expiração (TTL) definido
        self.redis_client.set(
            key, 
            workspace_json, 
            ex=self.ttl_seconds if self.ttl_seconds > 0 else None
        )