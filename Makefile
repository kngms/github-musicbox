.PHONY: help venv install test api cli-help clean clean-all

# Default target
help:
	@echo "Music Track Generator - Available targets:"
	@echo ""
	@echo "  make venv       - Create a virtual environment"
	@echo "  make install    - Install dependencies and package"
	@echo "  make test       - Run tests with pytest"
	@echo "  make api        - Start the API server"
	@echo "  make cli-help   - Show CLI help"
	@echo "  make clean      - Remove cache and build artifacts (preserves venv)"
	@echo "  make clean-all  - Remove everything including virtual environment"
	@echo ""

# Create virtual environment
venv:
	@if [ -d venv ]; then \
		echo "Virtual environment 'venv' already exists. Skipping creation."; \
	else \
		echo "Creating virtual environment..."; \
		python -m venv venv; \
		echo "Virtual environment created."; \
	fi
	@echo "Activate the virtual environment with:"
	@echo "  source venv/bin/activate  (Linux/Mac)"
	@echo "  venv\\Scripts\\activate     (Windows)"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	pip install -e .
	@echo "Installation complete!"

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v

# Start API server
api:
	@echo "Starting API server on http://0.0.0.0:8080"
	@echo "Press Ctrl+C to stop"
	uvicorn music_generator.api:app --host 0.0.0.0 --port 8080

# Define common clean commands
CLEAN_FIND_COMMANDS = find . -type d \( -name "__pycache__" -o -name "*.egg-info" -o -name ".pytest_cache" \) -prune -exec rm -rf {} + 2>/dev/null || true

# Show CLI help
cli-help:
	@echo "Music Track Generator CLI Commands:"
	@echo ""
	music-gen --help
	@echo ""
	@echo "Generate command options:"
	@echo ""
	music-gen generate --help

# Clean up cache and artifacts (preserves venv)
clean:
	@echo "Cleaning cache and build artifacts..."
	@$(CLEAN_FIND_COMMANDS)
	@echo "Clean complete!"

# Clean up everything including virtual environment
clean-all:
	@echo "Cleaning everything including venv..."
	rm -rf venv
	@$(CLEAN_FIND_COMMANDS)
	@echo "Clean complete!"
