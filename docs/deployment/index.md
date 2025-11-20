# Deployment Guide

This section provides comprehensive guides for deploying your Python application to production environments.

## Overview

This project is designed to be deployed in containerized environments with Azure services integration. The deployment guides cover:

- **Azure Deployment** - Deploying to Azure Container Apps, App Service, and AKS
- **Docker Production** - Building optimized production images
- **Secrets Management** - Secure handling of credentials and API keys
- **Monitoring** - Application Insights and Azure Monitor setup

## Quick Start

For a quick production deployment:

1. **Build the Docker image**:
   ```bash
   docker build -t myapp:latest .
   ```

2. **Set environment variables**:
   ```bash
   export IS_LOCAL=false
   export DEBUG=false
   export AZURE_MONITOR_CONNECTION_STRING="your-connection-string"
   ```

3. **Run the container**:
   ```bash
   docker run -p 8000:8000 \
     -e IS_LOCAL=false \
     -e AZURE_MONITOR_CONNECTION_STRING=$AZURE_MONITOR_CONNECTION_STRING \
     myapp:latest
   ```

## Deployment Guides

### [Azure Deployment](azure.md)
Learn how to deploy your application to Azure services:
- Azure Container Apps (recommended)
- Azure App Service
- Azure Kubernetes Service (AKS)
- CI/CD with Azure Pipelines

### [Docker Production](docker.md)
Best practices for production Docker builds:
- Multi-stage builds
- Image optimization
- Security hardening
- Health checks

### [Secrets Management](secrets.md)
Secure credential management:
- Azure Key Vault integration
- Environment variables
- Managed identities
- Secret rotation

### [Monitoring & Logging](monitoring.md)
Application monitoring and observability:
- Azure Monitor setup
- Application Insights
- Log aggregation
- Alerting strategies

## Prerequisites

Before deploying to production, ensure:

- [ ] Docker installed locally for testing
- [ ] Azure subscription (for Azure deployments)
- [ ] Azure CLI installed and configured
- [ ] Application Insights resource created
- [ ] Environment variables documented
- [ ] Tests passing (`uv run nox -s test`)
- [ ] Code linted (`uv run nox -s lint -- --pyright --ruff`)

## Environment Configuration

Production deployments require specific environment variables:

```bash
# Required
IS_LOCAL=false
DEBUG=false

# Azure Monitor (required for production logging)
AZURE_MONITOR_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=https://xxx

# Application Settings
TITLE=My Production API
VERSION=1.0.0
API_PREFIX_V1=/api/v1
ALLOWED_HOSTS=["myapp.azurewebsites.net", "myapp.com"]
```

See [Environment Variables Reference](../configurations/environment-variables.md) for complete documentation.

## Production Checklist

Before going to production:

### Code Quality
- [ ] All tests passing with 75%+ coverage
- [ ] No linting errors (Pyright + Ruff)
- [ ] Code reviewed and approved
- [ ] Dependencies updated and locked (`uv.lock`)

### Configuration
- [ ] Environment variables documented
- [ ] Secrets stored securely (Azure Key Vault)
- [ ] CORS configured correctly (`ALLOWED_HOSTS`)
- [ ] Debug mode disabled (`DEBUG=false`)

### Docker
- [ ] Production Dockerfile tested
- [ ] Image built and scanned for vulnerabilities
- [ ] Container runs successfully locally
- [ ] Health check endpoint implemented

### Azure Setup
- [ ] Resource group created
- [ ] Application Insights configured
- [ ] Managed identity assigned
- [ ] Key Vault access configured

### Monitoring
- [ ] Logging configured (Azure Monitor)
- [ ] Alerts set up for errors
- [ ] Performance metrics tracked
- [ ] Log retention configured

### Security
- [ ] HTTPS enforced
- [ ] Authentication implemented
- [ ] API rate limiting enabled
- [ ] Security headers configured
- [ ] Secrets rotated regularly

## Deployment Workflow

### 1. Local Testing
```bash
# Run tests
uv run nox -s test

# Lint code
uv run nox -s lint -- --pyright --ruff

# Build Docker image
docker build -t myapp:test .

# Test container locally
docker run -p 8000:8000 \
  -e IS_LOCAL=false \
  -e DEBUG=false \
  myapp:test
```

### 2. Push to Registry
```bash
# Tag image
docker tag myapp:test myregistry.azurecr.io/myapp:latest

# Login to Azure Container Registry
az acr login --name myregistry

# Push image
docker push myregistry.azurecr.io/myapp:latest
```

### 3. Deploy to Azure
```bash
# Deploy to Azure Container Apps
az containerapp up \
  --name myapp \
  --resource-group myapp-rg \
  --image myregistry.azurecr.io/myapp:latest \
  --environment myapp-env \
  --env-vars IS_LOCAL=false DEBUG=false
```

### 4. Verify Deployment
```bash
# Check application status
az containerapp show --name myapp --resource-group myapp-rg

# View logs
az containerapp logs show --name myapp --resource-group myapp-rg

# Test endpoint
curl https://myapp.azurecontainerapps.io/api/v1/
```

## Troubleshooting

### Container Won't Start
- Check logs: `docker logs container-id`
- Verify environment variables are set
- Ensure all required dependencies are installed
- Check port bindings

### Application Insights Not Receiving Logs
- Verify `AZURE_MONITOR_CONNECTION_STRING` is set correctly
- Ensure `IS_LOCAL=false`
- Check connection string format includes both `InstrumentationKey` and `IngestionEndpoint`
- Wait 2-5 minutes for initial telemetry to appear

### High Memory Usage
- Review container resource limits
- Check for memory leaks in application code
- Consider vertical scaling
- Implement connection pooling

### Slow Performance
- Enable Application Insights profiling
- Review database query performance
- Check external API response times
- Consider caching strategies
- Scale horizontally

## Support

For issues or questions:
- Check the [documentation](../index.md)
- Review [Azure documentation](https://docs.microsoft.com/azure)
- Open an issue on [GitHub](https://github.com/CRDigitalAndMining/python-uv/issues)

## Next Steps

- [Deploy to Azure](azure.md) - Step-by-step Azure deployment
- [Docker Production Guide](docker.md) - Optimize your Docker images
- [Secrets Management](secrets.md) - Secure your credentials
- [Monitoring Setup](monitoring.md) - Configure observability
