# Fix: "test-tenant slug already exists" Error

## Problem

When running `sagemcp tenant create --slug test-tenant --name "Test Tenant"`, you get an error saying the slug already exists.

## Root Cause

A tenant with slug "test-tenant" already exists in your database. This likely happened from:
1. A previous CLI test
2. API testing
3. Frontend testing
4. Docker volume persisting data between restarts

## Solutions

### Option 1: Delete the Existing Tenant (Recommended)

Make sure the SageMCP backend is running:
```bash
cd /home/user/SageMCP
make up
# or
docker-compose up -d
```

Then delete the tenant using curl:
```bash
# Run the delete script
chmod +x delete_test_tenant.sh
./delete_test_tenant.sh

# OR manually:
curl -X DELETE http://localhost:8000/api/v1/admin/tenants/test-tenant
```

Now you can create it again:
```bash
sagemcp tenant create --slug test-tenant --name "Test Tenant"
```

### Option 2: Use a Different Slug

Just use a different slug name:
```bash
sagemcp tenant create --slug my-tenant --name "My Tenant"
# or
sagemcp tenant create --slug demo-tenant --name "Demo Tenant"
# or
sagemcp tenant create --slug dev-tenant --name "Dev Tenant"
```

### Option 3: Reset the Database (Nuclear Option)

⚠️ **WARNING**: This deletes ALL tenants, connectors, and OAuth credentials!

```bash
cd /home/user/SageMCP

# Stop services
docker-compose down

# Remove the database volume
docker volume rm sagemcp_postgres_data

# Restart (will create fresh database)
docker-compose up -d
```

## Verify Solution

### 1. List all existing tenants:
```bash
# Using curl
curl http://localhost:8000/api/v1/admin/tenants | jq

# Using CLI (once installed)
sagemcp tenant list
```

### 2. Check if test-tenant exists:
```bash
curl http://localhost:8000/api/v1/admin/tenants/test-tenant
```

Expected responses:
- **404**: Tenant doesn't exist (good!)
- **200**: Tenant exists (need to delete it)

### 3. Try creating again:
```bash
sagemcp tenant create --slug test-tenant --name "Test Tenant"
```

Expected output:
```
✓ Created tenant: test-tenant

┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Slug         ┃ Name        ┃ Active ┃ Created       ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ test-tenant  │ Test Tenant │ ✓      │ 2025-11-15    │
└──────────────┴─────────────┴────────┴───────────────┘
```

## Debugging Commands

### Check if backend is running:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Check Docker containers:
```bash
docker-compose ps
# Should show 'app', 'postgres', and 'frontend' as 'Up'
```

### Check Docker logs:
```bash
docker-compose logs app
```

### Direct database access (via Adminer):
1. Open http://localhost:8080
2. Login with:
   - System: PostgreSQL
   - Server: postgres
   - Username: sage_mcp
   - Password: password
   - Database: sage_mcp
3. Browse `tenants` table to see all existing tenants

## Prevention

To avoid this issue in the future:

### 1. Use unique slugs for testing:
```bash
# Add a timestamp or random suffix
sagemcp tenant create --slug "test-$(date +%s)" --name "Test Tenant"
```

### 2. Clean up after testing:
```bash
# Delete test tenant after you're done
sagemcp tenant delete test-tenant --force
```

### 3. Use the `demo` tenant for persistent testing:
```bash
# Create once, reuse forever
sagemcp tenant create --slug demo --name "Demo Tenant"
```

## Still Having Issues?

### Issue: "Cannot connect to API"
**Solution**: Make sure the backend is running:
```bash
cd /home/user/SageMCP
docker-compose up -d app postgres
docker-compose logs -f app
```

### Issue: "Module not found: sage_mcp"
**Solution**: Install the CLI:
```bash
cd /home/user/SageMCP
pip install -e ".[cli]"
```

### Issue: "Tenant deleted but still getting error"
**Solution**: The database might be caching. Restart the backend:
```bash
docker-compose restart app
```

### Issue: "Want to see all my data"
**Solution**: Use Adminer database viewer:
```bash
# Access at http://localhost:8080
# Or use CLI
sagemcp tenant list
sagemcp connector list <tenant-slug>
sagemcp oauth list <tenant-slug>
```

## Quick Reference

```bash
# THE FIX (most common):
curl -X DELETE http://localhost:8000/api/v1/admin/tenants/test-tenant
sagemcp tenant create --slug test-tenant --name "Test Tenant"

# OR: Just use a different slug
sagemcp tenant create --slug my-company --name "My Company"
```

---

**Summary**: The "test-tenant" slug exists in your database. Either delete it first, or use a different slug name!
