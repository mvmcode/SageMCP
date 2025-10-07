import axios from 'axios'
import { Tenant, TenantCreate, Connector, ConnectorCreate, MCPServerInfo, OAuthProvider, OAuthCredential, OAuthConfig } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth (when implemented)
api.interceptors.request.use((config) => {
  // Add auth token when available
  // const token = localStorage.getItem('auth_token')
  // if (token) {
  //   config.headers.Authorization = `Bearer ${token}`
  // }
  
  // Debug logging for OAuth config requests
  if (config.url?.includes('/oauth/') && config.method === 'post') {
    console.log('OAuth Config API Request:', {
      method: config.method,
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
      data: config.data,
      headers: config.headers
    })
  }
  
  // Debug all POST requests to see if they're going to wrong endpoint
  if (config.method === 'post') {
    console.log('POST Request Debug:', {
      method: config.method,
      url: config.url,
      fullURL: `${config.baseURL}${config.url}`
    })
  }
  
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Debug logging for OAuth config errors
    if (error.config?.url?.includes('/oauth/') && error.config?.method === 'post') {
      console.error('OAuth Config API Error:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        url: error.config.url,
        method: error.config.method,
        fullURL: `${error.config.baseURL}${error.config.url}`,
        requestData: error.config.data,
        responseData: error.response?.data
      })
    }
    
    // Debug all 405 errors
    if (error.response?.status === 405) {
      console.error('405 Method Not Allowed Error:', {
        status: error.response.status,
        statusText: error.response.statusText,
        url: error.config?.url,
        method: error.config?.method,
        fullURL: `${error.config?.baseURL}${error.config?.url}`,
        allowedMethods: error.response.headers?.allow
      })
    }
    
    if (error.response?.status === 401) {
      // Handle unauthorized access
      // window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const tenantsApi = {
  list: () => api.get<Tenant[]>('/admin/tenants'),
  get: (slug: string) => api.get<Tenant>(`/admin/tenants/${slug}`),
  create: (data: TenantCreate) => api.post<Tenant>('/admin/tenants', data),
  update: (slug: string, data: TenantCreate) => 
    api.put<Tenant>(`/admin/tenants/${slug}`, data),
  delete: (slug: string) => api.delete(`/admin/tenants/${slug}`),
}

export const connectorsApi = {
  list: (tenantSlug: string) => 
    api.get<Connector[]>(`/admin/tenants/${tenantSlug}/connectors`),
  get: (tenantSlug: string, connectorId: string) => 
    api.get<Connector>(`/admin/tenants/${tenantSlug}/connectors/${connectorId}`),
  create: (tenantSlug: string, data: ConnectorCreate) => 
    api.post<Connector>(`/admin/tenants/${tenantSlug}/connectors`, data),
  update: (tenantSlug: string, connectorId: string, data: ConnectorCreate) => 
    api.put<Connector>(`/admin/tenants/${tenantSlug}/connectors/${connectorId}`, data),
  delete: (tenantSlug: string, connectorId: string) => 
    api.delete(`/admin/tenants/${tenantSlug}/connectors/${connectorId}`),
  toggle: (tenantSlug: string, connectorId: string) => 
    api.patch<Connector>(`/admin/tenants/${tenantSlug}/connectors/${connectorId}/toggle`),
}

export const mcpApi = {
  getInfo: (tenantSlug: string) => 
    api.get<MCPServerInfo>(`/${tenantSlug}/mcp/info`),
  sendMessage: (tenantSlug: string, message: any) => 
    api.post(`/${tenantSlug}/mcp`, message),
}

export const oauthApi = {
  listProviders: () => api.get<OAuthProvider[]>('/oauth/providers'),
  listCredentials: (tenantSlug: string) => 
    api.get<OAuthCredential[]>(`/oauth/${tenantSlug}/auth`),
  initiateOAuth: (tenantSlug: string, provider: string) => {
    // This should open a new window for OAuth flow
    const url = `/api/v1/oauth/${tenantSlug}/auth/${provider}`
    console.log('Opening OAuth popup for:', provider, 'URL:', url)
    const popup = window.open(url, 'oauth', 'width=600,height=700,scrollbars=yes,resizable=yes')
    console.log('OAuth popup opened:', popup)
    return popup
  },
  revokeCredential: (tenantSlug: string, provider: string) => 
    api.delete(`/oauth/${tenantSlug}/auth/${provider}`),
  // OAuth Configuration Management
  listConfigs: (tenantSlug: string) => 
    api.get<OAuthConfig[]>(`/oauth/${tenantSlug}/config`),
  createConfig: (tenantSlug: string, config: { provider: string; client_id: string; client_secret: string }) => 
    api.post<OAuthConfig>(`/oauth/${tenantSlug}/config`, config),
  deleteConfig: (tenantSlug: string, provider: string) => 
    api.delete(`/oauth/${tenantSlug}/config/${provider}`),
}

export const healthApi = {
  check: () => api.get('/health'),
}

// Legacy function exports for tests
export const fetchTenants = () => tenantsApi.list()
export const createTenant = (data: TenantCreate) => tenantsApi.create(data)
export const fetchConnectors = (tenantSlug: string) => connectorsApi.list(tenantSlug)
export const createConnector = (tenantSlug: string, data: ConnectorCreate) => connectorsApi.create(tenantSlug, data)

export default api