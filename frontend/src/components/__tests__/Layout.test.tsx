import { describe, it, expect } from 'vitest'
import { render, screen } from '../../test/utils'
import Layout from '../Layout'

describe('Layout', () => {
  it('renders children correctly', () => {
    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    )
    
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('renders the main navigation', () => {
    render(
      <Layout>
        <div>Content</div>
      </Layout>
    )
    
    // Check for navigation items
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Tenants')).toBeInTheDocument()
    expect(screen.getByText('MCP Testing')).toBeInTheDocument()
  })

  it('renders the logo/title', () => {
    render(
      <Layout>
        <div>Content</div>
      </Layout>
    )
    
    expect(screen.getByText('Sage MCP')).toBeInTheDocument()
  })

  it('has proper semantic structure', () => {
    render(
      <Layout>
        <div>Content</div>
      </Layout>
    )
    
    // Should have nav and main elements
    expect(screen.getByRole('navigation')).toBeInTheDocument()
    expect(screen.getByRole('main')).toBeInTheDocument()
  })
})