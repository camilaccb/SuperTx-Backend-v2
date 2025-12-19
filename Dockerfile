# Imagem base
FROM python:3.10

# Não criar virtualenvs (recomendado para Docker)
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME="/opt/poetry"

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Adicionar Poetry ao PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Definir diretório de trabalho
WORKDIR /app

# Copiar apenas os arquivos de dependências primeiro (para cache)
COPY pyproject.toml poetry.lock* ./

# Instalar dependências do projeto
RUN poetry install --no-root

# Agora copiar o restante da aplicação
COPY . .

# Expor porta (opcional)
EXPOSE 5000

# Iniciar Flask
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
