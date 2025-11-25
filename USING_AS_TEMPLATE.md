# Using This Repository as a Template

This repository serves as a boilerplate for starting new Python projects with best practices built-in.

## Quick Start

### For Azure DevOps (Recommended)

Azure DevOps doesn't have a native "template repository" feature like GitHub, so we use the import/clone approach:

#### Method 1: Azure DevOps Import (Cleanest)

1. **Create new repo in Azure DevOps**
   - Go to your Azure DevOps project
   - Repos → New repository
   - Name: `your-new-project`
   - Initialize: Uncheck "Add a README"
   - Click "Create"

2. **Import from this template**
   ```bash
   # In Azure DevOps, go to your new empty repo
   # Click "Import" button
   # Or use the "Import a Git repository" option
   # Source URL: https://dev.azure.com/YourOrg/YourProject/_git/python-uv
   ```

3. **Clone and customize**
   ```bash
   git clone https://dev.azure.com/YourOrg/YourProject/_git/your-new-project
   cd your-new-project
   
   # Choose your starting branch
   git checkout main      # For production projects
   # OR
   git checkout minimal   # For POCs/prototypes
   
   # Update project metadata
   # Edit pyproject.toml:
   #   - name = "your-new-project"
   #   - description = "Your project description"
   #   - authors = [{ name = "Your Name", email = "you@company.com" }]
   
   # Edit README.md with project-specific information
   
   # Commit customizations
   git add pyproject.toml README.md
   git commit -m "chore: Customize project metadata"
   git push
   ```

#### Method 2: Clone and Push (Manual)

If import doesn't work or you want more control:

```bash
# 1. Clone the template
git clone https://dev.azure.com/YourOrg/YourProject/_git/python-uv your-new-project
cd your-new-project

# 2. Update remote to point to your new repo
git remote set-url origin https://dev.azure.com/YourOrg/YourProject/_git/your-new-project

# 3. Choose your branch
git checkout minimal  # or stay on main

# 4. Customize project files
# Edit pyproject.toml, README.md, .env

# 5. Push to your new repo
git push -u origin main
git push origin minimal  # if you want both branches
```

#### Method 3: Fresh Start (No History)

For a completely clean slate:

```bash
# 1. Clone template without history
git clone --depth=1 https://dev.azure.com/YourOrg/YourProject/_git/python-uv your-new-project
cd your-new-project

# 2. Choose your starting point
git checkout minimal  # or main

# 3. Remove git history and start fresh
rm -rf .git
git init
git add .
git commit -m "Initial commit from python-uv template"

# 4. Add your Azure DevOps remote
git remote add origin https://dev.azure.com/YourOrg/YourProject/_git/your-new-project

# 5. Push
git branch -M main
git push -u origin main

# Optional: Add minimal branch if needed
git checkout -b minimal origin/minimal  # from original
# ... or create from scratch
```

## Choosing Your Branch

### Use `main` branch when:
- ✅ Building production applications
- ✅ Need comprehensive documentation
- ✅ Want CI/CD pipelines included
- ✅ Working with a team
- ✅ Enterprise deployment
- ✅ Need full test coverage

### Use `minimal` branch when:
- ✅ Quick POC or prototype
- ✅ Personal experiment
- ✅ Learning project
- ✅ Speed over documentation
- ✅ Solo developer
- ✅ Throwaway code

## Post-Clone Customization Checklist

### Required Changes

- [ ] **pyproject.toml**
  ```toml
  name = "your-new-project"  # Change from "python-uv-template"
  description = "Your project description"
  authors = [{ name = "Your Name", email = "you@company.com" }]
  ```

- [ ] **README.md**
  - Update project title
  - Replace generic description with your project's purpose
  - Update installation instructions if needed
  - Add project-specific documentation

- [ ] **.env.local** (create from .env)
  ```bash
  cp .env .env.local
  # Edit .env.local with your values
  ```

### Optional Changes

- [ ] **LICENSE** - Update copyright holder if needed
- [ ] **.github/copilot-instructions.md** - Customize for your project (if using GitHub Copilot)
- [ ] **tools/config/settings.py** - Add project-specific settings
- [ ] Remove unused optional dependencies from pyproject.toml

### For Azure DevOps Specific Setup

- [ ] **azure-pipelines/** (main branch only)
  - Review and customize pipeline YAML files
  - Update service connections
  - Configure variable groups
  
- [ ] **Enable branch policies**
  - Go to Repos → Branches
  - Select main branch → Branch policies
  - Set up pull request requirements
  
- [ ] **Configure build pipelines**
  - Pipelines → New pipeline
  - Select Azure Repos Git
  - Choose existing Azure Pipelines YAML
  - Select azure-pipelines/test.yml (or others)

## Verification After Setup

Run these commands to verify everything works:

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Check linting
uv run ruff check .

# Check types
uv run pyright

# For main branch only:
uv run nox -s test
uv run nox -s lint
```

All checks should pass ✅

## Keeping Multiple Projects in Sync

If you want to pull template updates into your project later:

```bash
# Add template as upstream remote
git remote add template https://dev.azure.com/YourOrg/YourProject/_git/python-uv

# Fetch template updates
git fetch template

# View changes
git log HEAD..template/main --oneline

# Merge specific updates (carefully!)
git cherry-pick <commit-hash>

# Or merge all changes (risky - may conflict with your customizations)
git merge template/main
```

**Note:** Pulling updates is optional and often not needed. The template is meant as a starting point, not a framework.

## Common Pitfalls

### ❌ Don't forget to update project metadata
```bash
# BAD - leaving default names
name = "python-uv-template"

# GOOD - using your project name
name = "my-awesome-project"
```

### ❌ Don't commit sensitive data to .env
```bash
# BAD - .env is tracked by git
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=secret123...

# GOOD - use .env.local (gitignored)
cp .env .env.local
# Edit .env.local with real secrets
```

### ❌ Don't use wrong branch for your use case
```bash
# BAD - using main for quick POC (too much overhead)
git checkout main

# GOOD - using minimal for POC
git checkout minimal
```

### ✅ Do customize for your needs
```bash
# Remove unused optional dependencies
# Remove tools you don't need
# Simplify configs for your use case
```

## Azure DevOps + Dev Container

If using the dev container in Azure DevOps:

1. **Enable Docker in Azure Pipelines**
   - Use Microsoft-hosted agents with Docker
   - Or set up self-hosted agents with Docker

2. **VS Code Dev Containers**
   - Install "Remote - Containers" extension
   - Open folder in container works with Azure DevOps repos
   - All settings are already configured

3. **Codespaces Alternative**
   - Azure DevOps doesn't have Codespaces
   - Use local dev containers instead
   - Or GitHub Codespaces if mirroring to GitHub

## Example: Creating a FastAPI Project

```bash
# 1. Import template to new Azure DevOps repo
# 2. Clone
git clone https://dev.azure.com/YourOrg/YourProject/_git/my-fastapi-app
cd my-fastapi-app

# 3. Choose main branch (production-ready)
git checkout main

# 4. Customize
cat >> pyproject.toml << 'EOF'
[project]
name = "my-fastapi-app"
description = "A production-ready FastAPI application"
EOF

# 5. Install with FastAPI extras
uv sync --extra fastapi

# 6. Create your first endpoint
cat > main.py << 'EOF'
from fastapi import FastAPI
from tools.logger import Logger, LogType
from tools.config import Settings

settings = Settings()
logger = Logger(__name__, log_type=LogType.LOCAL)
app = FastAPI(**settings.fastapi_kwargs)

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"status": "healthy"}
EOF

# 7. Run
uv run uvicorn main:app --reload

# 8. Commit
git add .
git commit -m "feat: Initial FastAPI setup"
git push
```

## Summary

**Best Practice for Azure DevOps:**

1. ✅ Use "Import repository" in Azure DevOps
2. ✅ Choose `main` or `minimal` based on project scope
3. ✅ Customize `pyproject.toml` and `README.md`
4. ✅ Create `.env.local` for secrets
5. ✅ Run verification tests
6. ✅ Push and start building!

**The template gives you:**
- Production-ready utilities (Logger, Config, Timer)
- Modern Python tooling (uv, Ruff, Pyright)
- Dev container setup
- Optional CI/CD pipelines
- Best practices built-in

**You customize:**
- Project name and metadata
- Business logic
- Additional dependencies
- Project-specific settings
