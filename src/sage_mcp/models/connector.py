"""Connector model for managing tenant-specific connector configurations."""

import enum
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .tenant import Tenant


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


class Connector(Base):
    """Connector configuration for tenants."""
    
    __tablename__ = "connectors"
    
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
    configuration: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="connectors")
    
    def __repr__(self) -> str:
        return f"<Connector(type='{self.connector_type.value}', tenant_id='{self.tenant_id}')>"