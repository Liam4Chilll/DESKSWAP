FROM python:3.11-alpine

LABEL maintainer="Your Name <your.email@example.com>"
LABEL description="Desk Swap - Simple File Manager for Docker"
LABEL version="1.0"

# Install dependencies
RUN apk add --no-cache \
    wget \
    && pip install --no-cache-dir flask gunicorn

# Create app directory
WORKDIR /app

# Copy application files
COPY app.py .
COPY templates/ templates/

# Create data directory
RUN mkdir -p /data

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8080 || exit 1

# Run with Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "app:app"]
