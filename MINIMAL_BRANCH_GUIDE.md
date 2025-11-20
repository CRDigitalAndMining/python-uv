# Minimal Branch Creation Guide

## Manual Steps (If Script Fails)

If the automated script doesn't work, follow these manual steps:

### 1. Create Branch
```bash
git checkout -b minimal
```

### 2. Replace Files

```bash
# Replace with minimal versions
mv README.minimal.md README.md
mv pyproject.minimal.toml pyproject.toml
mv ruff.minimal.toml ruff.toml
mv pytest.minimal.ini pytest.ini
mv pyrightconfig.minimal.json pyrightconfig.json
```

### 3. Remove Heavy Files

```bash
# Remove documentation
rm -rf docs/
rm -f mkdocs.yml

# Remove CI/CD
rm -rf azure-pipelines/

# Remove pre-commit and coverage
rm -f .pre-commit-config.yaml
rm -f .coveragerc

# Remove nox automation
rm -f noxfile.py

# Optional: Remove Docker files (if not using containers for POCs)
# rm -f Dockerfile
# rm -rf .devcontainer/
```

### 4. Simplify Tests

```bash
# Remove detailed tests (keep only smoke tests)
rm -f tests/tools/test__logger.py
rm -f tests/tools/test__config.py
rm -f tests/tools/test__tracer.py

# Note: tests/test__minimal.py is the new smoke test
```

### 5. Update Dependencies

```bash
# Sync with minimal dependencies
uv sync

# Verify everything works
uv run pytest
uv run ruff check .
uv run pyright
```

### 6. Commit Changes

```bash
git add .
git commit -m "Create minimal POC branch

- Simplified README for quick start
- Reduced dependencies (removed mkdocs, pre-commit, nox, pytest-cov)
- Minimal configuration (simplified Ruff rules)
- Basic smoke tests only
- Removed documentation and CI/CD files"

git push -u origin minimal
```

## What's Removed vs Kept

### ❌ Removed (Heavy for POCs)
- `docs/` - Full documentation site
- `azure-pipelines/` - CI/CD pipeline configs
- `mkdocs.yml` - Documentation builder config
- `.pre-commit-config.yaml` - Git hooks
- `.coveragerc` - Coverage configuration
- `noxfile.py` - Task automation
- Detailed test files - `test__logger.py`, `test__config.py`, `test__tracer.py`

### ✅ Kept (Essential for POCs)
- `tools/` - Core utilities (Logger, Config, Timer)
- `tests/test__minimal.py` - Basic smoke tests
- `.env` - Environment template
- `pyproject.toml` - Minimal dependencies
- `ruff.toml` - Essential linting rules
- `pytest.ini` - Basic test configuration
- `pyrightconfig.json` - Type checking config

## File Comparison

### README.md
**Before**: 200+ lines with extensive docs, badges, deployment guides
**After**: ~100 lines focused on 5-minute quick start

### pyproject.toml
**Before**: 
- Dev dependencies: mkdocs, nox, pre-commit, pytest-cov, jupyter
- Full classifiers and metadata

**After**:
- Dev dependencies: Only pytest, ruff, pyright
- Minimal metadata

### ruff.toml
**Before**: ALL rules enabled (500+ rules) with specific exclusions
**After**: Only essential rules (E, F, I, UP)

### pytest.ini
**Before**: Coverage requirements (75% min), HTML reports, branch coverage
**After**: Basic test discovery, simple output

## Size Reduction

Approximate file count reduction:
- **Before**: ~60 files
- **After**: ~25 files (58% reduction)

Dependencies reduction:
- **Before**: 10 dev dependencies
- **After**: 3 dev dependencies (70% reduction)

## Quick Verification

After creating the branch, verify everything works:

```bash
# Should pass all smoke tests
uv run pytest
# Output: 4 tests passed

# Should have minimal linting output
uv run ruff check .
# Output: No errors

# Should type check successfully
uv run pyright
# Output: 0 errors
```
