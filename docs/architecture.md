# SageMCP Architecture

## High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        CD[Claude Desktop]
        WEB[Web Browser]
    end

    subgraph "SageMCP Platform"
        subgraph "Frontend - React App :3001"
            UI[React UI]
            PAGES[Pages: Dashboard, Tenants, Connectors]
            COMP[Components: Modals, Forms]
        end

        subgraph "Backend - FastAPI :8000"
            API[FastAPI Application]

            subgraph "API Routes"
                ADMIN["Admin API
/api/v1/admin/*"]
                OAUTH["OAuth API
/api/v1/oauth/*"]
                MCP_ROUTE["MCP API
/api/v1/SLUG/mcp"]
            end

            subgraph "Core Services"
                MCP_SERVER[MCP Server]
                MCP_TRANSPORT["MCP Transport
WebSocket/HTTP/SSE"]
            end

            subgraph "Connector System"
                REGISTRY[Connector Registry]
                BASE[Base Connector]

                subgraph "Connector Plugins"
                    GH["GitHub
24 tools"]
                    JIRA["Jira
20 tools"]
                    SLACK["Slack
11 tools"]
                    GDOCS["Google Docs
10 tools"]
                    NOTION["Notion
10 tools"]
                    ZOOM["Zoom
12 tools"]
                end
            end

            subgraph "Data Layer"
                ORM[SQLAlchemy ORM]
                DB_MGR[Database Manager]
            end
        end

        subgraph "Database"
            DB[("PostgreSQL /
Supabase")]

            subgraph "Tables"
                T_TENANT[Tenants]
                T_CONN[Connectors]
                T_OAUTH[OAuth Credentials]
                T_CONFIG[OAuth Configs]
            end
        end
    end

    subgraph "External Services"
        GITHUB_API[GitHub API]
        SLACK_API[Slack API]
        JIRA_API[Jira API]
        GOOGLE_API[Google APIs]
        NOTION_API[Notion API]
        ZOOM_API[Zoom API]
    end

    %% Client connections
    CD -->|WebSocket/HTTP| MCP_ROUTE
    WEB -->|HTTP| UI

    %% Frontend to Backend
    UI -->|REST API| ADMIN
    UI -->|REST API| OAUTH
    UI -->|WebSocket Test| MCP_ROUTE

    %% API routing
    ADMIN -->|Manage| ORM
    OAUTH -->|Auth Flow| ORM
    MCP_ROUTE -->|Protocol| MCP_TRANSPORT

    %% MCP flow
    MCP_TRANSPORT -->|Initialize| MCP_SERVER
    MCP_SERVER -->|Get Tools| REGISTRY
    MCP_SERVER -->|Execute| REGISTRY

    %% Connector registry
    REGISTRY -->|Manage| BASE
    BASE -.->|Implements| GH
    BASE -.->|Implements| JIRA
    BASE -.->|Implements| SLACK
    BASE -.->|Implements| GDOCS
    BASE -.->|Implements| NOTION
    BASE -.->|Implements| ZOOM

    %% Database connections
    ORM -->|Async Queries| DB_MGR
    DB_MGR -->|Connection Pool| DB

    DB -->|Store| T_TENANT
    DB -->|Store| T_CONN
    DB -->|Store| T_OAUTH
    DB -->|Store| T_CONFIG

    %% External API calls
    GH -->|REST API| GITHUB_API
    JIRA -->|REST API| JIRA_API
    SLACK -->|REST API| SLACK_API
    GDOCS -->|REST API| GOOGLE_API
    NOTION -->|REST API| NOTION_API
    ZOOM -->|REST API| ZOOM_API

    style CD fill:#e1f5ff
    style WEB fill:#e1f5ff
    style UI fill:#fff3e0
    style API fill:#f3e5f5
    style MCP_SERVER fill:#e8f5e9
    style REGISTRY fill:#e8f5e9
    style DB fill:#fce4ec
```

## Multi-Tenant Architecture

```mermaid
graph TB
    subgraph "Tenant 1: acme-corp"
        T1["Tenant: acme-corp
ID: uuid-1"]
        T1_CONN1["Connector: GitHub
Enabled"]
        T1_CONN2["Connector: Slack
Enabled"]
        T1_OAUTH1["OAuth: GitHub
access_token"]
        T1_OAUTH2["OAuth: Slack
access_token"]

        T1 --> T1_CONN1
        T1 --> T1_CONN2
        T1 --> T1_OAUTH1
        T1 --> T1_OAUTH2
        T1_CONN1 -.uses.-> T1_OAUTH1
        T1_CONN2 -.uses.-> T1_OAUTH2
    end

    subgraph "Tenant 2: startup-inc"
        T2["Tenant: startup-inc
ID: uuid-2"]
        T2_CONN1["Connector: Jira
Enabled"]
        T2_CONN2["Connector: Zoom
Enabled"]
        T2_OAUTH1["OAuth: Jira
access_token"]
        T2_OAUTH2["OAuth: Zoom
access_token"]

        T2 --> T2_CONN1
        T2 --> T2_CONN2
        T2 --> T2_OAUTH1
        T2 --> T2_OAUTH2
        T2_CONN1 -.uses.-> T2_OAUTH1
        T2_CONN2 -.uses.-> T2_OAUTH2
    end

    CD1["Claude Desktop
Tenant 1"]
    CD2["Claude Desktop
Tenant 2"]

    CD1 -->|"WS: /api/v1/acme-corp/connectors/ID/mcp"| T1
    CD2 -->|"WS: /api/v1/startup-inc/connectors/ID/mcp"| T2

    style T1 fill:#e3f2fd
    style T2 fill:#f3e5f5
    style CD1 fill:#e1f5ff
    style CD2 fill:#e1f5ff
```

## OAuth Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant SageMCP
    participant Provider as OAuth Provider (GitHub/Slack/etc)
    participant API as External API

    User->>Frontend: Click "Connect GitHub"
    Frontend->>SageMCP: POST /api/v1/oauth/github/auth
    SageMCP->>SageMCP: Generate state token
    SageMCP->>Frontend: Redirect URL with state
    Frontend->>Provider: Redirect to OAuth authorization
    Provider->>User: Show authorization page
    User->>Provider: Approve permissions
    Provider->>SageMCP: Redirect with auth code
    SageMCP->>Provider: Exchange code for token
    Provider->>SageMCP: Return access_token & refresh_token
    SageMCP->>SageMCP: Store OAuthCredential in DB
    SageMCP->>Frontend: Redirect to /oauth/success
    Frontend->>User: Show success message

    Note over SageMCP,API: Later: MCP Tool Execution
    User->>SageMCP: Execute tool via MCP
    SageMCP->>SageMCP: Load OAuth credential
    SageMCP->>API: Call API with access_token
    API->>SageMCP: Return data
    SageMCP->>User: Return MCP response
```

## MCP Tool Execution Flow

```mermaid
sequenceDiagram
    participant Client as Claude Desktop
    participant Transport as MCP Transport
    participant Server as MCP Server
    participant Registry as Connector Registry
    participant Connector as Connector Plugin
    participant DB as Database
    participant API as External API

    Client->>Transport: WebSocket Connect /api/v1/SLUG/connectors/ID/mcp
    Transport->>DB: Load Tenant & Connector
    DB->>Transport: Return config
    Transport->>Server: Initialize MCP Server

    Client->>Server: list_tools()
    Server->>Registry: Get connector by type
    Registry->>Connector: get_tools()
    Connector->>Server: Return tool definitions
    Server->>Client: Tool list

    Client->>Server: call_tool("github_list_repositories", args)
    Server->>Registry: Get GitHub connector
    Registry->>Connector: execute_tool(name, args, oauth)
    Connector->>DB: Validate OAuth credential
    DB->>Connector: OAuth token valid
    Connector->>API: GET /user/repos Authorization: Bearer TOKEN
    API->>Connector: Repository list
    Connector->>Server: Format as TextContent
    Server->>Client: MCP response with data
```

## Database Schema

```mermaid
erDiagram
    TENANT ||--o{ CONNECTOR : has
    TENANT ||--o{ OAUTH_CREDENTIAL : has
    TENANT ||--o{ OAUTH_CONFIG : has

    TENANT {
        uuid id PK
        string slug UK
        string name
        string description
        boolean is_active
        string contact_email
        json settings
        datetime created_at
        datetime updated_at
    }

    CONNECTOR {
        uuid id PK
        uuid tenant_id FK
        enum connector_type
        string name
        string description
        boolean is_enabled
        json configuration
        datetime created_at
        datetime updated_at
    }

    OAUTH_CREDENTIAL {
        uuid id PK
        uuid tenant_id FK
        string provider
        string provider_user_id
        string provider_username
        text access_token
        text refresh_token
        datetime expires_at
        string scopes
        string provider_data
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    OAUTH_CONFIG {
        uuid id PK
        uuid tenant_id FK
        string provider
        string client_id
        string client_secret
        boolean is_active
        datetime created_at
        datetime updated_at
    }
```

## Connector Plugin Architecture

```mermaid
graph TB
    subgraph "Connector Registry"
        REG["ConnectorRegistry
Singleton"]
        REG_MAP{Connector Map}

        REG --> REG_MAP
    end

    subgraph "Base Class"
        BASE["BaseConnector
Abstract Class"]

        BASE_PROPS["Properties:
- name
- display_name
- requires_oauth"]
        BASE_METHODS["Methods:
- get_tools
- get_resources
- execute_tool
- read_resource
- validate_oauth"]

        BASE --> BASE_PROPS
        BASE --> BASE_METHODS
    end

    subgraph "Connector Implementations"
        GH_CONN[GitHubConnector]
        JIRA_CONN[JiraConnector]
        SLACK_CONN[SlackConnector]
        NOTION_CONN[NotionConnector]
        ZOOM_CONN[ZoomConnector]

        GH_CONN --> GH_TOOLS["24 Tools:
- list_repositories
- create_issue
- list_pull_requests
- etc."]
        JIRA_CONN --> JIRA_TOOLS["20 Tools:
- search_issues
- create_issue
- list_projects
- etc."]
        SLACK_CONN --> SLACK_TOOLS["11 Tools:
- send_message
- list_channels
- search_messages
- etc."]
        NOTION_CONN --> NOTION_TOOLS["10 Tools:
- list_databases
- get_page
- create_page
- etc."]
        ZOOM_CONN --> ZOOM_TOOLS["12 Tools:
- list_meetings
- create_meeting
- list_recordings
- etc."]
    end

    REG_MAP -->|"github"| GH_CONN
    REG_MAP -->|"jira"| JIRA_CONN
    REG_MAP -->|"slack"| SLACK_CONN
    REG_MAP -->|"notion"| NOTION_CONN
    REG_MAP -->|"zoom"| ZOOM_CONN

    BASE -.->|inherits| GH_CONN
    BASE -.->|inherits| JIRA_CONN
    BASE -.->|inherits| SLACK_CONN
    BASE -.->|inherits| NOTION_CONN
    BASE -.->|inherits| ZOOM_CONN

    style REG fill:#e8f5e9
    style BASE fill:#fff3e0
    style GH_CONN fill:#e3f2fd
    style JIRA_CONN fill:#e3f2fd
    style SLACK_CONN fill:#e3f2fd
    style NOTION_CONN fill:#e3f2fd
    style ZOOM_CONN fill:#e3f2fd
```

## Request Flow: Creating and Using a Connector

```mermaid
sequenceDiagram
    autonumber
    participant Admin as Admin User
    participant UI as Web UI
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant Provider as OAuth Provider
    participant Claude as Claude Desktop
    participant Connector as Connector Plugin
    participant ExtAPI as External API

    Note over Admin,DB: Step 1: Create Tenant
    Admin->>UI: Create tenant "acme-corp"
    UI->>API: POST /api/v1/admin/tenants
    API->>DB: INSERT INTO tenants
    DB->>API: Tenant created
    API->>UI: Return tenant data

    Note over Admin,Provider: Step 2: Setup OAuth
    Admin->>UI: Configure GitHub OAuth
    UI->>API: POST /api/v1/oauth/github/auth
    API->>Provider: Redirect to authorization
    Provider->>Admin: Show authorization page
    Admin->>Provider: Approve
    Provider->>API: Callback with auth code
    API->>Provider: Exchange code for token
    Provider->>API: Return access_token
    API->>DB: INSERT INTO oauth_credentials
    API->>UI: OAuth success

    Note over Admin,DB: Step 3: Create Connector
    Admin->>UI: Add GitHub connector
    UI->>API: POST /api/v1/admin/tenants/ID/connectors
    API->>DB: INSERT INTO connectors
    DB->>API: Connector created
    API->>UI: Connector ready

    Note over Claude,ExtAPI: Step 4: Use MCP Tools
    Claude->>API: WebSocket connect /api/v1/acme-corp/connectors/ID/mcp
    API->>DB: Load tenant, connector, oauth
    DB->>API: Return configuration
    API->>Claude: WebSocket connected

    Claude->>API: call_tool("github_list_repositories")
    API->>Connector: execute_tool()
    Connector->>DB: Get OAuth credential
    DB->>Connector: access_token
    Connector->>ExtAPI: GET /user/repos Bearer TOKEN
    ExtAPI->>Connector: Repository list JSON
    Connector->>API: Format response
    API->>Claude: MCP TextContent response
```

## Technology Stack

```mermaid
graph LR
    subgraph "Frontend Stack"
        REACT[React 18]
        TS[TypeScript]
        VITE[Vite]
        RR[React Router]
        TAILWIND[Tailwind CSS]

        REACT --> TS
        REACT --> VITE
        REACT --> RR
        REACT --> TAILWIND
    end

    subgraph "Backend Stack"
        FASTAPI[FastAPI]
        PYTHON[Python 3.11+]
        SA[SQLAlchemy 2.0]
        PYDANTIC[Pydantic v2]
        MCP_SDK[MCP SDK]
        HTTPX[HTTPX]

        FASTAPI --> PYTHON
        FASTAPI --> SA
        FASTAPI --> PYDANTIC
        FASTAPI --> MCP_SDK
        FASTAPI --> HTTPX
    end

    subgraph "Database Stack"
        POSTGRES[PostgreSQL 15]
        SUPABASE[Supabase]
        ASYNCPG[AsyncPG]

        POSTGRES -.alternative.-> SUPABASE
        SA --> ASYNCPG
        ASYNCPG --> POSTGRES
        ASYNCPG --> SUPABASE
    end

    subgraph "DevOps Stack"
        DOCKER[Docker]
        DC[Docker Compose]
        K8S[Kubernetes]
        HELM[Helm Charts]

        DOCKER --> DC
        K8S --> HELM
    end

    subgraph "Testing Stack"
        PYTEST[Pytest]
        PYTEST_ASYNC[pytest-asyncio]
        MOCK[unittest.mock]

        PYTEST --> PYTEST_ASYNC
        PYTEST --> MOCK
    end

    style REACT fill:#61dafb
    style FASTAPI fill:#009688
    style POSTGRES fill:#336791
    style DOCKER fill:#2496ed
    style PYTEST fill:#0a9edc
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Ingress"
            ING["Ingress Controller
NGINX/Traefik"]
        end

        subgraph "Application Pods"
            FE1["Frontend Pod 1
React:3001"]
            FE2["Frontend Pod 2
React:3001"]
            BE1["Backend Pod 1
FastAPI:8000"]
            BE2["Backend Pod 2
FastAPI:8000"]
            BE3["Backend Pod 3
FastAPI:8000"]
        end

        subgraph "Services"
            FE_SVC["Frontend Service
ClusterIP"]
            BE_SVC["Backend Service
ClusterIP"]
        end

        subgraph "Configuration"
            CM["ConfigMap
- API URLs
- Feature flags"]
            SEC["Secrets
- OAuth credentials
- DB password
- SECRET_KEY"]
        end
    end

    subgraph "Managed Services"
        DB_MANAGED["Managed PostgreSQL
or Supabase"]
        REDIS["Redis Cache
Optional"]
    end

    USERS[Users/Clients]

    USERS -->|HTTPS| ING
    ING -->|Route /| FE_SVC
    ING -->|Route /api| BE_SVC

    FE_SVC --> FE1
    FE_SVC --> FE2

    BE_SVC --> BE1
    BE_SVC --> BE2
    BE_SVC --> BE3

    BE1 --> CM
    BE1 --> SEC
    BE2 --> CM
    BE2 --> SEC
    BE3 --> CM
    BE3 --> SEC

    BE1 -->|Connection Pool| DB_MANAGED
    BE2 -->|Connection Pool| DB_MANAGED
    BE3 -->|Connection Pool| DB_MANAGED

    BE1 -.->|Optional| REDIS
    BE2 -.->|Optional| REDIS
    BE3 -.->|Optional| REDIS

    style ING fill:#ff9800
    style FE_SVC fill:#4caf50
    style BE_SVC fill:#4caf50
    style DB_MANAGED fill:#2196f3
    style REDIS fill:#f44336
```

## Key Design Patterns

### 1. **Plugin Architecture**
- Connectors are dynamically registered via decorators
- All connectors inherit from `BaseConnector` abstract class
- Registry pattern for connector discovery and instantiation

### 2. **Multi-Tenancy**
- Path-based tenant isolation (`/api/v1/{tenant_slug}`)
- Foreign key relationships ensure data segregation
- Each tenant has isolated OAuth credentials and connectors

### 3. **Repository Pattern**
- SQLAlchemy ORM abstracts database operations
- Async database access via `asyncpg`
- Connection pooling for performance

### 4. **Factory Pattern**
- `MCPServer` factory creates server instances per request
- Connector factory creates connector instances from registry

### 5. **Decorator Pattern**
- `@register_connector` decorator for plugin registration
- FastAPI route decorators for API endpoints

### 6. **Adapter Pattern**
- Connectors adapt external APIs to MCP protocol
- Each connector translates between MCP tools and provider-specific APIs

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Network Security"
            HTTPS[HTTPS/TLS]
            CORS[CORS Middleware]
        end

        subgraph "Authentication"
            OAUTH[OAuth 2.0 Flow]
            JWT["JWT Tokens
Optional"]
            STATE["State Token
CSRF Protection"]
        end

        subgraph "Authorization"
            TENANT_ISO["Tenant Isolation
Path-based"]
            FK_CHECK["Foreign Key
Constraints"]
        end

        subgraph "Data Protection"
            TOKEN_ENC["Token Encryption
at rest"]
            SECRET_MGR["Secret Management
K8s Secrets/Vault"]
            ENV_VAR[Environment Variables]
        end

        subgraph "Input Validation"
            PYDANTIC[Pydantic Models]
            SQL_PREVENT["SQLAlchemy ORM
SQL Injection Prevention"]
        end
    end

    HTTPS --> OAUTH
    CORS --> OAUTH
    OAUTH --> STATE
    STATE --> TENANT_ISO
    TENANT_ISO --> FK_CHECK
    FK_CHECK --> TOKEN_ENC
    TOKEN_ENC --> SECRET_MGR
    SECRET_MGR --> ENV_VAR
    ENV_VAR --> PYDANTIC
    PYDANTIC --> SQL_PREVENT
```

## Performance Considerations

### Connection Pooling
- SQLAlchemy async engine with connection pool (default: 5-20 connections)
- HTTPX async client for external API calls
- WebSocket connection reuse for MCP protocol

### Caching Strategy (Optional)
- Redis for session data
- In-memory connector registry (singleton)
- OAuth token caching with TTL

### Scalability
- Horizontal scaling via Kubernetes replicas
- Stateless backend design (WebSocket state in transport layer)
- Database connection pooling
- Async I/O throughout the stack

## Monitoring & Observability

```mermaid
graph LR
    subgraph "Application"
        APP[SageMCP Backend]
    end

    subgraph "Metrics & Logs"
        METRICS["Prometheus Metrics
- Request count
- Response time
- Error rate"]
        LOGS["Structured Logs
- JSON format
- Log levels"]
        TRACES["Distributed Tracing
Optional: Jaeger/OTEL"]
    end

    subgraph "Monitoring"
        PROM[Prometheus]
        GRAF[Grafana]
        ALERT[AlertManager]
    end

    APP --> METRICS
    APP --> LOGS
    APP --> TRACES

    METRICS --> PROM
    PROM --> GRAF
    PROM --> ALERT

    LOGS --> GRAF
```

---

## Summary

SageMCP is a **multi-tenant MCP server platform** that enables Claude Desktop to connect to external services via OAuth-authenticated connectors. The architecture is:

- **Modular**: Plugin-based connector system
- **Scalable**: Async I/O, connection pooling, horizontal scaling
- **Secure**: OAuth 2.0, tenant isolation, token encryption
- **Extensible**: Easy to add new connectors following the base pattern
- **Production-ready**: Docker/Kubernetes deployment, comprehensive testing

The platform successfully bridges Claude Desktop's MCP protocol with external service APIs (GitHub, Slack, Jira, Google Docs, Notion, Zoom) through a unified, tenant-aware interface.
