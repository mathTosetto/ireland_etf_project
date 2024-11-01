.ONESHELL:

# Default Python version
PYTHON_VERSION ?= 3.11

VENV = .venv

# Determine OS and set paths accordingly
ifeq ($(OS),Windows_NT)
    PYTHON = $(VENV)/Scripts/python
    PIP = $(VENV)/Scripts/pip
    BIN = $(VENV)/Scripts
    ACTIVATE = $(VENV)/Scripts/activate
else
    PYTHON = $(VENV)/bin/python
    PIP = $(VENV)/bin/pip
    BIN = $(VENV)/bin
    ACTIVATE = $(VENV)/bin/activate
endif

UV = $(BIN)/uv

# Default target
init: clean venv setup_dependencies show-info activate

# Clean up files
clean:
	rm -rf $(VENV) cdk.out build dist **/*.egg-info .pytest_cache node_modules .coverage .ruff_cache

# Create .venv with specified Python version
venv:
	python3 -m venv $(VENV)

# Download the necessary libs
setup_dependencies:
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install uv
	$(UV) pip install -r requirements.txt

# Pre-commit setup
setup_precommit:
	@echo "Setting up the pre-commit config"
	pre-commit clean
	pre-commit install
	pre-commit autoupdate

# Show Python version and paths
show-info:
	@echo "OS: $(OS)"
	@echo "Python path: $(PYTHON)"
	@echo "Pip path: $(PIP)"
	@echo "Bin directory: $(BIN)"
	@echo "Activate script: $(ACTIVATE)"
	@echo "Using Python version: $(PYTHON_VERSION)"
	@$(PYTHON) --version

# Target to remind how to activate the virtual environment
activate:
	@echo "To activate the virtual environment, run:"
	@echo ""
	@echo "On Windows (CMD):"
	@echo "    $(ACTIVATE)"
	@echo ""
	@echo "On Windows (PowerShell):"
	@echo "    & $(ACTIVATE)"
	@echo ""
	@echo "On Unix-like systems (Linux, macOS):"
	@echo "    source $(ACTIVATE)"

# Mark targets as phony
.PHONY: init clean venv setup_dependencies setup_precommit show-info activate