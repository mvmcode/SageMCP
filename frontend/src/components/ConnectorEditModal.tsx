import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'
import toast from 'react-hot-toast'
import { connectorsApi } from '@/utils/api'
import { Connector } from '@/types'

interface ConnectorEditModalProps {
  isOpen: boolean
  onClose: () => void
  connector: Connector
  tenantSlug: string
}

export default function ConnectorEditModal({
  isOpen,
  onClose,
  connector,
  tenantSlug
}: ConnectorEditModalProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    name: connector.name,
    description: connector.description || ''
  })

  // Update form data when connector changes
  useEffect(() => {
    setFormData({
      name: connector.name,
      description: connector.description || ''
    })
  }, [connector])

  const updateMutation = useMutation({
    mutationFn: () => connectorsApi.update(tenantSlug, connector.id, {
      connector_type: connector.connector_type,
      name: formData.name,
      description: formData.description || undefined,
      configuration: connector.configuration
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connectors', tenantSlug] })
      toast.success('Connector updated successfully')
      onClose()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update connector')
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.name.trim()) {
      toast.error('Connector name is required')
      return
    }

    updateMutation.mutate()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={onClose} />
        <div className="relative bg-white rounded-lg shadow-xl max-w-lg w-full">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Edit Connector</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit}>
            <div className="px-6 py-4 space-y-4">
              {/* Connector Type (read-only) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Connector Type
                </label>
                <input
                  type="text"
                  value={connector.connector_type}
                  readOnly
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed capitalize"
                />
                <p className="text-xs text-gray-500 mt-1">Connector type cannot be changed</p>
              </div>

              {/* Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name <span className="text-error-600">*</span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="My GitHub Connector"
                  required
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Optional description"
                  rows={3}
                />
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="btn-secondary"
                disabled={updateMutation.isPending}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={updateMutation.isPending}
              >
                {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
