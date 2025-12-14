# Makefile for xclip-win32yank-wrapper project

# Default target
.PHONY: all
default: help

# Help command
.PHONY: help
help:
	@echo "xclip-win32yank-wrapper Makefile"
	@echo ""
	@echo "Commands:"
	@echo "  make setup          - Create virtual environment and install dependencies"
	@echo "  make test           - Run all tests"
	@echo "  make test-all       - Run all tests with verbose output"
	@echo "  make test-quick     - Run quick validation tests only"
	@echo "  make test-comprehensive - Run comprehensive tests"
	@echo "  make test-pyperclip - Run pyperclip compatibility tests"
	@echo "  make test-simple    - Run simple validation tests"
	@echo "  make test-wrapper   - Run xclip wrapper tests"
	@echo "  make clean          - Clean up test cache and build artifacts"
	@echo "  make help           - Show this help message"

# Setup virtual environment and install dependencies
.PHONY: setup
setup:
	@echo "Setting up virtual environment..."
	python3 -m venv venv 2>/dev/null || echo "Virtual environment already exists"
	@echo "Installing dependencies..."
	./venv/bin/pip install -r requirements.txt
	@echo "Setup complete!"
	@echo ""
	@echo "To activate the virtual environment, run:"
	@echo "  source venv/bin/activate"

# Run all tests
.PHONY: test
test: test-all

# Run all tests with verbose output
.PHONY: test-all
test-all:
	@echo "Running all tests..."
	./venv/bin/pytest tests/ -v --tb=short

# Run quick validation tests only
.PHONY: test-quick
test-quick:
	@echo "Running quick validation tests..."
	./venv/bin/pytest tests/test_simple.py -v --tb=short

# Run comprehensive tests
.PHONY: test-comprehensive
test-comprehensive:
	@echo "Running comprehensive tests..."
	./venv/bin/pytest tests/test_comprehensive.py -v --tb=short

# Run pyperclip compatibility tests
.PHONY: test-pyperclip
test-pyperclip:
	@echo "Running pyperclip compatibility tests..."
	./venv/bin/pytest tests/test_pyperclip_compatibility.py -v --tb=short

# Run xclip wrapper tests
.PHONY: test-wrapper
test-wrapper:
	@echo "Running xclip wrapper tests..."
	./venv/bin/pytest tests/test_xclip_wrapper.py -v --tb=short

# Clean up test cache and build artifacts
.PHONY: clean
clean:
	@echo "Cleaning up..."
	rm -rf .pytest_cache
	rm -rf **/__pycache__
	rm -rf **/*.pyc
	@echo "Clean complete!"

# Install xclip wrapper to PATH
.PHONY: install
install:
	@echo "Installing xclip wrapper to ~/.local/bin..."
	mkdir -p ~/.local/bin
	cp xclip ~/.local/bin/
	chmod +x ~/.local/bin/xclip
	@echo "Installation complete!"
	@echo "You may need to add ~/.local/bin to your PATH or log out and back in."
