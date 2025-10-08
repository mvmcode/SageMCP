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
        # Convert postgres:// to postgresql+asyncpg://
        database_url = str(self.settings.database_url)
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)

        self.engine = create_async_engine(
            database_url,
            poolclass=NullPool if self.settings.environment == "test" else None,
            echo=self.settings.debug,
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
