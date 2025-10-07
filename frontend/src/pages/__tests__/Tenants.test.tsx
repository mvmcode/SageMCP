import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '../../test/utils'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Tenants from '../Tenants'
import * as api from '../../utils/api'

// Mock the API
vi.mock('../../utils/api', () => ({
  fetchTenants: vi.fn(),
  createTenant: vi.fn(),
}))

const mockFetchTenants = vi.mocked(api.fetchTenants)

describe('Tenants', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false, cacheTime: 0 },
        mutations: { retry: false },
      },
    })
    vi.clearAllMocks()
  })

  const renderWithClient = (component: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    )
  }

  it('renders tenants page with title', () => {
    mockFetchTenants.mockResolvedValue({ data: [] } as any)
    
    renderWithClient(<Tenants />)
    
    expect(screen.getByText('Tenants')).toBeInTheDocument()
    expect(screen.getByText('Create Tenant')).toBeInTheDocument()
  })

  it('shows loading state initially', () => {
    mockFetchTenants.mockImplementation(() => new Promise(() => { /* Never resolves */ }))

    renderWithClient(<Tenants />)

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('displays tenants when loaded', async () => {
    const mockTenants = [
      {
        id: '1',
        slug: 'tenant-1',
        name: 'Tenant 1',
        description: 'First tenant',
        contact_email: 'tenant1@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: '2',
        slug: 'tenant-2',
        name: 'Tenant 2',
        description: 'Second tenant',
        contact_email: 'tenant2@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ]
    
    mockFetchTenants.mockResolvedValue({ data: mockTenants } as any)
    
    renderWithClient(<Tenants />)
    
    await waitFor(() => {
      expect(screen.getByText('Tenant 1')).toBeInTheDocument()
      expect(screen.getByText('Tenant 2')).toBeInTheDocument()
    })
  })

  it('shows empty state when no tenants', async () => {
    mockFetchTenants.mockResolvedValue({ data: [] } as any)
    
    renderWithClient(<Tenants />)
    
    await waitFor(() => {
      expect(screen.getByText('No tenants found')).toBeInTheDocument()
    })
  })

  it('handles error state', async () => {
    mockFetchTenants.mockRejectedValue(new Error('Failed to fetch'))
    
    renderWithClient(<Tenants />)
    
    await waitFor(() => {
      expect(screen.getByText('Error loading tenants')).toBeInTheDocument()
    })
  })

  it('opens create tenant modal when button clicked', async () => {
    mockFetchTenants.mockResolvedValue({ data: [] } as any)
    
    renderWithClient(<Tenants />)
    
    const createButton = screen.getByText('Create Tenant')
    fireEvent.click(createButton)
    
    await waitFor(() => {
      expect(screen.getByText('Create New Tenant')).toBeInTheDocument()
    })
  })
})