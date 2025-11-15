#!/bin/bash
# Script to delete the test-tenant from SageMCP database

SAGEMCP_URL="${SAGEMCP_URL:-http://localhost:8000}"

echo "🗑️  Deleting test-tenant from $SAGEMCP_URL..."
echo ""

# Delete test-tenant
response=$(curl -s -w "\n%{http_code}" -X DELETE "${SAGEMCP_URL}/api/v1/admin/tenants/test-tenant")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 204 ]; then
    echo "✅ Success! Tenant 'test-tenant' has been deleted"
    echo ""
    echo "You can now create it again:"
    echo "  sagemcp tenant create --slug test-tenant --name 'Test Tenant'"
elif [ "$http_code" -eq 404 ]; then
    echo "⚠️  Tenant 'test-tenant' not found (already deleted or never existed)"
else
    echo "❌ Failed to delete tenant (HTTP $http_code)"
    echo "Response: $body"
fi

echo ""
echo "To list all tenants:"
echo "  curl ${SAGEMCP_URL}/api/v1/admin/tenants | jq"
