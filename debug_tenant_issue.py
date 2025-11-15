#!/usr/bin/env python3
"""Debug script to check tenant existence and CLI connectivity."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import httpx


async def check_api_connection(base_url: str = "http://localhost:8000"):
    """Check if API is accessible."""
    print(f"🔍 Checking API connection to {base_url}...")

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print(f"✅ API is accessible at {base_url}")
                return True
            else:
                print(f"⚠️  API returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False


async def list_existing_tenants(base_url: str = "http://localhost:8000"):
    """List all existing tenants."""
    print(f"\n🔍 Fetching existing tenants from {base_url}...")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{base_url}/api/v1/admin/tenants")

            if response.status_code == 200:
                tenants = response.json()
                if tenants:
                    print(f"\n📋 Found {len(tenants)} existing tenant(s):\n")
                    for tenant in tenants:
                        print(f"  • Slug: {tenant['slug']}")
                        print(f"    Name: {tenant['name']}")
                        print(f"    Active: {tenant.get('is_active', 'N/A')}")
                        print(f"    Created: {tenant.get('created_at', 'N/A')}")
                        print()

                    # Check if test-tenant exists
                    test_tenant = next((t for t in tenants if t['slug'] == 'test-tenant'), None)
                    if test_tenant:
                        print("❗ FOUND: Tenant 'test-tenant' already exists!")
                        print(f"   Created at: {test_tenant.get('created_at')}")
                        print(f"\n💡 Solution: Either delete it or use a different slug")
                        print(f"   To delete: DELETE {base_url}/api/v1/admin/tenants/test-tenant")
                        return True
                else:
                    print("✅ No existing tenants found")
                    return False
            else:
                print(f"⚠️  Failed to list tenants: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return None

    except Exception as e:
        print(f"❌ Error fetching tenants: {e}")
        return None


async def test_tenant_creation(base_url: str = "http://localhost:8000", slug: str = "test-tenant-2"):
    """Try creating a test tenant."""
    print(f"\n🔍 Testing tenant creation with slug '{slug}'...")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            data = {
                "slug": slug,
                "name": f"Test Tenant {slug}",
                "description": "Created by debug script"
            }

            response = await client.post(
                f"{base_url}/api/v1/admin/tenants",
                json=data
            )

            if response.status_code == 201:
                tenant = response.json()
                print(f"✅ Successfully created tenant!")
                print(f"   Slug: {tenant['slug']}")
                print(f"   ID: {tenant['id']}")
                return True
            elif response.status_code == 400:
                error = response.json()
                if "already exists" in error.get('detail', '').lower():
                    print(f"⚠️  Tenant '{slug}' already exists")
                    return False
                else:
                    print(f"❌ Bad request: {error.get('detail', response.text)}")
                    return False
            else:
                print(f"❌ Failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Error creating tenant: {e}")
        return False


async def delete_tenant(base_url: str = "http://localhost:8000", slug: str = "test-tenant"):
    """Delete a tenant."""
    print(f"\n🗑️  Attempting to delete tenant '{slug}'...")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.delete(f"{base_url}/api/v1/admin/tenants/{slug}")

            if response.status_code in [200, 204]:
                print(f"✅ Tenant '{slug}' deleted successfully")
                return True
            elif response.status_code == 404:
                print(f"⚠️  Tenant '{slug}' not found")
                return False
            else:
                print(f"❌ Failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Error deleting tenant: {e}")
        return False


async def main():
    """Run all debugging checks."""
    print("=" * 70)
    print("SageMCP Tenant Creation Debug Tool")
    print("=" * 70)

    base_url = os.getenv("SAGEMCP_URL", "http://localhost:8000")

    # Check API connection
    connected = await check_api_connection(base_url)
    if not connected:
        print("\n❌ Cannot proceed - API is not accessible")
        print(f"\n💡 Make sure the SageMCP backend is running:")
        print("   cd /home/user/SageMCP")
        print("   make up")
        return 1

    # List existing tenants
    await list_existing_tenants(base_url)

    # Offer to delete test-tenant
    print("\n" + "=" * 70)
    print("Options:")
    print("=" * 70)
    print("\n1. Delete 'test-tenant' (if it exists)")
    print("2. Try creating 'test-tenant-2' instead")
    print("3. Skip and exit")

    choice = input("\nEnter choice (1/2/3): ").strip()

    if choice == "1":
        await delete_tenant(base_url, "test-tenant")
        print("\n✅ You can now try creating 'test-tenant' again from the CLI")
    elif choice == "2":
        await test_tenant_creation(base_url, "test-tenant-2")
    else:
        print("\n✅ Exiting without changes")

    print("\n" + "=" * 70)
    print("Debug session complete")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
