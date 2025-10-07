"""Main FastAPI application for Sage MCP."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as api_router
from .config import get_settings
from .database.connection import db_manager
from .database.migrations import create_tables

# Import connectors to register them
from .connectors import github  # noqa


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    settings = get_settings()
    
    # Initialize database
    db_manager.initialize()
    
    # Create tables if they don't exist
    await create_tables()
    
    print(f"🚀 {settings.app_name} v{settings.app_version} started")
    print(f"🌍 Environment: {settings.environment}")
    print(f"🗄️  Database: Connected")
    
    yield
    
    # Shutdown
    await db_manager.close()
    print("👋 Sage MCP shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Multi-tenant MCP (Model Context Protocol) server platform",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "description": "Multi-tenant MCP (Model Context Protocol) server platform",
            "environment": settings.environment,
            "endpoints": {
                "health": "/health",
                "docs": "/docs" if settings.debug else "Disabled in production",
                "api": {
                    "admin": "/api/v1/admin",
                    "oauth": "/api/v1/oauth", 
                    "mcp": "/api/v1/{tenant_slug}/mcp"
                }
            },
            "usage": {
                "create_tenant": "POST /api/v1/admin/tenants",
                "list_tenants": "GET /api/v1/admin/tenants",
                "mcp_websocket": "WS /api/v1/{tenant_slug}/mcp",
                "mcp_http": "POST /api/v1/{tenant_slug}/mcp",
                "mcp_info": "GET /api/v1/{tenant_slug}/mcp/info"
            }
        }

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment
        }
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )