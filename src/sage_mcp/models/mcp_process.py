"""MCP Process model for tracking external MCP server processes."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from .connector import Connector
    from .tenant import Tenant


class ProcessStatus(enum.Enum):
    """Status of an external MCP process."""

    STARTING = "starting"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    RESTARTING = "restarting"


class MCPProcess(Base):
    """Tracking information for external MCP server processes."""

    __tablename__ = "mcp_processes"

    # Foreign keys
    connector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connectors.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Process information
    pid: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    runtime_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Status tracking
    status: Mapped[ProcessStatus] = mapped_column(
        Enum(
            ProcessStatus,
            name="processstatus",
            create_constraint=False,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=ProcessStatus.STARTING
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )

    last_health_check: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Error information
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Restart tracking
    restart_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Resource limits
    cpu_limit_millicores: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    memory_limit_mb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    connector: Mapped["Connector"] = relationship("Connector")
    tenant: Mapped["Tenant"] = relationship("Tenant")

    def __repr__(self) -> str:
        return (
            f"<MCPProcess(connector_id='{self.connector_id}', "
            f"status='{self.status.value}', pid={self.pid})>"
        )
