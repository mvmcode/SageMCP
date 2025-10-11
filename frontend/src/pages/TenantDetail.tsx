import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  ArrowLeft, 
  Building2, 
  Plug, 
  Activity, 
  Settings,
  Plus,
  MoreVertical,
  Edit,
  Trash2,
  ToggleLeft,
  ToggleRight,
  Copy
} from 'lucide-react'
import toast from 'react-hot-toast'
import { tenantsApi, connectorsApi } from '@/utils/api'
import { cn } from '@/utils/cn'
import ConnectorModal from '@/components/ConnectorModal'
import OAuthManager from '@/components/OAuthManager'

const TabButton = ({ 
  isActive, 
  onClick, 
  children 
}: { 
  isActive: boolean
  onClick: () => void
  children: React.ReactNode 
}) => (
  <button
    onClick={onClick}
    className={cn(
      'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
      isActive
        ? 'bg-primary-100 text-primary-700'
        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
    )}
  >
    {children}
  </button>
)

const ConnectorCard = ({ connector, tenantSlug }: { connector: any, tenantSlug: string }) => {
  const [showMenu, setShowMenu] = useState(false)
  const queryClient = useQueryClient()

  // Connector-specific URLs
  const mcpWebSocketUrl = `ws://${window.location.host}/${tenantSlug}/connectors/${connector.id}/mcp`
  const mcpHttpUrl = `http://${window.location.host}/api/v1/${tenantSlug}/connectors/${connector.id}/mcp`
  const isLocalhost = window.location.hostname === 'localhost'

  const copyUrl = (url: string, type: string) => {
    navigator.clipboard.writeText(url)
    toast.success(`MCP ${type} URL copied to clipboard`)
  }


  const deleteMutation = useMutation({
    mutationFn: () => connectorsApi.delete(tenantSlug, connector.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connectors', tenantSlug] })
      toast.success('Connector deleted successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete connector')
    }
  })

  const toggleMutation = useMutation({
    mutationFn: () => connectorsApi.toggle(tenantSlug, connector.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connectors', tenantSlug] })
      toast.success(connector.is_enabled ? 'Connector disabled' : 'Connector enabled')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to toggle connector')
    }
  })

  const handleDelete = () => {
    if (confirm(`Are you sure you want to delete connector "${connector.name}"?`)) {
      deleteMutation.mutate()
    }
    setShowMenu(false)
  }

  return (
    <div className="card">
      <div className="card-content">
        <div className="flex items-start justify-between">
          <div>
            <h4 className="font-medium text-gray-900">{connector.name}</h4>
            <p className="text-sm text-gray-600 capitalize">{connector.connector_type}</p>
            {connector.description && (
              <p className="text-sm text-gray-500 mt-1">{connector.description}</p>
            )}
            
            {/* MCP Server URLs */}
            <div className="mt-2 p-2 bg-gray-50 rounded border">
              <p className="text-xs font-medium text-gray-700 mb-2">MCP Server URLs:</p>
              
              {/* WebSocket URL */}
              <div className="mb-2">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-gray-600 mb-1">WebSocket:</p>
                    <p className="text-xs font-mono text-gray-600 truncate">{mcpWebSocketUrl}</p>
                  </div>
                  <button
                    onClick={() => copyUrl(mcpWebSocketUrl, 'WebSocket')}
                    className="ml-2 p-1 hover:bg-gray-200 rounded"
                    title="Copy WebSocket URL"
                  >
                    <Copy className="h-3 w-3 text-gray-500" />
                  </button>
                </div>
              </div>

              {/* HTTP URL */}
              <div className="mb-2">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-gray-600 mb-1">HTTP:</p>
                    <p className="text-xs font-mono text-gray-600 truncate">{mcpHttpUrl}</p>
                  </div>
                  <button
                    onClick={() => copyUrl(mcpHttpUrl, 'HTTP')}
                    className="ml-2 p-1 hover:bg-gray-200 rounded"
                    title="Copy HTTP URL"
                  >
                    <Copy className="h-3 w-3 text-gray-500" />
                  </button>
                </div>
              </div>

              {isLocalhost && (
                <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded">
                  <p className="text-xs text-blue-700">
                    <strong>For Claude:</strong> Use the HTTP URL with ngrok for HTTPS:
                    <br />
                    1. Run: <code className="bg-blue-100 px-1 rounded">ngrok http 3000</code>
                    <br />
                    2. Use: <code className="bg-blue-100 px-1 rounded">https://your-ngrok-url.ngrok.io/api/v1/{tenantSlug}/mcp</code>
                  </p>
                </div>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className={cn(
              'status-badge',
              connector.is_enabled ? 'status-active' : 'status-inactive'
            )}>
              {connector.is_enabled ? 'Enabled' : 'Disabled'}
            </span>
            
            <button 
              onClick={() => toggleMutation.mutate()}
              disabled={toggleMutation.isPending}
              className="p-1 hover:bg-gray-100 rounded disabled:opacity-50"
            >
              {connector.is_enabled ? (
                <ToggleRight className="h-5 w-5 text-success-600" />
              ) : (
                <ToggleLeft className="h-5 w-5 text-gray-400" />
              )}
            </button>
            
            <div className="relative">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <MoreVertical className="h-4 w-4 text-gray-400" />
              </button>
              
              {showMenu && (
                <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10">
                  <button 
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </button>
                  <button 
                    onClick={handleDelete}
                    disabled={deleteMutation.isPending}
                    className="flex items-center w-full px-4 py-2 text-sm text-error-600 hover:bg-error-50 disabled:opacity-50"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function TenantDetail() {
  const { slug } = useParams<{ slug: string }>()
  const [activeTab, setActiveTab] = useState('overview')
  const [showConnectorModal, setShowConnectorModal] = useState(false)

  const { data: tenant, isLoading: tenantLoading } = useQuery({
    queryKey: ['tenant', slug],
    queryFn: () => tenantsApi.get(slug!).then(res => res.data),
    enabled: !!slug
  })

  const { data: connectors = [] } = useQuery({
    queryKey: ['connectors', slug],
    queryFn: () => connectorsApi.list(slug!).then(res => res.data),
    enabled: !!slug
  })

  if (tenantLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <div className="h-8 w-8 bg-gray-200 rounded animate-pulse"></div>
          <div className="h-6 w-48 bg-gray-200 rounded animate-pulse"></div>
        </div>
        <div className="h-4 w-96 bg-gray-200 rounded animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="card-content">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!tenant) {
    return (
      <div className="text-center py-12">
        <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Tenant not found</h3>
        <p className="text-gray-600 mb-4">The tenant you're looking for doesn't exist.</p>
        <Link to="/tenants" className="btn-primary">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Tenants
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/tenants"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-gray-600" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-gray-900">{tenant.name}</h1>
              <span className={cn(
                'status-badge',
                tenant.is_active ? 'status-active' : 'status-inactive'
              )}>
                {tenant.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <p className="text-gray-600 font-mono">{tenant.slug}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button className="btn-secondary">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </button>
          <Link to={`/mcp-test?tenant=${tenant.slug}`} className="btn-primary">
            <Activity className="h-4 w-4 mr-2" />
            Test MCP
          </Link>
        </div>
      </div>

      {/* Description */}
      {tenant.description && (
        <div className="card">
          <div className="card-content">
            <p className="text-gray-700">{tenant.description}</p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex space-x-2">
        <TabButton
          isActive={activeTab === 'overview'}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </TabButton>
        <TabButton
          isActive={activeTab === 'connectors'}
          onClick={() => setActiveTab('connectors')}
        >
          Connectors ({connectors.length})
        </TabButton>
        <TabButton
          isActive={activeTab === 'oauth'}
          onClick={() => setActiveTab('oauth')}
        >
          OAuth Settings
        </TabButton>
        <TabButton
          isActive={activeTab === 'activity'}
          onClick={() => setActiveTab('activity')}
        >
          Activity
        </TabButton>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Stats */}
          <div className="card">
            <div className="card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Connectors</p>
                  <p className="text-2xl font-bold text-gray-900">{connectors.length}</p>
                </div>
                <Plug className="h-8 w-8 text-primary-600" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Connectors</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {connectors.filter(c => c.is_enabled).length}
                  </p>
                </div>
                <Activity className="h-8 w-8 text-success-600" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Connector Types</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {new Set(connectors.map(c => c.connector_type)).size}
                  </p>
                </div>
                <Building2 className="h-8 w-8 text-primary-600" />
              </div>
            </div>
          </div>

          {/* Contact Info */}
          {tenant.contact_email && (
            <div className="md:col-span-3">
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold text-gray-900">Contact Information</h3>
                </div>
                <div className="card-content">
                  <p className="text-sm font-medium text-gray-600">Email</p>
                  <p className="text-gray-900">{tenant.contact_email}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'connectors' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Connectors</h3>
            <button 
              onClick={() => {
                console.log('Add Connector button clicked (tenant detail)!')
                setShowConnectorModal(true)
              }}
              className="btn-primary"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Connector
            </button>
          </div>

          {connectors.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {connectors.map((connector) => (
                <ConnectorCard 
                  key={connector.id} 
                  connector={connector} 
                  tenantSlug={slug!} 
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Plug className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No connectors configured</h3>
              <p className="text-gray-600 mb-4">Add your first connector to get started</p>
              <button 
                onClick={() => {
                  console.log('Add Connector button clicked (tenant detail empty state)!')
                  setShowConnectorModal(true)
                }}
                className="btn-primary"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Connector
              </button>
            </div>
          )}
        </div>
      )}

      {activeTab === 'oauth' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">OAuth Configuration</h3>
              <p className="text-sm text-gray-600">Configure OAuth providers for this tenant to enable connector authentication</p>
            </div>
          </div>
          
          <OAuthManager tenantSlug={slug!} />
        </div>
      )}

      {activeTab === 'activity' && (
        <div className="card">
          <div className="card-content">
            <div className="text-center py-12">
              <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Activity log coming soon</h3>
              <p className="text-gray-600">Track all events and changes for this tenant</p>
            </div>
          </div>
        </div>
      )}

      <ConnectorModal
        isOpen={showConnectorModal}
        onClose={() => setShowConnectorModal(false)}
        preselectedTenant={tenant?.slug}
      />
    </div>
  )
}