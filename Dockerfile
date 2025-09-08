# syntax=docker/dockerfile:1.6
# Multi-stage build for minimal image size
# Requires Docker BuildKit (DOCKER_BUILDKIT=1)
FROM python:3.11-alpine AS builder

# Install build dependencies
# Use BuildKit cache mount for package manager cache
RUN --mount=type=cache,target=/var/cache/apk \
    apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    libxml2-dev \
    libxslt-dev \
    cargo \
    && pip install --upgrade pip poetry

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Export requirements from Poetry
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Production stage
FROM python:3.11-alpine

# Install runtime dependencies only
RUN apk add --no-cache \
    libxml2 \
    libxslt \
    libffi \
    openssl \
    ca-certificates \
    curl \
    && pip install --upgrade pip

# Create non-root user
RUN addgroup -g 1000 -S appuser && \
    adduser -u 1000 -S appuser -G appuser

# Set working directory
WORKDIR /app

# Copy requirements and install
# Use BuildKit cache mount for pip cache
COPY --from=builder /app/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set Python path
ENV PYTHONPATH=/app/src

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import cmsnbiclient; print('OK')" || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "cmsnbiclient"]