# Secrets Management

Secure handling of credentials, API keys, and sensitive configuration data.

## Overview

Never hardcode secrets in your code or Docker images. This guide covers secure secret management practices for production deployments.

## Azure Key Vault (Recommended)

Azure Key Vault provides centralized secret storage with access controls and audit logging.

### Setup Key Vault

```bash
# Variables
RESOURCE_GROUP=myapp-rg
KEYVAULT_NAME=myapp-kv  # Must be globally unique
LOCATION=eastus

# Create Key Vault
az keyvault create \
  --name $KEYVAULT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --enable-rbac-authorization false

# Store secrets
az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name "AzureMonitorConnectionString" \
  --value "InstrumentationKey=xxx;IngestionEndpoint=https://xxx"

az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name "DatabasePassword" \
  --value "your-secure-password"
```

### Grant Access with Managed Identity

```bash
# Get your app's managed identity
PRINCIPAL_ID=$(az containerapp show \
  --name myapp \
  --resource-group $RESOURCE_GROUP \
  --query identity.principalId \
  --output tsv)

# Grant secret read access
az keyvault set-policy \
  --name $KEYVAULT_NAME \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list
```

### Access Secrets in Python

```bash
# Add Azure Identity and Key Vault SDK
uv add azure-identity azure-keyvault-secrets
```

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Initialize Key Vault client
credential = DefaultAzureCredential()
vault_url = "https://myapp-kv.vault.azure.net"
client = SecretClient(vault_url=vault_url, credential=credential)

# Retrieve secrets
connection_string = client.get_secret("AzureMonitorConnectionString").value
db_password = client.get_secret("DatabasePassword").value

# Use in your app
from tools.logger import Logger, LogType

logger = Logger(
    __name__,
    log_type=LogType.AZURE_MONITOR,
    connection_string=connection_string
)
```

## Environment Variables (Development)

Use `.env.local` for local development secrets (never commit).

### Local Development

```bash
# .env.local (not in git)
IS_LOCAL=true
DEBUG=true
AZURE_MONITOR_CONNECTION_STRING=InstrumentationKey=xxx
DATABASE_URL=postgresql://user:password@localhost:5432/db
API_KEY=your-dev-api-key
```

### Access in Code

```python
from tools.config import Settings

# Extends Settings for custom variables
class AppSettings(Settings):
    database_url: str
    api_key: str

settings = AppSettings()  # Loads from .env and .env.local
```

## Docker Secrets

For Docker Swarm deployments.

### Create Docker Secret

```bash
# From file
docker secret create db_password ./db_password.txt

# From stdin
echo "my-secret-value" | docker secret create api_key -
```

### Use in Docker Compose

```yaml
version: '3.8'

services:
  api:
    image: myapp:latest
    secrets:
      - db_password
      - api_key
    environment:
      DATABASE_PASSWORD_FILE: /run/secrets/db_password
      API_KEY_FILE: /run/secrets/api_key

secrets:
  db_password:
    external: true
  api_key:
    external: true
```

### Read Secrets in Python

```python
def read_secret_file(path: str) -> str:
    """Read secret from Docker secret file."""
    with open(path) as f:
        return f.read().strip()

# Read from secret files
db_password = read_secret_file("/run/secrets/db_password")
api_key = read_secret_file("/run/secrets/api_key")
```

## Kubernetes Secrets

For AKS deployments.

### Create Kubernetes Secret

```bash
# From literal values
kubectl create secret generic app-secrets \
  --from-literal=AZURE_MONITOR_CONNECTION_STRING="InstrumentationKey=xxx" \
  --from-literal=DATABASE_PASSWORD="your-password"

# From files
kubectl create secret generic app-secrets \
  --from-file=./secrets/azure-connection-string.txt \
  --from-file=./secrets/db-password.txt
```

### Use in Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        env:
        - name: AZURE_MONITOR_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: AZURE_MONITOR_CONNECTION_STRING
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_PASSWORD
```

## Best Practices

### 1. Never Commit Secrets ✅

```gitignore
# .gitignore
.env.local
*.key
*.pem
secrets/
credentials.json
```

### 2. Rotate Secrets Regularly

```bash
# Rotate Azure Key Vault secret
az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name "DatabasePassword" \
  --value "new-secure-password"

# Update Kubernetes secret
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_PASSWORD="new-password" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 3. Use Managed Identities

Avoid connection strings when possible:

```python
# ✅ Better - Managed Identity
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()

# ❌ Avoid - Connection strings
connection_string = "AccountKey=xxx"
```

### 4. Principle of Least Privilege

Grant only necessary permissions:

```bash
# ✅ Good - Specific permissions
az keyvault set-policy \
  --name $KEYVAULT_NAME \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list

# ❌ Too broad
az keyvault set-policy \
  --name $KEYVAULT_NAME \
  --object-id $PRINCIPAL_ID \
  --secret-permissions all
```

### 5. Audit Secret Access

Enable Key Vault logging:

```bash
# Enable diagnostics
az monitor diagnostic-settings create \
  --name keyvault-logs \
  --resource $KEYVAULT_RESOURCE_ID \
  --logs '[{"category": "AuditEvent", "enabled": true}]' \
  --workspace $WORKSPACE_ID
```

### 6. Never Log Secrets

```python
# ❌ DON'T DO THIS
logger.info(f"API Key: {api_key}")
logger.debug(f"Password: {password}")

# ✅ Safe logging
logger.info("API authentication successful")
logger.info(f"Connected to database: {db_name}")
```

## CI/CD Secret Management

### Azure Pipelines

Store secrets as variables:

```yaml
# azure-pipelines.yml
variables:
  - group: production-secrets  # Variable group with secrets

steps:
- script: |
    az containerapp update \
      --name myapp \
      --resource-group $(RESOURCE_GROUP) \
      --set-env-vars \
        AZURE_MONITOR_CONNECTION_STRING="$(AZURE_MONITOR_CONNECTION_STRING)"
  env:
    AZURE_MONITOR_CONNECTION_STRING: $(AZURE_MONITOR_CONNECTION_STRING)
```

### GitHub Actions

Use GitHub Secrets:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Deploy
        run: |
          az containerapp update \
            --name myapp \
            --set-env-vars \
              AZURE_MONITOR_CONNECTION_STRING="${{ secrets.AZURE_MONITOR_CONNECTION_STRING }}"
```

## Security Checklist

- [ ] No secrets in code or Docker images
- [ ] `.env.local` in `.gitignore`
- [ ] Use Azure Key Vault for production secrets
- [ ] Enable managed identities
- [ ] Rotate secrets regularly
- [ ] Audit secret access
- [ ] Never log sensitive data
- [ ] Use least privilege access
- [ ] Encrypt secrets at rest
- [ ] Use secure secret transmission (TLS)

## Troubleshooting

### "Access Denied" to Key Vault

```bash
# Check access policies
az keyvault show --name $KEYVAULT_NAME --query properties.accessPolicies

# Verify managed identity has access
az keyvault set-policy \
  --name $KEYVAULT_NAME \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list
```

### Environment Variables Not Loading

```bash
# Check if variable is set
docker exec myapp env | grep AZURE_MONITOR

# Verify .env.local exists locally
ls -la .env.local
```

## Next Steps

- [Azure Deployment](azure.md) - Deploy with managed identities
- [Monitoring Setup](monitoring.md) - Monitor secret access
- [Environment Variables](../configurations/environment-variables.md) - Variable reference

## Resources

- [Azure Key Vault Documentation](https://docs.microsoft.com/azure/key-vault/)
- [Managed Identities](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/)
- [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
