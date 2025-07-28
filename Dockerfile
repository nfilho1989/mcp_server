
FROM ubuntu:22.04

# Evitar prompts durante a instalação
ENV DEBIAN_FRONTEND=noninteractive

# Atualizar o sistema e instalar dependências
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    wget \
    git \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python3-openssl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Python 3.11
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Configurar Python 3.11 como padrão
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Instalar pip para Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Instalar Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements.txt primeiro (para cache eficiente do Docker)
COPY requirements.txt /app/

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Criar estrutura de diretórios
RUN mkdir -p /app/src/elasticsearch_client \
    && mkdir -p /app/src/mcp_server \
    && mkdir -p /app/src/agents \
    && mkdir -p /app/data \
    && mkdir -p /app/notebooks

# Copiar todos os arquivos do projeto
COPY .env /app/
COPY src/ /app/src/
COPY setup_ollama.sh /app/
COPY entrypoint.sh /app/

# Dar permissão de execução aos scripts
RUN chmod +x /app/src/init_app.py && chmod +x /app/setup_ollama.sh && chmod +x /app/entrypoint.sh

# Definir variável de ambiente para Python
ENV PYTHONUNBUFFERED=1

# Expor portas
EXPOSE 8000 9200

# Usar o entrypoint personalizado
ENTRYPOINT ["/app/entrypoint.sh"]