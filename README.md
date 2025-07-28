# MCP + Elasticsearch + LangChain Demo

Este projeto demonstra a integração entre Model Context Protocol (MCP), Elasticsearch e LangChain para criar um sistema de RAG (Retrieval-Augmented Generation).

## 🚀 Como executar

### 1. Acessar o container

```bash
docker exec -it mcp-elasticsearch-server /bin/bash
```

### 2. Executar o aplicativo principal

```bash
cd /app
python src/init_app.py
```

### 3. Opções disponíveis

1. **Testar Elasticsearch**: Verifica se a conexão e busca estão funcionando
2. **Iniciar servidor MCP**: Inicia o servidor MCP (ainda não conectado ao agente)
3. **Iniciar agente de IA**: Chat interativo com o assistente
4. **Exemplo completo**: Demonstração de todas as funcionalidades
5. **Limpar dados**: Remove todos os dados do índice

## 📝 Exemplos de perguntas para o agente

- "Quais posts existem sobre usuários?"
- "Me mostre os posts mais recentes"
- "Quantos documentos existem por categoria?"
- "Busque posts que mencionam email"
- "Me dê detalhes do post com ID post_1"

## 🛠️ Instalando Ollama (para o modelo LLM gratuito)

Para usar o agente de IA, você precisa instalar o Ollama no container:

```bash
# Dentro do container
curl -fsSL https://ollama.ai/install.sh | sh

# Baixar o modelo Llama2 (ou mistral para algo menor)
ollama pull llama2
# ou
ollama pull mistral

# Iniciar o servidor Ollama em background
ollama serve &
```

## 📊 Arquitetura

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────┐
│                 │     │                  │     │               │
│  LangChain      │────▶│  MCP Server      │────▶│ Elasticsearch │
│  Agent          │     │                  │     │               │
│                 │     │                  │     │               │
└─────────────────┘     └──────────────────┘     └───────────────┘
        │                                                 │
        │                                                 │
        └─────────────────────────────────────────────────┘
                    Direct ES Access (for now)
```

## 🔧 Estrutura do Projeto

```
/app/
├── src/
│   ├── mcp_server/
│   │   ├── mcp_config.json
│   │   └── server.py
│   ├── elasticsearch_client/
│   │   └── es_client.py
│   ├── agents/
│   │   └── elasticsearch_agent.py
│   └── init_app.py
├── data/
├── notebooks/
├── requirements.txt
└── .env
```

## 🐛 Troubleshooting

**Problema**: Elasticsearch não conecta
- Solução: Verifique se o container está rodando: `docker ps`

**Problema**: Ollama não funciona
- Solução: Instale e inicie o Ollama conforme instruções acima

**Problema**: Agente não responde
- Solução: Verifique se o modelo foi baixado: `ollama list`
