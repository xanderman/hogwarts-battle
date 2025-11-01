# Makefile for Hogwarts Battle

.PHONY: help test test-verbose clean

# Default target
help:
	@echo "Hogwarts Battle - Available Make Commands"
	@echo ""
	@echo "  make test          Run all unit tests"
	@echo "  make test-verbose  Run all unit tests with verbose output"
	@echo "  make clean         Remove Python cache files and test artifacts"
	@echo "  make help          Show this help message"

# Run all unit tests
test:
	@echo "Running unit tests..."
	@python3 -m unittest discover -s tests/unit -p "test_*.py"

# Run tests with verbose output
test-verbose:
	@echo "Running unit tests (verbose)..."
	@python3 -m unittest discover -s tests/unit -p "test_*.py" -v

# Clean up Python cache files
clean:
	@echo "Cleaning Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete!"
