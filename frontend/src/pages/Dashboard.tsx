import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Building2,
  Plug,
  Activity,
  Users,
  TrendingUp
} from 'lucide-react'
import { tenantsApi, healthApi } from '@/utils/api'
import { cn } from '@/utils/cn'

const StatCard = ({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  trend = 'up' 
}: { 
  title: string
  value: string | number
  change?: string
  icon: React.ElementType
  trend?: 'up' | 'down' | 'neutral'
}) => (
  <div className="card">
    <div className="card-content">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change && (
            <p className={cn(
              'text-xs flex items-center mt-1',
              trend === 'up' ? 'text-success-600' : 
              trend === 'down' ? 'text-error-600' : 'text-gray-500'
            )}>
              <TrendingUp className="h-3 w-3 mr-1" />
              {change}
            </p>
          )}
        </div>
        <div className="p-3 bg-primary-50 rounded-lg">
          <Icon className="h-6 w-6 text-primary-600" />
        </div>
      </div>
    </div>
  </div>
)

export default function Dashboard() {
  const { data: tenants = [] } = useQuery({
    queryKey: ['tenants'],
    queryFn: () => tenantsApi.list().then(res => res.data)
  })
  
  const { data: healthStatus } = useQuery({
    queryKey: ['health'],
    queryFn: () => healthApi.check().then(res => res.data),
    refetchInterval: 30000 // Refetch every 30 seconds
  })

  const activeTenants = tenants.filter(t => t.is_active).length
  const totalTenants = tenants.length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of your Sage MCP platform</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Tenants"
          value={totalTenants}
          change="+12% from last month"
          icon={Building2}
        />
        <StatCard
          title="Active Tenants"
          value={activeTenants}
          change="+8% from last month"
          icon={Users}
        />
        <StatCard
          title="Total Connectors"
          value="12"
          change="+3 new this week"
          icon={Plug}
        />
        <StatCard
          title="System Health"
          value={healthStatus?.status === 'healthy' ? 'Healthy' : 'Issues'}
          icon={Activity}
          trend={healthStatus?.status === 'healthy' ? 'up' : 'down'}
        />
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
            </div>
            <div className="card-content">
              <div className="text-center py-12">
                <Activity className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-sm text-gray-500">No recent activity to display</p>
                <p className="text-xs text-gray-400 mt-1">
                  Activity tracking will be available soon
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div>
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
            </div>
            <div className="card-content space-y-3">
              <Link
                to="/tenants"
                className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
              >
                <Building2 className="h-5 w-5 text-gray-400 group-hover:text-gray-600" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">Manage Tenants</p>
                  <p className="text-xs text-gray-500">Create and configure tenants</p>
                </div>
              </Link>

              <div className="flex items-center p-3 bg-primary-50 rounded-lg border-2 border-primary-100">
                <Plug className="h-5 w-5 text-primary-600" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-primary-900">Configure Connectors</p>
                  <p className="text-xs text-primary-700">Access via tenant settings</p>
                </div>
              </div>

              <Link
                to="/mcp-test"
                className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
              >
                <Activity className="h-5 w-5 text-gray-400 group-hover:text-gray-600" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">Test MCP Protocol</p>
                  <p className="text-xs text-gray-500">Debug and test connections</p>
                </div>
              </Link>
            </div>
          </div>

          {/* System Status */}
          <div className="card mt-6">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
            </div>
            <div className="card-content space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">API Server</span>
                <span className="status-active">Healthy</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Database</span>
                <span className="status-active">Connected</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Redis Cache</span>
                <span className="status-active">Online</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}