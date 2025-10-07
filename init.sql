-- Database initialization script for Sage MCP
-- This script creates extensions and any initial data needed

-- Create UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create any additional extensions as needed
-- CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Insert initial data if needed
-- (Tables will be created automatically by SQLAlchemy)

-- Example: Create a default tenant for development
-- This will be inserted via the application API, not here
-- INSERT INTO tenants (id, slug, name, description, is_active, contact_email, created_at, updated_at)
-- VALUES (
--     uuid_generate_v4(),
--     'demo',
--     'Demo Tenant',
--     'Default tenant for development and testing',
--     true,
--     'demo@example.com',
--     NOW(),
--     NOW()
-- ) ON CONFLICT (slug) DO NOTHING;