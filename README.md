# Ruta Agustina

Plataforma web de planificación académica para estudiantes de la
Universidad Nacional de San Agustín de Arequipa (UNSA).

Este repositorio es un monorepo con dos proyectos:

- **`backend/`** — API REST en Django + Django REST Framework (monolito
  modular). Esta tarea deja únicamente la configuración base
  (`config/`, Docker, dependencias, linting, testing); todavía no hay
  ninguna app de negocio implementada.
- **`frontend/`** — actualmente un placeholder (ver
  [`frontend/README.md`](./frontend/README.md)). El frontend real es un
  proyecto en React desplegado en Vercel.

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) y Docker Compose, **o**
- [uv](https://docs.astral.sh/uv/) + Python 3.14 (para correr el backend
  directamente, sin Docker) y un PostgreSQL accesible.

## Levantar el proyecto con Docker Compose (recomendado)

1. Copia el archivo de variables de entorno de ejemplo:

   ```bash
   cp backend/.env.example backend/.env
   ```

   Ajusta `DJANGO_SECRET_KEY` y lo que necesites. Los valores por defecto ya
   apuntan al Postgres local que levanta el propio `docker-compose` (no a
   Supabase).

2. Levanta todo el stack (backend + base de datos local + frontend):

   ```bash
   docker compose up --build
   ```

3. Verifica que el backend responde con la documentación de la API:

   - Schema OpenAPI: <http://localhost:8000/api/schema/>
   - Swagger UI: <http://localhost:8000/api/docs/>

   Todavía no hay ningún endpoint de negocio — solo la infraestructura de
   DRF funcionando (no hay apps de negocio en esta tarea).

4. Para correr comandos de Django dentro del contenedor (migraciones,
   `createsuperuser`, etc.):

   ```bash
   docker compose exec backend python manage.py migrate
   docker compose exec backend python manage.py createsuperuser
   ```

> **Nota:** el Postgres de `docker-compose` es solo para desarrollo local.
> En producción (Render) el backend se conecta a Supabase, usando las
> mismas variables de entorno con otros valores — el código de settings no
> cambia entre ambos casos.

## Levantar solo el backend con uv (sin Docker)

Necesitas un PostgreSQL corriendo en algún lado (por ejemplo, solo el
servicio `db` de este mismo compose: `docker compose up db`).

```bash
cd backend
cp .env.example .env   # ajusta DB_HOST=localhost si el Postgres no está en Docker

uv sync                 # instala dependencias de producción + desarrollo
uv run python manage.py migrate
uv run python manage.py runserver
```

## Tests

```bash
cd backend
uv run pytest
```

La configuración de pytest (`pytest-django`, `DJANGO_SETTINGS_MODULE`, etc.)
vive en `pyproject.toml` y ya está lista para cuando existan apps con
tests — no requiere configuración adicional.

## Linter y formato (Ruff)

```bash
cd backend
uv run ruff check .      # lint
uv run ruff format .     # formato
```

## Estructura del backend

```
backend/
├── config/               # Configuración del proyecto (settings, URLs raíz, wsgi/asgi)
│   ├── settings/
│   │   ├── base.py       # Compartido por todos los entornos
│   │   ├── local.py      # Desarrollo (hereda de base.py)
│   │   └── production.py # Producción / Render (hereda de base.py)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                 # Futuras apps de negocio (core, accounts, curricula, ...)
│   └── README.md         # Convención a seguir cuando se agreguen apps
├── manage.py
├── pyproject.toml        # Dependencias (uv), Ruff y pytest
├── Dockerfile
├── .dockerignore
└── .env.example
```

## Fuera de alcance de esta configuración inicial

- Apps de negocio (`core`, `accounts`, `curricula`, etc.).
- Lógica de negocio, modelos o vistas.
- Flujo real de login con Google (solo está declarado JWT como mecanismo
  de autenticación).
- CI/CD (GitHub Actions).
