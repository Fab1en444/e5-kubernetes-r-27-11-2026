# Étape 1 : build (compilateur + headers MySQL, nécessaires à mysqlclient)
FROM python:3.10-slim AS builder
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc pkg-config default-libmysqlclient-dev \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /venv && /venv/bin/pip install --no-cache-dir -r requirements.txt
COPY . .
RUN DEBUG=False /venv/bin/python manage.py collectstatic --noinput

# Étape 2 : image finale (bibliothèque client MariaDB uniquement), non-root
FROM python:3.10-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends libmariadb3 \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -r -u 10001 appuser
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/venv/bin:$PATH" DEBUG=False
WORKDIR /app
COPY --from=builder /venv /venv
COPY --from=builder --chown=10001:10001 /app /app
USER 10001
EXPOSE 5005
CMD ["gunicorn", "--bind", "0.0.0.0:5005", "--workers", "1", "--threads", "2", "--access-logfile", "-", "core.wsgi"]
