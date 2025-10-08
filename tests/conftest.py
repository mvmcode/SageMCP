"""Test configuration and fixtures."""

import pytest
import asyncio
import os
from unittest.mock import AsyncMock, Mock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from sage_mcp.main import app
from sage_mcp.database.connection import get_db_context
from sage_mcp.models.base import Base
from sage_mcp.models.tenant import Tenant
from sage_mcp.models.connector import Connector, ConnectorType
from sage_mcp.models.oauth_credential import OAuthCredential


# Test database URL - use DATABASE_URL from env or fallback to SQLite
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")

# Create test engine
if TEST_DATABASE_URL.startswith("sqlite"):
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL or other databases
    test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create tables before tests and drop them after."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop all tables after all tests
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up database between tests."""
    yield
    # Clean up all data after each test for PostgreSQL
    if not TEST_DATABASE_URL.startswith("sqlite"):
        session = TestingSessionLocal()
        try:
            # Delete in correct order to avoid foreign key constraints
            session.query(OAuthCredential).delete()
            session.query(Connector).delete()
            session.query(Tenant).delete()
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()


@pytest.fixture
def db_session():
    """Create a test database session."""
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture
def client(db_session) -> TestClient:
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db_context] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
async def sample_tenant(db_session) -> Tenant:
    """Create a sample tenant for testing."""
    tenant = Tenant(
        slug="test-tenant",
        name="Test Tenant",
        description="A test tenant",
        contact_email="test@example.com",
        is_active=True
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
async def sample_connector(db_session, sample_tenant) -> Connector:
    """Create a sample connector for testing."""
    connector = Connector(
        name="Test GitHub Connector",
        description="GitHub integration for testing",
        connector_type=ConnectorType.GITHUB,
        tenant_id=sample_tenant.id,
        is_enabled=True,
        configuration={}
    )
    db_session.add(connector)
    db_session.commit()
    db_session.refresh(connector)
    return connector


@pytest.fixture
async def sample_oauth_credential(db_session, sample_tenant) -> OAuthCredential:
    """Create a sample OAuth credential for testing."""
    credential = OAuthCredential(
        tenant_id=sample_tenant.id,
        provider="github",
        provider_user_id="123456",
        provider_username="testuser",
        access_token="test_access_token",
        token_type="Bearer",
        scopes="repo,user:email,read:org",
        is_active=True
    )
    db_session.add(credential)
    db_session.commit()
    db_session.refresh(credential)
    return credential


@pytest.fixture
def mock_github_api():
    """Mock GitHub API responses."""
    mock = Mock()
    mock.json.return_value = {
        "login": "testuser",
        "id": 123456,
        "type": "User",
        "name": "Test User",
        "public_repos": 5,
        "total_private_repos": 2
    }
    mock.headers = {
        "X-OAuth-Scopes": "repo, user:email, read:org",
        "X-Accepted-OAuth-Scopes": ""
    }
    return mock


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for testing."""
    mock = AsyncMock()
    mock.initialize.return_value = True
    mock.connectors = []
    return mock
