#!/bin/bash

echo "Iniciando container MCP + Elasticsearch + LangChain..."

# Configurar Ollama
echo "Configurando Ollama..."
/app/setup_ollama.sh

echo ""
echo "Container pronto!"
echo "Para usar o sistema, execute: python /app/src/init_app.py"
echo ""

# Manter o container rodando
exec /bin/bash