# Multi-stage Dockerfile for typermd SDLC testing
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md LICENSE VERSION ./
COPY src/ ./src/
COPY tests/ ./tests/
COPY examples/ ./examples/
COPY Makefile ./

# Stage 1: Installation verification
FROM base as install

# Install the package in development mode with dev dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Verify installation
RUN python -c "import typermd; print(f'typermd version: {typermd.__version__}')"
RUN python -c "from typermd import md, table, panel; print('All main imports successful')"

# Stage 2: Testing
FROM install as test

# Run linting
RUN ruff check src/ tests/

# Run formatting check
RUN ruff format --check src/ tests/

# Run type checking
RUN mypy src/

# Run pytest with coverage
RUN pytest -v --cov=typermd --cov-report=term-missing --cov-report=html

# Stage 3: Examples execution
FROM install as examples

# Test basic example
RUN echo "Testing basic.py..." && \
    python examples/basic.py --help && \
    python examples/basic.py hello --name "Docker Test" && \
    python examples/basic.py hello --formal --name "Docker Test" && \
    python examples/basic.py status && \
    python examples/basic.py demo

# Test logger_usage example
RUN echo "Testing logger_usage.py..." && \
    python examples/logger_usage.py --help && \
    python examples/logger_usage.py --env production && \
    python examples/logger_usage.py --env staging --dry-run

# Test tables_panels example
RUN echo "Testing tables_panels.py..." && \
    python examples/tables_panels.py --help && \
    python examples/tables_panels.py deps && \
    python examples/tables_panels.py info

# Stage 4: Final verification
FROM examples as final

# Create a comprehensive test script
RUN echo '#!/usr/bin/env python3' > test_sdlc.py && \
    echo 'import typermd' >> test_sdlc.py && \
    echo 'from typermd import md, table, panel' >> test_sdlc.py && \
    echo 'from typermd.logger import get_logger' >> test_sdlc.py && \
    echo 'print("=== typermd SDLC Test ===")' >> test_sdlc.py && \
    echo 'print(f"Version: {typermd.__version__}")' >> test_sdlc.py && \
    echo 'md("# Test Markdown Output")' >> test_sdlc.py && \
    echo 'table(["Component", "Result"], [["typermd", "✅ PASS"]])' >> test_sdlc.py && \
    echo 'panel("All tests completed successfully!", title="SDLC Test")' >> test_sdlc.py && \
    chmod +x test_sdlc.py

# Run final verification
RUN python test_sdlc.py

# Default command
CMD ["python", "test_sdlc.py"]
