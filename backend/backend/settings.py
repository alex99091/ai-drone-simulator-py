import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# --- 기본 ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-key")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]").split(",") if h.strip()
]

INSTALLED_APPS = [
    # Django 기본
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 3rd
    "corsheaders",
    "channels",

    # Local apps
    "apps.common.apps.CommonConfig",
    "apps.api.apps.ApiConfig",
    "apps.ws.apps.WsConfig",
    "apps.control.apps.ControlConfig",
    "apps.telemetry.apps.TelemetryConfig",
    "apps.stream.apps.StreamConfig",
    "apps.adapters.apps.AdaptersConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

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
            ],
        },
    },
]

ASGI_APPLICATION = "backend.asgi.application"
WSGI_APPLICATION = "backend.wsgi.application"

# --- DB ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- CORS / CSRF ---
# 기본은 모두 허용(개발 편의). 운영 시 false로 두고 허용 도메인만 열어주세요.
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "true").lower() == "true"
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        o.strip()
        for o in os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if o.strip()
    ]
# CSRF는 별도 목록
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
]
CORS_ALLOW_CREDENTIALS = True

# --- Channels / Redis (조건부) ---
REDIS_URL = os.getenv("REDIS_URL", "").strip()
if REDIS_URL:
    # 운영/로컬에 Redis가 떠 있을 때 사용
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],  # ex) redis://localhost:6379/0
                "symmetric_encryption_keys": [SECRET_KEY],
                "capacity": int(os.getenv("CHANNEL_CAPACITY", "10000")),
            },
        }
    }
else:
    # 개발용: Redis 없이도 WS 동작 (단일 프로세스/인스턴스에서 사용 권장)
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }

# --- Telemetry cache backend (store.py에서 사용) ---
TELEMETRY_CACHE_BACKEND = os.getenv(
    "TELEMETRY_CACHE_BACKEND",
    "redis" if REDIS_URL else "memory"
)
TELEMETRY_REDIS_URL = REDIS_URL or ""

# --- 앱별 기본값 (읽기 전용) ---
TELLO = {
    "IP": os.getenv("TELLO_IP", "192.168.10.1"),
    "CMD_PORT": int(os.getenv("TELLO_CMD_PORT", "8889")),
    "STATE_PORT": int(os.getenv("TELLO_STATE_PORT", "8890")),
    "VIDEO_PORT": int(os.getenv("TELLO_VIDEO_PORT", "11111")),
}
STATUS_POLL_INTERVAL_SEC = int(os.getenv("STATUS_POLL_INTERVAL_SEC", "10"))
VIDEO_JPEG_QUALITY = int(os.getenv("VIDEO_JPEG_QUALITY", "70"))

# --- 로깅 ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "[{levelname}] {name} - {message}", "style": "{"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
