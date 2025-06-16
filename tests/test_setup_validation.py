"""Validation tests to ensure the testing infrastructure is properly configured."""

import os
import sys
from pathlib import Path

import pytest


class TestInfrastructureSetup:
    """Test class to validate the testing infrastructure setup."""
    
    def test_pytest_is_installed(self):
        """Verify that pytest is installed and importable."""
        assert pytest.__version__
        
    def test_modules_directory_in_path(self):
        """Verify that the modules directory is in the Python path."""
        workspace_path = Path(__file__).parent.parent
        assert str(workspace_path) in sys.path
        
    def test_can_import_modules(self):
        """Verify that we can import from the modules directory."""
        try:
            import modules.common
            assert modules.common
        except ImportError:
            pytest.fail("Failed to import modules.common")
    
    @pytest.mark.unit
    def test_unit_marker_works(self):
        """Verify that the unit test marker is recognized."""
        assert True
    
    @pytest.mark.integration
    def test_integration_marker_works(self):
        """Verify that the integration test marker is recognized."""
        assert True
    
    @pytest.mark.slow
    def test_slow_marker_works(self):
        """Verify that the slow test marker is recognized."""
        assert True
    
    def test_temp_dir_fixture(self, temp_dir):
        """Verify that the temp_dir fixture works correctly."""
        assert temp_dir.exists()
        assert temp_dir.is_dir()
        
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()
        assert test_file.read_text() == "test content"
    
    def test_mock_config_fixture(self, mock_config):
        """Verify that the mock_config fixture works correctly."""
        assert mock_config.get() == "mock_value"
        assert list(mock_config.items()) == [("key1", "value1"), ("key2", "value2")]
    
    def test_mock_os_env_fixture(self, mock_os_env):
        """Verify that the mock_os_env fixture works correctly."""
        assert os.environ["TEST_VAR"] == "test_value"
        assert os.environ["HOME"] == "/test/home"
        assert "TEST_VAR" in mock_os_env
    
    def test_sample_file_fixture(self, sample_file):
        """Verify that the sample_file fixture works correctly."""
        assert sample_file.exists()
        assert sample_file.is_file()
        assert sample_file.read_text() == "This is a sample file for testing."
    
    def test_mock_subprocess_fixture(self, mock_subprocess):
        """Verify that the mock_subprocess fixture works correctly."""
        import subprocess
        
        result = subprocess.run(["echo", "test"])
        assert result.returncode == 0
        assert result.stdout == "Success"
        assert mock_subprocess.called
    
    def test_mock_platform_fixture(self, mock_platform):
        """Verify that the mock_platform fixture works correctly."""
        import platform
        
        assert platform.system() == "Linux"
        assert platform.machine() == "x86_64"
        assert mock_platform["system"].called
        assert mock_platform["machine"].called
    
    def test_coverage_is_running(self):
        """Verify that coverage is active during test runs."""
        try:
            import coverage
            assert coverage
        except ImportError:
            pytest.fail("Coverage module not found")


class TestDirectoryStructure:
    """Test class to validate the directory structure."""
    
    def test_tests_directory_exists(self):
        """Verify that the tests directory exists."""
        tests_dir = Path(__file__).parent
        assert tests_dir.exists()
        assert tests_dir.name == "tests"
    
    def test_unit_directory_exists(self):
        """Verify that the unit tests directory exists."""
        unit_dir = Path(__file__).parent / "unit"
        assert unit_dir.exists()
        assert unit_dir.is_dir()
        assert (unit_dir / "__init__.py").exists()
    
    def test_integration_directory_exists(self):
        """Verify that the integration tests directory exists."""
        integration_dir = Path(__file__).parent / "integration"
        assert integration_dir.exists()
        assert integration_dir.is_dir()
        assert (integration_dir / "__init__.py").exists()
    
    def test_conftest_exists(self):
        """Verify that conftest.py exists."""
        conftest_file = Path(__file__).parent / "conftest.py"
        assert conftest_file.exists()
        assert conftest_file.is_file()