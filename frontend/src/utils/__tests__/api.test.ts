import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { fetchTenants, createTenant, fetchConnectors, createConnector } from '../api'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

describe('API utils', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('fetchTenants', () => {
    it('should fetch tenants successfully', async () => {
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
      ]

      mockedAxios.get.mockResolvedValue({ data: mockTenants })

      const result = await fetchTenants()

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/admin/tenants')
      expect(result).toEqual(mockTenants)
    })

    it('should handle fetch tenants error', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Network error'))

      await expect(fetchTenants()).rejects.toThrow('Network error')
    })
  })

  describe('createTenant', () => {
    it('should create tenant successfully', async () => {
      const newTenant = {
        slug: 'new-tenant',
        name: 'New Tenant',
        description: 'A new tenant',
        contact_email: 'new@example.com',
      }

      const createdTenant = {
        id: '123',
        ...newTenant,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      mockedAxios.post.mockResolvedValue({ data: createdTenant })

      const result = await createTenant(newTenant)

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/admin/tenants', newTenant)
      expect(result).toEqual(createdTenant)
    })

    it('should handle create tenant error', async () => {
      const newTenant = {
        slug: 'new-tenant',
        name: 'New Tenant',
        description: 'A new tenant',
        contact_email: 'new@example.com',
      }

      mockedAxios.post.mockRejectedValue(new Error('Validation error'))

      await expect(createTenant(newTenant)).rejects.toThrow('Validation error')
    })
  })

  describe('fetchConnectors', () => {
    it('should fetch connectors for a tenant', async () => {
      const tenantSlug = 'test-tenant'
      const mockConnectors = [
        {
          id: '1',
          name: 'GitHub Connector',
          description: 'GitHub integration',
          connector_type: 'github',
          is_enabled: true,
          configuration: {},
          tenant_id: 'tenant-id',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ]

      mockedAxios.get.mockResolvedValue({ data: mockConnectors })

      const result = await fetchConnectors(tenantSlug)

      expect(mockedAxios.get).toHaveBeenCalledWith(`/api/v1/admin/tenants/${tenantSlug}/connectors`)
      expect(result).toEqual(mockConnectors)
    })
  })

  describe('createConnector', () => {
    it('should create connector successfully', async () => {
      const tenantSlug = 'test-tenant'
      const newConnector = {
        name: 'GitHub Connector',
        description: 'GitHub integration',
        connector_type: 'github',
        configuration: {},
      }

      const createdConnector = {
        id: '123',
        ...newConnector,
        is_enabled: true,
        tenant_id: 'tenant-id',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      mockedAxios.post.mockResolvedValue({ data: createdConnector })

      const result = await createConnector(tenantSlug, newConnector)

      expect(mockedAxios.post).toHaveBeenCalledWith(
        `/api/v1/admin/tenants/${tenantSlug}/connectors`,
        newConnector
      )
      expect(result).toEqual(createdConnector)
    })
  })
})