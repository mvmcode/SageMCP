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
  Copy,
  Info,
  X,
  Wrench,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import toast from 'react-hot-toast'
import { tenantsApi, connectorsApi } from '@/utils/api'
import { cn } from '@/utils/cn'
import ConnectorModal from '@/components/ConnectorModal'
import ExternalMCPModal from '@/components/ExternalMCPModal'
import ProcessStatus from '@/components/ProcessStatus'
import OAuthManager from '@/components/OAuthManager'
import ToolManagement from '@/components/ToolManagement'

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

const ConnectionInfoModal = ({
  isOpen,
  onClose,
  connector,
  tenantSlug
}: {
  isOpen: boolean
  onClose: () => void
  connector: any
  tenantSlug: string
}) => {
  const mcpWebSocketUrl = `ws://${window.location.host}/${tenantSlug}/connectors/${connector.id}/mcp`
  const mcpHttpUrl = `http://${window.location.host}/api/v1/${tenantSlug}/connectors/${connector.id}/mcp`
  const isLocalhost = window.location.hostname === 'localhost'

  const copyUrl = (url: string, type: string) => {
    navigator.clipboard.writeText(url)
    toast.success(`${type} URL copied to clipboard`)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={onClose} />
        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Connection Information</h3>
              <p className="text-sm text-gray-600">{connector.name}</p>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4 space-y-4">
            {/* WebSocket URL */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                WebSocket URL
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={mcpWebSocketUrl}
                  readOnly
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 font-mono text-sm"
                />
                <button
                  onClick={() => copyUrl(mcpWebSocketUrl, 'WebSocket')}
                  className="btn-secondary"
                >
                  <Copy className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* HTTP URL */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                HTTP URL
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={mcpHttpUrl}
                  readOnly
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 font-mono text-sm"
                />
                <button
                  onClick={() => copyUrl(mcpHttpUrl, 'HTTP')}
                  className="btn-secondary"
                >
                  <Copy className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Claude Desktop Setup Instructions */}
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="text-sm font-semibold text-blue-900 mb-2">
                Claude Desktop Setup
              </h4>
              {isLocalhost ? (
                <div className="text-sm text-blue-800 space-y-2">
                  <p><strong>Note:</strong> You're running on localhost. For Claude Desktop to connect, you need to expose your server via HTTPS:</p>
                  <ol className="list-decimal list-inside space-y-1 ml-2">
                    <li>Install ngrok: <code className="bg-blue-100 px-1 rounded">brew install ngrok</code></li>
                    <li>Run: <code className="bg-blue-100 px-1 rounded">ngrok http 3000</code></li>
                    <li>Copy the HTTPS URL from ngrok (e.g., <code className="bg-blue-100 px-1 rounded">https://abc123.ngrok.io</code>)</li>
                    <li>Install mcp-remote if needed: <code className="bg-blue-100 px-1 rounded">npm install -g mcp-remote</code></li>
                    <li>Add to Claude Desktop config:</li>
                  </ol>
                  <pre className="bg-blue-100 p-3 rounded mt-2 overflow-x-auto text-xs">
{`{
  "mcpServers": {
    "${connector.name}": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://your-ngrok-url.ngrok.io/api/v1/${tenantSlug}/connectors/${connector.id}/mcp"
      ]
    }
  }
}`}
                  </pre>
                  <p className="mt-2 text-xs text-blue-700">
                    <strong>Note:</strong> If npx is not found, add an <code className="bg-blue-100 px-1 rounded">"env"</code> section with your Node.js PATH. Find it with: <code className="bg-blue-100 px-1 rounded">echo $PATH</code>
                  </p>
                  <pre className="bg-blue-100 p-2 rounded text-xs mt-1">
{`"env": {
  "PATH": "/path/to/node/bin:/usr/local/bin:/usr/bin:/bin"
}`}
                  </pre>
                </div>
              ) : (
                <div className="text-sm text-blue-800 space-y-2">
                  <p>Add this configuration to your Claude Desktop config file:</p>
                  <ol className="list-decimal list-inside space-y-1 ml-2 mb-2">
                    <li>Install mcp-remote if needed: <code className="bg-blue-100 px-1 rounded">npm install -g mcp-remote</code></li>
                    <li>Add the configuration below:</li>
                  </ol>
                  <pre className="bg-blue-100 p-3 rounded mt-2 overflow-x-auto text-xs">
{`{
  "mcpServers": {
    "${connector.name}": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "${mcpHttpUrl}"
      ]
    }
  }
}`}
                  </pre>
                  <p className="mt-2 text-xs text-blue-700">
                    <strong>Note:</strong> If npx is not found, add an <code className="bg-blue-100 px-1 rounded">"env"</code> section with your Node.js PATH. Find it with: <code className="bg-blue-100 px-1 rounded">echo $PATH</code>
                  </p>
                  <pre className="bg-blue-100 p-2 rounded text-xs mt-1">
{`"env": {
  "PATH": "/path/to/node/bin:/usr/local/bin:/usr/bin:/bin"
}`}
                  </pre>
                  <p className="mt-2 text-xs">
                    Config file location:
                    <br />
                    • macOS: <code className="bg-blue-100 px-1 rounded">~/Library/Application Support/Claude/claude_desktop_config.json</code>
                    <br />
                    • Windows: <code className="bg-blue-100 px-1 rounded">%APPDATA%\Claude\claude_desktop_config.json</code>
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
            <button onClick={onClose} className="btn-primary">
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

const ConnectorCard = ({ connector, tenantSlug }: { connector: any, tenantSlug: string }) => {
  const [showMenu, setShowMenu] = useState(false)
  const [showConnectionInfo, setShowConnectionInfo] = useState(false)
  const [showTools, setShowTools] = useState(false)
  const queryClient = useQueryClient()


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
    <>
      <ConnectionInfoModal
        isOpen={showConnectionInfo}
        onClose={() => setShowConnectionInfo(false)}
        connector={connector}
        tenantSlug={tenantSlug}
      />

      <div className="card">
        <div className="card-content">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">{connector.name}</h4>
              <p className="text-sm text-gray-600 capitalize">{connector.connector_type}</p>
              {connector.description && (
                <p className="text-sm text-gray-500 mt-1">{connector.description}</p>
              )}

              {/* Process Status for External MCP Servers */}
              <div className="mt-3">
                <ProcessStatus
                  connectorId={connector.id}
                  runtimeType={connector.runtime_type}
                  showControls={true}
                />
              </div>

              {/* Action Buttons */}
              <div className="mt-3 flex items-center gap-3">
                <button
                  onClick={() => setShowConnectionInfo(true)}
                  className="inline-flex items-center text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  <Info className="h-4 w-4 mr-1" />
                  Connection Info
                </button>
                <button
                  onClick={() => setShowTools(!showTools)}
                  className="inline-flex items-center text-sm text-purple-600 hover:text-purple-700 font-medium"
                >
                  <Wrench className="h-4 w-4 mr-1" />
                  Manage Tools
                  {showTools ? (
                    <ChevronUp className="h-4 w-4 ml-1" />
                  ) : (
                    <ChevronDown className="h-4 w-4 ml-1" />
                  )}
                </button>
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

        {/* Expandable Tool Management Section */}
        {showTools && (
          <div className="border-t border-gray-200 px-4 py-4 bg-gray-50">
            <ToolManagement
              tenantSlug={tenantSlug}
              connectorId={connector.id}
              connectorName={connector.name}
            />
          </div>
        )}
      </div>
    </>
  )
}

export default function TenantDetail() {
  const { slug } = useParams<{ slug: string }>()
  const [activeTab, setActiveTab] = useState('overview')
  const [showConnectorModal, setShowConnectorModal] = useState(false)
  const [showExternalMCPModal, setShowExternalMCPModal] = useState(false)

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
            <div className="flex items-center space-x-2">
              <button
                onClick={() => {
                  console.log('Add Connector button clicked (tenant detail)!')
                  setShowConnectorModal(true)
                }}
                className="btn-secondary"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Native Connector
              </button>
              <button
                onClick={() => {
                  console.log('Add External MCP Server button clicked!')
                  setShowExternalMCPModal(true)
                }}
                className="btn-primary"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add External MCP Server
              </button>
            </div>
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
              <div className="flex items-center justify-center space-x-3">
                <button
                  onClick={() => {
                    console.log('Add Connector button clicked (tenant detail empty state)!')
                    setShowConnectorModal(true)
                  }}
                  className="btn-secondary"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Native Connector
                </button>
                <button
                  onClick={() => {
                    console.log('Add External MCP Server button clicked (empty state)!')
                    setShowExternalMCPModal(true)
                  }}
                  className="btn-primary"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add External MCP Server
                </button>
              </div>
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

      <ExternalMCPModal
        isOpen={showExternalMCPModal}
        onClose={() => setShowExternalMCPModal(false)}
        preselectedTenant={tenant?.slug}
      />
    </div>
  )
}