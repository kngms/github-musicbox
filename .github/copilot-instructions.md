# Music Track Generator - Copilot Instructions

## Project Overview

This is a Python-based music track generation system with CLI and REST API interfaces. The project supports two modes:
- **Simulate mode** (default): No GCP credentials required, generates prompts and metadata for development/testing
- **GCP mode**: Production deployment with Google Cloud Vertex AI integration

**Tech Stack:**
- Python 3.9+
- FastAPI for REST API
- Click for CLI interface
- Pydantic for data validation
- PyYAML for preset management
- Google Cloud Platform (Vertex AI) - optional

## Build, Test, and Lint Commands

### Installation
```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .

# Or use Makefile
make install
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Or use Makefile
make test
```

### Running the Application
```bash
# CLI - List presets
music-gen list-presets

# CLI - Generate track (simulate mode)
music-gen generate --text "Your lyrics" --genre rock --preset rock_anthem

# API Server
uvicorn music_generator.api:app --host 0.0.0.0 --port 8080
# Or use: make api

# Docker
docker build -t music-track-generator .
docker run -p 8080:8080 music-track-generator
```

## Project Structure

```
src/music_generator/
├── __init__.py
├── api.py           # FastAPI REST API server
├── cli.py           # Click-based CLI interface
├── generator.py     # Music generation logic (simulate/gcp modes)
├── models.py        # Pydantic data models
└── presets.py       # Preset management system

presets/             # Built-in YAML preset configurations
tests/              # pytest test suite
examples/           # Usage examples
docs/              # Documentation
```

## Code Style and Conventions

### Python Style
- Follow PEP 8 conventions
- Use type hints for function parameters and return values
- Use Pydantic models for data validation and structure
- Use descriptive variable names (e.g., `duration_seconds`, `text_input`)
- Use docstrings for classes and non-trivial functions

### Naming Conventions
- Snake_case for variables, functions, and module names
- PascalCase for class names
- UPPER_CASE for constants and environment variables
- Prefix private methods/attributes with underscore `_`

### Import Organization
1. Standard library imports
2. Third-party library imports (google-cloud, pydantic, fastapi, etc.)
3. Local application imports
4. Blank line between each group

Example:
```python
import os
from pathlib import Path

from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException

from music_generator.models import TrackConfig
from music_generator.presets import PresetManager
```

### Error Handling
- Use FastAPI's HTTPException for API errors with appropriate status codes
- Use Click's ClickException for CLI errors
- Log errors with appropriate severity levels
- Provide meaningful error messages to users

### Logging
- Use Python's built-in `logging` module
- Log configuration details at INFO level on startup
- Log errors at ERROR level
- Use structured log messages (not f-strings directly in log calls)

### Environment Variables
- Use descriptive names with `MUSIC_GEN_` prefix
- Provide defaults for optional variables
- Document all environment variables in README
- Use `python-dotenv` for local development

## Testing Practices

### Test Structure
- Place all tests in `tests/` directory
- Use `pytest` framework
- Name test files with `test_` prefix (e.g., `test_api.py`)
- Name test functions with `test_` prefix

### Test Coverage
- Test both simulate and GCP modes when applicable
- Test API endpoints with various inputs (valid, invalid, edge cases)
- Test CLI commands
- Test preset management (load, save, delete)
- Test error handling and validation

### Test Fixtures
- Use pytest fixtures for common setup (e.g., test client, sample data)
- Keep fixtures in test files or `conftest.py`

### Mocking
- Mock external services (GCP Vertex AI) in tests
- Use environment variables to control test behavior
- Ensure tests can run without GCP credentials

## Git Workflow

### Commits
- Write clear, descriptive commit messages
- Use present tense ("Add feature" not "Added feature")
- Keep commits focused and atomic
- Reference issue numbers when applicable

### Branches
- Create feature branches from main
- Use descriptive branch names (e.g., `feature/add-preset`, `fix/api-validation`)
- Keep branches up to date with main

### Pull Requests
- Ensure all tests pass before creating PR
- Update documentation if changing functionality
- Add tests for new features
- Keep PRs focused on a single feature or fix

## Boundaries and Restrictions

### DO NOT Modify
- **Built-in preset files** in `presets/` directory unless specifically requested
- **Docker configuration** (Dockerfile, .dockerignore) unless deployment-related changes
- **Setup.py package configuration** unless adding new dependencies
- **GitHub workflows** unless specifically working on CI/CD

### Security Considerations
- Never commit API keys, credentials, or secrets
- Use environment variables for sensitive configuration
- Validate all user inputs (API and CLI)
- Follow security best practices for FastAPI endpoints
- Be careful with file operations (path traversal, etc.)

### Backwards Compatibility
- Maintain API endpoint compatibility when making changes
- Deprecate features before removing them
- Keep CLI command structure consistent
- Document breaking changes clearly

### Dependencies
- Only add new dependencies if absolutely necessary
- Prefer Python standard library when possible
- Keep dependencies up to date but test compatibility
- Add new dependencies to both `requirements.txt` and `setup.py`

## Mode-Specific Guidance

### Simulate Mode (Default)
- Should work without any GCP credentials
- Return mock responses with realistic structure
- Log that operation is simulated
- Perfect for development and testing

### GCP Mode
- Requires `GOOGLE_CLOUD_PROJECT` environment variable
- Uses Google Cloud Vertex AI
- Should gracefully handle missing credentials
- Should provide clear error messages about missing configuration

## API Development

### FastAPI Endpoints
- Use proper HTTP status codes (200, 201, 400, 401, 404, 500)
- Include request/response models with Pydantic
- Add endpoint descriptions and OpenAPI tags
- Implement proper error handling
- Support API key authentication when configured

### Request/Response Models
- Use Pydantic models for validation
- Include Field descriptions for API documentation
- Use proper types and constraints
- Provide examples for complex models

## CLI Development

### Click Commands
- Use descriptive option names with short flags
- Provide helpful descriptions for all options
- Include examples in help text
- Use appropriate option types (int, float, choice, etc.)
- Validate inputs with Click parameters

### User Experience
- Provide clear success/error messages
- Use colors/formatting with `rich` library when helpful
- Show progress for long-running operations
- Exit with appropriate status codes (0 for success, non-zero for errors)

## Documentation

- Keep README.md up to date with feature changes
- Document all CLI commands and options
- Document all API endpoints
- Include examples for common use cases
- Update environment variable documentation
- Add inline comments for complex logic only
- Use docstrings for public APIs

## Common Patterns

### Adding a New Preset
1. Create YAML file in `presets/` directory
2. Include all required fields (name, description, genre, structure, etc.)
3. Add tips for users
4. Test loading and using the preset

### Adding a New CLI Command
1. Add command function to `cli.py`
2. Use Click decorators for options/arguments
3. Add input validation
4. Provide helpful error messages
5. Add tests for the command

### Adding a New API Endpoint
1. Add route to `api.py`
2. Define Pydantic request/response models in `models.py`
3. Add appropriate authentication if needed
4. Handle errors with proper HTTP status codes
5. Add tests for success and error cases
6. Update API documentation

## Performance Considerations

- Lazy load presets only when needed
- Cache preset data when appropriate
- Use async/await for I/O operations when applicable
- Keep API response times reasonable
- Log performance metrics for long operations
