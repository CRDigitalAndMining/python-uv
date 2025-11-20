#!/bin/bash
# Script to create the minimal POC branch from main

echo "Creating minimal branch for POCs..."

# Create and checkout new branch
git checkout -b minimal

echo "Replacing files with minimal versions..."

# Replace configuration files
mv README.minimal.md README.md
mv pyproject.minimal.toml pyproject.toml
mv ruff.minimal.toml ruff.toml
mv pytest.minimal.ini pytest.ini
mv pyrightconfig.minimal.json pyrightconfig.json

echo "Removing heavy documentation and CI/CD..."

# Remove documentation
rm -rf docs/
rm -f mkdocs.yml

# Remove CI/CD pipelines
rm -rf azure-pipelines/

# Remove pre-commit and coverage config
rm -f .pre-commit-config.yaml
rm -f .coveragerc

# Remove nox automation (too heavy for POCs)
rm -f noxfile.py

# Remove Dockerfile and devcontainer (optional - keep if using Docker)
# Uncomment these lines if you want a truly minimal setup:
# rm -f Dockerfile
# rm -rf .devcontainer/

echo "Simplifying tests..."

# Keep only the minimal smoke test
rm -f tests/tools/test__logger.py
rm -f tests/tools/test__config.py
rm -f tests/tools/test__tracer.py

# Remove conftest if it exists and has no critical fixtures
# Uncomment if you don't need any shared fixtures:
# rm -f tests/conftest.py

echo "Updating dependencies..."

# Sync with minimal dependencies
uv sync

echo "Running tests to verify setup..."
uv run pytest

echo ""
echo "✅ Minimal branch created successfully!"
echo ""
echo "Branch: minimal"
echo "Removed:"
echo "  - docs/ (full documentation)"
echo "  - azure-pipelines/ (CI/CD configs)"
echo "  - mkdocs.yml (documentation builder)"
echo "  - .pre-commit-config.yaml (git hooks)"
echo "  - .coveragerc (coverage config)"
echo "  - noxfile.py (task automation)"
echo ""
echo "Kept:"
echo "  - tools/ (Logger, Config, Timer)"
echo "  - tests/ (minimal smoke tests)"
echo "  - .env template"
echo "  - Basic linting (Ruff, Pyright)"
echo ""
echo "Next steps:"
echo "  1. Review changes: git status"
echo "  2. Commit: git add . && git commit -m 'Create minimal POC branch'"
echo "  3. Push: git push -u origin minimal"
