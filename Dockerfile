# Utilisation de l'image slim
FROM python:3.12-slim

# Empêcher Python de générer des fichiers .pyc et forcer les logs dans le terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Installation des dépendances système requises (spécifiquement pour confluent-kafka)
# Le paramètre --no-install-recommends et le rm -rf allègent considérablement la taille de l'image finale
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Séparation de la copie des dépendances (Layer Caching)
# ASTUCE : Il est fortement recommandé d'utiliser un requirements.txt. 
# Si tu modifies ton code API, Docker n'aura pas à retélécharger toutes ces librairies lourdes.
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Si tu maintiens l'installation inline, la voici :
RUN pip install --no-cache-dir fastapi uvicorn pandas pymongo redis pyarrow fastparquet openpyxl kafka-python confluent-kafka cassandra-driver requests strawberry-graphql neo4j

# 3. Création d'un utilisateur non-root pour des raisons de sécurité
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app
USER appuser

# 4. Copie du code source après l'installation des dépendances
COPY . .

EXPOSE 8080

CMD ["uvicorn", "pipeline.export.imf.imf_export.api.main:app", "--host", "0.0.0.0", "--port", "8080"]