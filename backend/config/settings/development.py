from .base import *  # noqa: F401,F403
from .base import env

DEBUG = env.bool("DJANGO_DEBUG", default=True)

DATABASES["default"]["OPTIONS"]["sslmode"] = env.str("DB_SSLMODE", default="disable")  # noqa: F405
