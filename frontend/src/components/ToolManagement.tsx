import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import {
  Power,
  PowerOff,
  Search,
  RefreshCw,
  CheckSquare,
  Square,
  AlertTriangle
} from 'lucide-react'
import { toolsApi } from '@/utils/api'
import { cn } from '@/utils/cn'

interface ToolManagementProps {
  tenantSlug: string
  connectorId: string
  connectorName: string
}

export default function ToolManagement({ tenantSlug, connectorId, connectorName }: ToolManagementProps) {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')

  // Fetch tools list
  const { data: toolsData, isLoading, error } = useQuery({
    queryKey: ['tools', tenantSlug, connectorId],
    queryFn: async () => {
      const response = await toolsApi.list(tenantSlug, connectorId)
      return response.data
    }
  })

  // Toggle single tool mutation
  const toggleToolMutation = useMutation({
    mutationFn: async ({ toolName, isEnabled }: { toolName: string; isEnabled: boolean }) => {
      await toolsApi.toggle(tenantSlug, connectorId, toolName, isEnabled)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tools', tenantSlug, connectorId] })
      toast.success('Tool updated successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update tool')
    }
  })

  // Enable all tools mutation
  const enableAllMutation = useMutation({
    mutationFn: async () => {
      await toolsApi.enableAll(tenantSlug, connectorId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tools', tenantSlug, connectorId] })
      toast.success('All tools enabled')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to enable all tools')
    }
  })

  // Disable all tools mutation
  const disableAllMutation = useMutation({
    mutationFn: async () => {
      await toolsApi.disableAll(tenantSlug, connectorId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tools', tenantSlug, connectorId] })
      toast.success('All tools disabled')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to disable all tools')
    }
  })

  // Sync tools mutation
  const syncToolsMutation = useMutation({
    mutationFn: async () => {
      const response = await toolsApi.sync(tenantSlug, connectorId)
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tools', tenantSlug, connectorId] })
      if (data.added.length > 0 || data.removed.length > 0) {
        toast.success(data.summary)
      } else {
        toast.success('Tools are already in sync')
      }
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to sync tools')
    }
  })

  // Filter tools based on search query
  const filteredTools = useMemo(() => {
    if (!toolsData?.tools) return []
    if (!searchQuery) return toolsData.tools

    const query = searchQuery.toLowerCase()
    return toolsData.tools.filter(tool =>
      tool.tool_name.toLowerCase().includes(query) ||
      tool.description?.toLowerCase().includes(query)
    )
  }, [toolsData?.tools, searchQuery])

  // Check if tool is dangerous (has delete/create in name)
  const isDangerousTool = (toolName: string) => {
    const dangerous = ['delete', 'create', 'remove']
    return dangerous.some(keyword => toolName.toLowerCase().includes(keyword))
  }

  const handleToggleTool = (toolName: string, currentState: boolean) => {
    toggleToolMutation.mutate({ toolName, isEnabled: !currentState })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Failed to load tools</p>
      </div>
    )
  }

  if (!toolsData) {
    return null
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Tools for {connectorName}
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            {toolsData.summary.enabled} of {toolsData.summary.total} tools enabled
          </p>
        </div>
      </div>

      {/* Bulk Actions */}
      <div className="flex flex-wrap items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
        <button
          onClick={() => enableAllMutation.mutate()}
          disabled={enableAllMutation.isPending}
          className={cn(
            "flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md transition-colors",
            "bg-green-100 text-green-700 hover:bg-green-200",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        >
          <Power className="h-4 w-4" />
          Enable All
        </button>

        <button
          onClick={() => disableAllMutation.mutate()}
          disabled={disableAllMutation.isPending}
          className={cn(
            "flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md transition-colors",
            "bg-red-100 text-red-700 hover:bg-red-200",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        >
          <PowerOff className="h-4 w-4" />
          Disable All
        </button>

        <button
          onClick={() => syncToolsMutation.mutate()}
          disabled={syncToolsMutation.isPending}
          className={cn(
            "flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md transition-colors",
            "bg-blue-100 text-blue-700 hover:bg-blue-200",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        >
          <RefreshCw className={cn("h-4 w-4", syncToolsMutation.isPending && "animate-spin")} />
          Sync Tools
        </button>

        {/* Search */}
        <div className="ml-auto flex items-center gap-2 flex-1 max-w-xs">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search tools..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Tools List */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <div className="divide-y divide-gray-200 max-h-[500px] overflow-y-auto">
          {filteredTools.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              {searchQuery ? 'No tools match your search' : 'No tools available'}
            </div>
          ) : (
            filteredTools.map((tool) => (
              <div
                key={tool.tool_name}
                className={cn(
                  "p-4 hover:bg-gray-50 transition-colors",
                  !tool.is_enabled && "opacity-60"
                )}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className={cn(
                        "text-sm font-medium truncate",
                        tool.is_enabled ? "text-gray-900" : "text-gray-500"
                      )}>
                        {tool.tool_name}
                      </h4>
                      {isDangerousTool(tool.tool_name) && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          <AlertTriangle className="h-3 w-3" />
                          Dangerous
                        </span>
                      )}
                    </div>
                    {tool.description && (
                      <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                        {tool.description}
                      </p>
                    )}
                  </div>

                  {/* Toggle Button */}
                  <button
                    onClick={() => handleToggleTool(tool.tool_name, tool.is_enabled)}
                    disabled={toggleToolMutation.isPending}
                    className={cn(
                      "flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md transition-colors",
                      "border",
                      tool.is_enabled
                        ? "bg-green-50 border-green-300 text-green-700 hover:bg-green-100"
                        : "bg-gray-50 border-gray-300 text-gray-600 hover:bg-gray-100",
                      "disabled:opacity-50 disabled:cursor-not-allowed"
                    )}
                    title={tool.is_enabled ? 'Disable tool' : 'Enable tool'}
                  >
                    {tool.is_enabled ? (
                      <>
                        <CheckSquare className="h-4 w-4" />
                        Enabled
                      </>
                    ) : (
                      <>
                        <Square className="h-4 w-4" />
                        Disabled
                      </>
                    )}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
