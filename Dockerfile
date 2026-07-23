FROM python:3.12-slim

WORKDIR /app

# Dependance systeme pour numpy/pandas
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY economie/dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY economie/dashboard/ .

# Cloud Run injecte PORT ; 8080 par defaut
ENV PORT=8080
EXPOSE ${PORT}

# gunicorn avec 2 workers ; le cache TTL est par worker (x2 requetes BQ max)
CMD exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 --timeout 120 app:server
