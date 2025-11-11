# PyPI Publishing Guide

This document explains how to set up and use the automated PyPI publishing workflow for the SageMCP CLI.

## Overview

The PyPI publishing workflow automatically publishes the `sage-mcp` package (with CLI support) to PyPI when:

1. **CLI changes are detected** on the `main` branch
2. **Version changes** are detected in `__init__.py` or `pyproject.toml`
3. **Manual trigger** via GitHub Actions UI
4. **Release is published** on GitHub

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Trigger Conditions                        │
├─────────────────────────────────────────────────────────────┤
│ • Push to main (CLI changes)                                │
│ • Manual workflow dispatch                                  │
│ • GitHub release published                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              1. Detect Changes                              │
├─────────────────────────────────────────────────────────────┤
│ Check if CLI or version files changed                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              2. Test CLI                                    │
├─────────────────────────────────────────────────────────────┤
│ • Run pytest on CLI tests                                   │
│ • Test on Python 3.11 and 3.12                             │
│ • Verify installation                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              3. Build Package                               │
├─────────────────────────────────────────────────────────────┤
│ • Build wheel and sdist                                     │
│ • Validate with twine                                       │
│ • Upload artifacts                                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         4. Publish to Test PyPI (optional)                  │
├─────────────────────────────────────────────────────────────┤
│ • Publish to test.pypi.org                                  │
│ • Verify installation                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         5. Publish to Production PyPI                       │
├─────────────────────────────────────────────────────────────┤
│ • Publish to pypi.org                                       │
│ • Create GitHub release                                     │
│ • Verify installation                                       │
└─────────────────────────────────────────────────────────────┘
```

## Setup Instructions

### 1. Configure PyPI Trusted Publishing

Trusted publishing is the recommended way to publish to PyPI from GitHub Actions (no API tokens needed).

#### For Production PyPI

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher:
   - **PyPI Project Name**: `sage-mcp`
   - **Owner**: `mvmcode` (your GitHub org/user)
   - **Repository**: `SageMCP`
   - **Workflow**: `pypi-publish.yml`
   - **Environment**: `pypi`

#### For Test PyPI

1. Go to https://test.pypi.org/manage/account/publishing/
2. Add a new publisher with the same settings:
   - **PyPI Project Name**: `sage-mcp`
   - **Owner**: `mvmcode`
   - **Repository**: `SageMCP`
   - **Workflow**: `pypi-publish.yml`
   - **Environment**: `test-pypi`

### 2. Configure GitHub Environments

#### Production Environment (pypi)

1. Go to repository **Settings** → **Environments**
2. Create environment: `pypi`
3. Configure protection rules:
   - ✅ **Required reviewers**: Add team members who can approve
   - ✅ **Deployment branches**: Select `main` only
4. No secrets needed (uses trusted publishing)

#### Test Environment (test-pypi)

1. Create environment: `test-pypi`
2. Configure protection rules:
   - ⬜ **Required reviewers**: Optional for testing
   - ✅ **Deployment branches**: Select `main` only

### 3. Alternative: Using API Tokens

If you prefer using API tokens instead of trusted publishing:

1. Get API tokens:
   - PyPI: https://pypi.org/manage/account/token/
   - Test PyPI: https://test.pypi.org/manage/account/token/

2. Add secrets to repository:
   - `PYPI_API_TOKEN` - Production PyPI token
   - `TEST_PYPI_API_TOKEN` - Test PyPI token

3. Update workflow to use tokens:
   ```yaml
   - name: Publish to PyPI
     uses: pypa/gh-action-pypi-publish@release/v1
     with:
       password: ${{ secrets.PYPI_API_TOKEN }}
   ```

## Usage

### Automatic Publishing (Recommended)

The workflow automatically triggers when CLI changes are pushed to `main`:

```bash
# Make CLI changes
git checkout -b feature/cli-improvement
# ... make changes in src/sage_mcp/cli/
git add src/sage_mcp/cli/
git commit -m "Add new CLI feature"
git push origin feature/cli-improvement

# Create PR and merge to main
# Workflow triggers automatically after merge
```

### Manual Publishing

Use when you need to publish without code changes:

1. Go to **Actions** → **Publish to PyPI**
2. Click **Run workflow**
3. Select branch: `main`
4. (Optional) Enter version number
5. (Optional) Skip tests if already run
6. Click **Run workflow**

### Publishing a Release

1. Update version in `src/sage_mcp/__init__.py`:
   ```python
   __version__ = "0.2.0"
   ```

2. Commit and push:
   ```bash
   git add src/sage_mcp/__init__.py
   git commit -m "Bump version to 0.2.0"
   git push origin main
   ```

3. Create a GitHub release:
   ```bash
   gh release create v0.2.0 \
     --title "Release v0.2.0" \
     --notes "New features and improvements"
   ```

4. Workflow automatically publishes to PyPI

## Workflow Triggers

### 1. Push to Main (CLI Changes)

**Triggers when:**
- Files in `src/sage_mcp/cli/` are modified
- `pyproject.toml` is modified
- `src/sage_mcp/__init__.py` is modified

**Actions:**
- ✅ Run tests
- ✅ Build package
- ✅ Publish to Test PyPI
- ⬜ Does NOT publish to production (requires manual trigger or release)

### 2. Manual Workflow Dispatch

**Triggers when:**
- Manually triggered from GitHub Actions UI

**Actions:**
- ✅ Run tests
- ✅ Build package
- ⬜ Skip Test PyPI
- ✅ Publish to production PyPI
- ✅ Create GitHub release

### 3. GitHub Release

**Triggers when:**
- A GitHub release is published

**Actions:**
- ✅ Run tests
- ✅ Build package
- ⬜ Skip Test PyPI
- ✅ Publish to production PyPI

## Version Management

### Automatic Versioning

The workflow reads the version from `src/sage_mcp/__init__.py`:

```python
__version__ = "0.1.0"
```

### Manual Version Override

When manually triggering, you can specify a version:

1. Go to **Actions** → **Publish to PyPI** → **Run workflow**
2. Enter version: `0.2.0`
3. Run workflow

### Version Bumping Strategy

Follow semantic versioning (SemVer):

- **Major** (1.0.0): Breaking changes
- **Minor** (0.2.0): New features, backwards compatible
- **Patch** (0.1.1): Bug fixes

Example bump script:

```bash
# Bump patch version
./scripts/bump-version.sh patch

# Bump minor version
./scripts/bump-version.sh minor

# Bump major version
./scripts/bump-version.sh major
```

## Testing Before Publishing

### Local Testing

```bash
# Install in editable mode
pip install -e ".[cli,dev]"

# Run tests
pytest tests/cli/ -v

# Test installation
sagemcp --version
sagemcp --help
```

### Test PyPI Testing

After publishing to Test PyPI:

```bash
# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  sage-mcp[cli]

# Verify
sagemcp --version
```

### Build Testing

Test the build locally before pushing:

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*

# Test installation from local build
pip install dist/sage_mcp-*.whl
sagemcp --version
```

## Monitoring and Debugging

### Check Workflow Status

```bash
# View recent workflow runs
gh run list --workflow=pypi-publish.yml

# View specific run
gh run view <run-id>

# Watch a running workflow
gh run watch
```

### Common Issues

#### 1. Package Already Exists

**Error:** `File already exists`

**Solution:**
- PyPI does not allow re-uploading the same version
- Bump version number
- Or use `skip-existing: true` in workflow (already configured for Test PyPI)

#### 2. Trusted Publishing Not Configured

**Error:** `403 Forbidden`

**Solution:**
- Follow setup instructions above
- Ensure environment names match exactly
- Verify workflow filename is correct

#### 3. Tests Failing

**Error:** Test stage fails

**Solution:**
- Review test logs in GitHub Actions
- Fix failing tests locally
- Push fixes and retry

#### 4. Import Errors

**Error:** Module not found after installation

**Solution:**
- Verify `pyproject.toml` includes all dependencies
- Check package structure in `[tool.hatch.build.targets.wheel]`
- Test local build: `pip install dist/*.whl`

### Workflow Logs

View detailed logs:

1. Go to **Actions** tab
2. Click on workflow run
3. Click on job (e.g., "test-cli", "build", "publish-prod")
4. Expand steps to see detailed output

## Security Considerations

### Trusted Publishing Benefits

- ✅ No API tokens to manage
- ✅ Automatic token rotation
- ✅ Scoped to specific workflow
- ✅ Reduced risk of token leakage

### Best Practices

1. **Use environments** for production deploys
2. **Require reviews** for production environment
3. **Limit workflow permissions** to minimum required
4. **Monitor releases** via GitHub notifications
5. **Sign releases** (optional, for extra security)

### Permissions

The workflow requires:

```yaml
permissions:
  id-token: write    # For trusted publishing
  contents: write    # For creating releases
```

These are scoped to the workflow only.

## Rollback Procedure

If a bad version is published:

### 1. Yank the Version on PyPI

```bash
# Install twine
pip install twine

# Yank version (makes it uninstallable for new users)
twine yank sage-mcp <version> -r pypi
```

Or via PyPI web UI:
1. Go to https://pypi.org/project/sage-mcp/
2. Find the version
3. Click "Options" → "Yank release"

### 2. Publish Fixed Version

```bash
# Bump to patch version
# Edit src/sage_mcp/__init__.py: __version__ = "0.1.1"

git add src/sage_mcp/__init__.py
git commit -m "Hotfix: Fix critical issue in 0.1.0"
git push origin main

# Manually trigger workflow or create release
```

### 3. Notify Users

Create a GitHub issue or discussion:

```markdown
## ⚠️ Version 0.1.0 Yanked

Version 0.1.0 has been yanked due to [issue description].

**Action Required:**
- Upgrade to 0.1.1: `pip install --upgrade sage-mcp[cli]`
- Or pin to working version: `sage-mcp[cli]==0.0.9`

**What's Fixed in 0.1.1:**
- [List of fixes]
```

## Maintenance

### Regular Checks

- **Weekly**: Check for failed workflow runs
- **Monthly**: Review dependency versions
- **Quarterly**: Update GitHub Actions versions

### Dependency Updates

Update action versions in workflow:

```yaml
- uses: actions/checkout@v4  # Check for v5
- uses: actions/setup-python@v4  # Check for v5
- uses: pypa/gh-action-pypi-publish@release/v1  # Check for updates
```

### Metrics

Track publishing metrics:

- **Success rate**: % of successful publishes
- **Time to publish**: From merge to PyPI
- **Test coverage**: CLI test coverage percentage
- **Install verification**: Installation success rate

## Reference

### Related Documentation

- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)

### Workflow File

`.github/workflows/pypi-publish.yml`

### Key Files

- `pyproject.toml` - Package configuration
- `src/sage_mcp/__init__.py` - Version definition
- `src/sage_mcp/cli/` - CLI source code
- `tests/cli/` - CLI tests

### Support

- **Issues**: https://github.com/mvmcode/SageMCP/issues
- **Discussions**: https://github.com/mvmcode/SageMCP/discussions
- **Discord**: https://discord.gg/kpHzRzmy

## Quick Reference

### Publish Commands

```bash
# Test locally
python -m build && twine check dist/*

# Push CLI changes (auto-publishes to Test PyPI)
git push origin main

# Manual publish to production
gh workflow run pypi-publish.yml

# Create release (auto-publishes to production)
gh release create v0.2.0
```

### Version Bump

```bash
# Edit version
vim src/sage_mcp/__init__.py

# Commit and push
git add src/sage_mcp/__init__.py
git commit -m "Bump version to 0.2.0"
git push origin main
```

### Verify Installation

```bash
# Install from PyPI
pip install sage-mcp[cli]

# Verify
sagemcp --version
sagemcp --help
```

---

**Last Updated**: 2025-11-10
**Workflow Version**: 1.0
**Status**: ✅ Ready for Production
