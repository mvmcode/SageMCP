# GitHub Actions CI/CD Pipeline

This directory contains the complete CI/CD pipeline configuration for the SageMCP project.

## 📋 Workflows Overview

### 1. `ci.yml` - Main CI Pipeline
**Trigger**: Push to `main`/`develop`, Pull Requests
**Purpose**: Comprehensive testing and validation

**Jobs:**
- **Backend Tests**: Run pytest with PostgreSQL service
- **Frontend Tests**: Run vitest with coverage
- **Backend Linting**: flake8, black, isort, mypy
- **Docker Build**: Test container builds
- **Integration Tests**: Full docker-compose validation
- **Security Scan**: Trivy vulnerability scanning

### 2. `pr-checks.yml` - Pull Request Validation
**Trigger**: Pull Request events
**Purpose**: Selective testing based on changed files

**Features:**
- **Path filtering**: Only runs relevant jobs for changed components
- **Backend checks**: Code formatting, linting, type checking, tests
- **Frontend checks**: TypeScript, linting, tests, build verification
- **Docker checks**: Container build validation
- **Security scanning**: Critical/High vulnerability detection
- **PR comments**: Automated coverage and status reporting

### 3. `deploy.yml` - Deployment Pipeline
**Trigger**: Push to `main`, Release tags
**Purpose**: Build and push container images

**Jobs:**
- **Multi-platform builds**: linux/amd64, linux/arm64
- **Container Registry**: GitHub Container Registry (ghcr.io)
- **Staging deployment**: Automatic on `main` branch
- **Production deployment**: Manual on release tags

### 4. `release.yml` - Release Management
**Trigger**: Version tags (v*)
**Purpose**: Automated release creation and artifact publishing

**Features:**
- **Release notes generation**: Automatic changelog from git history
- **Multi-platform images**: Cross-platform container builds
- **GitHub releases**: Automated with artifacts
- **Helm chart updates**: Version synchronization
- **Deployment notifications**: Ready-to-deploy status

### 5. `security.yml` - Security & Compliance
**Trigger**: Daily schedule, Push to `main`, Pull Requests
**Purpose**: Continuous security monitoring

**Scans:**
- **Dependency vulnerabilities**: Python (safety) and npm audit
- **Container security**: Trivy image scanning
- **Code analysis**: GitHub CodeQL (Python & JavaScript)
- **Secret detection**: TruffleHog scanning
- **License compliance**: Automated license checking
- **Security reports**: Aggregated findings and recommendations

## 🔧 Configuration Files

### `dependabot.yml`
Automated dependency updates for:
- Python packages (pip)
- npm packages (frontend)
- GitHub Actions
- Docker base images
- Weekly schedule with automatic PR creation

## 🚀 Usage Instructions

### Setting Up CI/CD

1. **Repository Secrets** (if needed):
   ```
   # For private registries or deployment
   DOCKER_REGISTRY_TOKEN
   DEPLOYMENT_TOKEN
   ```

2. **Branch Protection Rules**:
   - Require PR reviews
   - Require status checks to pass
   - Require up-to-date branches
   - Include administrators

3. **Environment Configuration**:
   - **Staging**: Auto-deploy from `main`
   - **Production**: Manual approval for releases

### Triggering Workflows

```bash
# Trigger CI on feature branch
git push origin feature-branch

# Create PR (triggers pr-checks.yml)
gh pr create --title "Feature: New functionality"

# Release new version (triggers release.yml)
git tag v1.0.0
git push origin v1.0.0

# Manual security scan
gh workflow run security.yml
```

## 📊 Workflow Status

### Required Checks
- ✅ Backend Tests
- ✅ Frontend Tests  
- ✅ Backend Linting
- ✅ Docker Build
- ✅ Security Scan

### Optional Checks
- 🔍 Integration Tests
- 📝 License Compliance
- 🔒 Dependency Scan

## 🛠️ Local Testing

### Validate workflows locally:
```bash
# Install act (GitHub Actions runner)
brew install act

# Run CI workflow
act -j backend-test

# Run PR checks
act pull_request -j backend-checks
```

### Test scripts:
```bash
# Backend
make test-backend
make lint

# Frontend  
cd frontend
npm run test:coverage
npm run lint
npm run type-check

# Docker
make build
docker-compose up -d
```

## 🔍 Monitoring & Debugging

### Workflow Logs
- GitHub Actions tab shows all workflow runs
- Individual job logs available for debugging
- Artifact downloads for test reports and coverage

### Security Alerts
- Dependabot PRs for vulnerability fixes
- Security tab shows CodeQL and Trivy findings
- Automated license compliance reports

### Performance Metrics
- Build times tracked across runs
- Test coverage trends monitored
- Container image size optimization

## 📚 Best Practices

### Code Quality
- All code must pass linting and type checking
- Minimum 80% test coverage required
- Security scans must pass (no critical/high vulnerabilities)

### Releases
- Use semantic versioning (v1.2.3)
- Include comprehensive release notes
- Test releases in staging before production

### Security
- Regular dependency updates via Dependabot
- Automated vulnerability scanning
- Secrets management through GitHub Secrets

## 🆘 Troubleshooting

### Common Issues

1. **Test Failures**:
   ```bash
   # Check test logs in GitHub Actions
   # Run tests locally to reproduce
   make test-backend
   cd frontend && npm test
   ```

2. **Build Failures**:
   ```bash
   # Verify Docker builds locally
   docker build -t test .
   docker-compose build
   ```

3. **Security Scan Failures**:
   ```bash
   # Update dependencies
   pip install --upgrade -r requirements.txt
   cd frontend && npm audit fix
   ```

4. **Deployment Issues**:
   ```bash
   # Check image tags and registry access
   docker pull ghcr.io/username/sagemcp/backend:latest
   ```

For more help, check the [main project README](../README.md) or create an issue.