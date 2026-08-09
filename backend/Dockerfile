# syntax=docker/dockerfile:1
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

# Dependencias del sistema necesarias para compilar psycopg y otras libs nativas.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# uv como gestor de dependencias / entorno virtual.
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copiar solo los archivos de definición de dependencias primero, para
# aprovechar el cacheo de capas de Docker: si el código cambia pero las
# dependencias no, esta capa no se vuelve a construir. El entorno virtual
# se crea en /opt/venv (fuera de /app) a propósito: en docker-compose.yml,
# el servicio "backend" monta ./backend:/app como bind mount para permitir
# desarrollo con hot-reload, y ese montaje reemplaza cualquier contenido
# de /app por el del host — si el .venv viviera dentro de /app, el montaje
# lo taparía y el contenedor arrancaría sin dependencias instaladas.
COPY pyproject.toml ./
COPY uv.lock* ./
RUN uv sync --no-dev

# Resto del código del proyecto (todavía sin apps de negocio en esta tarea).
COPY . .

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
