# Sage MCP - Multi-Tenant MCP Server Platform

A scalable, multi-tenant platform for hosting MCP (Model Context Protocol) servers with OAuth integration and connector plugins for various services. Built for seamless integration with Claude Desktop and other MCP clients.

## 🚀 Features

- **Multi-Tenant Architecture**: Path-based tenant isolation (`yourdomain.com/tenant1/mcp`)
- **MCP Protocol Compliance**: Full WebSocket, HTTP, and SSE transport with Claude Desktop compatibility
- **OAuth 2.0 Integration**: Secure authentication for GitHub, GitLab, Google, and other services
- **Plugin System**: Extensible connector architecture for easy service integration
- **Built-in Connectors**: 
  - ✅ **GitHub** - Full repository access, issues, PRs, file content, search
  - 🚧 GitLab, Google Docs, Notion (coming soon)
- **Web Management Interface**: React-based frontend for tenant and connector management
- **PostgreSQL Database**: Robust data persistence with SQLAlchemy
- **Docker Support**: Complete containerization for development and production
- **Kubernetes Ready**: Helm charts for AWS EKS deployment
- **Admin API**: RESTful API for tenant and connector management
- **Real-time Debugging**: Token scope checking and connection diagnostics

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │◄──►│   FastAPI App   │◄──►│   Connectors    │
│ (Claude Desktop)│    │                 │    │   ✅ GitHub     │
└─────────────────┘    │  ┌───────────┐  │    │   🚧 GitLab     │
                       │  │Multi-Tenant│  │    │   🚧 Notion     │
┌─────────────────┐    │  │  Router   │  │    │   🚧 Slack      │
│  React Frontend │◄──►│  └───────────┘  │    │   + Custom      │
│ (Web Interface) │    │                 │    └─────────────────┘
└─────────────────┘    │  ┌───────────┐  │    
                       │  │OAuth Flow │  │    ┌─────────────────┐
┌─────────────────┐    │  │ & Tokens  │  │◄──►│   PostgreSQL    │
│  OAuth Provider │◄──►│  └───────────┘  │    │    Database     │
│ (GitHub, etc)   │    └─────────────────┘    └─────────────────┘
└─────────────────┘
```

## 🚦 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL (included in Docker setup)

### Quick Start with Docker

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd sage-mcp
   make setup
   ```

2. **Configure OAuth** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your OAuth credentials
   ```

3. **Start the platform**:
   ```bash
   make up
   ```

4. **Access the services**:
   - **Frontend**: http://localhost:3000 (React management interface)
   - **API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs
   - **Database Admin**: http://localhost:8080 (Adminer)
   - **Health Check**: http://localhost:8000/health

### Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -e .
   ```

2. **Setup database**:
   ```bash
   # Start PostgreSQL
   docker-compose up postgres -d
   ```

3. **Run the application**:
   ```bash
   uvicorn sage_mcp.main:app --reload
   ```

## 📚 Usage

### Using the Web Interface

1. **Open the frontend**: http://localhost:3000
2. **Create a tenant** using the web interface
3. **Add connectors** and configure OAuth credentials
4. **Copy the MCP server URL** for your Claude Desktop configuration

### Claude Desktop Configuration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "sage-mcp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-everything"],
      "env": {
        "MCP_SERVER_URL": "ws://localhost:8000/api/v1/{tenant-slug}/mcp"
      }
    }
  }
}
```

Or use the HTTP endpoint:
```
http://localhost:8000/api/v1/{tenant-slug}/mcp
```

### Available GitHub Tools

Once GitHub OAuth is configured, you'll have access to **24 comprehensive tools**:

**Repository Management (6 tools):**
- `github_list_repositories` - List accessible repositories with filters
- `github_get_repository` - Get detailed repository information
- `github_search_repositories` - Search repositories by query
- `github_get_repo_stats` - Get repository statistics and languages
- `github_list_contributors` - List contributors with contribution counts
- `github_get_file_content` - Get file content from repositories

**Commits & Code Changes (3 tools):**
- `github_list_commits` - List commits with filters (author, date, path)
- `github_get_commit` - Get commit details including diffs and stats
- `github_compare_commits` - Compare branches or commits

**Branch Management (2 tools):**
- `github_list_branches` - List repository branches
- `github_get_branch` - Get branch details and protection status

**Issues & Pull Requests (2 tools):**
- `github_list_issues` - List repository issues with filters
- `github_list_pull_requests` - List pull requests with filters

**User Information & Activity (4 tools):**
- `github_get_user_info` - Get user profile and repositories
- `github_get_user_stats` - Get comprehensive user statistics
- `github_get_user_activity` - Get recent user activity events
- `github_list_organizations` - List user's organizations

**GitHub Actions / Workflows (3 tools):**
- `github_list_workflows` - List repository workflows
- `github_list_workflow_runs` - List workflow run history
- `github_get_workflow_run` - Get detailed workflow run information

**Releases (2 tools):**
- `github_list_releases` - List repository releases
- `github_get_release` - Get release details and assets

**OAuth & Debugging (2 tools):**
- `github_check_token_scopes` - Debug OAuth token permissions
- `github_list_organizations` - List accessible organizations

### API Usage (Alternative)

#### Creating a Tenant

```bash
curl -X POST "http://localhost:8000/api/v1/admin/tenants" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "acme-corp",
    "name": "ACME Corporation",
    "description": "ACME Corp tenant",
    "contact_email": "admin@acme.com"
  }'
```

#### Adding a GitHub Connector

```bash
curl -X POST "http://localhost:8000/api/v1/admin/tenants/acme-corp/connectors" \
  -H "Content-Type: application/json" \
  -d '{
    "connector_type": "github",
    "name": "ACME GitHub",
    "description": "GitHub integration for ACME"
  }'
```

## 🔧 Configuration

### Environment Variables

```bash
# Application
DEBUG=true
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/sage_mcp

# Note: Redis dependency has been removed for simplicity

# Security
SECRET_KEY=your-secret-key

# OAuth - GitHub
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# OAuth - GitLab
GITLAB_CLIENT_ID=your-gitlab-client-id
GITLAB_CLIENT_SECRET=your-gitlab-client-secret

# OAuth - Google
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### OAuth Setup

#### GitHub
1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create a new OAuth App with these settings:
   - **Application name**: Your app name
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/oauth/success`
3. Copy Client ID and Client Secret to your `.env` file
4. **Important**: For organization repositories, ensure your OAuth app has organization access:
   - Organization Settings > Third-party access > Grant access to your OAuth app

**Required Scopes**: `repo`, `user:email`, `read:org`

#### GitLab
1. Go to GitLab Settings > Applications
2. Create a new application
3. Set Redirect URI to: `http://localhost:8000/api/v1/oauth/{tenant}/callback/gitlab`
4. Copy Application ID and Secret to your `.env` file

## 🔌 Adding New Connectors

1. **Create connector class**:
   ```python
   # src/sage_mcp/connectors/myservice.py
   from .base import BaseConnector
   from .registry import register_connector
   from ..models.connector import ConnectorType

   @register_connector(ConnectorType.MYSERVICE)
   class MyServiceConnector(BaseConnector):
       @property
       def display_name(self) -> str:
           return "My Service"
       
       @property 
       def description(self) -> str:
           return "Integration with My Service"
       
       @property
       def requires_oauth(self) -> bool:
           return True
       
       async def get_tools(self, connector, oauth_cred=None):
           # Return list of MCP tools
           pass
       
       async def execute_tool(self, connector, tool_name, arguments, oauth_cred=None):
           # Execute tool logic
           pass
   ```

2. **Add to connector enum**:
   ```python
   # src/sage_mcp/models/connector.py
   class ConnectorType(enum.Enum):
       # ... existing types
       MYSERVICE = "myservice"
   ```

3. **Import in main app**:
   ```python
   # src/sage_mcp/main.py
   from .connectors import myservice  # noqa
   ```

## 🚀 Deployment

### Docker Compose (Development)

```bash
make up
```

### Kubernetes (Production)

*Coming soon - Helm charts for AWS EKS deployment*

## 🛠️ Development

### Testing

The project uses SQLite in-memory database for testing to simplify setup and improve speed:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run backend tests
pytest tests/ -v --cov=src/sage_mcp --cov-report=term

# Run specific test
pytest tests/unit/test_config.py -v
```

### CI/CD Workflows

The project includes comprehensive GitHub Actions workflows for automated testing and validation.

📖 **[View CI/CD Documentation](.github/workflows/README.md)** for detailed information about:
- Continuous Integration pipeline
- Pull Request checks
- Release management
- Dependabot configuration

### Available Make Commands

```bash
make help            # Show all available commands
make build           # Build Docker images
make up              # Start all services
make down            # Stop all services
make logs            # View logs from all services
make logs-app        # View backend logs only
make logs-frontend   # View frontend logs only
make shell           # Open shell in app container
make frontend-shell  # Open shell in frontend container
make db-shell        # Open PostgreSQL shell
make test            # Run all tests (backend + frontend)
make test-backend    # Run backend tests only
make test-frontend   # Run frontend tests only
make test-coverage   # Run tests with coverage reports
make lint            # Run linting
make format          # Format code
make clean           # Clean up containers and volumes
make setup           # Initial development setup
```

### Project Structure

```
sage-mcp/
├── src/sage_mcp/           # Backend (FastAPI)
│   ├── api/                 # FastAPI routes (admin, OAuth, MCP)
│   ├── auth/                # Authentication handlers
│   ├── connectors/          # Connector plugins
│   │   ├── github.py        # ✅ GitHub integration
│   │   ├── gitlab.py        # 🚧 GitLab (coming soon)
│   │   └── base.py          # Base connector class
│   ├── database/            # Database utilities
│   ├── mcp/                 # MCP protocol implementation
│   │   ├── server.py        # MCP server logic
│   │   └── transport.py     # WebSocket/HTTP transport
│   ├── models/              # SQLAlchemy models
│   ├── config.py            # Configuration
│   └── main.py              # Application entry point
├── tests/                  # Backend tests
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── conftest.py         # Test configuration
├── frontend/               # Frontend (React + TypeScript)
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── utils/           # Utilities
│   │   └── test/            # Test utilities and setup
│   ├── package.json        # Node.js dependencies
│   ├── vite.config.ts      # Vite configuration
│   └── vitest.config.ts    # Test configuration
├── helm/                   # Kubernetes Helm charts
├── docker-compose.yml      # Local development setup
├── Dockerfile             # Backend container
├── pyproject.toml         # Python project config
├── requirements.txt       # Python dependencies
├── LICENSE                # Apache 2.0 License
└── Makefile               # Development commands
```

## 🔒 Security

- **OAuth 2.0** for secure service authentication with proper scope management
- **Tenant isolation** at the database and application level
- **Secure credential storage** with proper encryption for access tokens
- **Rate limiting** and request validation
- **CORS** and security headers configured
- **Organization access control** for GitHub repositories
- **Token scope validation** and debugging tools

## 📊 Monitoring & Debugging

- **Health check endpoint**: `/health`
- **Structured logging** with request tracing
- **Database connection monitoring**
- **OAuth token expiration tracking**
- **Real-time debugging tools**:
  - `github_check_token_scopes` - Validate OAuth permissions
  - `github_list_organizations` - Check organization access
  - Detailed error messages for 403/auth issues
- **MCP protocol compliance** validation
- **Connection diagnostics** for Claude Desktop integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

Apache 2.0 License - see LICENSE file for details.

## 🆘 Support

- Documentation: [Coming soon]
- Issues: [GitHub Issues]
- Email: support@sage-mcp.com

---

## 🎯 Current Status

**✅ Production Ready Features:**
- Multi-tenant MCP server platform
- GitHub connector with full OAuth integration
- React-based management interface
- Claude Desktop compatible MCP protocol
- Organization repository access
- Real-time debugging and diagnostics

**🚧 In Development:**
- GitLab connector
- Google Docs connector
- Notion connector
- Advanced connector configuration
- Kubernetes Helm charts

**📈 Recent Updates:**
- ✅ **All tests passing (40/40)** with SQLite in-memory database
- ✅ Simplified CI/CD with no PostgreSQL service required
- ✅ Improved test coverage (41%) and automated quality checks
- Fixed MCP protocol compliance for Claude Desktop
- Implemented proper OAuth scope handling for organizations
- Added token debugging and diagnostic tools
- Updated tool names to follow MCP naming conventions
- Cleaned response format to eliminate validation errors
- Removed unused Redis dependency for simplified architecture
- Added comprehensive test suite (backend: pytest, frontend: vitest)
- Created Apache 2.0 license
- Enhanced development workflow with improved Makefile commands

---

Built with ❤️ using FastAPI, SQLAlchemy, React, and the MCP protocol.
