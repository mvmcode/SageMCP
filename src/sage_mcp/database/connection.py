"""Database connection and session management."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from ..config import get_settings


class DatabaseManager:
    """Database connection manager."""

    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.session_factory = None

    def initialize(self):
        """Initialize database engine and session factory."""
        # Get the appropriate database URL based on provider
        # For Supabase, always use the generated URL regardless of DATABASE_URL env var
        if self.settings.database_provider == "supabase":
            database_url = self.settings.get_database_url()
        else:
            database_url = self.settings.database_url
        
        # Convert postgres:// to postgresql+asyncpg://
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)

        # Add connection arguments for Supabase compatibility
        connect_args = {}
        if self.settings.database_provider == "supabase":
            # SSL configuration for Supabase connection pooler
            connect_args.update({
                "ssl": "require",
                "server_settings": {
                    "application_name": "sagemcp"
                }
            })

        self.engine = create_async_engine(
            database_url,
            poolclass=NullPool if self.settings.environment == "test" else None,
            echo=self.settings.debug,
            connect_args=connect_args,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    if not db_manager.session_factory:
        db_manager.initialize()

    async with db_manager.session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager to get database session."""
    async for session in get_db_session():
        yield session
