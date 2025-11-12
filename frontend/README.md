# Sage MCP Frontend

Modern React-based web interface for the Sage MCP platform, built with TypeScript, Tailwind CSS, and inspired by Airbyte's clean design.

## Features

- **Dashboard**: Overview of system health, tenant statistics, and quick actions
- **Tenant Management**: Create, view, and manage multi-tenant configurations
- **Connector Configuration**: Set up and manage integrations across tenants
- **MCP Protocol Testing**: Real-time testing interface with WebSocket and HTTP support
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling with Airbyte-inspired design system
- **React Query** for server state management
- **React Router** for navigation
- **React Hook Form** with Zod validation
- **Framer Motion** for animations
- **Lucide React** for icons

## Development

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open http://localhost:3001 in your browser

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Docker

### Development
```bash
# Build and run with docker-compose (includes backend)
docker-compose up frontend
```

### Production
```bash
# Build production image
docker build -t sage-mcp-frontend .

# Run container
docker run -p 3001:80 sage-mcp-frontend
```

## Environment Variables

- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:8000)

## Design System

The interface follows Airbyte's design principles:

- **Clean, minimal interface** with focus on functionality
- **Consistent color palette** with primary blues and semantic colors
- **Card-based layouts** for content organization
- **Responsive grid systems** for different screen sizes
- **Accessible components** with proper ARIA labels
- **Loading states and error handling** throughout the app

## Key Components

### Layout
- **Sidebar Navigation**: Primary navigation with active states
- **Top Bar**: Secondary actions and system status
- **Responsive Design**: Mobile-friendly collapsible sidebar

### Pages
- **Dashboard**: System overview with stats and quick actions
- **Tenants**: Grid view of all tenants with search and filtering
- **Tenant Detail**: Individual tenant management with tabs
- **Connectors**: Cross-tenant connector management
- **MCP Testing**: Real-time protocol testing interface

### Components
- **Status Badges**: Visual indicators for active/inactive states
- **Loading States**: Skeleton loading for better UX
- **Form Components**: Validated forms with error handling
- **Modal Dialogs**: Accessible overlays for actions

## API Integration

The frontend integrates with the Sage MCP backend through:

- **REST API**: CRUD operations for tenants and connectors
- **WebSocket**: Real-time MCP protocol testing
- **React Query**: Caching and synchronization of server state

## Contributing

1. Follow the existing code style and patterns
2. Use TypeScript for all new components
3. Add proper error handling and loading states
4. Test responsiveness across device sizes
5. Follow accessibility best practices