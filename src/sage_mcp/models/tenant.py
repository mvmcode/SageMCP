"""Tenant model for multi-tenancy support."""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .oauth_credential import OAuthCredential
    from .oauth_config import OAuthConfig
    from .connector import Connector


class Tenant(Base):
    """Tenant model for multi-tenant isolation."""

    __tablename__ = "tenants"

    # Tenant identifier (used in URL path)
    slug: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    # Display name for the tenant
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Optional description
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tenant status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Contact information
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Configuration settings (JSON)
    settings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    oauth_credentials: Mapped[List["OAuthCredential"]] = relationship(
        "OAuthCredential",
        back_populates="tenant",
        cascade="all, delete-orphan"
    )

    oauth_configs: Mapped[List["OAuthConfig"]] = relationship(
        "OAuthConfig",
        back_populates="tenant",
        cascade="all, delete-orphan"
    )

    connectors: Mapped[List["Connector"]] = relationship(
        "Connector",
        back_populates="tenant",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Tenant(slug='{self.slug}', name='{self.name}')>"
