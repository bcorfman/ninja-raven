SHELL := env PYTHON_VERSION=3.12 /bin/bash
.SILENT: setup install devinstall tools test run lint format compose-up compose-down migrate docker-build docker-run

PYTHON_VERSION ?= 3.12

# Install uv and prepare the environment
setup:
	curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
install:
	uv python pin $(PYTHON_VERSION)
	uv sync --frozen --no-dev

devinstall:
	uv python pin $(PYTHON_VERSION)
	uv add pytest pytest-cov --dev
	uv sync --all-extras --dev

# Install tools
tools:
	uv tool install ruff --force
	uv tool install ipython --force

# Run tests
test:
	uv run pytest

# Run the Django project
run:
	uv run python manage.py runserver

# Lint code
lint:
	uv tool run ruff check -q

# Format code
format:
	uv tool run ruff format

# Docker-Compose Tasks
compose-up:
	docker-compose up -d

compose-down:
	docker-compose down

# Django Management Commands
migrate:
	uv run python manage.py migrate

# Initialize the Database and Services Locally
init-local: compose-up devinstall migrate

# Build Docker Image
docker-build:
	docker build -t checkers-backend .

# Run Docker Container
docker-run:
	docker run -p 8000:8000 checkers-backend

# Run All Tasks
all: setup devinstall tools lint format test
