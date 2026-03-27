.PHONY: install test lint format build clean

install:
	pip install -e ".[dev]"

test:
	pytest -v --tb=short

test-cov:
	pytest -v --cov=typermd --cov-report=term-missing

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

build:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info src/*.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
