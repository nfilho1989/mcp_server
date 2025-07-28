#!/bin/bash

echo "Configurando Ollama..."

# Verificar se Ollama já está instalado
if command -v ollama &> /dev/null; then
    echo "Ollama já está instalado"
else
    echo "Instalando Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Iniciar servidor Ollama
echo "Iniciando servidor Ollama..."
ollama serve &
OLLAMA_PID=$!

# Aguardar servidor iniciar
echo "Aguardando servidor Ollama iniciar..."
sleep 5

# Verificar se o modelo já existe
if ollama list | grep -q "mistral"; then
    echo "Modelo Mistral já está instalado"
else
    echo "Baixando modelo Mistral (isso pode demorar alguns minutos)..."
    ollama pull mistral
fi

echo "Ollama configurado com sucesso!"
echo "ID do servidor Ollama: $OLLAMA_PID"
echo ""
echo "Para parar o servidor Ollama depois, use: kill $OLLAMA_PID"