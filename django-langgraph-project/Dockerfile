# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.8.3

WORKDIR /app

# deps de build + libgomp (OpenMP) que algumas libs nativas usam
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libgomp1 \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# Copia manifestos primeiro (cache)
COPY pyproject.toml poetry.lock* /app/

# (debug) só mostre versões
RUN python -V && poetry --version

# Sincroniza o lock com o pyproject:
# 1) tenta manter versões (no-update); se não der, faz lock completo
RUN poetry lock --no-update || poetry lock

# Instala deps (sem instalar o próprio projeto)
RUN poetry install --no-interaction --no-ansi --no-root

# Copia o resto do código
COPY . /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
