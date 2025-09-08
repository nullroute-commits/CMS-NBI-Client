#!/bin/bash
# Check Docker, Docker Compose, and Docker Buildx versions

set -e

echo "Checking Docker versions..."
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Required versions
REQUIRED_DOCKER_VERSION="24.0"
REQUIRED_COMPOSE_VERSION="2.21"
REQUIRED_BUILDX_VERSION="0.12"

# Function to compare versions
version_gt() {
    test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"
}

# Check Docker version
echo -n "Docker Engine: "
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    echo -n "$DOCKER_VERSION"
    
    if version_gt "$DOCKER_VERSION" "$REQUIRED_DOCKER_VERSION"; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗ (requires $REQUIRED_DOCKER_VERSION+)${NC}"
        exit 1
    fi
else
    echo -e "${RED}Not installed${NC}"
    exit 1
fi

# Check Docker Compose version
echo -n "Docker Compose: "
if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | sed 's/v//')
    echo -n "v$COMPOSE_VERSION"
    
    if version_gt "$COMPOSE_VERSION" "$REQUIRED_COMPOSE_VERSION"; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗ (requires v$REQUIRED_COMPOSE_VERSION+)${NC}"
        exit 1
    fi
else
    echo -e "${RED}Not installed or not v2${NC}"
    echo -e "${YELLOW}Note: Docker Compose v2 is included in Docker Engine 20.10+${NC}"
    exit 1
fi

# Check Docker Buildx version
echo -n "Docker Buildx: "
if docker buildx version &> /dev/null; then
    BUILDX_VERSION=$(docker buildx version | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | sed 's/v//' | head -1)
    echo -n "v$BUILDX_VERSION"
    
    if version_gt "$BUILDX_VERSION" "$REQUIRED_BUILDX_VERSION"; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗ (requires v$REQUIRED_BUILDX_VERSION+)${NC}"
        exit 1
    fi
else
    echo -e "${RED}Not installed${NC}"
    echo -e "${YELLOW}Note: Docker Buildx is included in Docker Desktop${NC}"
    exit 1
fi

# Check BuildKit
echo -n "BuildKit: "
if [[ "$DOCKER_BUILDKIT" == "1" ]] || docker info 2>/dev/null | grep -q "buildkit"; then
    echo -e "${GREEN}Enabled ✓${NC}"
else
    echo -e "${YELLOW}Not enabled (recommended)${NC}"
    echo -e "${YELLOW}Enable with: export DOCKER_BUILDKIT=1${NC}"
fi

echo ""
echo -e "${GREEN}All required versions are installed!${NC}"
echo ""
echo "Additional recommendations:"
echo "- Use 'docker compose' (v2) instead of 'docker-compose' (v1)"
echo "- Enable BuildKit for better performance: export DOCKER_BUILDKIT=1"
echo "- For multi-platform builds, ensure QEMU is set up"