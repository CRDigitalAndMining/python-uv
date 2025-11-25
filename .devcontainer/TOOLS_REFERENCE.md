# DevContainer Tools Reference

## Installed Tools

### Core Development Tools

#### **Docker CLI**

```bash
# List containers
docker ps

# View images
docker images

# Build image
docker build -t myapp .

# Run container
docker run -it myapp

# Container logs
docker logs <container-id>
```

#### **HTTP/API Testing Tools**

**HTTPie** (command-line)

```bash
# GET request
http GET https://api.example.com/endpoint

# POST with JSON
http POST https://api.example.com/endpoint key=value

# Custom headers
http GET https://api.example.com/endpoint Authorization:"Bearer token"
```

**jq** (JSON processor)

```bash
# Pretty print JSON
echo '{"name":"test"}' | jq

# Extract field
echo '{"user":{"name":"John"}}' | jq '.user.name'

# Filter arrays
echo '[{"id":1},{"id":2}]' | jq '.[].id'
```

### VS Code Extensions

#### **Azure Extensions**

- **Azure Resource Groups** - Manage Azure resources (includes authentication)
- **Azure Functions** - Develop and deploy functions

#### **Python Development**

- **Ruff** - Fast linting and formatting
- **Python** - Language support
- **Pylance** - Type checking and IntelliSense
- **Python Debugger (debugpy)** - Debugging support
- **autoDocstring** - Generate docstrings

#### **API Development & Testing**

- **REST Client** - Test HTTP requests in `.http` files
- **Thunder Client** - Lightweight REST API client (Postman alternative)

Example `.http` file:

```http
### Test Azure AI endpoint
POST https://{{endpoint}}/openai/deployments/{{deployment}}/chat/completions?api-version=2024-02-01
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Hello"}
  ]
}
```

#### **Container Development**

- **Docker** - Manage containers, images, and registries

#### **Code Quality**

- **Error Lens** - Inline error/warning display
- **Better Comments** - Highlight TODO, FIXME, etc.
- **Trailing Spaces** - Highlight and remove trailing spaces
- **Spell Checker** - Catch typos in code and comments

#### **Productivity**

- **GitLens** - Enhanced Git integration
- **Material Icon Theme** - Better file icons
- **Indent Rainbow** - Colorize indentation levels

## Common Workflows

### Debugging Agent Issues

```bash
# Check Azure authentication
az account show

# Test network connectivity
ping management.azure.com
curl -I https://management.azure.com

# View agent logs with jq
uv run python poc/01_basic_agent.py 2>&1 | jq

# Debug with Python debugger (in VS Code)
# Set breakpoint in code, press F5
```

### Container Management

```bash
# Check if Docker is available
docker --version

# List running containers
docker ps

# View container logs
docker logs <container-name>

# Execute command in container
docker exec -it <container-name> bash
```

### HTTP API Testing

Create `test-agent.http`:

```http
### Variables
@endpoint = your-endpoint
@deployment = gpt-4o-mini
@apikey = your-api-key

### Test chat completion
POST {{endpoint}}/openai/deployments/{{deployment}}/chat/completions?api-version=2024-02-01
api-key: {{apikey}}
Content-Type: application/json

{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "max_tokens": 100
}
```

Then use REST Client extension to send requests.

## Useful Commands

### System Information

```bash
# Check Python version
python --version

# Check uv version
uv --version

# Check Azure CLI version
az --version

# System resources
htop

# Network diagnostics
netstat -tulpn
dig example.com
```

### Git Productivity

```bash
# Git status with LFS
git lfs status

# View commit history (GitLens provides UI)
git log --oneline --graph

# Interactive staging
git add -p
```

### Package Management

```bash
# Install with extras
uv sync --extra devui --prerelease=allow

# Update dependencies
uv sync --upgrade

# Add new package
uv add <package>

# Check for outdated packages
uv pip list --outdated
```

## Environment Variables

Set in `.env.local`:

```bash
# Azure
AZURE_AI_PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com/
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_SUBSCRIPTION_ID=your-subscription-id

# Development
IS_LOCAL=true
DEBUG=true

# Optional: Disable Azure telemetry
AZURE_CORE_COLLECT_TELEMETRY=false
```

## Keyboard Shortcuts (VS Code)

- **F5** - Start debugging
- **Ctrl+Shift+P** - Command palette
- **Ctrl+`** - Toggle terminal
- **Ctrl+Shift+D** - Debug view
- **Ctrl+Shift+E** - Explorer view
- **Ctrl+Shift+G** - Source control view
- **Ctrl+Shift+X** - Extensions view

## Tips

1. **Use REST Client for API testing** instead of curl for better readability
2. **Enable GitLens blame annotations** to see who changed what
3. **Use Error Lens** to see errors inline (no need to hover)
4. **Use Thunder Client** for Postman-like experience in VS Code
5. **Docker extension** provides GUI for container management

## Troubleshooting

### Docker not accessible

```bash
# Check Docker service
sudo systemctl status docker

# Add user to docker group (requires logout/login)
sudo usermod -aG docker $USER
```

### Python environment issues

```bash
# Recreate venv
rm -rf .venv
uv sync --prerelease=allow
```

### Extension not working

```bash
# Reload VS Code
Ctrl+Shift+P → "Developer: Reload Window"

# Or restart entire container
Ctrl+Shift+P → "Dev Containers: Rebuild Container"
```
