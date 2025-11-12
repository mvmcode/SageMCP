"""Tests for CLI configuration management."""

import tempfile
from pathlib import Path

import pytest

from sage_mcp.cli.config import CLIConfig, ConfigManager, ProfileConfig


def test_profile_config_defaults():
    """Test ProfileConfig default values."""
    config = ProfileConfig()
    assert config.base_url == "http://localhost:8000"
    assert config.api_key is None
    assert config.output_format == "table"
    assert config.timeout == 30


def test_profile_config_custom():
    """Test ProfileConfig with custom values."""
    config = ProfileConfig(
        base_url="https://api.example.com",
        api_key="test-key",
        output_format="json",
        timeout=60,
    )
    assert config.base_url == "https://api.example.com"
    assert config.api_key == "test-key"
    assert config.output_format == "json"
    assert config.timeout == 60


def test_cli_config_defaults():
    """Test CLIConfig default values."""
    config = CLIConfig()
    assert config.profiles == {}
    assert config.settings.default_profile == "default"
    assert config.settings.auto_update is True
    assert config.settings.log_level == "INFO"


def test_config_manager_initialization():
    """Test ConfigManager initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = ConfigManager(config_dir)

        assert manager.config_dir == config_dir
        assert manager.config_file == config_dir / "config.toml"
        assert manager._config is None


def test_config_manager_ensure_config_dir():
    """Test configuration directory creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "test_config"
        manager = ConfigManager(config_dir)

        assert not config_dir.exists()
        manager.ensure_config_dir()
        assert config_dir.exists()


def test_config_manager_load_empty():
    """Test loading configuration when file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = ConfigManager(config_dir)

        config = manager.load()
        assert isinstance(config, CLIConfig)
        assert config.profiles == {}


def test_config_manager_save_and_load():
    """Test saving and loading configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = ConfigManager(config_dir)

        # Create and save config
        config = CLIConfig()
        config.profiles["test"] = ProfileConfig(base_url="https://test.com")
        manager.save(config)

        # Load and verify
        loaded_config = manager.load()
        assert "test" in loaded_config.profiles
        assert loaded_config.profiles["test"].base_url == "https://test.com"


def test_config_manager_add_profile():
    """Test adding a profile."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = ConfigManager(config_dir)

        manager.add_profile("prod", "https://api.prod.com", "secret-key")

        config = manager.load()
        assert "prod" in config.profiles
        assert config.profiles["prod"].base_url == "https://api.prod.com"
        assert config.profiles["prod"].api_key == "secret-key"


def test_config_manager_get_profile():
    """Test getting a profile."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = ConfigManager(config_dir)

        manager.add_profile("dev", "https://dev.com")
        manager.set_default_profile("dev")

        profile = manager.get_profile()
        assert profile.base_url == "https://dev.com"

        profile = manager.get_profile("dev")
        assert profile.base_url == "https://dev.com"


def test_config_manager_get_profile_not_found():
    """Test getting a non-existent profile."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = ConfigManager(config_dir)

        with pytest.raises(ValueError, match="Profile 'missing' not found"):
            manager.get_profile("missing")


def test_config_manager_delete_profile():
    """Test deleting a profile."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = ConfigManager(config_dir)

        manager.add_profile("test1", "https://test1.com")
        manager.add_profile("test2", "https://test2.com")
        manager.set_default_profile("test2")

        manager.delete_profile("test1")

        config = manager.load()
        assert "test1" not in config.profiles
        assert "test2" in config.profiles


def test_config_manager_delete_default_profile():
    """Test deleting the default profile raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = ConfigManager(config_dir)

        manager.add_profile("default", "https://default.com")
        manager.set_default_profile("default")

        with pytest.raises(ValueError, match="Cannot delete default profile"):
            manager.delete_profile("default")


def test_config_manager_set_default_profile():
    """Test setting default profile."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = ConfigManager(config_dir)

        manager.add_profile("prod", "https://prod.com")
        manager.set_default_profile("prod")

        config = manager.load()
        assert config.settings.default_profile == "prod"


def test_config_manager_set_default_profile_not_found():
    """Test setting non-existent profile as default raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = ConfigManager(config_dir)

        with pytest.raises(ValueError, match="Profile 'missing' not found"):
            manager.set_default_profile("missing")


def test_config_manager_list_profiles():
    """Test listing all profiles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = ConfigManager(config_dir)

        manager.add_profile("dev", "https://dev.com")
        manager.add_profile("staging", "https://staging.com")
        manager.add_profile("prod", "https://prod.com")

        profiles = manager.list_profiles()
        assert len(profiles) == 3
        assert "dev" in profiles
        assert "staging" in profiles
        assert "prod" in profiles


def test_config_manager_initialize_default():
    """Test initializing default configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = ConfigManager(config_dir)

        manager.initialize_default()

        config = manager.load()
        assert "default" in config.profiles
        assert config.profiles["default"].base_url == "http://localhost:8000"
