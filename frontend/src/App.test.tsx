import { describe, it, expect } from 'vitest'
import { render, screen } from './test/utils'
import App from './App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByText('Sage MCP')).toBeInTheDocument()
  })

  it('has navigation links', () => {
    render(<App />)
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Tenants')).toBeInTheDocument()
    expect(screen.getByText('MCP Testing')).toBeInTheDocument()
  })

  it('renders the main content area', () => {
    render(<App />)
    
    // Should have a main element
    const main = screen.getByRole('main')
    expect(main).toBeInTheDocument()
  })
})