# CMS-NBI-Client Documentation

This directory contains the source files for the CMS-NBI-Client documentation, built with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Building Documentation Locally

### Prerequisites

Install the documentation dependencies:

```bash
# Using pip
pip install mkdocs mkdocs-material mkdocstrings[python] pymdown-extensions

# Using Poetry
poetry install --with docs
```

### Build and Serve

To build and serve the documentation locally:

```bash
# Serve with live reload (development)
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

The documentation will be available at `http://localhost:8000`.

## Documentation Structure

```
docs/
├── index.md                 # Home page
├── guides/                  # User guides
│   ├── installation.md     # Installation guide
│   ├── quickstart.md       # Quick start tutorial
│   ├── configuration.md    # Configuration guide
│   ├── basic-usage.md      # Basic usage patterns
│   └── ...                 # Other guides
├── api/                    # API reference
│   ├── client.md          # Client API
│   ├── config.md          # Configuration API
│   └── ...                # Other API docs
├── examples/              # Code examples
│   ├── e7-operations.md   # E7 operation examples
│   └── ...                # Other examples
└── changelog.md           # Version history
```

## Writing Documentation

### Adding a New Page

1. Create a new Markdown file in the appropriate directory
2. Add the page to the navigation in `mkdocs.yml`
3. Follow the existing documentation style

### Documentation Style Guide

- Use clear, concise language
- Include code examples for all features
- Add type hints in code examples
- Use admonitions for warnings and tips
- Keep examples practical and runnable

### Code Examples

Always test code examples before including them:

```python
import asyncio
from cmsnbiclient import CMSClient, Config

async def example():
    config = Config(
        credentials={"username": "admin", "password": "secret"},
        connection={"host": "cms.example.com"}
    )
    
    async with CMSClient(config) as client:
        # Your example code here
        pass

asyncio.run(example())
```

## API Documentation

API documentation is automatically generated from docstrings using mkdocstrings. Follow Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> dict:
    """Brief description of the function.
    
    Longer description explaining what the function does,
    when to use it, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception is raised
        
    Example:
        ```python
        result = example_function("test", 42)
        print(result)
        ```
    """
    pass
```

## Contributing to Documentation

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the documentation locally
5. Submit a pull request

## Deployment

Documentation is automatically deployed to GitHub Pages when changes are pushed to the main branch via GitHub Actions.