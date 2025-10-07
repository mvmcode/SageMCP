import { Routes, Route } from 'react-router-dom'
import Layout from '@/components/Layout'
import Dashboard from '@/pages/Dashboard'
import Tenants from '@/pages/Tenants'
import TenantDetail from '@/pages/TenantDetail'
import Connectors from '@/pages/Connectors'
import MCPTesting from '@/pages/MCPTesting'
import OAuthSuccess from '@/pages/OAuthSuccess'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="tenants" element={<Tenants />} />
        <Route path="tenants/:slug" element={<TenantDetail />} />
        <Route path="connectors" element={<Connectors />} />
        <Route path="mcp-test" element={<MCPTesting />} />
        <Route path="oauth/success" element={<OAuthSuccess />} />
      </Route>
    </Routes>
  )
}

export default App