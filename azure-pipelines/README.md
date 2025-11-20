# Azure DevOps Pipelines

This directory contains Azure DevOps Pipeline configurations equivalent to the GitHub Actions workflows.

## Available Pipelines

| Pipeline File | Purpose | GitHub Actions Equivalent |
|---------------|---------|---------------------------|
| `docker-validation.yml` | Validate Dockerfile with hadolint and build | `docker.yml` |
| `devcontainer-validation.yml` | Validate DevContainer setup | `devcontainer.yml` |
| `format-check.yml` | Check code formatting with Ruff | `format.yml` |
| `lint.yml` | Run Pyright and Ruff linting | `lint.yml` |
| `test.yml` | Run pytest with coverage reporting | `test.yml` |
| `docs-deploy.yml` | Build and deploy MkDocs documentation | `gh-deploy.yml` |

## Setup Instructions

### 1. Import Pipelines to Azure DevOps

For each pipeline file:

1. Go to your Azure DevOps project
2. Navigate to **Pipelines** → **New Pipeline**
3. Select **Azure Repos Git** (or your source)
4. Choose **Existing Azure Pipelines YAML file**
5. Select the pipeline file from this directory
6. Save and run

### 2. Create Service Connections (if needed)

Some pipelines may require service connections:

- **Docker Registry** - For pushing images
- **Azure Subscription** - For deploying documentation
- **API Tokens** - For external services

### 3. Configure Variables

Set pipeline variables as needed:

```yaml
# In Azure DevOps UI: Pipelines → Edit → Variables
AZURE_STATIC_WEB_APPS_API_TOKEN: <your-token>
```

## Key Differences from GitHub Actions

### Trigger Syntax
```yaml
# GitHub Actions
on:
  push:
    branches: [main]

# Azure DevOps
trigger:
  branches:
    include:
      - main
```

### Runner/Agent
```yaml
# GitHub Actions
runs-on: ubuntu-latest

# Azure DevOps
pool:
  vmImage: 'ubuntu-latest'
```

### Steps
```yaml
# GitHub Actions
- uses: actions/checkout@v5

# Azure DevOps
- checkout: self
```

### Path Filters
Both support path filtering, but syntax differs:
```yaml
# GitHub Actions
paths:
  - "**.py"

# Azure DevOps
paths:
  include:
    - '**.py'
```

## uv Installation

All pipelines install `uv` using the official installation script:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
echo "##vso[task.prependpath]$HOME/.cargo/bin"
```

This is equivalent to the custom GitHub Action `.github/actions/setup-python-with-uv`.

## Running Locally

You can test nox commands locally before running in pipelines:

```bash
# Format check
uv run nox -s fmt

# Linting
uv run nox -s lint -- --pyright --ruff

# Tests
uv run nox -s test
```

## Notes

- **PR labeler**: Not included - use Azure DevOps work item auto-linking instead
- **PR Agent**: Not included - Azure DevOps has built-in PR review features
- **Coverage badges**: Configure using Azure DevOps dashboard widgets
- **Documentation deployment**: Requires configuration based on your hosting solution (see `docs-deploy.yml` comments)

## Migration Checklist

- [ ] Import all required pipelines to Azure DevOps
- [ ] Configure service connections
- [ ] Set up pipeline variables
- [ ] Test each pipeline with a PR
- [ ] Configure branch policies to require pipeline success
- [ ] Update README badges to point to Azure DevOps
- [ ] Remove `.github/workflows` directory (if no longer needed)
