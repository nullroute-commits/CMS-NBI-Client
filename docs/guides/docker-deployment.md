# Docker Deployment Guide

This guide covers deploying CMS-NBI-Client using Docker and Docker Compose with Alpine-based images.

## Overview

CMS-NBI-Client provides Docker images based on Alpine Linux for minimal size and enhanced security. The deployment stack includes:

- **Application**: Main CMS-NBI-Client service
- **Redis**: Caching layer
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **NGINX**: Reverse proxy (optional)

## Quick Start

### Development Environment

```bash
# Clone the repository
git clone https://github.com/somenetworking/CMS-NBI-Client.git
cd CMS-NBI-Client

# Start development environment
docker compose up -d

# View logs
docker compose logs -f app

# Access services
# - Application: inside container
# - Documentation: http://localhost:8000
# - Mock CMS: http://localhost:18443
```

### Running Tests

```bash
# Run all tests
docker compose -f docker compose.test.yml up test-runner

# Run unit tests only
docker compose -f docker compose.test.yml run --rm unit-tests

# Run integration tests
docker compose -f docker compose.test.yml run --rm integration-tests

# Run linting
docker compose -f docker compose.test.yml run --rm lint

# Run security scans
docker compose -f docker compose.test.yml run --rm security
```

## Production Deployment

### Prerequisites

- Docker Engine 24.0+ (includes Docker Compose v2)
- Docker Buildx v0.12+ (included in Docker Desktop)
- Docker Compose v2.21+ (included in Docker Engine)
- 2GB RAM minimum
- 10GB disk space

To verify your versions:
```bash
docker --version          # Should be 24.0 or higher
docker compose version    # Should be v2.21 or higher
docker buildx version     # Should be v0.12 or higher
```

### Environment Configuration

Create a `.env` file for production:

```bash
# CMS Configuration
CMS_USERNAME=your_username
CMS_PASSWORD=your_password
CMS_HOST=cms.example.com
CMS_PROTOCOL=https
CMS_VERIFY_SSL=true

# Performance Settings
POOL_SIZE=200
MAX_CONCURRENT=100
CACHE_TTL=600
CIRCUIT_BREAKER=true

# Monitoring
GRAFANA_PASSWORD=secure_password
LOG_LEVEL=INFO

# Version
VERSION=2.0.0
```

### Deploy Production Stack

```bash
# Deploy with docker compose
docker compose -f docker compose.prod.yml up -d

# Check status
docker compose -f docker compose.prod.yml ps

# View logs
docker compose -f docker compose.prod.yml logs -f

# Scale application
docker compose -f docker compose.prod.yml up -d --scale app=3
```

### Zero-Downtime Updates

```bash
# Pull latest images
docker compose -f docker compose.prod.yml pull

# Update with zero downtime
docker compose -f docker compose.prod.yml up -d --no-deps app

# Verify new version
docker compose -f docker compose.prod.yml exec app python -c "import cmsnbiclient; print(cmsnbiclient.__version__)"
```

## Docker Images

### Base Images

All images are based on Alpine Linux for security and size optimization:

- **Production**: `python:3.11-alpine` (50MB base)
- **Development**: Includes additional tools (150MB)
- **Test**: Minimal test runner (80MB)

### Image Variants

```bash
# Production image
cms-nbi-client:latest
cms-nbi-client:2.0.0
cms-nbi-client:2.0

# Development image
cms-nbi-client:dev

# Test images
cms-nbi-client:test
cms-nbi-client:mock-server
```

### Multi-Architecture Support

Images support multiple architectures:
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM64)
- `linux/arm/v7` (ARMv7)

## Service Configuration

### Application Service

```yaml
environment:
  # Connection settings
  - CMS_CONNECTION__HOST=${CMS_HOST}
  - CMS_CONNECTION__PROTOCOL=${CMS_PROTOCOL:-https}
  - CMS_CONNECTION__VERIFY_SSL=${CMS_VERIFY_SSL:-true}
  
  # Performance tuning
  - CMS_PERFORMANCE__CONNECTION_POOL_SIZE=${POOL_SIZE:-200}
  - CMS_PERFORMANCE__MAX_CONCURRENT_REQUESTS=${MAX_CONCURRENT:-100}
  - CMS_PERFORMANCE__CACHE_TTL=${CACHE_TTL:-300}
  
  # Redis caching
  - REDIS_URL=redis://redis:6379/0
```

### Redis Configuration

Optimized for caching with memory limits:

```yaml
command: redis-server 
  --appendonly yes 
  --maxmemory 256mb 
  --maxmemory-policy allkeys-lru
```

### Monitoring Stack

Prometheus and Grafana are pre-configured:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Health Checks

All services include health checks:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import cmsnbiclient; print('OK')"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

## Resource Limits

Production deployment includes resource constraints:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 256M
```

## Networking

Services use a dedicated bridge network:

```yaml
networks:
  production:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## Volume Management

Persistent data storage:

```yaml
volumes:
  redis-data:      # Redis persistence
  prometheus-data: # Metrics history
  grafana-data:    # Dashboard configs
```

## Security Considerations

### Non-Root User

All containers run as non-root user:

```dockerfile
RUN addgroup -g 1000 -S appuser && \
    adduser -u 1000 -S appuser -G appuser
USER appuser
```

### Secret Management

Use Docker secrets or environment files:

```bash
# Create secrets
echo "mypassword" | docker secret create cms_password -

# Use in compose
services:
  app:
    secrets:
      - cms_password
```

### Network Isolation

Services are isolated in custom networks with no unnecessary exposure.

## Logging

Centralized logging configuration:

```yaml
logging:
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"
```

## Backup and Recovery

### Backup Redis Data

```bash
# Backup Redis
docker compose -f docker compose.prod.yml exec redis redis-cli BGSAVE
docker cp $(docker compose -f docker compose.prod.yml ps -q redis):/data/dump.rdb ./redis-backup.rdb

# Restore Redis
docker cp ./redis-backup.rdb $(docker compose -f docker compose.prod.yml ps -q redis):/data/dump.rdb
docker compose -f docker compose.prod.yml restart redis
```

### Backup Prometheus Data

```bash
# Create snapshot
curl -XPOST http://localhost:9090/api/v1/admin/tsdb/snapshot

# Copy snapshot
docker cp $(docker compose -f docker compose.prod.yml ps -q prometheus):/prometheus/snapshots ./prometheus-backup
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose -f docker compose.prod.yml logs app

# Inspect container
docker compose -f docker compose.prod.yml run --rm app sh

# Check health
docker inspect $(docker compose -f docker compose.prod.yml ps -q app) | jq '.[0].State.Health'
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Increase limits
docker compose -f docker compose.prod.yml up -d --scale app=5

# Clear cache
docker compose -f docker compose.prod.yml exec redis redis-cli FLUSHALL
```

### Network Problems

```bash
# Test connectivity
docker compose -f docker compose.prod.yml exec app ping cms.example.com

# Check DNS
docker compose -f docker compose.prod.yml exec app nslookup cms.example.com
```

## CI/CD Integration

The project includes GitHub Actions workflows for:

1. **Building images** on every push
2. **Running tests** in Docker
3. **Security scanning** with Trivy
4. **Deploying** to staging/production

See `.github/workflows/` for details.

## Best Practices

1. **Always use specific versions** in production
2. **Set resource limits** to prevent resource exhaustion
3. **Use health checks** for all services
4. **Enable logging** with rotation
5. **Regular security updates** of base images
6. **Monitor resource usage** with Prometheus
7. **Backup persistent data** regularly
8. **Use secrets** for sensitive data

## Next Steps

- [Configuration Guide](configuration.md) - Detailed configuration options
- [Monitoring Guide](monitoring.md) - Set up monitoring and alerts
- [Security Guide](security.md) - Security best practices