# Installation Guide

This guide covers various ways to install CMS-NBI-Client in your environment.

## Requirements

- **Python**: 3.9 or higher
- **Operating System**: Linux, macOS, or Windows
- **Network**: Access to CMS instance

## Installation Methods

### Using pip (Recommended)

The simplest way to install CMS-NBI-Client is using pip:

```bash
pip install cms-nbi-client
```

For a specific version:

```bash
pip install cms-nbi-client==2.0.0
```

### Using Poetry

If you're using Poetry for dependency management:

```bash
poetry add cms-nbi-client
```

### From Source

To install the latest development version from GitHub:

```bash
# Clone the repository
git clone https://github.com/somenetworking/CMS-NBI-Client.git
cd CMS-NBI-Client

# Install with pip
pip install .

# Or install with Poetry
poetry install
```

### Development Installation

For development work, install in editable mode with development dependencies:

```bash
# Clone the repository
git clone https://github.com/somenetworking/CMS-NBI-Client.git
cd CMS-NBI-Client

# Using pip
pip install -e ".[dev]"

# Using Poetry (recommended for development)
poetry install --with dev
```

## Dependency Management

### Core Dependencies

The following packages are automatically installed:

- `aiohttp`: Async HTTP client
- `pydantic`: Data validation
- `structlog`: Structured logging
- `defusedxml`: Secure XML parsing
- `cryptography`: Encryption support
- `tenacity`: Retry logic

### Optional Dependencies

For additional features:

```bash
# For YAML configuration support
pip install cms-nbi-client[yaml]

# For development tools
pip install cms-nbi-client[dev]

# For documentation generation
pip install cms-nbi-client[docs]

# All extras
pip install cms-nbi-client[all]
```

## Virtual Environments

We strongly recommend using a virtual environment:

### Using venv

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install
pip install cms-nbi-client
```

### Using conda

```bash
# Create environment
conda create -n cms-nbi python=3.9

# Activate
conda activate cms-nbi

# Install
pip install cms-nbi-client
```

## Verifying Installation

After installation, verify it's working:

```python
python -c "import cmsnbiclient; print(cmsnbiclient.__version__)"
# Output: 2.0.0
```

Or check from command line:

```bash
pip show cms-nbi-client
```

## Docker Installation

For containerized environments:

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Install CMS-NBI-Client
RUN pip install cms-nbi-client

# Your application
COPY . /app
WORKDIR /app

CMD ["python", "app.py"]
```

## Platform-Specific Notes

### Linux

Most Linux distributions include Python 3.9+. If not:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev

# RHEL/CentOS
sudo yum install python39 python39-devel

# Arch
sudo pacman -S python
```

### macOS

Using Homebrew:

```bash
brew install python@3.9
```

### Windows

1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Use PowerShell or Command Prompt for installation

## Troubleshooting

### Import Error

If you get `ModuleNotFoundError: No module named 'cmsnbiclient'`:

1. Ensure you've activated your virtual environment
2. Verify installation: `pip list | grep cms-nbi-client`
3. Check Python path: `python -c "import sys; print(sys.path)"`

### SSL Certificate Errors

If you encounter SSL errors:

```python
from cmsnbiclient import Config

config = Config(
    connection={"verify_ssl": False}  # Only for testing!
)
```

For production, properly configure certificates instead.

### Permission Errors

On Linux/macOS, you might need to use `pip install --user` or run with appropriate permissions.

### Dependency Conflicts

If you have dependency conflicts:

1. Create a fresh virtual environment
2. Install cms-nbi-client first
3. Then install other packages

## Next Steps

- [Quick Start Guide](quickstart.md) - Get started with your first script
- [Configuration Guide](configuration.md) - Learn about configuration options
- [Basic Usage](basic-usage.md) - Explore common use cases