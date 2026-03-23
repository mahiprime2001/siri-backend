FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY siriapp ./siriapp
COPY auth_api ./auth_api
COPY manage.py ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir uv \
    && UV_SYSTEM_PYTHON=1 uv sync --frozen --no-dev

EXPOSE 8080

CMD ["sh", "-c", "uv run manage.py migrate && uv run gunicorn siriapp.wsgi:application --bind 0.0.0.0:8080"]
