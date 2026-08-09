#!/usr/bin/env python
"""Utilidad de línea de comandos de Django para tareas administrativas."""

import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Está instalado y disponible en tu "
            "PYTHONPATH? ¿Olvidaste activar el entorno? Si usas uv, prueba "
            "con `uv run manage.py ...`."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
