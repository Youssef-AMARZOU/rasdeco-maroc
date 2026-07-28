FROM python:3.12-slim

WORKDIR /app

# Install system deps for google-cloud SDK
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    | tee /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    apt-get update && apt-get install -y --no-install-recommends google-cloud-sdk && \
    rm -rf /var/lib/apt/lists/*

COPY dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose le port Cloud Run
ENV PORT=8080
EXPOSE 8080

CMD exec gunicorn dashboard.app:server \
    --bind :$PORT \
    --workers 2 \
    --timeout 120 \
    --access-logfile -
