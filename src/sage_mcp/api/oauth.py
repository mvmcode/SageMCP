"""OAuth API routes for connector authentication."""

import os
import secrets
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, field_validator
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_db_session
from ..models.oauth_credential import OAuthCredential
from ..models.oauth_config import OAuthConfig
from ..models.tenant import Tenant

router = APIRouter()

# OAuth provider configurations
OAUTH_PROVIDERS = {
    "github": {
        "name": "GitHub",
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "user_url": "https://api.github.com/user",
        "scopes": ["repo", "user:email", "read:org"],
        "client_id": (
            os.getenv("GITHUB_CLIENT_ID")
            if os.getenv("GITHUB_CLIENT_ID")
            and os.getenv("GITHUB_CLIENT_ID") != "your-github-client-id"
            else None
        ),
        "client_secret": (
            os.getenv("GITHUB_CLIENT_SECRET")
            if os.getenv("GITHUB_CLIENT_SECRET")
            and os.getenv("GITHUB_CLIENT_SECRET") != "your-github-client-secret"
            else None
        ),
    },
    "gitlab": {
        "name": "GitLab",
        "auth_url": "https://gitlab.com/oauth/authorize",
        "token_url": "https://gitlab.com/oauth/token",
        "user_url": "https://gitlab.com/api/v4/user",
        "scopes": ["api", "read_user"],
        "client_id": (
            os.getenv("GITLAB_CLIENT_ID")
            if os.getenv("GITLAB_CLIENT_ID")
            and os.getenv("GITLAB_CLIENT_ID") != "your-gitlab-client-id"
            else None
        ),
        "client_secret": (
            os.getenv("GITLAB_CLIENT_SECRET")
            if os.getenv("GITLAB_CLIENT_SECRET")
            and os.getenv("GITLAB_CLIENT_SECRET") != "your-gitlab-client-secret"
            else None
        ),
    },
    "google": {
        "name": "Google",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "user_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scopes": [
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email"
        ],
        "client_id": (
            os.getenv("GOOGLE_CLIENT_ID")
            if os.getenv("GOOGLE_CLIENT_ID")
            and os.getenv("GOOGLE_CLIENT_ID") != "your-google-client-id"
            else None
        ),
        "client_secret": (
            os.getenv("GOOGLE_CLIENT_SECRET")
            if os.getenv("GOOGLE_CLIENT_SECRET")
            and os.getenv("GOOGLE_CLIENT_SECRET") != "your-google-client-secret"
            else None
        ),
    }
}


class OAuthCredentialResponse(BaseModel):
    id: str
    provider: str
    provider_user_id: str
    provider_username: Optional[str]
    token_type: str
    scopes: Optional[str]
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class OAuthConfigCreate(BaseModel):
    """Request model for creating OAuth configuration."""
    provider: str
    client_id: str
    client_secret: str


class OAuthConfigResponse(BaseModel):
    """Response model for OAuth configuration."""
    id: str
    provider: str
    client_id: str
    is_active: bool
    created_at: datetime

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


@router.get("/{tenant_slug}/auth/{provider}")
async def initiate_oauth(
    tenant_slug: str,
    provider: str,
    request: Request,
    session: AsyncSession = Depends(get_db_session)
):
    """Initiate OAuth flow for a provider."""
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider: {provider}"
        )

    # Verify tenant exists
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    provider_config = OAUTH_PROVIDERS[provider]

    # Check for tenant-specific OAuth configuration first
    tenant_config_result = await session.execute(
        select(OAuthConfig).where(
            OAuthConfig.tenant_id == tenant.id,
            OAuthConfig.provider == provider,
            OAuthConfig.is_active.is_(True)
        )
    )
    tenant_oauth_config = tenant_config_result.scalar_one_or_none()

    # Use tenant config if available, otherwise fall back to global config
    if tenant_oauth_config:
        client_id = tenant_oauth_config.client_id
        client_secret = tenant_oauth_config.client_secret
    else:
        client_id = provider_config["client_id"]
        client_secret = provider_config["client_secret"]

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500,
            detail=(
                f"OAuth not configured for {provider}. "
                "Please configure OAuth credentials for this tenant."
            )
        )

    # Generate state parameter for CSRF protection
    state = secrets.token_urlsafe(32)

    # Build redirect URI
    # For development, use localhost:3000 directly since we know the
    # frontend port. In production, this would come from environment
    # variables or proper proxy headers
    base_url_str = str(request.base_url)
    if 'localhost' in base_url_str and ':3000' not in base_url_str:
        # Development mode - frontend is on localhost:3000
        base_url = "http://localhost:3000"
    else:
        # Check for forwarded headers (for production)
        forwarded_host = request.headers.get('x-forwarded-host')
        forwarded_proto = request.headers.get('x-forwarded-proto', 'http')

        if forwarded_host:
            base_url = f"{forwarded_proto}://{forwarded_host}"
        else:
            # Fallback to request base URL
            base_url = str(request.base_url).rstrip('/')

    redirect_uri = (
        f"{base_url}/api/v1/oauth/{tenant_slug}/callback/{provider}"
    )
    print(f"DEBUG: Final redirect_uri = {redirect_uri}")

    # Build authorization URL
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(provider_config["scopes"]),
        "state": state,
        "response_type": "code"
    }

    auth_url = (
        f"{provider_config['auth_url']}?{urllib.parse.urlencode(params)}"
    )

    # Store state in session or cache (for now, we'll include it in the redirect)
    return RedirectResponse(url=auth_url)


@router.get("/{tenant_slug}/callback/{provider}")
async def oauth_callback(
    tenant_slug: str,
    provider: str,
    request: Request,
    session: AsyncSession = Depends(get_db_session)
):
    """Handle OAuth callback from provider."""
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider: {provider}"
        )

    # Verify tenant exists
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get query parameters
    params = dict(request.query_params)

    if "error" in params:
        error = params.get("error", "unknown")
        error_description = params.get(
            "error_description", "No description provided"
        )
        raise HTTPException(
            status_code=400,
            detail=(
                f"OAuth error from {provider}: {error} - "
                f"{error_description}"
            )
        )

    if "code" not in params:
        raise HTTPException(
            status_code=400,
            detail="Authorization code not provided"
        )

    auth_code = params["code"]
    provider_config = OAUTH_PROVIDERS[provider]

    # Check for tenant-specific OAuth configuration first
    tenant_config_result = await session.execute(
        select(OAuthConfig).where(
            OAuthConfig.tenant_id == tenant.id,
            OAuthConfig.provider == provider,
            OAuthConfig.is_active.is_(True)
        )
    )
    tenant_oauth_config = tenant_config_result.scalar_one_or_none()

    # Use tenant config if available, otherwise fall back to global config
    if tenant_oauth_config:
        client_id = tenant_oauth_config.client_id
        client_secret = tenant_oauth_config.client_secret
    else:
        client_id = provider_config["client_id"]
        client_secret = provider_config["client_secret"]

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500,
            detail=(
                f"OAuth not configured for {provider}. "
                "Please configure OAuth credentials for this tenant."
            )
        )

    # Build redirect URI (must match the one used in initiate_oauth)
    # For development, use localhost:3000 directly since we know the
    # frontend port. In production, this would come from environment
    # variables or proper proxy headers
    base_url_str = str(request.base_url)
    if 'localhost' in base_url_str and ':3000' not in base_url_str:
        # Development mode - frontend is on localhost:3000
        base_url = "http://localhost:3000"
    else:
        # Check for forwarded headers (for production)
        forwarded_host = request.headers.get('x-forwarded-host')
        forwarded_proto = request.headers.get('x-forwarded-proto', 'http')

        if forwarded_host:
            base_url = f"{forwarded_proto}://{forwarded_host}"
        else:
            # Fallback to request base URL
            base_url = str(request.base_url).rstrip('/')

    redirect_uri = (
        f"{base_url}/api/v1/oauth/{tenant_slug}/callback/{provider}"
    )

    # Exchange authorization code for access token
    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "redirect_uri": redirect_uri,
    }

    if provider == "google":
        token_data["grant_type"] = "authorization_code"

    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            provider_config["token_url"],
            data=token_data,
            headers=headers
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Failed to exchange authorization code: "
                    f"{token_response.text}"
                )
            )

        token_info = token_response.json()

    access_token = token_info.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received")

    # Get user information from provider
    user_headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            provider_config["user_url"],
            headers=user_headers
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Failed to get user info: {user_response.text}"
                )
            )

        user_info = user_response.json()

    # Extract user data based on provider
    if provider == "github":
        provider_user_id = str(user_info["id"])
        provider_username = user_info["login"]
    elif provider == "gitlab":
        provider_user_id = str(user_info["id"])
        provider_username = user_info["username"]
    elif provider == "google":
        provider_user_id = user_info["id"]
        provider_username = user_info.get("name", user_info.get("email"))
    else:
        provider_user_id = str(user_info.get("id", "unknown"))
        provider_username = user_info.get(
            "login", user_info.get("username", "unknown")
        )

    # Calculate expiration time
    expires_at = None
    if "expires_in" in token_info:
        expires_at = datetime.utcnow() + timedelta(
            seconds=int(token_info["expires_in"])
        )

    # Check if credential already exists for this tenant/provider/user
    existing_cred = await session.execute(
        select(OAuthCredential).where(
            OAuthCredential.tenant_id == tenant.id,
            OAuthCredential.provider == provider,
            OAuthCredential.provider_user_id == provider_user_id
        )
    )
    existing = existing_cred.scalar_one_or_none()

    if existing:
        # Update existing credential
        existing.access_token = access_token
        existing.refresh_token = token_info.get("refresh_token")
        existing.token_type = token_info.get("token_type", "bearer")
        existing.expires_at = expires_at
        existing.scopes = token_info.get("scope")
        existing.provider_data = str(user_info)
        existing.is_active = True
        existing.updated_at = datetime.utcnow()
    else:
        # Create new credential
        oauth_cred = OAuthCredential(
            tenant_id=tenant.id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_username=provider_username,
            access_token=access_token,
            refresh_token=token_info.get("refresh_token"),
            token_type=token_info.get("token_type", "bearer"),
            expires_at=expires_at,
            scopes=token_info.get("scope"),
            provider_data=str(user_info),
            is_active=True
        )
        session.add(oauth_cred)

    await session.commit()

    # Redirect to frontend with success message
    # Use same logic as redirect URI generation for consistency
    base_url_str = str(request.base_url)
    if 'localhost' in base_url_str and ':3000' not in base_url_str:
        # Development mode - frontend is on localhost:3000
        frontend_url = "http://localhost:3000"
    else:
        # Check for forwarded headers (for production)
        forwarded_host = request.headers.get('x-forwarded-host')
        forwarded_proto = request.headers.get('x-forwarded-proto', 'http')

        if forwarded_host:
            frontend_url = f"{forwarded_proto}://{forwarded_host}"
        else:
            # Fallback to request base URL, try to replace 8000 with 3000
            frontend_url = base_url_str.rstrip('/').replace(':8000', ':3000')

    success_url = (
        f"{frontend_url}/oauth/success?provider={provider}&"
        f"tenant={tenant_slug}"
    )
    print(f"DEBUG: OAuth success redirect URL = {success_url}")

    return RedirectResponse(url=success_url)


@router.delete("/{tenant_slug}/auth/{provider}")
async def revoke_oauth(
    tenant_slug: str,
    provider: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Revoke OAuth credentials for a provider."""
    # Verify tenant exists
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Delete OAuth credentials for this tenant and provider
    result = await session.execute(
        delete(OAuthCredential).where(
            OAuthCredential.tenant_id == tenant.id,
            OAuthCredential.provider == provider
        )
    )

    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No OAuth credentials found for {provider}"
        )

    return {
        "message": f"OAuth credentials revoked for {provider}",
        "tenant": tenant_slug,
        "provider": provider,
        "revoked_count": result.rowcount
    }


@router.get(
    "/{tenant_slug}/auth",
    response_model=List[OAuthCredentialResponse]
)
async def list_oauth_credentials(
    tenant_slug: str,
    session: AsyncSession = Depends(get_db_session)
):
    """List OAuth credentials for a tenant."""
    # Verify tenant exists
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get OAuth credentials for this tenant
    credentials_result = await session.execute(
        select(OAuthCredential).where(
            OAuthCredential.tenant_id == tenant.id
        )
    )
    credentials = credentials_result.scalars().all()

    return list(credentials)


@router.get("/providers")
async def list_oauth_providers():
    """List available OAuth providers and their configuration status."""
    providers = []
    for provider_id, config in OAUTH_PROVIDERS.items():
        providers.append({
            "id": provider_id,
            "name": config["name"],
            "scopes": config["scopes"],
            "configured": bool(config["client_id"] and config["client_secret"]),
            "auth_url": config["auth_url"]
        })

    return providers


@router.get("/{tenant_slug}/config")
async def list_oauth_configs(
    tenant_slug: str,
    session: AsyncSession = Depends(get_db_session)
):
    """List OAuth configurations for a tenant."""
    # Verify tenant exists
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get OAuth configurations
    configs_result = await session.execute(
        select(OAuthConfig).where(OAuthConfig.tenant_id == tenant.id)
    )
    configs = configs_result.scalars().all()

    return list(configs)


@router.post("/{tenant_slug}/config")
async def create_oauth_config(
    tenant_slug: str,
    config_data: OAuthConfigCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create or update OAuth configuration for a tenant."""
    # Verify tenant exists
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Validate provider
    if config_data.provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider: {config_data.provider}"
        )

    # Check if configuration already exists
    existing_config = await session.execute(
        select(OAuthConfig).where(
            OAuthConfig.tenant_id == tenant.id,
            OAuthConfig.provider == config_data.provider
        )
    )
    existing = existing_config.scalar_one_or_none()

    if existing:
        # Update existing configuration
        existing.client_id = config_data.client_id
        existing.client_secret = config_data.client_secret
        existing.is_active = True
        await session.commit()
        await session.refresh(existing)
        return existing
    else:
        # Create new configuration
        new_config = OAuthConfig(
            tenant_id=tenant.id,
            provider=config_data.provider,
            client_id=config_data.client_id,
            client_secret=config_data.client_secret
        )
        session.add(new_config)
        await session.commit()
        await session.refresh(new_config)
        return new_config


@router.delete("/{tenant_slug}/config/{provider}")
async def delete_oauth_config(
    tenant_slug: str,
    provider: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Delete OAuth configuration for a tenant and provider."""
    # Verify tenant exists
    tenant_result = await session.execute(
        select(Tenant).where(Tenant.slug == tenant_slug)
    )
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Find and delete configuration
    config_result = await session.execute(
        select(OAuthConfig).where(
            OAuthConfig.tenant_id == tenant.id,
            OAuthConfig.provider == provider
        )
    )
    config = config_result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=404,
            detail="OAuth configuration not found"
        )

    await session.delete(config)
    await session.commit()

    return {
        "message": (
            f"OAuth configuration for {provider} deleted successfully"
        )
    }
