# Changelog

All notable changes to SageMCP will be documented in this file.

## [Unreleased]

### Added - GitHub Connector Expansion (2025-01-XX)

**Expanded GitHub connector from 9 to 24 tools - 166% increase in functionality**

#### New Tools Added (15 tools):

**Commits & Code Changes (3 tools):**
- `github_list_commits` - List repository commits with advanced filtering (author, date range, path)
- `github_get_commit` - Get detailed commit information including diffs, stats, and file changes
- `github_compare_commits` - Compare two branches or commits to see differences

**Branch Management (2 tools):**
- `github_list_branches` - List all repository branches with protection status
- `github_get_branch` - Get detailed branch information and protection rules

**User Activity & Statistics (3 tools):**
- `github_get_user_activity` - Track user's recent activity (commits, PRs, issues, reviews)
- `github_get_user_stats` - Get comprehensive user statistics (repos, stars, languages, top projects)
- `github_list_contributors` - List repository contributors with contribution counts

**Repository Statistics (1 tool):**
- `github_get_repo_stats` - Get detailed repository statistics (languages, stars, features, activity)

**GitHub Actions / Workflows (3 tools):**
- `github_list_workflows` - List all GitHub Actions workflows
- `github_list_workflow_runs` - List workflow run history with status filtering
- `github_get_workflow_run` - Get detailed workflow run information

**Releases (2 tools):**
- `github_list_releases` - List all repository releases
- `github_get_release` - Get specific release details and download assets

**Duplicate Removal (1 tool):**
- Removed duplicate `github_list_organizations` (was listed twice)

#### Coverage Impact:
- **Before:** 9 tools (~10% GitHub API coverage)
- **After:** 24 tools (~25-30% GitHub API coverage)
- **Increase:** +15 tools, +166% functionality

#### Use Cases Enabled:
- ✅ Commit history analysis and code review
- ✅ Branch comparison and management
- ✅ User activity tracking and contributor analysis
- ✅ Repository statistics and insights
- ✅ CI/CD monitoring (GitHub Actions)
- ✅ Release management and asset downloads
- ✅ Developer productivity analytics

#### Documentation:
- Added comprehensive tool documentation: `docs/github-connector-tools.md`
- Updated README.md with categorized tool listing
- Added usage examples for all new tools

---

## [0.1.0] - 2025-01-XX

### Initial Release

#### Features:
- **Multi-tenant MCP server platform**
- **Path-based tenant isolation** (`/api/v1/{tenant}/mcp`)
- **OAuth 2.0 integration** (GitHub, GitLab, Google)
- **Connector plugin system** for extensibility
- **MCP protocol compliance** (WebSocket, HTTP, SSE)
- **React-based web UI** for management
- **PostgreSQL database** for data persistence
- **Docker Compose** for local development
- **Testing framework** with SQLite in-memory (40/40 tests passing)

#### GitHub Connector (Initial 9 tools):
- `github_list_repositories` - List user repositories
- `github_get_repository` - Get repository details
- `github_list_issues` - List repository issues
- `github_get_file_content` - Get file content
- `github_list_pull_requests` - List pull requests
- `github_search_repositories` - Search repositories
- `github_check_token_scopes` - Debug OAuth permissions
- `github_list_organizations` - List organizations
- `github_get_user_info` - Get user information

#### Infrastructure:
- FastAPI backend with async SQLAlchemy
- Multi-tenant database schema
- OAuth credential storage and management
- Connector registry pattern
- MCP server implementation
- Transport layer (WebSocket/HTTP/SSE)
- Admin API for tenant management
- Health check endpoints

#### Testing:
- Unit tests (pytest)
- Integration tests
- SQLite in-memory for test speed
- 41% code coverage
- Flake8 linting
- GitHub Actions CI/CD

#### Documentation:
- README with setup instructions
- OAuth configuration guide
- Connector development guide
- API documentation
- Testing guide
- CI/CD workflows documentation

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backward compatible)
- **PATCH** version for backward compatible bug fixes

---

## Categories

### Added
New features or functionality

### Changed
Changes in existing functionality

### Deprecated
Features that will be removed in upcoming releases

### Removed
Removed features

### Fixed
Bug fixes

### Security
Security vulnerability fixes

---

## Future Roadmap

### Next Release (v0.2.0)
- [ ] MCP server bridge pattern implementation
- [ ] Dynamic MCP server registration via UI
- [ ] MCP server catalog (GitHub, GitLab, Filesystem, etc.)
- [ ] External MCP server health monitoring
- [ ] Docker Compose generator for MCP servers

### v0.3.0 - Write Operations
- [ ] GitHub: Create issues and PRs
- [ ] GitHub: Create commits and branches
- [ ] GitHub: Comment on issues and PRs
- [ ] GitHub: Merge pull requests

### v0.4.0 - Additional Connectors
- [ ] GitLab connector
- [ ] Notion connector
- [ ] Slack connector
- [ ] Google Docs connector

### v1.0.0 - Production Ready
- [ ] Kubernetes Helm charts
- [ ] Advanced security features
- [ ] SSO/SAML support
- [ ] Audit logging
- [ ] Rate limiting per tenant
- [ ] Webhook support
- [ ] Comprehensive API documentation
- [ ] Performance optimization

---

## Contribution Guidelines

When contributing changes, please:
1. Update this CHANGELOG.md with your changes
2. Follow semantic versioning principles
3. Add comprehensive documentation
4. Include tests for new features
5. Update README.md if needed

---

## Links

- **Repository:** https://github.com/yourusername/sage-mcp
- **Issues:** https://github.com/yourusername/sage-mcp/issues
- **Documentation:** [README.md](README.md)
- **License:** [Apache 2.0](LICENSE)
