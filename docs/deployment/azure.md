# Azure Deployment Guide

Deploy your Python application to Azure cloud platform using modern container services.

## Deployment Options

Azure offers multiple deployment options. Choose based on your needs:

| Service | Use Case | Complexity | Scaling |
|---------|----------|------------|---------|
| **Azure Container Apps** | Microservices, APIs, event-driven apps | Low | Automatic |
| **Azure App Service** | Web apps, APIs with managed platform | Low | Manual/Auto |
| **Azure Kubernetes Service (AKS)** | Complex microservices, full Kubernetes | High | Manual/Auto |
| **Azure Container Instances** | Simple containers, batch jobs | Very Low | Manual |

**Recommended**: **Azure Container Apps** for most use cases - serverless, automatic scaling, and low operational overhead.

## Prerequisites

- Azure subscription ([Create free account](https://azure.microsoft.com/free/))
- Azure CLI installed ([Install guide](https://docs.microsoft.com/cli/azure/install-azure-cli))
- Docker Desktop installed
- Azure Container Registry (ACR) or Docker Hub account

### Install Azure CLI

```bash
# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Windows
# Download from https://aka.ms/installazurecliwindows
```

### Login to Azure

```bash
az login
az account set --subscription "Your Subscription Name"
```

## Option 1: Azure Container Apps (Recommended)

Azure Container Apps is a serverless container platform ideal for microservices and APIs.

### Benefits
- ✅ Automatic scaling (including scale to zero)
- ✅ Built-in load balancing
- ✅ HTTPS by default
- ✅ Managed certificates
- ✅ Integrated with Application Insights
- ✅ Pay only for what you use

### Step 1: Create Azure Container Registry

```bash
# Set variables
RESOURCE_GROUP=myapp-rg
LOCATION=eastus
ACR_NAME=myappregistry  # Must be globally unique
APP_NAME=myapp

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Create container registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true
```

### Step 2: Build and Push Docker Image

```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build image in ACR (recommended)
az acr build \
  --registry $ACR_NAME \
  --image $APP_NAME:latest \
  --file Dockerfile \
  .

# Or build locally and push
docker build -t $ACR_NAME.azurecr.io/$APP_NAME:latest .
docker push $ACR_NAME.azurecr.io/$APP_NAME:latest
```

### Step 3: Create Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app $APP_NAME-insights \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --application-type web

# Get connection string
CONNECTION_STRING=$(az monitor app-insights component show \
  --app $APP_NAME-insights \
  --resource-group $RESOURCE_GROUP \
  --query connectionString \
  --output tsv)

echo "Connection String: $CONNECTION_STRING"
```

### Step 4: Deploy to Container Apps

```bash
# Create Container Apps environment
az containerapp env create \
  --name $APP_NAME-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Create container app
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $APP_NAME-env \
  --image $ACR_NAME.azurecr.io/$APP_NAME:latest \
  --registry-server $ACR_NAME.azurecr.io \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    IS_LOCAL=false \
    DEBUG=false \
    AZURE_MONITOR_CONNECTION_STRING="$CONNECTION_STRING" \
    TITLE="My Production API" \
    VERSION="1.0.0" \
  --cpu 0.5 \
  --memory 1Gi \
  --min-replicas 1 \
  --max-replicas 10
```

### Step 5: Configure Managed Identity (Recommended)

```bash
# Enable system-assigned managed identity
az containerapp identity assign \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --system-assigned

# Get the managed identity principal ID
PRINCIPAL_ID=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query identity.principalId \
  --output tsv)

echo "Managed Identity Principal ID: $PRINCIPAL_ID"
```

### Step 6: Verify Deployment

```bash
# Get application URL
APP_URL=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Application URL: https://$APP_URL"

# Test the endpoint
curl https://$APP_URL/api/v1/

# View logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow
```

## Option 2: Azure App Service

Azure App Service provides a fully managed platform for web applications.

### Deploy to App Service

```bash
# Create App Service plan
az appservice plan create \
  --name $APP_NAME-plan \
  --resource-group $RESOURCE_GROUP \
  --is-linux \
  --sku B1

# Create web app
az webapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_NAME-plan \
  --deployment-container-image-name $ACR_NAME.azurecr.io/$APP_NAME:latest

# Configure app settings
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    IS_LOCAL=false \
    DEBUG=false \
    AZURE_MONITOR_CONNECTION_STRING="$CONNECTION_STRING"

# Enable logging
az webapp log config \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --docker-container-logging filesystem

# Get app URL
echo "App URL: https://$APP_NAME.azurewebsites.net"
```

## Option 3: Azure Kubernetes Service (AKS)

For complex applications requiring full Kubernetes features.

### Deploy to AKS

```bash
# Create AKS cluster
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME-aks \
  --node-count 3 \
  --enable-managed-identity \
  --attach-acr $ACR_NAME \
  --generate-ssh-keys

# Get credentials
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME-aks

# Create Kubernetes secret for connection string
kubectl create secret generic app-secrets \
  --from-literal=AZURE_MONITOR_CONNECTION_STRING="$CONNECTION_STRING"

# Apply Kubernetes manifests
kubectl apply -f k8s/
```

**Sample Kubernetes Deployment (`k8s/deployment.yaml`)**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myappregistry.azurecr.io/myapp:latest
        ports:
        - containerPort: 8000
        env:
        - name: IS_LOCAL
          value: "false"
        - name: DEBUG
          value: "false"
        - name: AZURE_MONITOR_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: AZURE_MONITOR_CONNECTION_STRING
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## CI/CD with Azure Pipelines

Automate deployment with Azure Pipelines.

**Sample Pipeline (`azure-pipelines-deploy.yml`)**:

```yaml
trigger:
  branches:
    include:
    - main

variables:
  azureSubscription: 'Your-Service-Connection'
  resourceGroup: 'myapp-rg'
  containerRegistry: 'myappregistry.azurecr.io'
  imageName: 'myapp'
  containerAppName: 'myapp'

stages:
- stage: Build
  jobs:
  - job: BuildAndPush
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: Docker@2
      displayName: Build and Push
      inputs:
        containerRegistry: $(containerRegistry)
        repository: $(imageName)
        command: buildAndPush
        Dockerfile: Dockerfile
        tags: |
          $(Build.BuildId)
          latest

- stage: Deploy
  dependsOn: Build
  jobs:
  - deployment: DeployToProduction
    environment: 'production'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureCLI@2
            displayName: Deploy to Container Apps
            inputs:
              azureSubscription: $(azureSubscription)
              scriptType: bash
              scriptLocation: inlineScript
              inlineScript: |
                az containerapp update \
                  --name $(containerAppName) \
                  --resource-group $(resourceGroup) \
                  --image $(containerRegistry)/$(imageName):$(Build.BuildId)
```

## Update Deployment

### Update Container Apps

```bash
# Update with new image
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image $ACR_NAME.azurecr.io/$APP_NAME:v2

# Update environment variables
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars VERSION="2.0.0"

# Scale replicas
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 2 \
  --max-replicas 20
```

## Monitoring and Logs

### View Application Logs

```bash
# Container Apps logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow

# App Service logs
az webapp log tail \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
```

### View Metrics in Portal

1. Navigate to Azure Portal
2. Find your Container App / App Service
3. Go to "Monitoring" → "Metrics"
4. View Application Insights data

## Cleanup Resources

```bash
# Delete resource group (removes all resources)
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## Best Practices

1. **Use Managed Identity** instead of connection strings where possible
2. **Enable auto-scaling** to handle traffic spikes
3. **Use staging slots** for zero-downtime deployments
4. **Monitor costs** with Azure Cost Management
5. **Implement health checks** for reliability
6. **Use Azure Key Vault** for secrets
7. **Enable HTTPS only** for security
8. **Tag resources** for organization and cost tracking

## Troubleshooting

### Image Pull Errors

```bash
# Grant Container App access to ACR
az containerapp registry set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --server $ACR_NAME.azurecr.io \
  --username $(az acr credential show --name $ACR_NAME --query username -o tsv) \
  --password $(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)
```

### Application Not Starting

Check logs and ensure:
- All environment variables are set
- Application Insights connection string is valid
- Container port matches ingress target port (8000)
- Application starts successfully locally with same config

## Next Steps

- [Docker Production Guide](docker.md) - Optimize your container images
- [Secrets Management](secrets.md) - Use Azure Key Vault
- [Monitoring Setup](monitoring.md) - Configure Application Insights
- [Environment Variables](../configurations/environment-variables.md) - Complete reference

## Resources

- [Azure Container Apps Documentation](https://docs.microsoft.com/azure/container-apps/)
- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Azure Kubernetes Service Documentation](https://docs.microsoft.com/azure/aks/)
- [Azure Container Registry Documentation](https://docs.microsoft.com/azure/container-registry/)
