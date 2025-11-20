# Docker Production Guide

Optimize your Docker images for production deployments with security, performance, and size in mind.

## Production Dockerfile

The included `Dockerfile` is optimized for production with:
- Multi-stage builds to minimize image size
- Non-root user for security
- Health checks for reliability
- Efficient layer caching

### Current Dockerfile Analysis

```dockerfile
# Stage 1: Build stage with uv
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

# Stage 2: Runtime stage
FROM python:3.14-slim-bookworm
# Includes OpenCV dependencies
# Copies only necessary files
# Runs as non-root user
```

## Building for Production

### Build Image

```bash
# Build with specific tag
docker build -t myapp:1.0.0 .

# Build with build args
docker build \
  --build-arg VARIANT=3.14 \
  -t myapp:1.0.0 \
  .

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t myapp:1.0.0 \
  .
```

### Optimize Build

```bash
# Use BuildKit for better caching
DOCKER_BUILDKIT=1 docker build -t myapp:1.0.0 .

# Build with no cache
docker build --no-cache -t myapp:1.0.0 .
```

## Image Optimization

### 1. Multi-Stage Builds ✅

Already implemented. Reduces image size by ~50%.

### 2. Minimize Layers

```dockerfile
# ❌ Bad - Multiple layers
RUN apt-get update
RUN apt-get install -y package1
RUN apt-get install -y package2

# ✅ Good - Single layer
RUN apt-get update && \
    apt-get install -y package1 package2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### 3. Use .dockerignore

Create `.dockerignore`:

```
.git
.gitignore
.venv
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
htmlcov
.coverage
*.md
!README.md
docs/
tests/
.devcontainer
```

### 4. Order Dockerfile Instructions

```dockerfile
# 1. Install system dependencies (changes rarely)
# 2. Copy dependency files (changes occasionally)
# 3. Install Python dependencies (changes occasionally)
# 4. Copy application code (changes frequently)
```

## Security Best Practices

### 1. Run as Non-Root User ✅

Already implemented in Dockerfile:

```dockerfile
RUN useradd -m -u 1000 user && chown -R user /app
USER user
```

### 2. Scan for Vulnerabilities

```bash
# Using Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image myapp:1.0.0

# Using Docker Scout
docker scout cves myapp:1.0.0

# Using Snyk
snyk container test myapp:1.0.0
```

### 3. Use Official Base Images

```dockerfile
# ✅ Official Python image
FROM python:3.14-slim-bookworm

# ❌ Avoid unknown sources
FROM randomuser/python:latest
```

### 4. Keep Images Updated

```bash
# Rebuild regularly with latest base image
docker build --pull -t myapp:1.0.0 .
```

### 5. Don't Include Secrets

```dockerfile
# ❌ Never do this
ENV API_KEY=secret123

# ✅ Use runtime environment variables
docker run -e API_KEY=$API_KEY myapp:1.0.0
```

## Health Checks

Add health check to Dockerfile:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"
```

Or use a simple health endpoint:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

## Running in Production

### Basic Run

```bash
docker run -d \
  --name myapp \
  -p 8000:8000 \
  -e IS_LOCAL=false \
  -e DEBUG=false \
  -e AZURE_MONITOR_CONNECTION_STRING="$CONNECTION_STRING" \
  myapp:1.0.0
```

### With Resource Limits

```bash
docker run -d \
  --name myapp \
  -p 8000:8000 \
  --memory="1g" \
  --cpus="1.0" \
  --restart=unless-stopped \
  -e IS_LOCAL=false \
  myapp:1.0.0
```

### With Docker Compose

**docker-compose.prod.yml**:

```yaml
version: '3.8'

services:
  api:
    image: myapp:1.0.0
    ports:
      - "8000:8000"
    environment:
      IS_LOCAL: false
      DEBUG: false
      AZURE_MONITOR_CONNECTION_STRING: ${AZURE_MONITOR_CONNECTION_STRING}
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"\]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

Run with:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Image Registry

### Push to Docker Hub

```bash
docker login
docker tag myapp:1.0.0 username/myapp:1.0.0
docker push username/myapp:1.0.0
```

### Push to Azure Container Registry

```bash
az acr login --name myregistry
docker tag myapp:1.0.0 myregistry.azurecr.io/myapp:1.0.0
docker push myregistry.azurecr.io/myapp:1.0.0
```

### Push to GitHub Container Registry

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker tag myapp:1.0.0 ghcr.io/username/myapp:1.0.0
docker push ghcr.io/username/myapp:1.0.0
```

## Image Tagging Strategy

```bash
# Version tag
docker tag myapp:latest myapp:1.0.0

# Git commit SHA
docker tag myapp:latest myapp:$(git rev-parse --short HEAD)

# Build number (CI/CD)
docker tag myapp:latest myapp:build-$BUILD_NUMBER

# Environment
docker tag myapp:1.0.0 myapp:1.0.0-production
```

## Monitoring Container

### View Logs

```bash
docker logs myapp
docker logs -f myapp  # Follow logs
docker logs --tail 100 myapp  # Last 100 lines
```

### Inspect Container

```bash
docker inspect myapp
docker stats myapp
docker top myapp
```

### Execute Commands

```bash
# Run shell
docker exec -it myapp /bin/bash

# Run Python
docker exec -it myapp python

# Check Python version
docker exec myapp python --version
```

## Performance Tuning

### 1. Use Production WSGI Server

Add to your app (e.g., using Gunicorn for FastAPI):

```bash
uv add gunicorn uvicorn[standard]
```

Update `CMD` in Dockerfile:

```dockerfile
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 2. Enable HTTP/2

When using a reverse proxy:

```nginx
server {
    listen 443 ssl http2;
    # ...
}
```

### 3. Optimize Python

```dockerfile
# Use optimized Python
ENV PYTHONOPTIMIZE=1
ENV PYTHONDONTWRITEBYTECODE=1
```

## Troubleshooting

### Container Exits Immediately

```bash
# Check logs
docker logs myapp

# Run interactively
docker run -it --rm myapp /bin/bash
```

### Out of Memory

```bash
# Check current usage
docker stats myapp

# Increase memory limit
docker update --memory="2g" myapp
```

### Slow Build Times

- Use Docker BuildKit
- Optimize layer caching
- Use `.dockerignore`
- Consider multi-stage builds

## Best Practices Checklist

- [ ] Use multi-stage builds
- [ ] Run as non-root user
- [ ] Scan for vulnerabilities
- [ ] Add health checks
- [ ] Use `.dockerignore`
- [ ] Pin base image versions
- [ ] Set resource limits
- [ ] Configure logging
- [ ] Use production WSGI server
- [ ] Enable restart policies

## Next Steps

- [Azure Deployment](azure.md) - Deploy containers to Azure
- [Secrets Management](secrets.md) - Secure credential handling
- [Monitoring Setup](monitoring.md) - Track application health

## Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
