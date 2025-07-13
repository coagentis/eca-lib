# -*- coding: utf-8 -*-
import json
from typing import Dict

class ProceduralRule:
    """Representa uma regra ou fluxo de trabalho carregado."""
    def __init__(self, name: str, steps: list):
        self.name = name
        self.steps = steps

    def __repr__(self):
        return f"ProceduralRule(name='{self.name}', steps={len(self.steps)})"

def load_rules_from_json(file_path: str) -> Dict[str, ProceduralRule]:
    """
    Carrega um arquivo JSON e o converte em um dicionário de objetos ProceduralRule.
    """
    rules = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for rule_name, rule_data in data.get('rules', {}).items():
                steps = rule_data.get('steps', [])
                rules[rule_name] = ProceduralRule(name=rule_name, steps=steps)
    except FileNotFoundError:
        print(f"Aviso: Arquivo de regras não encontrado em {file_path}")
    except Exception as e:
        print(f"Erro ao carregar regras do arquivo {file_path}: {e}")
    
    return rules