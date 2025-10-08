"""Database migration utilities."""

from sqlalchemy.ext.asyncio import AsyncEngine

from ..models.base import Base
from .connection import db_manager


async def create_tables(engine: AsyncEngine = None):
    """Create all database tables."""
    if engine is None:
        if not db_manager.engine:
            db_manager.initialize()
        engine = db_manager.engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(engine: AsyncEngine = None):
    """Drop all database tables."""
    if engine is None:
        if not db_manager.engine:
            db_manager.initialize()
        engine = db_manager.engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
