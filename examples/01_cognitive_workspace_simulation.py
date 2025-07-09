# -*- coding: utf-8 -*-
"""
Este exemplo demonstra o conceito central da ECA: a Área de Trabalho Cognitiva.
Simulamos uma usuária, Ana, que primeiro interage com um domínio (fiscal) e
depois troca abruptamente de contexto para outro (cadastro de produto),
mostrando como o Orquestrador gerencia o estado de forma fluida.
"""

import os
import json
from eca import ECAOrchestrator
from eca.adapters import JSONPersonaProvider, JSONMemoryProvider, JSONSessionProvider

def pretty_print_workspace(context: dict):
    """Função auxiliar para imprimir o workspace de forma legível."""
    print(json.dumps(context, indent=2, ensure_ascii=False))

def run_simulation():
    """Executa a simulação completa."""
    
    # --- 1. Setup: Apontar para os arquivos de dados ---
    # Em uma aplicação real, estes caminhos viriam de uma configuração.
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, 'database')
    
    personas_file = os.path.join(db_path, 'personas.json')
    memories_file = os.path.join(db_path, 'memories.json')
    
    # O arquivo de sessão é onde o estado da "Área de Trabalho" será salvo.
    sessions_file = os.path.join(base_dir, 'workspaces', 'user_sessions.json')
    os.makedirs(os.path.dirname(sessions_file), exist_ok=True)

    # --- 2. Instanciar os Provedores (Adapters) ---
    # Cada provedor é responsável por uma parte do conhecimento.
    persona_provider = JSONPersonaProvider(file_path=personas_file)
    memory_provider = JSONMemoryProvider(file_path=memories_file)
    session_provider = JSONSessionProvider(file_path=sessions_file)

    # --- 3. Injetar os provedores no Orquestrador ---
    # O Orquestrador não sabe de onde vêm os dados, apenas como usá-los.
    orchestrator = ECAOrchestrator(
        persona_provider=persona_provider,
        memory_provider=memory_provider,
        session_provider=session_provider
    )

    # --- 4. Simulação da Conversa da Ana ---
    user_id = "ana_paula"
    
    print("="*80 + f"\n>>> Interação 1: Ana inicia uma tarefa fiscal.\n" + "="*80)
    context1 = orchestrator.generate_dynamic_context(user_id, "Preciso analisar a NF-e 78910.")
    pretty_print_workspace(context1)

    print("\n" + "="*80 + f"\n>>> Interação 2: Ana troca abruptamente para cadastro de produto.\n" + "="*80)
    context2 = orchestrator.generate_dynamic_context(user_id, "Ah, antes que eu esqueça, qual o próximo código de produto?")
    pretty_print_workspace(context2)

if __name__ == "__main__":
    run_simulation()