from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_DIR = BASE_DIR.parent

env = environ.Env()
environ.Env.read_env(ROOT_DIR / '.env')

SECRET_KEY = env('DJANGO_SECRET_KEY')

DEBUG = env.bool(
    'DJANGO_DEBUG',
    default=False,
)

SITE_ID = 1

ALLOWED_HOSTS = env.list(
    'DJANGO_ALLOWED_HOSTS',
    default=[],
)

CORS_ALLOWED_ORIGINS = env.list(
    'DJANGO_CORS_ALLOWED_ORIGINS',
    default=[],
)

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env.list(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    default=[],
)

SECURE_SSL_REDIRECT = not DEBUG

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SECURE_HSTS_SECONDS = env.int(
    'DJANGO_SECURE_HSTS_SECONDS',
    default=0,
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    'DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS',
    default=False,
)
SECURE_HSTS_PRELOAD = env.bool(
    'DJANGO_SECURE_HSTS_PRELOAD',
    default=False,
)

if env.bool(
    'DJANGO_TRUST_PROXY_SSL_HEADER',
    default=False,
):
    SECURE_PROXY_SSL_HEADER = (
        'HTTP_X_FORWARDED_PROTO',
        'https',
    )

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.headless',
    'rest_framework',
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.core',
    'apps.accounts',
    'apps.academics',
    'apps.scheduling',
    'apps.grading',
    'apps.syllabi',
]

INSTALLED_APPS = [
    *DJANGO_APPS,
    *THIRD_PARTY_APPS,
    *LOCAL_APPS,
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'apps.core.middleware.RequestIDMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = env(
    'DATABASE_URL',
    default='',
)

if DATABASE_URL:
    DATABASES = {
        'default': env.db_url_config(
            DATABASE_URL,
        ),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('POSTGRES_DB'),
            'USER': env('POSTGRES_USER'),
            'PASSWORD': env('POSTGRES_PASSWORD'),
            'HOST': env(
                'POSTGRES_HOST',
                default='localhost',
            ),
            'PORT': env.int(
                'POSTGRES_PORT',
                default=5432,
            ),
        }
    }

REDIS_URL = env(
    'REDIS_URL',
    default='',
)

if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': ('django.core.cache.backends.redis.RedisCache'),
            'LOCATION': REDIS_URL,
            'KEY_PREFIX': 'augustinian-path',
        },
    }
else:
    CACHES = {
        'default': {
            'BACKEND': ('django.core.cache.backends.locmem.LocMemCache'),
            'LOCATION': 'augustinian-path-local',
            'KEY_PREFIX': 'augustinian-path',
        },
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'accounts.User'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*']
ACCOUNT_EMAIL_VERIFICATION = 'none'

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

HEADLESS_ONLY = True
HEADLESS_CLIENTS = ('browser',)

FRONTEND_URL = env(
    'FRONTEND_URL',
    default='http://localhost:5173',
).rstrip('/')

HEADLESS_FRONTEND_URLS = {
    'socialaccount_login_error': FRONTEND_URL,
}

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APPS': [
            {
                'client_id': env(
                    'GOOGLE_OAUTH_CLIENT_ID',
                    default='',
                ),
                'secret': env(
                    'GOOGLE_OAUTH_CLIENT_SECRET',
                    default='',
                ),
                'key': '',
            },
        ],
        'SCOPE': [
            'profile',
            'email',
        ],
        'OAUTH_PKCE_ENABLED': True,
    },
}

ACCOUNT_ADAPTER = 'apps.accounts.adapters.GoogleOnlyAccountAdapter'

SOCIALACCOUNT_ADAPTER = 'apps.accounts.adapters.InstitutionalSocialAccountAdapter'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'apps.core.throttles.AnonymousBurstRateThrottle',
        'apps.core.throttles.AnonymousSustainedRateThrottle',
        'apps.core.throttles.UserBurstRateThrottle',
        'apps.core.throttles.UserSustainedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anonymous_burst': env(
            'DJANGO_THROTTLE_ANONYMOUS_BURST_RATE',
            default='120/min',
        ),
        'anonymous_sustained': env(
            'DJANGO_THROTTLE_ANONYMOUS_SUSTAINED_RATE',
            default='5000/day',
        ),
        'user_burst': env(
            'DJANGO_THROTTLE_USER_BURST_RATE',
            default='120/min',
        ),
        'user_sustained': env(
            'DJANGO_THROTTLE_USER_SUSTAINED_RATE',
            default='2000/day',
        ),
    },
    'EXCEPTION_HANDLER': ('apps.core.exceptions.api_exception_handler'),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Ruta Agustina API',
    'DESCRIPTION': (
        'API para la planificación académica y generación inteligente de horarios.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'ENUM_NAME_OVERRIDES': {
        'StudentCourseAttemptStatusEnum': [
            ('ENROLLED', 'En curso'),
            ('PASSED', 'Aprobado'),
            ('FAILED', 'Desaprobado'),
            ('WITHDRAWN', 'Retirado'),
        ],
        'SyllabusStatusEnum': [
            ('DRAFT', 'Borrador'),
            ('PUBLISHED', 'Publicado'),
            ('ARCHIVED', 'Archivado'),
        ],
    },
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.hooks.postprocess_schema_enums',
        ('apps.core.openapi.add_standard_error_responses'),
    ],
}


LANGUAGE_CODE = 'es-pe'

TIME_ZONE = 'America/Lima'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': ('whitenoise.storage.CompressedManifestStaticFilesStorage'),
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
