# Quick Installation Guide for SageMCP Helm Chart

## Prerequisites

```bash
# Add Bitnami repository for dependencies
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

## Installation Options

### Option 1: Quick Start (Development)

```bash
# Install with default values
helm install sagemcp ./helm --create-namespace --namespace sagemcp
```

### Option 2: Production with Custom Domain

```bash
# Create custom values
cat > my-values.yaml <<EOF
config:
  baseUrl: "https://api.yourdomain.com"
  frontendUrl: "https://yourdomain.com"

secrets:
  secretKey: "$(openssl rand -base64 32)"

ingress:
  enabled: true
  hosts:
    - host: yourdomain.com
      paths:
        - path: /api
          pathType: Prefix
          backend: backend
        - path: /
          pathType: Prefix
          backend: frontend
  tls:
    - secretName: sagemcp-tls
      hosts:
        - yourdomain.com
EOF

# Install
helm install sagemcp ./helm -f my-values.yaml --namespace sagemcp --create-namespace
```

### Option 3: Using External Database

```bash
cat > external-db-values.yaml <<EOF
postgresql:
  enabled: false

redis:
  enabled: false

externalDatabase:
  host: "your-postgres-host.com"
  username: "sage_mcp"
  password: "your-secure-password"
  database: "sage_mcp"

externalRedis:
  host: "your-redis-host.com"
  password: "your-redis-password"
EOF

helm install sagemcp ./helm -f external-db-values.yaml --namespace sagemcp --create-namespace
```

## Verify Installation

```bash
# Check pods
kubectl get pods -n sagemcp

# Check services
kubectl get svc -n sagemcp

# View installation notes
helm get notes sagemcp -n sagemcp
```

## Access the Application

### With Port-Forward (Development)

```bash
# Frontend
kubectl port-forward -n sagemcp svc/sagemcp-frontend 3000:80

# Backend API
kubectl port-forward -n sagemcp svc/sagemcp-backend 8000:8000

# Visit http://localhost:3000 for frontend
# Visit http://localhost:8000/docs for API docs
```

### With Ingress (Production)

Configure DNS to point to your ingress controller's external IP:

```bash
kubectl get ingress -n sagemcp
```

## Upgrading

```bash
# Upgrade to new version
helm upgrade sagemcp ./helm -f my-values.yaml -n sagemcp

# With specific image tags
helm upgrade sagemcp ./helm \
  --set backend.image.tag=v1.0.0 \
  --set frontend.image.tag=v1.0.0 \
  -n sagemcp
```

## Uninstall

```bash
# Uninstall the chart
helm uninstall sagemcp -n sagemcp

# Delete namespace and PVCs
kubectl delete namespace sagemcp
```

## Common Issues

### Pods not starting

```bash
# Check pod status
kubectl describe pod -n sagemcp <pod-name>

# Check logs
kubectl logs -n sagemcp <pod-name>
```

### Database connection errors

```bash
# Verify PostgreSQL is running
kubectl get pods -n sagemcp -l app.kubernetes.io/name=postgresql

# Check database logs
kubectl logs -n sagemcp -l app.kubernetes.io/name=postgresql
```

### Ingress not working

```bash
# Check ingress resource
kubectl describe ingress -n sagemcp

# Verify ingress controller is installed
kubectl get pods -A | grep ingress
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/mvmcode/SageMCP/issues
- Discussions: https://github.com/mvmcode/SageMCP/discussions
