# -*- coding: utf-8 -*-

import os
import json
from dataclasses import asdict
from datetime import datetime

from eca import (
    ECAOrchestrator,
    JSONMemoryProvider,
    JSONPersonaProvider,
    JSONSessionProvider,
    EpisodicMemory,
)

def pretty_print_object(context_object):
    """Função auxiliar para imprimir qualquer objeto dataclass de forma legível."""
    if not context_object:
        print("Objeto de contexto está vazio.")
        return
    context_as_dict = asdict(context_object)
    print(json.dumps(context_as_dict, indent=2, ensure_ascii=False))

def run_simulation():
    """Executa a simulação completa."""
    
    # --- 1. Setup: Apontar para os arquivos de dados ---
    try:
        # O base_dir é o diretório do script atual (.../eca-lib/examples)
        base_dir = os.path.dirname(__file__)
        
        # CORREÇÃO: O project_root é um nível acima do diretório 'examples'
        project_root = os.path.abspath(os.path.join(base_dir, '..'))

        # CORREÇÃO: Construir os caminhos a partir da raiz do projeto
        db_path = os.path.join(project_root, 'examples/database')
        knowledge_path = os.path.join(project_root, 'examples/knowledge_base')
        workspaces_path = os.path.join(project_root, 'examples/workspaces')
        prompts_path = os.path.join(project_root, 'eca/prompts')

        # Arquivos de dados
        personas_file = os.path.join(db_path, 'personas.json')
        semantic_memories_file = os.path.join(db_path, 'memories.json')
        episodic_memories_file = os.path.join(db_path, 'interaction_log.json')
        
        # Arquivo de sessão
        sessions_file = os.path.join(workspaces_path, 'user_sessions.json')
        # Arquivo de prompt mestre
        meta_prompt_file = os.path.join(prompts_path, 'meta_prompt_template_pt_BR.txt')

        # Garante que os diretórios e arquivos vazios existam
        os.makedirs(workspaces_path, exist_ok=True)
        os.makedirs(db_path, exist_ok=True)
        for f in [sessions_file, episodic_memories_file, personas_file, semantic_memories_file]:
            if not os.path.exists(f):
                with open(f, 'w') as fp:
                    if f.endswith('.json'):
                        fp.write('{}' if 'sessions' in f else '[]')

    except Exception as e:
        print(f"Erro de configuração: {e}")
        print(f"Verifique se a estrutura de pastas está correta.")
        return

    # --- 2. Instanciar os Provedores (Adapters) ---
    persona_provider = JSONPersonaProvider(file_path=personas_file)
    session_provider = JSONSessionProvider(file_path=sessions_file)
    memory_provider = JSONMemoryProvider(
        semantic_path=semantic_memories_file,
        episodic_path=episodic_memories_file
    )

    # --- 3. Injetar os provedores no Orquestrador ---
    orchestrator = ECAOrchestrator(
        persona_provider=persona_provider,
        memory_provider=memory_provider,
        session_provider=session_provider,
        meta_prompt_template_path=meta_prompt_file,
        knowledge_base_path=knowledge_path
    )

    # --- 4. Simulação da Conversa da Ana ---
    user_id = "ana_paula"
    
    print("="*80 + f"\n>>> Interação 1: Ana inicia uma tarefa fiscal.\n" + "="*80)
    entrada1 = "qual o ultimo status da analize de minha nfe 78910."
    prompt_final_1 = orchestrator.generate_final_prompt(user_id, entrada1)
    
    print("\n--- 🗣️ PROMPT FINAL GERADO PARA O LLM ---")
    print(prompt_final_1)
    # Simulação da resposta da IA para logar na memória episódica
    resposta_ia_1 = "Entendido, Ana. Para analisar a NF-e 78910, por favor, anexe o arquivo ou me forneça a chave de acesso."
    print(f"\n--- 🤖 RESPOSTA SIMULADA DA IA ---\n{resposta_ia_1}\n")
    # NOVO: Salvando a interação no log
    memory_provider.log_interaction(EpisodicMemory(user_id, "fiscal", entrada1, resposta_ia_1, datetime.now().isoformat()))
    print("------------------------------------------")


    print("\n" + "="*80 + f"\n>>> Interação 2: Ana troca de contexto para cadastro.\n" + "="*80)
    entrada2 = "Ok, obrigado. Agora preciso cadastrar um novo produto."
    prompt_final_2 = orchestrator.generate_final_prompt(user_id, entrada2)

    print("\n--- 🗣️ PROMPT FINAL GERADO PARA O LLM ---")
    print(prompt_final_2)
    # Simulação da resposta da IA
    resposta_ia_2 = "Claro. Para iniciar o cadastro, por favor, me informe a descrição completa e a marca do novo produto."
    print(f"\n--- 🤖 RESPOSTA SIMULADA DA IA ---\n{resposta_ia_2}\n")
    # NOVO: Salvando a segunda interação no log
    memory_provider.log_interaction(EpisodicMemory(user_id, "product_catalog", entrada2, resposta_ia_2, datetime.now().isoformat()))
    print("------------------------------------------")


if __name__ == "__main__":
    run_simulation()