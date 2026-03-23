import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env if present (local dev / Docker env-file)
load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-c*$3m0@v!nwp(ep^ql3x_!9p%)xfxl%gp%r0x7=q)^zim57=^4",
)
JWT_SECRET = os.environ.get("JWT_SECRET", "")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "auth_api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "siriapp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "siriapp.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

# JWT / Auth settings
_access_minutes = int(os.environ.get("ACCESS_TOKEN_MINUTES", "15"))
_refresh_minutes = int(os.environ.get("REFRESH_TOKEN_MINUTES", "0"))
_refresh_hours = int(os.environ.get("REFRESH_TOKEN_HOURS", "0"))
_refresh_days = int(os.environ.get("REFRESH_TOKEN_DAYS", "0"))

if _refresh_minutes > 0:
    _refresh_lifetime = timedelta(minutes=_refresh_minutes)
elif _refresh_hours > 0:
    _refresh_lifetime = timedelta(hours=_refresh_hours)
elif _refresh_days > 0:
    _refresh_lifetime = timedelta(days=_refresh_days)
else:
    _refresh_lifetime = timedelta(hours=2)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=_access_minutes),
    "REFRESH_TOKEN_LIFETIME": _refresh_lifetime,
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "SIGNING_KEY": JWT_SECRET or SECRET_KEY,
}

# Refresh cookie (sliding inactivity expiry)
AUTH_REFRESH_COOKIE_NAME = os.environ.get("AUTH_REFRESH_COOKIE_NAME", "refresh_token")
AUTH_REFRESH_COOKIE_MAX_AGE = int(os.environ.get("REFRESH_COOKIE_MAX_AGE", "7200"))
AUTH_REFRESH_COOKIE_SECURE = os.environ.get("AUTH_REFRESH_COOKIE_SECURE", "1") == "1"
AUTH_REFRESH_COOKIE_SAMESITE = os.environ.get("AUTH_REFRESH_COOKIE_SAMESITE", "Lax")
AUTH_REFRESH_COOKIE_PATH = "/"

# Access cookie (optional helper; access token is still returned in JSON)
AUTH_ACCESS_COOKIE_NAME = os.environ.get("AUTH_ACCESS_COOKIE_NAME", "access_token")
AUTH_ACCESS_COOKIE_MAX_AGE = int(os.environ.get("ACCESS_COOKIE_MAX_AGE", "900"))
AUTH_ACCESS_COOKIE_SECURE = os.environ.get("AUTH_ACCESS_COOKIE_SECURE", "1") == "1"
AUTH_ACCESS_COOKIE_SAMESITE = os.environ.get("AUTH_ACCESS_COOKIE_SAMESITE", "Lax")
AUTH_ACCESS_COOKIE_PATH = "/"

# Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY", "")
