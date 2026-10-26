import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env if present (simple parser, no extra dependency). Real environment variables win.
_env = BASE_DIR / ".env"
if _env.exists():
    for line in _env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

ON_VERCEL = bool(os.environ.get("VERCEL"))
ON_RENDER = bool(os.environ.get("RENDER"))
HOSTED = ON_VERCEL or ON_RENDER

# Safe default: debug is ON only on your own computer.
DEBUG = os.environ.get("DEBUG", "0" if HOSTED else "1") == "1"

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-insecure-key-change-me"
    else:
        raise ImproperlyConfigured("SECRET_KEY is not set. Add it in your hosting dashboard under Environment Variables.")

_hosts = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]
if not _hosts:
    _hosts = ["*"] if DEBUG else ["localhost", "127.0.0.1"]
if ON_VERCEL:
    _hosts.append(".vercel.app")
if ON_RENDER:
    _hosts.append(".onrender.com")
ALLOWED_HOSTS = _hosts

CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
if ON_VERCEL:
    CSRF_TRUSTED_ORIGINS.append("https://*.vercel.app")
if ON_RENDER:
    CSRF_TRUSTED_ORIGINS.append("https://*.onrender.com")

if not DEBUG:  # behind the host's HTTPS proxy
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

SHOP_NAME = os.environ.get("SHOP_NAME", "Rosée")

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "store", "orders", "dashboard",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "store.context.shop",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"

# Empty or missing DATABASE_URL -> local SQLite file (fine on your computer, NOT on Vercel).
_db_url = os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
DATABASES = {"default": dj_database_url.parse(_db_url, conn_max_age=0 if ON_VERCEL else 600)}
if ON_VERCEL and DATABASES["default"]["ENGINE"].endswith("sqlite3"):
    raise ImproperlyConfigured("DATABASE_URL is not set. Vercel cannot keep a SQLite file: add your Neon PostgreSQL connection string.")

AUTH_PASSWORD_VALIDATORS = [{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"}]
LANGUAGE_CODE = "en"
TIME_ZONE = "Africa/Algiers"
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
WHITENOISE_USE_FINDERS = True  # serve static files straight from the repo: no collectstatic step needed
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
# Uploaded photos go to Cloudinary when CLOUDINARY_URL is set (required on Vercel).
if os.environ.get("CLOUDINARY_URL"):
    STORAGES["default"] = {"BACKEND": "store.storage.CloudinaryStorage"}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/dashboard/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30
