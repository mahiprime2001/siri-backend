FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY siriapp ./siriapp
COPY auth_api ./auth_api
COPY manage.py ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

EXPOSE 5050

CMD ["sh", "-c", "python manage.py migrate && gunicorn siriapp.wsgi:application --bind 0.0.0.0:5050"]
