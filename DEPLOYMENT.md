# Deployment Guide

Advanced deployment scenarios for Desk Swap.

## Table of Contents

- [Production Deployment](#production-deployment)
- [Reverse Proxy Setup](#reverse-proxy-setup)
- [Authentication](#authentication)
- [HTTPS Configuration](#https-configuration)
- [Cloud Platforms](#cloud-platforms)
- [Monitoring](#monitoring)

## Production Deployment

### Environment Variables

```yaml
environment:
  - ROOT_PATH=/data                    # Root directory
  - FLASK_PORT=8080                    # Server port
  - PYTHONUNBUFFERED=1                 # Python logging
  - GUNICORN_WORKERS=4                 # Number of workers
  - GUNICORN_TIMEOUT=120               # Request timeout
```

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

### Health Checks

```yaml
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:8080"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 5s
```

## Reverse Proxy Setup

### Nginx

```nginx
server {
    listen 80;
    server_name files.yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for large file downloads
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        
        # Increase buffer size for large files
        proxy_buffering off;
        proxy_request_buffering off;
    }
}
```

### Traefik

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.deskswap.rule=Host(`files.yourdomain.com`)"
  - "traefik.http.routers.deskswap.entrypoints=websecure"
  - "traefik.http.routers.deskswap.tls.certresolver=letsencrypt"
  - "traefik.http.services.deskswap.loadbalancer.server.port=8080"
```

### Caddy

```caddy
files.yourdomain.com {
    reverse_proxy localhost:8080
    
    # Increase timeouts
    timeouts {
        read_body 5m
        write 5m
    }
}
```

## Authentication

### Basic Auth with Nginx

```nginx
server {
    listen 80;
    server_name files.yourdomain.com;
    
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    location / {
        proxy_pass http://localhost:8080;
        # ... other proxy settings
    }
}
```

Create password file:
```bash
sudo htpasswd -c /etc/nginx/.htpasswd username
```

### OAuth2 Proxy

```yaml
services:
  oauth2-proxy:
    image: quay.io/oauth2-proxy/oauth2-proxy:latest
    command:
      - --provider=google
      - --email-domain=yourdomain.com
      - --upstream=http://deskswap:8080
      - --http-address=0.0.0.0:4180
    environment:
      - OAUTH2_PROXY_CLIENT_ID=your-client-id
      - OAUTH2_PROXY_CLIENT_SECRET=your-client-secret
      - OAUTH2_PROXY_COOKIE_SECRET=your-cookie-secret
    ports:
      - "4180:4180"
    
  deskswap:
    build: .
    # ... existing config
```

## HTTPS Configuration

### Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d files.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Self-Signed Certificate

```bash
# Generate certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/deskswap.key \
  -out /etc/ssl/certs/deskswap.crt

# Nginx configuration
server {
    listen 443 ssl;
    server_name files.yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/deskswap.crt;
    ssl_certificate_key /etc/ssl/private/deskswap.key;
    
    # ... rest of config
}
```

## Cloud Platforms

### AWS ECS

```json
{
  "family": "deskswap",
  "containerDefinitions": [
    {
      "name": "deskswap",
      "image": "yourusername/deskswap:latest",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "mountPoints": [
        {
          "sourceVolume": "data",
          "containerPath": "/data",
          "readOnly": true
        }
      ]
    }
  ],
  "volumes": [
    {
      "name": "data",
      "host": {
        "sourcePath": "/your/data/path"
      }
    }
  ]
}
```

### Google Cloud Run

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: deskswap
spec:
  template:
    spec:
      containers:
      - image: gcr.io/your-project/deskswap:latest
        ports:
        - containerPort: 8080
        env:
        - name: ROOT_PATH
          value: "/data"
        volumeMounts:
        - name: data
          mountPath: /data
          readOnly: true
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: data-pvc
```

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name deskswap \
  --image yourusername/deskswap:latest \
  --dns-name-label deskswap \
  --ports 8080 \
  --cpu 1 \
  --memory 1 \
  --azure-file-volume-account-name mystorageaccount \
  --azure-file-volume-account-key $STORAGE_KEY \
  --azure-file-volume-share-name myshare \
  --azure-file-volume-mount-path /data
```

## Monitoring

### Prometheus Metrics

Add to `app.py`:

```python
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)
```

### Logging Configuration

```yaml
services:
  deskswap:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Health Check Endpoint

Add to `app.py`:

```python
@app.route('/health')
def health():
    return {'status': 'healthy', 'version': '1.0'}, 200
```

## Performance Tuning

### Large File Optimization

```yaml
environment:
  - GUNICORN_WORKERS=4
  - GUNICORN_TIMEOUT=300
  - GUNICORN_WORKER_CLASS=sync
  - GUNICORN_MAX_REQUESTS=1000
  - GUNICORN_MAX_REQUESTS_JITTER=50
```

### Caching Headers

Add to nginx:

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Security Hardening

### Container Security

```dockerfile
# Run as non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
```

### Read-Only Root Filesystem

```yaml
services:
  deskswap:
    read_only: true
    tmpfs:
      - /tmp
```

### Security Headers

Add to nginx:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

## Backup and Recovery

### Volume Backup

```bash
# Backup
docker run --rm \
  -v deskswap_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/deskswap-backup.tar.gz /data

# Restore
docker run --rm \
  -v deskswap_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/deskswap-backup.tar.gz -C /
```

## Troubleshooting

### Check Logs

```bash
docker compose logs -f deskswap
```

### Verify Permissions

```bash
docker compose exec deskswap ls -la /data
```

### Test Connection

```bash
curl -I http://localhost:8080
```

### Performance Testing

```bash
ab -n 1000 -c 10 http://localhost:8080/
```

