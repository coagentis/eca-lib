# Arquivo: examples/brazilian_backoffice_agent/run.py
# -*- coding: utf-8 -*-
"""
Este exemplo demonstra o fluxo COMPLETO da ECA: desde a entrada do usuário
até a geração do prompt final otimizado, mostrando a troca de contexto.
"""
import os
import json
from dataclasses import asdict

# Assumindo a estrutura de pastas que definimos
from eca import ECAOrchestrator
from eca.adapters.json_adapter import JSONMemoryProvider, JSONPersonaProvider, JSONSessionProvider

def pretty_print_context_object(context_object):
    """
    Função auxiliar para imprimir o 'estado mental' (o objeto CognitiveWorkspace)
    de forma legível.
    """
    # Converte o objeto de dataclass em um dicionário puro para impressão
    context_as_dict = asdict(context_object)
    print("--- 🧠 Objeto de Contexto Dinâmico Gerado ---")
    print(json.dumps(context_as_dict, indent=2, ensure_ascii=False))
    print("---------------------------------------------")

def run_simulation():
    """Executa a simulação completa."""
    
    # --- 1. Setup: Apontar para todos os arquivos necessários ---
    # Isso simula uma aplicação real carregando suas configurações.
    try:
        base_dir = os.path.dirname(__file__)
        #/home/roberto/project/pessoal/eca-lib/examples/database/memories.json
        #/home/roberto/project/pessoal/eca-lib/examples/03_dossier_simulation/knowledge_base
        
        knowledge_path = os.path.join(base_dir, 'examples/knowledge_base')
        workspaces_path = os.path.join(base_dir, 'examples/workspaces')
        prompts_path = os.path.join(base_dir, 'examples/prompts')

        db_path = os.path.join(base_dir, 'examples/database')
        personas_file = os.path.join(db_path, 'personas.json')
        memories_file = os.path.join(db_path, 'memories.json')

        sessions_file = os.path.join(workspaces_path, 'user_sessions.json')
        meta_prompt_file = os.path.join(prompts_path, 'meta_prompt_template.txt')

        # Garante que o diretório de workspaces exista
        os.makedirs(workspaces_path, exist_ok=True)
        if not os.path.exists(sessions_file):
            with open(sessions_file, 'w') as f:
                f.write('{}') # Cria um JSON vazio se o arquivo não existir

    except FileNotFoundError as e:
        print(f"Erro de configuração: Não foi possível encontrar um arquivo necessário.")
        print(f"Verifique se a estrutura de pastas está correta e o arquivo '{e.filename}' existe.")
        return

    # --- 2. Instanciar os Provedores (Adapters) ---
    persona_provider = JSONPersonaProvider(file_path=personas_file)
    memory_provider = JSONMemoryProvider(file_path=memories_file)
    session_provider = JSONSessionProvider(file_path=sessions_file)

    # --- 3. Injetar os provedores e caminhos no Orquestrador ---
    # Agora passamos todos os 5 argumentos que o __init__ espera.
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
    entrada1 = "Preciso analisar a nfe 78910."
    # Primeiro, usamos o método de baixo nível para ver o "cérebro" da IA
    context_obj_1 = orchestrator.generate_context_object(user_id, entrada1)
    pretty_print_context_object(context_obj_1)
    # Depois, usamos o método de alto nível para ver o prompt final
    prompt_final_1 = orchestrator.generate_final_prompt(user_id, entrada1)
    print("\n--- 🗣️ PROMPT FINAL GERADO PARA O LLM ---")
    print(prompt_final_1)
    print("------------------------------------------")


    print("\n" + "="*80 + f"\n>>> Interação 2: Ana troca de contexto para cadastro.\n" + "="*80)
    entrada2 = "Ok, obrigado. Agora preciso cadastrar um novo produto."
    # Repetimos o processo para a segunda interação
    context_obj_2 = orchestrator.generate_context_object(user_id, entrada2)
    pretty_print_context_object(context_obj_2)
    prompt_final_2 = orchestrator.generate_final_prompt(user_id, entrada2)
    print("\n--- 🗣️ PROMPT FINAL GERADO PARA O LLM ---")
    print(prompt_final_2)
    print("------------------------------------------")


if __name__ == "__main__":
    run_simulation()