.PHONY: help build up down logs shell test lint format clean

# Default target
help:
	@echo "Available commands:"
	@echo "  build      - Build Docker images"
	@echo "  up         - Start all services"
	@echo "  down       - Stop all services"
	@echo "  logs       - View logs from all services"
	@echo "  logs-app   - View logs from the app service only"
	@echo "  logs-frontend - View logs from the frontend service only"
	@echo "  shell      - Open shell in the app container"
	@echo "  frontend-shell - Open shell in the frontend container"
	@echo "  db-shell   - Open PostgreSQL shell"
	@echo "  test       - Run all tests (backend + frontend)"
	@echo "  test-backend - Run backend tests only"
	@echo "  test-frontend - Run frontend tests only"
	@echo "  test-coverage - Run tests with coverage reports"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code"
	@echo "  clean      - Clean up containers and volumes"
	@echo "  setup      - Initial setup for development"

# Build Docker images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# View app logs only
logs-app:
	docker-compose logs -f app

# View frontend logs only
logs-frontend:
	docker-compose logs -f frontend

# Open shell in app container
shell:
	docker-compose exec app bash

# Open shell in frontend container
frontend-shell:
	docker-compose exec frontend sh

# Open PostgreSQL shell
db-shell:
	docker-compose exec postgres psql -U sage_mcp -d sage_mcp

# Run all tests
test:
	@echo "Running backend tests..."
	docker-compose exec app pytest
	@echo "Running frontend tests..."
	docker-compose exec frontend npm test
	
# Run backend tests only
test-backend:
	docker-compose exec app pytest

# Run frontend tests only  
test-frontend:
	docker-compose exec frontend npm test

# Run tests with coverage
test-coverage:
	docker-compose exec app pytest --cov=src/sage_mcp --cov-report=html
	docker-compose exec frontend npm run test:coverage

# Run linting
lint:
	docker-compose exec app flake8 src/
	docker-compose exec app mypy src/

# Format code
format:
	docker-compose exec app black src/
	docker-compose exec app isort src/

# Clean up
clean:
	docker-compose down -v
	docker system prune -f

# Initial setup
setup:
	@echo "Setting up Sage MCP for development..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from .env.example..."; \
		cp .env.example .env; \
		echo "Please edit .env file with your configuration."; \
	fi
	@echo "Building Docker images..."
	@make build
	@echo "Starting services..."
	@make up
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Setup complete!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API documentation: http://localhost:8000/docs"
	@echo "Database admin: http://localhost:8080"