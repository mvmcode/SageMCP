"""Connector tool state model for managing individual tool enable/disable."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from .connector import Connector


class ConnectorToolState(Base):
    """Tool state configuration for connectors.

    Stores the enabled/disabled state for individual tools within a connector.
    Each tool from the connector's get_tools() method can have its own state.
    """

    __tablename__ = "connector_tool_states"
    __table_args__ = (
        UniqueConstraint('connector_id', 'tool_name', name='uq_connector_tool'),
    )

    # Foreign key to connector
    connector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connectors.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Tool name (e.g., "github_list_repositories")
    tool_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # Whether this tool is enabled
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    connector: Mapped["Connector"] = relationship("Connector", back_populates="tool_states")

    def __repr__(self) -> str:
        return f"<ConnectorToolState(connector_id='{self.connector_id}', tool='{self.tool_name}', enabled={self.is_enabled})>"
