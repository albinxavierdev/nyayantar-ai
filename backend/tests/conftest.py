"""
Test configuration and fixtures for document generation tests
"""
import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock
from datetime import datetime

# Set up test environment
os.environ["TESTING"] = "true"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017/test_db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_directory():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_legal_service():
    """Mock legal service for testing"""
    service = Mock()
    service.get_legal_response = AsyncMock(return_value="Mock AI response")
    return service


@pytest.fixture
def sample_document_data():
    """Sample document data for testing"""
    return {
        "applicant_name": "John Doe",
        "case_number": "ABC123",
        "offense": "Theft",
        "ipc_section": "379",
        "incident_date": "15/12/2023",
        "applicant_relation": "legal counsel",
        "court_name": "District Court of New Delhi",
        "court_address": "123 Court Street, New Delhi",
        "your_name": "Lawyer Name",
        "your_address": "456 Law Street, New Delhi",
        "your_contact": "+91-9876543210"
    }


@pytest.fixture
def sample_user():
    """Sample user for testing"""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "name": "Test User"
    }


@pytest.fixture
def sample_conversation():
    """Sample conversation for testing"""
    return {
        "id": "test-conversation-123",
        "user_id": "test-user-123",
        "title": "Test Conversation",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
