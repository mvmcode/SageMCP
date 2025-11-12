# SageMCP Helm Chart

This Helm chart deploys SageMCP - a Multi-tenant Model Context Protocol (MCP) Platform on Kubernetes.

## Prerequisites

- Kubernetes 1.21+
- Helm 3.8+
- PV provisioner support in the underlying infrastructure (for PostgreSQL and Redis persistence)

## Installing the Chart

### Quick Start

```bash
# Add the Bitnami repository (for PostgreSQL and Redis dependencies)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install with default values
helm install sagemcp ./helm

# Or install with custom values
helm install sagemcp ./helm -f my-values.yaml
```

### Production Installation

For production deployments, you should customize the values:

```bash
# Create a custom values file
cat > production-values.yaml <<EOF
# Production configuration
config:
  baseUrl: "https://api.sagemcp.example.com"
  frontendUrl: "https://sagemcp.example.com"

# Generate a secure secret key
secrets:
  secretKey: "$(openssl rand -base64 32)"
  github:
    clientId: "your-github-client-id"
    clientSecret: "your-github-client-secret"

# Enable ingress
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: sagemcp.example.com
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
        - sagemcp.example.com

# Production resources
backend:
  replicaCount: 3
  resources:
    limits:
      cpu: 2000m
      memory: 2Gi
    requests:
      cpu: 1000m
      memory: 1Gi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10

frontend:
  replicaCount: 3
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10

# PostgreSQL with persistence
postgresql:
  primary:
    persistence:
      size: 50Gi
    resources:
      limits:
        cpu: 2000m
        memory: 2Gi

# Redis with persistence
redis:
  master:
    persistence:
      size: 10Gi
EOF

# Install with production values
helm install sagemcp ./helm -f production-values.yaml
```

## Configuration

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.storageClass` | Global storage class for PV | `""` |

### Backend Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.replicaCount` | Number of backend replicas | `2` |
| `backend.image.repository` | Backend image repository | `ghcr.io/mvmcode/sagemcp/backend` |
| `backend.image.tag` | Backend image tag | `latest` |
| `backend.image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `backend.service.type` | Kubernetes service type | `ClusterIP` |
| `backend.service.port` | Service port | `8000` |
| `backend.resources.limits.cpu` | CPU limit | `1000m` |
| `backend.resources.limits.memory` | Memory limit | `1Gi` |
| `backend.resources.requests.cpu` | CPU request | `500m` |
| `backend.resources.requests.memory` | Memory request | `512Mi` |
| `backend.autoscaling.enabled` | Enable HPA | `false` |
| `backend.autoscaling.minReplicas` | Minimum replicas | `2` |
| `backend.autoscaling.maxReplicas` | Maximum replicas | `10` |

### Frontend Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.replicaCount` | Number of frontend replicas | `2` |
| `frontend.image.repository` | Frontend image repository | `ghcr.io/mvmcode/sagemcp/frontend` |
| `frontend.image.tag` | Frontend image tag | `latest` |
| `frontend.image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `frontend.service.type` | Kubernetes service type | `ClusterIP` |
| `frontend.service.port` | Service port | `80` |
| `frontend.resources.limits.cpu` | CPU limit | `500m` |
| `frontend.resources.limits.memory` | Memory limit | `512Mi` |

### Ingress Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `nginx` |
| `ingress.hosts` | Ingress hosts configuration | See values.yaml |
| `ingress.tls` | TLS configuration | See values.yaml |

### Database Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgresql.enabled` | Enable built-in PostgreSQL | `true` |
| `postgresql.auth.username` | PostgreSQL username | `sage_mcp` |
| `postgresql.auth.password` | PostgreSQL password | `changeme` |
| `postgresql.auth.database` | PostgreSQL database | `sage_mcp` |
| `postgresql.primary.persistence.size` | Database storage size | `10Gi` |
| `externalDatabase.host` | External database host | `""` |
| `externalDatabase.port` | External database port | `5432` |

### Redis Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.enabled` | Enable built-in Redis | `true` |
| `redis.auth.password` | Redis password | `changeme` |
| `redis.master.persistence.size` | Redis storage size | `2Gi` |
| `externalRedis.host` | External Redis host | `""` |
| `externalRedis.port` | External Redis port | `6379` |

### Application Secrets

| Parameter | Description | Default |
|-----------|-------------|---------|
| `secrets.secretKey` | Application secret key | `change-me-to-a-secure-random-string` |
| `secrets.github.clientId` | GitHub OAuth client ID | `""` |
| `secrets.github.clientSecret` | GitHub OAuth client secret | `""` |
| `secrets.slack.clientId` | Slack OAuth client ID | `""` |
| `secrets.slack.clientSecret` | Slack OAuth client secret | `""` |

### Application Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `config.baseUrl` | API base URL | `https://sagemcp.example.com` |
| `config.frontendUrl` | Frontend URL | `https://sagemcp.example.com` |
| `config.accessTokenExpireMinutes` | Access token expiration | `30` |
| `config.refreshTokenExpireDays` | Refresh token expiration | `7` |

## Using External Databases

To use external PostgreSQL and Redis:

```yaml
# Disable built-in databases
postgresql:
  enabled: false

redis:
  enabled: false

# Configure external databases
externalDatabase:
  host: "postgres.example.com"
  port: 5432
  username: "sage_mcp"
  password: "your-secure-password"
  database: "sage_mcp"
  sslMode: "require"

externalRedis:
  host: "redis.example.com"
  port: 6379
  password: "your-redis-password"
  database: 0
```

## Upgrading

```bash
# Upgrade to a new version
helm upgrade sagemcp ./helm -f my-values.yaml

# Upgrade with specific image tags
helm upgrade sagemcp ./helm \
  --set backend.image.tag=v1.2.0 \
  --set frontend.image.tag=v1.2.0
```

## Uninstalling

```bash
# Uninstall the release
helm uninstall sagemcp

# Delete PVCs if needed
kubectl delete pvc -l app.kubernetes.io/instance=sagemcp
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -l app.kubernetes.io/instance=sagemcp
```

### View Logs

```bash
# Backend logs
kubectl logs -l app.kubernetes.io/component=backend -f

# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend -f

# Database logs
kubectl logs -l app.kubernetes.io/component=primary,app.kubernetes.io/name=postgresql -f
```

### Database Connection Issues

```bash
# Check database connectivity
kubectl run -it --rm debug --image=postgres:15-alpine --restart=Never -- \
  psql -h sagemcp-postgresql -U sage_mcp -d sage_mcp
```

### Redis Connection Issues

```bash
# Check Redis connectivity
kubectl run -it --rm debug --image=redis:7-alpine --restart=Never -- \
  redis-cli -h sagemcp-redis-master -a <password> ping
```

## Advanced Configuration

### Custom Resource Limits

```yaml
backend:
  resources:
    limits:
      cpu: 2000m
      memory: 2Gi
    requests:
      cpu: 1000m
      memory: 1Gi
```

### Node Affinity

```yaml
backend:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: node-role.kubernetes.io/worker
            operator: In
            values:
            - "true"
```

### Pod Disruption Budget

You can add a PDB for high availability:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: sagemcp-backend-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/component: backend
```

## Security Considerations

1. **Change Default Passwords**: Always change default PostgreSQL and Redis passwords
2. **Generate Secure Keys**: Use `openssl rand -base64 32` for `secrets.secretKey`
3. **Enable TLS**: Configure TLS/SSL for ingress
4. **Network Policies**: Consider implementing network policies to restrict pod communication
5. **RBAC**: Review and customize service account permissions
6. **Secret Management**: Consider using external secret management (e.g., Sealed Secrets, External Secrets Operator)

## Support

- GitHub Issues: https://github.com/mvmcode/SageMCP/issues
- Discussions: https://github.com/mvmcode/SageMCP/discussions
- Documentation: https://github.com/mvmcode/SageMCP

## License

MIT
