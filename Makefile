PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
VENV_PYTHON := $(VENV)/bin/python

.PHONY: init dev test lint

init:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	cd frontend/src && npm install

dev:
	@echo "Launching backend and frontend. Press Ctrl+C to stop."
	@$(VENV_PYTHON) run_dev.py

test:
	$(VENV)/bin/pytest

