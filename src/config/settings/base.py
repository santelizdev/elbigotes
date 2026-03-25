from pathlib import Path

from config.settings.env import BASE_DIR, get_bool, get_env, get_int, get_list


SECRET_KEY = get_env("DJANGO_SECRET_KEY", "unsafe-development-secret-key")
DEBUG = get_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = get_list("DJANGO_ALLOWED_HOSTS", ["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = get_list("DJANGO_CSRF_TRUSTED_ORIGINS", [])

LANGUAGE_CODE = get_env("DJANGO_LANGUAGE_CODE", "es-cl")
TIME_ZONE = get_env("DJANGO_TIME_ZONE", "America/Santiago")
USE_I18N = True
USE_TZ = True

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "corsheaders",
    "rest_framework",
    "django_filters",
    "apps.core",
    "apps.accounts",
    "apps.memberships",
    "apps.taxonomy",
    "apps.places",
    "apps.lost_pets",
    "apps.claims",
    "apps.ingestion",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

AUTH_USER_MODEL = "accounts.User"

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": get_env("POSTGRES_DB", "elbigotes"),
        "USER": get_env("POSTGRES_USER", "elbigotes"),
        "PASSWORD": get_env("POSTGRES_PASSWORD", "elbigotes"),
        "HOST": get_env("POSTGRES_HOST", "localhost"),
        "PORT": get_int("POSTGRES_PORT", 5432),
    }
}

STATIC_URL = "/static/"
STATIC_ROOT = Path(get_env("DJANGO_STATIC_ROOT", str(BASE_DIR / "staticfiles")))
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(get_env("DJANGO_MEDIA_ROOT", str(BASE_DIR / "media")))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = get_list("CORS_ALLOWED_ORIGINS", [])
CORS_ALLOWED_ORIGIN_REGEXES = get_list("CORS_ALLOWED_ORIGIN_REGEXES", [])
CORS_ALLOW_ALL_ORIGINS = get_bool("CORS_ALLOW_ALL_ORIGINS", False)
CORS_ALLOW_CREDENTIALS = get_bool("CORS_ALLOW_CREDENTIALS", False)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": get_env("API_THROTTLE_ANON", "120/hour"),
        "user": get_env("API_THROTTLE_USER", "600/hour"),
    },
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "apps.core.api.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": get_int("API_PAGE_SIZE", 20),
}

CELERY_BROKER_URL = get_env("CELERY_BROKER_URL", get_env("REDIS_URL", "redis://localhost:6379/0"))
CELERY_RESULT_BACKEND = get_env(
    "CELERY_RESULT_BACKEND", get_env("REDIS_URL", "redis://localhost:6379/1")
)
CELERY_TASK_TIME_LIMIT = get_int("CELERY_TASK_TIME_LIMIT", 300)
CELERY_TASK_SOFT_TIME_LIMIT = get_int("CELERY_TASK_SOFT_TIME_LIMIT", 240)
GEOCODING_PROVIDER = get_env("GEOCODING_PROVIDER", "nominatim")
GEOCODING_TIMEOUT = get_int("GEOCODING_TIMEOUT", 10)
GEOCODING_USER_AGENT = get_env("GEOCODING_USER_AGENT", "elbigotes-backend/0.1")
CELERY_BEAT_SCHEDULE = {
    "ping-ingestion-sources": {
        "task": "apps.ingestion.tasks.sync_active_sources",
        "schedule": 3600.0,
    },
    "place-quality-audit": {
        "task": "apps.ingestion.tasks.audit_places_consistency",
        "schedule": 6 * 3600.0,
    },
    "cleanup-old-sync-runs": {
        "task": "apps.ingestion.tasks.cleanup_old_sync_runs",
        "schedule": 24 * 3600.0,
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
