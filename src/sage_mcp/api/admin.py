"""Admin API routes for tenant and connector management."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_db_session
from ..models.connector import Connector, ConnectorType
from ..models.tenant import Tenant

router = APIRouter()


class TenantCreate(BaseModel):
    slug: str
    name: str
    description: Optional[str] = None
    contact_email: Optional[str] = None


class TenantResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    description: Optional[str]
    is_active: bool
    contact_email: Optional[str]

    class Config:
        from_attributes = True


class ConnectorCreate(BaseModel):
    connector_type: ConnectorType
    name: str
    description: Optional[str] = None
    configuration: Optional[str] = None


class ConnectorResponse(BaseModel):
    id: UUID
    connector_type: ConnectorType
    name: str
    description: Optional[str]
    is_enabled: bool
    configuration: Optional[str]

    class Config:
        from_attributes = True


@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new tenant."""
    # Check if tenant slug already exists
    from sqlalchemy import select

    existing = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_data.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Tenant slug already exists")

    # Create new tenant
    tenant = Tenant(
        slug=tenant_data.slug,
        name=tenant_data.name,
        description=tenant_data.description,
        contact_email=tenant_data.contact_email
    )

    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)

    return tenant


@router.get("/tenants", response_model=List[TenantResponse])
async def list_tenants(
    session: AsyncSession = Depends(get_db_session)
):
    """List all tenants."""
    from sqlalchemy import select

    result = await session.execute(select(Tenant))
    tenants = result.scalars().all()

    return list(tenants)


@router.get("/tenants/{tenant_slug}", response_model=TenantResponse)
async def get_tenant(
    tenant_slug: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get a specific tenant."""
    from sqlalchemy import select

    result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return tenant


@router.post("/tenants/{tenant_slug}/connectors", response_model=ConnectorResponse)
async def create_connector(
    tenant_slug: str,
    connector_data: ConnectorCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new connector for a tenant."""
    from sqlalchemy import select

    # Get tenant
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Create connector
    connector = Connector(
        tenant_id=tenant.id,
        connector_type=connector_data.connector_type,
        name=connector_data.name,
        description=connector_data.description,
        configuration=connector_data.configuration
    )

    session.add(connector)
    await session.commit()
    await session.refresh(connector)

    return connector


@router.get("/tenants/{tenant_slug}/connectors", response_model=List[ConnectorResponse])
async def list_connectors(
    tenant_slug: str,
    session: AsyncSession = Depends(get_db_session)
):
    """List connectors for a tenant."""
    from sqlalchemy import select

    # Get tenant
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get connectors
    connector_result = await session.execute(
        select(Connector).where(Connector.tenant_id == tenant.id)
    )
    connectors = connector_result.scalars().all()

    return list(connectors)


@router.delete("/tenants/{tenant_slug}")
async def delete_tenant(
    tenant_slug: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a tenant and all its connectors."""
    from sqlalchemy import select, delete

    # Get tenant
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Delete all connectors for this tenant first
    await session.execute(
        delete(Connector).where(Connector.tenant_id == tenant.id)
    )

    # Delete the tenant
    await session.execute(
        delete(Tenant).where(Tenant.id == tenant.id)
    )

    await session.commit()

    return {
        "message": (
            f"Tenant '{tenant_slug}' and all its connectors "
            "have been deleted"
        )
    }


@router.put("/tenants/{tenant_slug}", response_model=TenantResponse)
async def update_tenant(
    tenant_slug: str,
    tenant_data: TenantCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update a tenant."""
    from sqlalchemy import select, update

    # Check if tenant exists
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Update tenant
    await session.execute(
        update(Tenant)
        .where(Tenant.slug == tenant_slug)
        .values(
            name=tenant_data.name,
            description=tenant_data.description,
            contact_email=tenant_data.contact_email
        )
    )

    await session.commit()
    await session.refresh(tenant)

    return tenant


@router.get(
    "/tenants/{tenant_slug}/connectors/{connector_id}",
    response_model=ConnectorResponse
)
async def get_connector(
    tenant_slug: str,
    connector_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get a specific connector."""
    from sqlalchemy import select

    # Get tenant
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get connector
    connector_result = await session.execute(
        select(Connector).where(
            Connector.id == connector_id,
            Connector.tenant_id == tenant.id
        )
    )
    connector = connector_result.scalar_one_or_none()

    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    return connector


@router.put(
    "/tenants/{tenant_slug}/connectors/{connector_id}",
    response_model=ConnectorResponse
)
async def update_connector(
    tenant_slug: str,
    connector_id: str,
    connector_data: ConnectorCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update a connector."""
    from sqlalchemy import select, update

    # Get tenant
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get connector
    connector_result = await session.execute(
        select(Connector).where(
            Connector.id == connector_id,
            Connector.tenant_id == tenant.id
        )
    )
    connector = connector_result.scalar_one_or_none()

    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    # Update connector
    await session.execute(
        update(Connector)
        .where(Connector.id == connector_id)
        .values(
            connector_type=connector_data.connector_type,
            name=connector_data.name,
            description=connector_data.description,
            configuration=connector_data.configuration
        )
    )

    await session.commit()
    await session.refresh(connector)

    return connector


@router.delete("/tenants/{tenant_slug}/connectors/{connector_id}")
async def delete_connector(
    tenant_slug: str,
    connector_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a connector."""
    from sqlalchemy import select, delete

    # Get tenant
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get connector
    connector_result = await session.execute(
        select(Connector).where(
            Connector.id == connector_id,
            Connector.tenant_id == tenant.id
        )
    )
    connector = connector_result.scalar_one_or_none()

    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    # Delete connector
    await session.execute(
        delete(Connector).where(Connector.id == connector_id)
    )

    await session.commit()

    return {
        "message": f"Connector '{connector.name}' has been deleted"
    }


@router.patch(
    "/tenants/{tenant_slug}/connectors/{connector_id}/toggle",
    response_model=ConnectorResponse
)
async def toggle_connector(
    tenant_slug: str,
    connector_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Toggle connector enabled/disabled status."""
    from sqlalchemy import select, update

    # Get tenant
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get connector
    connector_result = await session.execute(
        select(Connector).where(
            Connector.id == connector_id,
            Connector.tenant_id == tenant.id
        )
    )
    connector = connector_result.scalar_one_or_none()

    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    # Toggle enabled status
    new_status = not connector.is_enabled
    await session.execute(
        update(Connector)
        .where(Connector.id == connector_id)
        .values(is_enabled=new_status)
    )

    await session.commit()
    await session.refresh(connector)

    return connector
