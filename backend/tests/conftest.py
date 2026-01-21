"""Pytest configuration and fixtures."""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add repo root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set environment variable for WeasyPrint
os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/lib'

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from backend.main import app
    return TestClient(app)

@pytest.fixture
def test_book_id():
    """Return a test book ID that exists in the books directory."""
    return "学会提问（原书第12版）_data"

@pytest.fixture
def alt_book_id():
    """Return an alternative test book ID."""
    return "关键跃升：新任管理者成事的底层逻辑_data"
