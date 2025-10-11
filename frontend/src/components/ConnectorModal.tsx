import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { X, Github, Gitlab, MessageSquare, Zap, Key } from 'lucide-react'
import { tenantsApi, connectorsApi } from '@/utils/api'
import { ConnectorType, ConnectorCreate } from '@/types'
import { cn } from '@/utils/cn'

const connectorSchema = z.object({
  tenant_slug: z.string().min(1, 'Please select a tenant'),
  connector_type: z.nativeEnum(ConnectorType, {
    errorMap: () => ({ message: 'Please select a connector type' })
  }),
  name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
  description: z.string().optional(),
})

type ConnectorFormData = z.infer<typeof connectorSchema>

const ConnectorTypeCard = ({
  type,
  selected,
  disabled,
  onSelect,
}: {
  type: ConnectorType
  selected: boolean
  disabled?: boolean
  onSelect: (type: ConnectorType) => void
}) => {
  const configs = {
    [ConnectorType.GITHUB]: {
      icon: Github,
      name: 'GitHub',
      description: 'Connect to GitHub repositories and issues',
      color: 'bg-gray-900 text-white',
    },
    [ConnectorType.GITLAB]: {
      icon: Gitlab,
      name: 'GitLab',
      description: 'Connect to GitLab projects and merge requests',
      color: 'bg-orange-500 text-white',
    },
    [ConnectorType.SLACK]: {
      icon: MessageSquare,
      name: 'Slack',
      description: 'Connect to Slack channels and messages',
      color: 'bg-purple-600 text-white',
    },
    [ConnectorType.DISCORD]: {
      icon: MessageSquare,
      name: 'Discord',
      description: 'Connect to Discord servers and channels',
      color: 'bg-indigo-600 text-white',
    },
    [ConnectorType.CUSTOM]: {
      icon: Zap,
      name: 'Custom',
      description: 'Build your own custom connector',
      color: 'bg-gray-600 text-white',
    },
  }

  const config = configs[type]
  const Icon = config.icon

  return (
    <button
      type="button"
      onClick={() => !disabled && onSelect(type)}
      disabled={disabled}
      className={cn(
        'p-4 border-2 rounded-lg transition-all text-left w-full relative',
        disabled
          ? 'border-gray-200 bg-gray-50 opacity-60 cursor-not-allowed'
          : selected
          ? 'border-primary-500 bg-primary-50'
          : 'border-gray-200 hover:border-gray-300'
      )}
    >
      <div className="flex items-start space-x-3">
        <div className={cn('p-2 rounded-lg', config.color)}>
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-gray-900">{config.name}</h4>
          <p className="text-xs text-gray-500 mt-1">
            {disabled ? 'Already exists for this tenant' : config.description}
          </p>
        </div>
      </div>
    </button>
  )
}

interface ConnectorModalProps {
  isOpen: boolean
  onClose: () => void
  preselectedTenant?: string
}

export default function ConnectorModal({ 
  isOpen, 
  onClose, 
  preselectedTenant 
}: ConnectorModalProps) {
  const [step, setStep] = useState<'type' | 'details'>('type')
  const [selectedType, setSelectedType] = useState<ConnectorType | null>(null)
  const queryClient = useQueryClient()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    reset
  } = useForm<ConnectorFormData>({
    resolver: zodResolver(connectorSchema),
    defaultValues: preselectedTenant ? { tenant_slug: preselectedTenant } : undefined
  })


  const { data: tenants = [] } = useQuery({
    queryKey: ['tenants'],
    queryFn: () => tenantsApi.list().then(res => res.data),
    enabled: isOpen
  })

  // Fetch existing connectors for the selected tenant to check for duplicates
  const selectedTenantSlug = preselectedTenant || undefined
  const { data: existingConnectors = [] } = useQuery({
    queryKey: ['connectors', selectedTenantSlug],
    queryFn: () => selectedTenantSlug ? connectorsApi.list(selectedTenantSlug).then(res => res.data) : Promise.resolve([]),
    enabled: isOpen && !!selectedTenantSlug
  })

  // Get list of connector types already in use
  const usedConnectorTypes = new Set(existingConnectors.map(c => c.connector_type))

  const createMutation = useMutation({
    mutationFn: ({ tenant_slug, ...data }: ConnectorFormData) => 
      connectorsApi.create(tenant_slug, data as ConnectorCreate),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connectors'] })
      queryClient.invalidateQueries({ queryKey: ['all-connectors'] })
      toast.success('Connector created successfully')
      handleClose()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create connector')
    }
  })

  const handleClose = () => {
    setStep('type')
    setSelectedType(null)
    reset()
    onClose()
  }


  const handleTypeSelect = (type: ConnectorType) => {
    setSelectedType(type)
    setValue('connector_type', type)
    setStep('details')
  }

  const handleBack = () => {
    setStep('type')
  }

  const requiresOAuth = (type: ConnectorType) => {
    return [ConnectorType.GITHUB, ConnectorType.GITLAB].includes(type)
  }

  const onSubmit = (data: ConnectorFormData) => {
    // Add configuration as null since it's not used yet
    const payload = {
      ...data,
      configuration: null
    }
    createMutation.mutate(payload as any)
  }

  console.log('ConnectorModal render:', { isOpen, step, selectedType })
  
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={handleClose} />
        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {step === 'type' ? 'Choose Connector Type' : 'Configure Connector'}
              </h3>
              <p className="text-sm text-gray-600">
                {step === 'type' 
                  ? 'Select the type of connector you want to create'
                  : `Setting up ${selectedType} connector`
                }
              </p>
            </div>
            <button onClick={handleClose} className="text-gray-400 hover:text-gray-600">
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4 max-h-[calc(90vh-120px)] overflow-y-auto">
            {step === 'type' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.values(ConnectorType).map((type) => (
                  <ConnectorTypeCard
                    key={type}
                    type={type}
                    selected={selectedType === type}
                    disabled={usedConnectorTypes.has(type)}
                    onSelect={handleTypeSelect}
                  />
                ))}
              </div>
            ) : (
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {/* OAuth Notice for OAuth-required connectors */}
                {selectedType && requiresOAuth(selectedType) && (
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <Key className="h-5 w-5 text-amber-600 mt-0.5" />
                      <div>
                        <h4 className="text-sm font-medium text-amber-900">
                          OAuth Configuration Required
                        </h4>
                        <p className="text-sm text-amber-700 mt-1">
                          This connector requires OAuth authentication. After creating the connector, 
                          go to the <strong>OAuth Settings</strong> tab to configure your {selectedType} credentials.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Tenant Selection (if not preselected) */}
                {!preselectedTenant && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tenant *
                    </label>
                    <select {...register('tenant_slug')} className="input-field">
                      <option value="">Select a tenant...</option>
                      {tenants.map(tenant => (
                        <option key={tenant.slug} value={tenant.slug}>
                          {tenant.name} ({tenant.slug})
                        </option>
                      ))}
                    </select>
                    {errors.tenant_slug && (
                      <p className="mt-1 text-sm text-error-600">{errors.tenant_slug.message}</p>
                    )}
                  </div>
                )}


                {/* Connector Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Connector Name *
                  </label>
                  <input
                    {...register('name')}
                    className="input-field"
                    placeholder={`My ${selectedType} Connector`}
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-error-600">{errors.name.message}</p>
                  )}
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    {...register('description')}
                    className="input-field"
                    rows={3}
                    placeholder="Brief description of this connector..."
                  />
                  {errors.description && (
                    <p className="mt-1 text-sm text-error-600">{errors.description.message}</p>
                  )}
                </div>

                {/* Hidden field for connector type */}
                <input type="hidden" {...register('connector_type')} />

                {/* Footer */}
                <div className="flex justify-between pt-4 border-t border-gray-200">
                  <button
                    type="button"
                    onClick={handleBack}
                    className="btn-secondary"
                  >
                    Back
                  </button>
                  <div className="flex space-x-3">
                    <button
                      type="button"
                      onClick={handleClose}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="btn-primary"
                    >
                      {isSubmitting ? 'Creating...' : 'Create Connector'}
                    </button>
                  </div>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}