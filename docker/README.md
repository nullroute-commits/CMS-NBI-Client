# Docker Setup for CMS-NBI-Client

This directory contains Docker-related configurations for the CMS-NBI-Client project.

## Version Requirements

This project requires the following minimum versions:

- **Docker Engine**: 24.0+ (includes Docker Compose v2)
- **Docker Compose**: v2.21+ (included in Docker Engine)
- **Docker Buildx**: v0.12+ (included in Docker Desktop)

### Checking Your Versions

Run the provided script to verify your Docker installation:

```bash
./scripts/check-docker-versions.sh
```

Or manually check:

```bash
docker --version
docker compose version
docker buildx version
```

## Key Features

### 1. Docker Compose v2

We use Docker Compose v2 (the `docker compose` command, not `docker-compose`). Key improvements:

- Better performance
- Improved error messages
- Native Docker CLI integration
- Compose Specification support

### 2. Docker Buildx

All images are built with Docker Buildx, providing:

- Multi-platform builds (amd64, arm64, arm/v7)
- Advanced caching strategies
- BuildKit features

### 3. BuildKit Optimizations

Our Dockerfiles use BuildKit features:

- Cache mounts for package managers
- Multi-stage builds
- Layer caching optimization
- Parallel builds

Enable BuildKit:
```bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
```

## Directory Structure

```
docker/
├── README.md                 # This file
├── prometheus/              # Prometheus configuration
│   └── prometheus.yml       # Prometheus scrape configs
├── grafana/                 # Grafana configuration
│   └── provisioning/        # Auto-provisioning
│       ├── dashboards/      # Dashboard definitions
│       └── datasources/     # Data source configs
└── nginx/                   # NGINX configuration (optional)
    ├── nginx.conf           # Main config
    └── conf.d/              # Site configurations
```

## Building Images

### Development Build

```bash
# Build with BuildKit
DOCKER_BUILDKIT=1 docker compose build

# Build specific service
docker compose build app

# Build with no cache
docker compose build --no-cache
```

### Production Build

```bash
# Multi-platform build
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  --tag cms-nbi-client:latest \
  --push .
```

## Compose Files

- `docker-compose.yml` - Development environment
- `docker-compose.test.yml` - Testing environment
- `docker-compose.prod.yml` - Production deployment
- `docker-compose.override.yml` - Local overrides (gitignored)

## Best Practices

1. **Always use BuildKit**: Set `DOCKER_BUILDKIT=1`
2. **Use specific versions**: Pin image versions in production
3. **Layer caching**: Order Dockerfile commands for optimal caching
4. **Multi-stage builds**: Keep final images small
5. **Security scanning**: Run Trivy on all images

## Troubleshooting

### BuildKit Not Enabled

```bash
# Enable for current session
export DOCKER_BUILDKIT=1

# Enable permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export DOCKER_BUILDKIT=1' >> ~/.bashrc
```

### Compose v2 Not Found

```bash
# Install Docker Engine (includes Compose v2)
curl -fsSL https://get.docker.com | sh

# Or install Compose plugin manually
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

### Multi-platform Builds Failing

```bash
# Set up QEMU for cross-platform builds
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

# Create and use buildx builder
docker buildx create --name multibuilder --use
docker buildx inspect --bootstrap
```

## Monitoring Stack

The production stack includes:

- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Redis**: Caching layer

Access URLs (production):
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## Security Notes

- All images run as non-root user (uid 1000)
- Secrets are never baked into images
- Use BuildKit secrets for sensitive data during build
- Regular security scanning with Trivy

## Updates

To update Docker components:

1. **Docker Desktop**: Download latest from docker.com
2. **Docker Engine**: Use your package manager
3. **Buildx**: Updated with Docker Desktop/Engine

Keep images updated:
```bash
# Pull latest base images
docker compose pull

# Rebuild with latest
docker compose build --pull
```