#!/bin/bash
# Script to run tests with proper environment setup

# Set library path for WeasyPrint on macOS
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH

# Install test dependencies if needed
if ! python -c "import pytest" 2>/dev/null; then
    echo "Installing test dependencies..."
    pip install pytest pytest-cov httpx
fi

# Run tests
echo "Running tests..."
python -m pytest tests/ -v "$@"
