# Environment Variables Reference

This document provides a comprehensive reference for all environment variables used in the project.

## Overview

The project uses **Pydantic Settings** for environment variable management. Variables are loaded from:

1. `.env` - Base configuration (committed to version control)
2. `.env.local` - Local overrides (not committed, in `.gitignore`)

Variables from `.env.local` override those in `.env`.

## Quick Start

Create a `.env.local` file for local development:

```bash
# Copy the template
cp .env .env.local

# Edit with your local values
IS_LOCAL=true
DEBUG=true
```

## Variable Reference

### Environment

| Variable   | Type   | Default | Description                                                                                                                                                      |
| ---------- | ------ | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `IS_LOCAL` | `bool` | `false` | Enable local development mode. When `true`, uses colored console logging and development settings. When `false`, uses Azure Monitor JSON logging for production. |
| `DEBUG`    | `bool` | `false` | Enable debug mode with verbose logging and detailed error messages. Should be `false` in production.                                                             |

### FastAPI Application

| Variable         | Type          | Default           | Description                                                                                                                                     |
| ---------------- | ------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `TITLE`          | `str`         | `"FastAPI"`       | Application title displayed in OpenAPI documentation and API responses.                                                                         |
| `SUMMARY`        | `str \| None` | `None`            | Short summary for OpenAPI docs (optional).                                                                                                      |
| `DESCRIPTION`    | `str`         | `""`              | Detailed description for OpenAPI documentation. Supports Markdown.                                                                              |
| `VERSION`        | `str`         | `"0.1.0"`         | Application version string (SemVer format recommended).                                                                                         |
| `OPENAPI_URL`    | `str`         | `"/openapi.json"` | URL path for OpenAPI schema JSON. Set to empty string to disable.                                                                               |
| `DOCS_URL`       | `str`         | `"/docs"`         | URL path for Swagger UI documentation. Set to `None` to disable.                                                                                |
| `REDOC_URL`      | `str`         | `"/redoc"`        | URL path for ReDoc documentation. Set to `None` to disable.                                                                                     |
| `OPENAPI_PREFIX` | `str`         | `""`              | Prefix for OpenAPI URLs. Useful when behind a proxy.                                                                                            |
| `API_PREFIX_V1`  | `str`         | `"/api/v1"`       | URL prefix for API version 1 endpoints (e.g., `/api/v1/users`).                                                                                 |
| `ALLOWED_HOSTS`  | `list[str]`   | `["*"]`           | List of allowed hosts for CORS. Use JSON array format: `["localhost", "example.com"]`. In production, specify exact domains instead of `["*"]`. |

### Azure Monitor (Production Logging)

| Variable                          | Type  | Default | Description                                                                                                                                                                           |
| --------------------------------- | ----- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AZURE_MONITOR_CONNECTION_STRING` | `str` | -       | Azure Application Insights connection string. Required when `IS_LOCAL=false`. Format: `InstrumentationKey=<key>;IngestionEndpoint=https://<region>.in.applicationinsights.azure.com/` |

## Usage Examples

### Development Environment

Create `.env.local` for local development:

```bash
# .env.local
IS_LOCAL=true
DEBUG=true
TITLE=My API - Development
VERSION=0.1.0-dev
```

### Production Environment

Set environment variables in your deployment platform (Azure App Service, Kubernetes, etc.):

```bash
# Production settings
IS_LOCAL=false
DEBUG=false
TITLE=My API
VERSION=1.0.0
API_PREFIX_V1=/api/v1
ALLOWED_HOSTS=["myapp.com", "www.myapp.com"]
AZURE_MONITOR_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=https://xxx.in.applicationinsights.azure.com/
```

### Docker Environment

Use environment variables in `docker-compose.yml`:

```yaml
services:
  api:
    image: my-api:latest
    environment:
      - IS_LOCAL=false
      - DEBUG=false
      - TITLE=My API
      - AZURE_MONITOR_CONNECTION_STRING=${AZURE_MONITOR_CONNECTION_STRING}
```

Or use an `.env` file with Docker Compose:

```bash
docker-compose --env-file .env.production up
```

## Accessing Variables in Code

### Basic Usage

```python
from tools.config import Settings

settings = Settings()

# Access variables
is_local = settings.IS_LOCAL
debug_mode = settings.debug
api_title = settings.title
```

### With Logger

```python
from tools.config import Settings
from tools.logger import Logger, LogType

settings = Settings()
logger = Logger(
    __name__,
    log_type=LogType.LOCAL if settings.IS_LOCAL else LogType.AZURE_MONITOR,
    connection_string=settings.azure_monitor_connection_string if not settings.IS_LOCAL else None,
)
```

### With FastAPI

```python
from fastapi import FastAPI
from tools.config import Settings

settings = Settings()

# Use fastapi_kwargs for automatic configuration
app = FastAPI(**settings.fastapi_kwargs)

@app.get("/")
async def root():
    return {
        "title": settings.title,
        "version": settings.version,
        "environment": "local" if settings.IS_LOCAL else "production"
    }
```

## Adding Custom Variables

To add new environment variables:

### 1. Update `tools/config/settings.py`

```python
class Settings(BaseSettings):
    # Existing fields...

    # Add your custom fields
    DATABASE_URL: str = "sqlite:///./app.db"
    REDIS_URL: str = "redis://localhost:6379"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB in bytes
```

### 2. Add to `.env` Template

```bash
# Custom Settings
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
REDIS_URL=redis://localhost:6379
MAX_UPLOAD_SIZE=10485760
```

### 3. Document in This File

Add your new variables to the reference table above.

### 4. Update `.env.local` for Local Development

```bash
# .env.local
DATABASE_URL=sqlite:///./dev.db
REDIS_URL=redis://localhost:6379
```

## Type Conversion

Pydantic automatically converts environment variables to the specified types:

| Python Type | Environment Format                     | Example                                      |
| ----------- | -------------------------------------- | -------------------------------------------- |
| `bool`      | `true`, `false`, `1`, `0`, `yes`, `no` | `DEBUG=true`                                 |
| `int`       | Numeric string                         | `MAX_CONNECTIONS=100`                        |
| `float`     | Numeric string with decimal            | `TIMEOUT=30.5`                               |
| `str`       | Any string                             | `TITLE=My API`                               |
| `list[str]` | JSON array                             | `ALLOWED_HOSTS=["localhost", "example.com"]` |

## Validation

Pydantic validates types automatically. Invalid values raise `ValidationError`:

```python
# This will raise ValidationError
# DEBUG=invalid_value

from tools.config import Settings

try:
    settings = Settings()
except ValidationError as e:
    print(e)
```

## Best Practices

### 1. Never Commit Secrets

- ✅ Commit `.env` with safe defaults
- ❌ Never commit `.env.local` (contains secrets)
- ✅ Use `.gitignore` to exclude `.env.local`

### 2. Use Descriptive Names

```bash
# Good
DATABASE_CONNECTION_TIMEOUT=30
AZURE_STORAGE_ACCOUNT_NAME=myaccount

# Less clear
DB_TIMEOUT=30
STORAGE=myaccount
```

### 3. Provide Defaults

Always provide sensible defaults in `Settings` class for optional variables.

### 4. Document Everything

Add all new variables to this reference document and to the `.env` template.

### 5. Use Type Hints

Specify correct types in `Settings` class for automatic validation:

```python
class Settings(BaseSettings):
    PORT: int = 8000  # ✅ Will validate as integer
    HOST: str = "0.0.0.0"  # ✅ Will validate as string
    ENABLE_FEATURE: bool = False  # ✅ Will validate as boolean
```

### 6. Environment-Specific Files

Consider using different `.env` files for different environments:

```bash
.env              # Base defaults (committed)
.env.local        # Local development (not committed)
.env.test         # Test environment
.env.staging      # Staging environment
.env.production   # Production environment (not committed)
```

## Troubleshooting

### Variable Not Loading

1. Check file naming: `.env` and `.env.local` (not `env.txt` or `.env.txt`)
2. Verify file is in project root directory
3. Check for typos in variable names
4. Ensure no spaces around `=`: use `DEBUG=true` not `DEBUG = true`

### Type Validation Error

```python
# Error: value is not a valid boolean
DEBUG=yes  # ❌ Use 'true' or 'false'
DEBUG=true  # ✅ Correct
```

### List Format Error

```bash
# Error: value is not a valid list
ALLOWED_HOSTS=localhost,example.com  # ❌ Not JSON

# Correct - use JSON array format
ALLOWED_HOSTS=["localhost", "example.com"]  # ✅
```

### Connection String Issues

```bash
# Azure Monitor connection string must include both parts
AZURE_MONITOR_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=https://xxx.in.applicationinsights.azure.com/
```

## Related Documentation

- [Settings Configuration](../guides/tools/config.md) - Detailed guide on Settings usage
- [Logger Configuration](../guides/tools/logger.md) - Using environment for logger configuration
- [FastAPI Use Case](../usecases/fastapi.md) - Environment variables in FastAPI applications

## Security Considerations

1. **Never log secrets**: Don't use `logger.info(f"API Key: {api_key}")`
2. **Use Azure Key Vault**: For production secrets management
3. **Rotate credentials**: Regular rotation of connection strings and keys
4. **Principle of least privilege**: Only grant necessary permissions
5. **Audit access**: Monitor who accesses production environment variables

For more on security, see [Security Best Practices](../deployment/secrets.md).
