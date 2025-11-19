import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { processApi } from '@/utils/api'
import { ProcessStatus as ProcessStatusEnum, ConnectorRuntimeType } from '@/types'
import { Activity, AlertCircle, CheckCircle, Clock, RotateCw, Square, XCircle } from 'lucide-react'
import { cn } from '@/utils/cn'
import toast from 'react-hot-toast'
import { formatDistanceToNow } from 'date-fns'

interface ProcessStatusProps {
  connectorId: string
  runtimeType: ConnectorRuntimeType
  showControls?: boolean
}

const StatusBadge = ({ status }: { status: ProcessStatusEnum }) => {
  const configs = {
    [ProcessStatusEnum.RUNNING]: {
      icon: CheckCircle,
      label: 'Running',
      className: 'bg-green-100 text-green-800 border-green-200'
    },
    [ProcessStatusEnum.STARTING]: {
      icon: Clock,
      label: 'Starting',
      className: 'bg-blue-100 text-blue-800 border-blue-200'
    },
    [ProcessStatusEnum.RESTARTING]: {
      icon: RotateCw,
      label: 'Restarting',
      className: 'bg-yellow-100 text-yellow-800 border-yellow-200'
    },
    [ProcessStatusEnum.STOPPED]: {
      icon: Square,
      label: 'Stopped',
      className: 'bg-gray-100 text-gray-800 border-gray-200'
    },
    [ProcessStatusEnum.ERROR]: {
      icon: XCircle,
      label: 'Error',
      className: 'bg-red-100 text-red-800 border-red-200'
    },
  }

  const config = configs[status] || configs[ProcessStatusEnum.STOPPED]
  const Icon = config.icon

  return (
    <span className={cn(
      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
      config.className
    )}>
      <Icon className="h-3 w-3 mr-1" />
      {config.label}
    </span>
  )
}

export default function ProcessStatus({ connectorId, runtimeType, showControls = true }: ProcessStatusProps) {
  const queryClient = useQueryClient()

  // Skip query if this is a native connector
  const isExternal = runtimeType !== ConnectorRuntimeType.NATIVE

  const { data: processStatus, isLoading, error, refetch } = useQuery({
    queryKey: ['process-status', connectorId],
    queryFn: () => processApi.getStatus(connectorId).then(res => res.data),
    enabled: isExternal,
    refetchInterval: 10000, // Refresh every 10 seconds
    retry: 1
  })

  const restartMutation = useMutation({
    mutationFn: () => processApi.restart(connectorId),
    onSuccess: () => {
      toast.success('Process restart initiated')
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['process-status', connectorId] })
      }, 2000)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to restart process')
    }
  })

  const terminateMutation = useMutation({
    mutationFn: () => processApi.terminate(connectorId),
    onSuccess: () => {
      toast.success('Process terminated')
      queryClient.invalidateQueries({ queryKey: ['process-status', connectorId] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to terminate process')
    }
  })

  // Native connector - show simple badge
  if (!isExternal) {
    return (
      <div className="flex items-center space-x-2">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
          <Activity className="h-3 w-3 mr-1" />
          Native (In-Process)
        </span>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
          <Clock className="h-3 w-3 mr-1 animate-spin" />
          Loading...
        </span>
      </div>
    )
  }

  if (error || !processStatus) {
    return (
      <div className="flex items-center space-x-2">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
          <Square className="h-3 w-3 mr-1" />
          Not Started
        </span>
        <p className="text-xs text-gray-500">Will start on first tool request</p>
      </div>
    )
  }

  const uptime = processStatus.started_at
    ? formatDistanceToNow(new Date(processStatus.started_at), { addSuffix: true })
    : 'Unknown'

  const lastHealthCheck = processStatus.last_health_check
    ? formatDistanceToNow(new Date(processStatus.last_health_check), { addSuffix: true })
    : 'Never'

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <StatusBadge status={processStatus.status} />
          {processStatus.pid && (
            <span className="text-xs text-gray-500">
              PID: <code className="bg-gray-100 px-1 rounded">{processStatus.pid}</code>
            </span>
          )}
        </div>
        {showControls && (
          <div className="flex items-center space-x-2">
            <button
              onClick={() => refetch()}
              className="text-xs text-gray-600 hover:text-gray-900 flex items-center"
              title="Refresh status"
            >
              <RotateCw className="h-3 w-3 mr-1" />
              Refresh
            </button>
            <button
              onClick={() => restartMutation.mutate()}
              disabled={restartMutation.isPending}
              className="btn-secondary text-xs py-1 px-2"
              title="Restart process"
            >
              <RotateCw className="h-3 w-3 mr-1" />
              Restart
            </button>
            <button
              onClick={() => terminateMutation.mutate()}
              disabled={terminateMutation.isPending}
              className="btn-secondary text-xs py-1 px-2 text-error-600 hover:text-error-700"
              title="Terminate process"
            >
              <Square className="h-3 w-3 mr-1" />
              Terminate
            </button>
          </div>
        )}
      </div>

      {/* Process Details */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-3 bg-gray-50 rounded-lg text-xs">
        <div>
          <div className="text-gray-500 mb-1">Started</div>
          <div className="font-medium text-gray-900">{uptime}</div>
        </div>
        <div>
          <div className="text-gray-500 mb-1">Last Health Check</div>
          <div className="font-medium text-gray-900">{lastHealthCheck}</div>
        </div>
        <div>
          <div className="text-gray-500 mb-1">Restart Count</div>
          <div className="font-medium text-gray-900">{processStatus.restart_count}</div>
        </div>
        <div>
          <div className="text-gray-500 mb-1">Runtime</div>
          <div className="font-medium text-gray-900">{processStatus.runtime_type}</div>
        </div>
      </div>

      {/* Error Message */}
      {processStatus.error_message && (
        <div className="flex items-start space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="text-xs font-medium text-red-900 mb-1">Error Message</div>
            <div className="text-xs text-red-700 font-mono break-all">
              {processStatus.error_message}
            </div>
          </div>
        </div>
      )}

      {/* Restart Limit Warning */}
      {processStatus.restart_count >= 3 && processStatus.status === ProcessStatusEnum.ERROR && (
        <div className="flex items-start space-x-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
          <AlertCircle className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <div className="text-xs font-medium text-amber-900 mb-1">Max Restart Limit Reached</div>
            <div className="text-xs text-amber-700">
              The process has reached the maximum restart limit (3 attempts). Manual intervention required.
              Click "Restart" to retry.
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
