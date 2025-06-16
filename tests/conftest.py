"""Shared pytest fixtures and configuration for all tests."""

import os
import sys
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Add the modules directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_config() -> MagicMock:
    """Create a mock configuration object."""
    config = MagicMock()
    config.get.return_value = "mock_value"
    config.items.return_value = [("key1", "value1"), ("key2", "value2")]
    return config


@pytest.fixture
def mock_os_env() -> Generator[dict, None, None]:
    """Mock environment variables for testing."""
    original_env = os.environ.copy()
    test_env = {
        "TEST_VAR": "test_value",
        "HOME": "/test/home",
        "PATH": "/test/bin:/usr/bin",
    }
    
    with patch.dict(os.environ, test_env, clear=True):
        yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_file(temp_dir: Path) -> Path:
    """Create a sample file in the temporary directory."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("This is a sample file for testing.")
    return file_path


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls for testing."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Success"
        mock_run.return_value.stderr = ""
        yield mock_run


@pytest.fixture
def mock_platform():
    """Mock platform information for cross-platform testing."""
    with patch("platform.system") as mock_system:
        mock_system.return_value = "Linux"
        with patch("platform.machine") as mock_machine:
            mock_machine.return_value = "x86_64"
            yield {"system": mock_system, "machine": mock_machine}


@pytest.fixture
def clean_imports():
    """Clean up imported modules to ensure test isolation."""
    modules_before = set(sys.modules.keys())
    yield
    modules_after = set(sys.modules.keys())
    
    # Remove any modules imported during the test
    for module in modules_after - modules_before:
        if module.startswith("modules."):
            sys.modules.pop(module, None)


@pytest.fixture(autouse=True)
def reset_cwd():
    """Reset the current working directory after each test."""
    original_cwd = os.getcwd()
    yield
    os.chdir(original_cwd)


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers descriptions
    config.addinivalue_line("markers", "unit: Mark test as a unit test")
    config.addinivalue_line("markers", "integration: Mark test as an integration test")
    config.addinivalue_line("markers", "slow: Mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add unit marker to tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to tests in integration directory
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)