.PHONY: venv install test api cli-help clean help

# Default Python version
PYTHON := python3
VENV := venv
BIN := $(VENV)/bin

help:
	@echo "Music Track Generator - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  venv       - Create a virtual environment"
	@echo "  install    - Install dependencies in virtual environment"
	@echo "  test       - Run tests"
	@echo "  api        - Start the API server"
	@echo "  cli-help   - Show CLI help"
	@echo "  clean      - Remove virtual environment and cache files"
	@echo ""

venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created at ./$(VENV)"
	@echo "Activate with: source $(BIN)/activate"

install: venv
	@echo "Installing dependencies..."
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	$(BIN)/pip install -e .
	@echo "Installation complete!"

test:
	@echo "Running tests..."
	pytest tests/ -v

api:
	@echo "Starting API server..."
	@echo "Access the API at http://localhost:8080"
	@echo "API documentation at http://localhost:8080/docs"
	uvicorn music_generator.api:app --host 0.0.0.0 --port 8080

cli-help:
	@echo "Music Track Generator CLI Help"
	@echo "================================"
	@echo ""
	music-gen --help
	@echo ""
	@echo "Generate command help:"
	@echo "----------------------"
	music-gen generate --help

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf src/music_generator/__pycache__
	rm -rf tests/__pycache__
	rm -rf *.egg-info
	rm -rf build dist
	@echo "Cleanup complete!"
