"""Connector model for managing tenant-specific connector configurations."""

import enum
import json
import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text, TypeDecorator, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class JSONType(TypeDecorator):
    """JSON type that handles serialization for SQLite and PostgreSQL."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Optional[Dict[str, Any]], dialect) -> Optional[str]:
        """Convert dict to JSON string before storing."""
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value: Optional[str], dialect) -> Optional[Dict[str, Any]]:
        """Convert JSON string back to dict after loading."""
        if value is not None:
            return json.loads(value)
        return None


if TYPE_CHECKING:
    from .tenant import Tenant
    from .connector_tool_state import ConnectorToolState


class ConnectorType(enum.Enum):
    """Supported connector types."""

    GITHUB = "github"
    GITLAB = "gitlab"
    GOOGLE_DOCS = "google_docs"
    NOTION = "notion"
    CONFLUENCE = "confluence"
    JIRA = "jira"
    LINEAR = "linear"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"
    ZOOM = "zoom"


class Connector(Base):
    """Connector configuration for tenants."""

    __tablename__ = "connectors"
    __table_args__ = (
        UniqueConstraint('tenant_id', 'connector_type', name='uq_tenant_connector_type'),
    )

    # Foreign key to tenant
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Connector type
    connector_type: Mapped[ConnectorType] = mapped_column(
        Enum(ConnectorType),
        nullable=False,
        index=True
    )

    # Display name for this connector instance
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Optional description
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Whether this connector is enabled
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Connector-specific configuration (JSON)
    configuration: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="connectors")
    tool_states: Mapped[list["ConnectorToolState"]] = relationship(
        "ConnectorToolState",
        back_populates="connector",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Connector(type='{self.connector_type.value}', tenant_id='{self.tenant_id}')>"
