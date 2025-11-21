# Branch Maintenance Guide

This repository uses a dual-branch strategy to serve different use cases.

## Branch Strategy

### `main` - Production-Ready Template
Full-featured template with comprehensive tooling for production deployments:
- ✅ Complete documentation (MkDocs site)
- ✅ CI/CD pipelines (Azure Pipelines)
- ✅ Pre-commit hooks
- ✅ Full test coverage (75% minimum)
- ✅ Task automation (nox)
- ✅ Deployment guides

**Use for:** Production projects, team collaboration, enterprise deployments

### `minimal` - POC/Prototype Template
Lightweight version optimized for rapid prototyping:
- ✅ Core utilities only (Logger, Config, Timer)
- ✅ Essential tooling (Ruff, Pyright, pytest)
- ✅ Minimal smoke tests
- ✅ Quick setup (5 minutes)
- ❌ No extensive documentation
- ❌ No CI/CD
- ❌ No pre-commit hooks

**Use for:** Quick POCs, experiments, learning, rapid iteration

## Keeping Branches in Sync

### Core Principle
**Changes flow from `main` → `minimal`**, never the reverse.

- `main` is the source of truth
- `minimal` cherry-picks selected changes from `main`
- POC-specific changes stay in `minimal` only

### When to Sync Changes

#### Always Cherry-Pick to `minimal`:
1. **Bug fixes** in `tools/` package
   ```bash
   # Fix in main
   git checkout main
   # ... make fixes to tools/logger/logger.py ...
   git add tools/
   git commit -m "fix: Correct Azure Monitor connection handling"

   # Cherry-pick to minimal
   git checkout minimal
   git cherry-pick <commit-hash>
   ```

2. **New utility features** in `tools/`
   ```bash
   # Add feature in main
   git checkout main
   # ... add new Timer feature ...
   git commit -m "feat: Add async support to Timer"

   # Cherry-pick to minimal
   git checkout minimal
   git cherry-pick <commit-hash>
   ```

3. **Core dependency updates**
   ```bash
   # Update in main
   git checkout main
   uv add pydantic@latest
   git add pyproject.toml uv.lock
   git commit -m "chore: Update pydantic to latest"

   # Cherry-pick to minimal
   git checkout minimal
   git cherry-pick <commit-hash>
   ```

4. **Essential configuration fixes**
   ```bash
   # Fix in main
   git checkout main
   # ... fix ruff.toml issue ...
   git commit -m "fix: Correct Ruff ignore pattern"

   # Cherry-pick to minimal
   git checkout minimal
   git cherry-pick <commit-hash>
   ```

#### Never Cherry-Pick to `minimal`:
- Documentation updates (docs/)
- CI/CD changes (azure-pipelines/)
- Coverage configuration
- Pre-commit hooks
- MkDocs configuration
- Nox tasks

### Cherry-Pick Workflow

#### Simple Case (Clean Apply)
```bash
# 1. Identify commit in main
git checkout main
git log --oneline -10  # Find the commit hash

# 2. Switch to minimal and cherry-pick
git checkout minimal
git cherry-pick <commit-hash>

# 3. Verify tests pass
uv run pytest
uv run ruff check .
uv run pyright

# 4. Push
git push origin minimal
```

#### Complex Case (Conflicts)
```bash
# 1. Start cherry-pick
git checkout minimal
git cherry-pick <commit-hash>

# 2. If conflicts occur:
# Git will pause and show conflicts in files
# Edit conflicting files manually

# 3. Resolve conflicts
git add <resolved-files>
git cherry-pick --continue

# 4. If cherry-pick doesn't apply cleanly:
# You may need to manually apply the changes
git cherry-pick --abort
# Then manually port the changes

# 5. Verify
uv run pytest
```

### Handling Merge Conflicts

Common conflict scenarios:

#### pyproject.toml Conflicts
```bash
# main has: mkdocs, nox, pre-commit, pytest-cov
# minimal has: only pytest, ruff, pyright

# Resolution: Keep minimal's simpler dependency list
# Only add if it's a core dependency (pydantic, azure-monitor, etc.)
```

#### README.md Conflicts
```bash
# main has: extensive docs with many sections
# minimal has: quick-start only

# Resolution: Keep minimal's quick-start approach
# Don't merge extensive documentation sections
```

#### Config File Conflicts
```bash
# ruff.toml, pytest.ini, etc.
# main has: extensive rules and coverage requirements
# minimal has: essential rules only

# Resolution: Evaluate case-by-case
# Only adopt if it fixes a bug or improves core functionality
```

### Multi-Commit Updates

When multiple related commits need syncing:

```bash
git checkout minimal

# Cherry-pick a range of commits
git cherry-pick <start-commit>^..<end-commit>

# Or cherry-pick multiple individual commits
git cherry-pick <commit1> <commit2> <commit3>
```

### Selective File Cherry-Pick

When you only want specific files from a commit:

```bash
git checkout minimal

# Show files in a commit
git show --name-only <commit-hash>

# Check out specific files from main
git checkout main -- tools/logger/logger.py
git commit -m "fix: Port logger fix from main"
```

## Branch-Specific Changes

### Changes That Stay in `main` Only

#### Documentation Updates
```bash
git checkout main
# Edit docs/guides/tools/logger.md
git commit -m "docs: Update logger examples"
# Don't cherry-pick to minimal
```

#### CI/CD Updates
```bash
git checkout main
# Edit azure-pipelines/test.yml
git commit -m "ci: Add Python 3.15 to test matrix"
# Don't cherry-pick to minimal
```

#### Nox Tasks
```bash
git checkout main
# Edit noxfile.py
git commit -m "chore: Add new nox session"
# Don't cherry-pick to minimal
```

### Changes That Stay in `minimal` Only

#### Simplified Configs
```bash
git checkout minimal
# Simplify ruff.toml rules
git commit -m "chore: Reduce ruff rules for minimal"
# Don't merge back to main
```

#### POC-Specific Documentation
```bash
git checkout minimal
# Update README with POC-specific notes
git commit -m "docs: Add POC quick tips"
# Don't merge back to main
```

## Decision Tree: Should I Cherry-Pick?

```
Does the change affect tools/ package code?
├─ YES → Cherry-pick to minimal
└─ NO → Is it a core dependency update?
    ├─ YES → Cherry-pick to minimal
    └─ NO → Is it a bug fix in shared config?
        ├─ YES → Cherry-pick to minimal
        └─ NO → Keep in main only
```

## Testing After Cherry-Pick

Always run full verification after cherry-picking:

```bash
# In minimal branch after cherry-pick
uv sync                    # Update dependencies
uv run pytest -v          # Run all tests
uv run ruff check .       # Lint check
uv run ruff format .      # Format check
uv run pyright            # Type check

# If all pass:
git push origin minimal
```

## Examples

### Example 1: Bug Fix in Logger

```bash
# Bug discovered and fixed in main
git checkout main
# Fix: tools/logger/logger.py - handle None connection_string
git commit -m "fix(logger): Handle None connection_string gracefully"

# Port to minimal
git checkout minimal
git cherry-pick HEAD~1  # or use commit hash
uv run pytest tests/test__minimal.py  # Verify
git push origin minimal
```

### Example 2: New Feature in Config Module

```bash
# New feature in main
git checkout main
# Add: tools/config/settings.py - add DATABASE_URL field
git commit -m "feat(config): Add DATABASE_URL setting"

# Port to minimal
git checkout minimal
git cherry-pick <commit-hash>

# Verify
uv run pytest
uv run pyright
git push origin minimal
```

### Example 3: Documentation Update (Don't Cherry-Pick)

```bash
# Documentation update in main
git checkout main
# Edit: docs/guides/tools/logger.md
git commit -m "docs: Add logger best practices"

# DO NOT cherry-pick to minimal
# Documentation stays in main only
```

### Example 4: Dependency Update

```bash
# Update Pydantic in main
git checkout main
uv add pydantic@2.13.0
git commit -m "chore: Update pydantic to 2.13.0"

# Port to minimal
git checkout minimal
git cherry-pick <commit-hash>
# Resolve pyproject.toml conflicts if needed
# Keep minimal's dev dependencies (don't add mkdocs, nox, etc.)
uv sync
uv run pytest
git push origin minimal
```

## Common Pitfalls

### ❌ Don't: Merge minimal back to main
```bash
# WRONG - never do this
git checkout main
git merge minimal
```

### ❌ Don't: Cherry-pick documentation to minimal
```bash
# WRONG - minimal should stay lightweight
git checkout minimal
git cherry-pick <docs-commit>
```

### ❌ Don't: Create features directly in minimal
```bash
# WRONG - create in main first
git checkout minimal
# ... add new feature to tools/ ...
```

### ✅ Do: Create features in main, then port
```bash
# CORRECT - main is source of truth
git checkout main
# ... add new feature to tools/ ...
git commit -m "feat: Add new utility"

git checkout minimal
git cherry-pick <commit-hash>
```

## Conflict Resolution Strategy

When conflicts occur during cherry-pick:

1. **Understand the conflict**
   ```bash
   git status  # See which files have conflicts
   git diff    # See the conflict markers
   ```

2. **Resolve based on branch purpose**
   - `minimal`: Keep simpler version, fewer dependencies
   - Prefer minimal's configuration philosophy
   - Only add complexity if it fixes a bug

3. **Test thoroughly**
   ```bash
   uv run pytest -v
   uv run ruff check .
   uv run pyright
   ```

4. **Document complex resolutions**
   ```bash
   git commit -m "fix: Port logger update (manually resolved pyproject.toml)"
   ```

## Quick Reference

```bash
# View branch differences
git diff main..minimal

# See what's in main but not in minimal
git log minimal..main --oneline

# See what's in minimal but not in main
git log main..minimal --oneline

# Cherry-pick from main to minimal
git checkout minimal
git cherry-pick <commit-from-main>

# Abort a failed cherry-pick
git cherry-pick --abort

# Continue after resolving conflicts
git cherry-pick --continue
```

## Summary

**Golden Rules:**
1. ✅ `main` → `minimal` (one direction only)
2. ✅ Cherry-pick bug fixes and core features
3. ✅ Keep minimal lightweight
4. ❌ Never merge `minimal` → `main`
5. ❌ Don't cherry-pick docs, CI/CD, or tooling to minimal
6. ✅ Always test after cherry-picking

**Branch Purposes:**
- `main`: Complete, documented, production-ready
- `minimal`: Fast, simple, POC-optimized

**Workflow:**
1. Develop in `main`
2. Identify what needs to sync
3. Cherry-pick to `minimal`
4. Test thoroughly
5. Push both branches
