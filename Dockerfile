# ==============================
# Etapa base: Python slim
# ==============================
FROM python:3.12-slim AS base

# Não gerar pyc + output limpo
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências de sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copiar manifestos do Poetry
COPY pyproject.toml poetry.lock /app/

# Instalar Poetry
RUN pip install --no-cache-dir poetry

# Forçar Poetry a não criar virtualenv
RUN poetry config virtualenvs.create false

# --- INSTALAÇÃO CPU-ONLY ---
RUN poetry install --no-root --no-interaction --no-ansi \
    && pip uninstall -y nvidia-pyindex nvidia-pip nvidia-nvjitlink-cu12 \
       nvidia-cublas-cu12 nvidia-cusparse-cu12 nvidia-cudnn-cu12 triton || true

# Copiar código do projeto
COPY . /app/

# Expor porta do Django
EXPOSE 8000

# Rodar servidor Django
CMD ["python", "web/manage.py", "runserver", "0.0.0.0:8000"]

