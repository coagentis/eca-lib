# 🧠 ECA-Lib: Engenharia de Contexto Aumentada

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![PyPI version](https://img.shields.io/pypi/v/eca-lib.svg)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-orange)

**ECA-Lib** é a implementação da arquitetura ECA, um paradigma para projetar e construir aplicações de IA stateful (com estado) sobre Grandes Modelos de Linguagem. A biblioteca fornece um sistema estruturado para a engenharia de contexto, permitindo que LLMs operem com memória de longo prazo e capacidade de multitarefa.

---

### 💥 O Problema: A Natureza Stateless dos LLMs e sua Amnésia

Grandes Modelos de Linguagem (LLMs) são incrivelmente poderosos, mas operam com uma limitação fundamental: por natureza, eles são stateless (sem estado). Eles não possuem memória entre as interações, o que torna um desafio construir aplicações de IA stateful que evoluem, aprendem com o passado e gerenciam tarefas complexas de forma contínua.

### ✨ A Solução: Arquitetura ECA

A **ECA (Engenharia de Contexto Aumentada)** é uma arquitetura de orquestração que resolve esse problema. Funciona como um "exoesqueleto" cognitivo para LLMs, fornecendo um sistema estruturado para a engenharia de contexto, onde a identidade, a memória e o estado são tratados como componentes de primeira classe. Ela orquestra a identidade, a memória e o foco do agente, gerando um prompt rico e dinâmico em tempo real.

Com a ECA, é possível projetar sistemas com as seguintes capacidades:

* ✅ **Gerenciamento de Identidade:** Permite a definição de múltiplas personas (com identidades, objetivos e regras próprias) que são carregadas dinamicamente. Isso torna o comportamento da IA configurável e não codificado, podendo agir como um especialista fiscal em um momento e como um organizador de catálogos no outro.
* 🧠 **Memória Híbrida e Persistente:** Implementa uma memória de longo prazo (semântica) via RAG (Geração Aumentada por Recuperação) e uma memória de curto prazo (episódica), permitindo que a aplicação consulte e "lembre" de fatos e interações passadas.
* 🚀 **Raciocinar Dinamicamente:** Alternar entre diferentes tarefas sem perder o contexto, utilizando uma "Área de Trabalho Cognitiva" que gerencia múltiplos domínios de foco. Introduzindo um sistema de gerenciamento de estado que permite à aplicação pausar uma tarefa, focar em outra e retornar ao contexto original sem perda de informação, simulando uma capacidade de raciocínio dinâmico.
* ⚙️ **Ser Orientado por Dados:** Definir personas, regras e memórias em arquivos de configuração, não em código rígido. Toda a lógica de comportamento (personas, regras, memórias) é tratada como dados, desacoplando a lógica da aplicação de suas fontes de conhecimento e permitindo máxima flexibilidade através de uma arquitetura de adaptadores.

### Diagrama da Arquitetura
```mermaid
graph TD
    subgraph "Usuário"
        A[👩‍💻 Usuário]
    end

    subgraph "Sistema ECA"
        B(Orquestrador Cognitivo)
        C{Base de Conhecimento}
        D[🧠 LLM]

        A -- 1- Entrada de Texto --> B
        B -- 2- Busca Contexto --> C
        C -- 3- Retorna Dados --> B
        B -- 4- Monta Prompt Otimizado --> D
        D -- 5- Gera Resposta --> B
        B -- 6- Entrega Resposta --> A
    end

    style C fill:#DB7093,stroke:#333,stroke-width:2px
```

### A Analogia do Chef de Cozinha: Entendendo a `eca-lib`

Para explicar de forma simples como a `eca-lib` funciona, vamos usar uma analogia: imagine um Chef de Cozinha em seu ambiente de trabalho.

#### Os Personagens Principais

  * **O Chef de Cozinha é o LLM** (o motor da IA, como GPT ou Llama). Ele é quem tem a criatividade para criar as respostas.
  * **A Cozinha Profissional é a `eca-lib`**. Ela é todo o sistema organizado (ferramentas, memórias, processos) que permite ao Chef trabalhar de forma eficiente e inteligente.

-----

#### O Processo Completo: Do Pedido ao Prato Final

**1. O Pedido Chega (O `prompt` do Usuário)**

  * *Nesta etapa, o pedido que um cliente faz no restaurante é o comando que o usuário envia para a IA.*

Um cliente faz um pedido, que pode ser simples ("Quero uma salada") ou complexo ("Quero o prato do dia, mas sou alérgico a nozes").

**2. O Chef Usa Sua Memória (A `Memória Híbrida` da lib)**

  * *Aqui, a memória do Chef representa como a `eca-lib` gerencia informações de curto e longo prazo.*

O Chef precisa de dois tipos de memória para trabalhar:

  * **Memória de Curto Prazo (Histórico da Conversa):** Ele olha seu **bloco de anotações** para lembrar detalhes recentes. Ex: "Ok, cliente da mesa 4, sem nozes".
  * **Memória de Longo Prazo (Base de Conhecimento / RAG):** Para pratos complexos, ele consulta seu **livro de receitas**. Ele não inventa, ele recupera a informação correta para garantir a qualidade.

**3. O Chef Organiza o Trabalho (A `Área de Trabalho Cognitiva`)**

  * *A bancada de trabalho do Chef é como a `eca-lib` gerencia múltiplas tarefas sem perder o foco.*

A bancada do Chef é super organizada. Isso permite que ele faça várias coisas ao mesmo tempo. Por exemplo, ele pode deixar um filé descansando (Tarefa A) enquanto prepara uma salada (Tarefa B), e depois voltar ao filé sem esquecer em que ponto parou.

**4. O Segredo do Chef (O `Achatamento de Tokens`)**

  * *Esta é a técnica que a `eca-lib` usa para evitar que o contexto fique grande demais, resumindo as informações sem perder o sentido.*

Com o tempo, a bancada do Chef pode ficar cheia de anotações. Para não se perder, ele cria uma **"redução"**: pega uma grande quantidade de caldo (o histórico longo e verboso da conversa) e ferve lentamente, evaporando a "água" (redundâncias) para criar um molho concentrado e rico em sabor (um resumo coeso). Isso mantém a essência, mas ocupa menos espaço na bancada (a janela de contexto).

**5. O Chef Usa Suas Ferramentas (Os `Adaptadores de Produção`)**

  * *Os equipamentos e a despensa da cozinha são os bancos de dados que a `eca-lib` usa para guardar e buscar informações.*

Um Chef precisa de acesso rápido aos ingredientes:

  * **A Despensa Organizada (PostgreSQL/pgvector):** É o estoque principal, onde tudo de longo prazo é guardado de forma organizada.
  * **O Balcão Rápido (Redis):** São os ingredientes já cortados e prontos para uso imediato, para agilidade máxima.

**6. O Prato é Servido (A Resposta Final da IA)**

  * *O prato final é a resposta inteligente e completa que a IA entrega ao usuário.*

Depois de usar suas memórias, sua bancada organizada e suas ferramentas, o Chef entrega um prato bem-executado que atende a tudo que o cliente pediu.

-----

#### Tabela Resumo

| Conceito da `eca-lib` | Analogia na Cozinha |
| :---------------------- | :-------------------- |
| **LLM** | O Chef de Cozinha |
| **`eca-lib`** | A Cozinha Profissional |
| **Prompt do Usuário** | O Pedido do Cliente |
| **Memória de Curto Prazo** | Bloco de Anotações do Chef |
| **Memória de Longo Prazo (RAG)** | Livro de Receitas |
| **Área de Trabalho Cognitiva** | Bancada de Trabalho Organizada|
| **Achatamento de Tokens** | Criar um "Molho de Redução" |
| **PostgreSQL / Vetorial** | Despensa Principal |
| **Redis / Cache** | Ingredientes de Acesso Rápido |
| **Resposta Final da IA** | O Prato Servido ao Cliente |


Assim, a `eca-lib` não é apenas o Chef, mas toda a cozinha de alta performance que o permite criar respostas complexas e contextuais de forma consistente e escalável.

### 📦 Instalação

```bash
pip install eca-lib
```
*(Nota: O pacote está em processo de publicação no PyPI)*

### 🚀 Quick Start

Este exemplo mostra como instanciar o orquestrador e gerar um prompt dinâmico de forma 100% autocontida.

1.  **Crie seus arquivos de dados**

    Em uma nova pasta para o seu projeto, crie os seguintes arquivos com o conteúdo exato abaixo:

      * **`personas.json`** - (Define as personalidades da IA)

        ```json
        [
          {
            "id": "fiscal",
            "name": "ÁBACO",
            "semantic_description": "Análise de documentos fiscais, notas fiscais, impostos como ICMS, IPI, conformidade tributária.",
            "persona_config": {
              "persona": "Você é ÁBACO, um assistente de IA especialista em análise fiscal. Você é objetivo, eficiente e baseado em dados.",
              "objective": "Analisar documentos fiscais, garantir conformidade e identificar inconsistências.",
              "golden_rules": [
                "A precisão é mais importante que a velocidade.",
                "Nunca presuma dados ambíguo; sempre sinalize para revisão humana."
              ]
            }
          },
          {
            "id": "product_catalog",
            "name": "CATÁLOGO",
            "semantic_description": "Gerenciamento de catálogo, cadastro de novos produtos, SKUs, organização de itens.",
            "persona_config": {
              "persona": "Você é CATÁLOGO, um assistente de IA focado em manter a integridade do cadastro de produtos.",
              "objective": "Garantir a organização e padronização do catálogo.",
              "golden_rules": [
                "Verifique se o produto já existe antes de cadastrar um novo."
              ]
            }
          }
        ]
        ```

      * **`memories.json`** - (A base de conhecimento inicial)

        ```json
        [
          {
            "id": "mem-uuid-456",
            "domain_id": "fiscal",
            "type": "business_rule",
            "text_content": "Toda validação de ICMS-ST deve cruzar a informação com o Protocolo ICMS vigente entre os estados da operação."
          },
          {
            "id": "mem-uuid-789",
            "domain_id": "product_catalog",
            "type": "business_rule",
            "text_content": "O último código de notebook cadastrado foi 'NB-1098'. Novos códigos devem seguir a sequência."
          }
        ]
        ```

2.  **Crie e execute o código Python**

    Na mesma pasta, crie o arquivo **`main.py`** com o conteúdo abaixo e depois execute os comandos.

    ```python
    # main.py

    # Importa as classes da biblioteca que você instalou com 'pip install eca-lib'
    from eca import (
        ECAOrchestrator, 
        # Os adaptadores JSON são ótimos para começar rapidamente
        JSONPersonaProvider, 
        JSONMemoryProvider, 
        JSONSessionProvider
    )

    # --- 1. Configuração dos Provedores (Adapters) ---
    # Apontamos para os arquivos que acabamos de criar.
    persona_provider = JSONPersonaProvider(file_path='personas.json')
    memory_provider = JSONMemoryProvider(
        semantic_path='memories.json', 
        episodic_path='interaction_log.json' # Este arquivo será criado automaticamente
    )
    session_provider = JSONSessionProvider(
        file_path='user_sessions.json' # Este também será criado automaticamente
    )

    # --- 2. Instanciação do Orquestrador ---
    # A biblioteca carrega o prompt padrão em português automaticamente.
    orchestrator = ECAOrchestrator(
        persona_provider=persona_provider,
        memory_provider=memory_provider,
        session_provider=session_provider,
        knowledge_base_path='.' # Usaremos o diretório atual
    )

    print("✅ Orquestrador ECA pronto para uso!")

    # --- 3. Simulação de uma Conversa ---
    user_id = "ana_paula"
    user_input = "Preciso cadastrar um novo notebook."

    print(f"\n🗣️  INPUT DO USUÁRIO: '{user_input}'")

    # Gera o prompt final, pronto para ser enviado a um LLM
    final_prompt = orchestrator.generate_final_prompt(user_id, user_input)

    print("\n✨ PROMPT DINÂMICO GERADO PELA ECA-LIB: ✨\n")
    print(final_prompt)
    ```

    **Comandos para executar:**

    ```bash
    # Crie e ative um ambiente virtual
    python -m venv venv
    source venv/bin/activate

    # Instale a biblioteca (a partir do PyPI, quando publicada)
    pip install eca-lib

    # Execute o script
    python main.py
    ```

### 📖 Documentação Completa

Para um mergulho profundo na teoria e nos detalhes da arquitetura, leia nosso **[Whitepaper de Arquitetura](ARCHITECTURE.md)**.

### 🤝 Como Contribuir

Contribuições são bem-vindas! Por favor, sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.

### 📜 Licença

Este projeto é licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
