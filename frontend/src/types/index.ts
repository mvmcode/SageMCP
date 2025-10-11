export interface Tenant {
  id: string
  slug: string
  name: string
  description?: string
  is_active: boolean
  contact_email?: string
  created_at?: string
  updated_at?: string
}

export interface TenantCreate {
  slug: string
  name: string
  description?: string
  contact_email?: string
}

export interface Connector {
  id: string
  connector_type: ConnectorType
  name: string
  description?: string
  is_enabled: boolean
  configuration?: string
  tenant_id: string
  created_at?: string
  updated_at?: string
}

export interface ConnectorCreate {
  connector_type: ConnectorType
  name: string
  description?: string
  configuration?: string
}

export enum ConnectorType {
  GITHUB = 'github',
  GITLAB = 'gitlab',
  SLACK = 'slack',
  DISCORD = 'discord',
  CUSTOM = 'custom'
}

export interface MCPServerInfo {
  tenant: string
  connector_id: string
  connector_name: string
  connector_type: string
  server_name: string
  server_version: string
  protocol_version: string
  capabilities: {
    tools?: { listChanged?: boolean }
    resources?: { subscribe?: boolean; listChanged?: boolean }
    prompts?: { listChanged?: boolean }
  }
}

export interface APIResponse<T> {
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface OAuthProvider {
  id: string
  name: string
  scopes: string[]
  configured: boolean
  auth_url: string
}

export interface OAuthCredential {
  id: string
  provider: string
  provider_user_id: string
  provider_username?: string
  token_type: string
  scopes?: string
  is_active: boolean
  expires_at?: string
  created_at: string
}

export interface OAuthConfig {
  id: string
  provider: string
  client_id: string
  is_active: boolean
  created_at: string
}

export interface OAuthConfigCreate {
  provider: string
  client_id: string
  client_secret: string
}