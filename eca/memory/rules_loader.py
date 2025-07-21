# -*- coding: utf-8 -*-
import json
from typing import Dict, List


class ProceduralRule:
    """Representa uma única regra procedural ou fluxo de trabalho.

    Esta classe atua como um contêiner de dados para uma regra nomeada,
    encapsulando seu nome e a sequência de passos que a compõem.

    Attributes:
        name (str): O nome único da regra.
        steps (List): Uma lista de passos que definem o procedimento da regra.
    """
    def __init__(self, name: str, steps: list):
        """Inicializa uma instância de ProceduralRule.

        Args:
            name (str): O nome identificador da regra.
            steps (list): A lista de passos que constituem a regra.
        """
        self.name = name
        self.steps = steps

    def __repr__(self) -> str:
        """Retorna uma representação de string legível do objeto.

        Returns:
            str: Uma representação do objeto para fins de depuração.
        """
        return f"ProceduralRule(name='{self.name}', steps={len(self.steps)})"


def load_rules_from_json(file_path: str) -> Dict[str, ProceduralRule]:
    """Carrega regras procedurais de um arquivo JSON para objetos.

    Esta função lê um arquivo JSON com uma estrutura específica, o analisa
    e converte cada regra definida em um objeto `ProceduralRule`,
    retornando um dicionário com todas as regras carregadas.

    A estrutura JSON esperada é:
    {
      "rules": {
        "nome_da_regra_1": {
          "steps": [...]
        },
        "nome_da_regra_2": {
          "steps": [...]
        }
      }
    }

    Args:
        file_path (str): O caminho para o arquivo JSON contendo as regras.

    Returns:
        Dict[str, ProceduralRule]: Um dicionário onde as chaves são os nomes
        das regras e os valores são os objetos `ProceduralRule`
        correspondentes. Retorna um dicionário vazio se o arquivo não for
        encontrado ou ocorrer um erro.
    """
    rules: Dict[str, ProceduralRule] = {}
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