
# Ceci Eco Mode — Assistente Virtual Leve com IA para Transporte Público

![Status](https://img.shields.io/badge/status-Estável-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-green)

## Sobre o Projeto

**Ceci Eco Mode** é uma assistente virtual otimizada para fornecer informações acessíveis sobre transporte público, combinando processamento de linguagem natural (NLP) eficiente com recursos de inteligência artificial (IA) generativa. Projetada para ambientes com recursos computacionais limitados, ela mantém alta precisão e desempenho.

## Funcionalidades

* **NLP Simulado com Regex e Embeddings**: Utiliza expressões regulares e o modelo `all-MiniLM-L6-v2` para compreender intenções básicas.
* **Fallback para OpenAI API**: Em casos de interações mais complexas, recorre à API da OpenAI para geração de respostas contextuais.
* **Arquitetura Modular**: Componentes separados para fácil manutenção e escalabilidade.
* **API RESTful com Documentação Interativa**: Interface clara e acessível para desenvolvedores.

## Arquitetura do Projeto

```
Usuário → FastAPI (REST)
        → NLP Simulado (Regex + MiniLM)
        → [Fallback] → OpenAI API (LLM)
        → Processamento e Resposta
```

## Tecnologias e Ferramentas

* **Linguagem**: Python 3.11
* **Framework**: FastAPI
* **Modelos de Linguagem**: Sentence Transformers (`all-MiniLM-L6-v2`), OpenAI API
* **Outros**: Regex, Uvicorn, LangDetect, DeepTranslator

## Como Rodar Localmente

1. Clone o repositório:

```bash
git clone https://github.com/viniruggeri/ceci_eco.git
cd ceci_eco
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente criando um arquivo `.env` na raiz do projeto com sua chave da OpenAI:

```
OPENAI_API_KEY=sk-xxxxxx
```

4. Inicie a aplicação:

```bash
uvicorn app:app --reload
```

5. Acesse a documentação interativa em [http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs)

## Licença

Este projeto está licenciado sob a Licença Apache 2.0.

## Desenvolvido por

**Vinicius Ruggeri**
[LinkedIn](https://www.linkedin.com/in/viniruggeri) | [GitHub](https://github.com/viniruggeri)

---
