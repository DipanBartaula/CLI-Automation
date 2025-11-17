import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "content": "Test response",
        "role": "assistant",
        "finish_reason": "stop"
    }

@pytest.fixture
def mock_tool_call():
    """Mock tool call for testing."""
    return {
        "id": "call_123",
        "name": "test_tool",
        "arguments": {"param": "value"}
    }
