"""Database migration utilities."""

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text

from ..models.base import Base
from ..models.connector_tool_state import ConnectorToolState
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


async def upgrade_add_connector_tool_states(engine: AsyncEngine = None):
    """Migration: Add connector_tool_states table for tool-level enable/disable.

    This migration adds a new table to store individual tool states within connectors.
    Safe to run on existing databases - checks if table exists first.
    """
    if engine is None:
        if not db_manager.engine:
            db_manager.initialize()
        engine = db_manager.engine

    async with engine.begin() as conn:
        # Check if table already exists
        result = await conn.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = 'connector_tool_states')"
        ))
        table_exists = result.scalar()

        if not table_exists:
            # Create only the connector_tool_states table
            await conn.run_sync(
                lambda sync_conn: ConnectorToolState.__table__.create(
                    sync_conn, checkfirst=True
                )
            )
            print("✓ Created connector_tool_states table")
        else:
            print("✓ connector_tool_states table already exists")
