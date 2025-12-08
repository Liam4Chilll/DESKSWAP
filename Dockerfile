FROM python:3.11-alpine

WORKDIR /app

# Installer les dépendances de compilation pour psutil
RUN apk add --no-cache gcc python3-dev musl-dev linux-headers

# Installer Flask et psutil
RUN pip install --no-cache-dir flask psutil

# Copier l'application
COPY app.py .
COPY templates ./templates

# Exposer le port
EXPOSE 8080

# Lancer l'application
CMD ["python", "app.py"]
