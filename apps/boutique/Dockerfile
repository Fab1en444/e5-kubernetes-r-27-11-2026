# Étape 1 : installation des dépendances dans un environnement virtuel
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /venv && /venv/bin/pip install --no-cache-dir -r requirements.txt

# Étape 2 : image finale minimale, utilisateur non-root
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/venv/bin:$PATH"
RUN useradd -r -u 10001 appuser
WORKDIR /app
COPY --from=builder /venv /venv
COPY app.py init_db.py ./
COPY templates/ templates/
USER 10001
EXPOSE 5000
# 1 worker + 4 threads : économe en mémoire
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--access-logfile", "-", "app:app"]
