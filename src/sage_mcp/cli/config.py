"""Configuration management for SageMCP CLI."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import toml
from pydantic import BaseModel, Field


class ProfileConfig(BaseModel):
    """Configuration for a single profile."""

    base_url: str = Field(default="http://localhost:8000", description="API base URL")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    output_format: str = Field(default="table", description="Default output format")
    timeout: int = Field(default=30, description="Request timeout in seconds")


class CLISettings(BaseModel):
    """Global CLI settings."""

    default_profile: str = Field(default="default", description="Default profile name")
    auto_update: bool = Field(default=True, description="Auto-update check")
    log_level: str = Field(default="INFO", description="Logging level")


class CLIConfig(BaseModel):
    """Main CLI configuration."""

    profiles: Dict[str, ProfileConfig] = Field(default_factory=dict)
    settings: CLISettings = Field(default_factory=CLISettings)


class ConfigManager:
    """Manages CLI configuration files."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_dir: Configuration directory path. Defaults to ~/.sage-mcp
        """
        self.config_dir = config_dir or Path.home() / ".sage-mcp"
        self.config_file = self.config_dir / "config.toml"
        self._config: Optional[CLIConfig] = None

    def ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> CLIConfig:
        """Load configuration from file.

        Returns:
            CLIConfig instance
        """
        if self._config:
            return self._config

        if not self.config_file.exists():
            self._config = CLIConfig()
            return self._config

        try:
            with open(self.config_file, "r") as f:
                data = toml.load(f)
                self._config = CLIConfig(**data)
                return self._config
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}")

    def save(self, config: Optional[CLIConfig] = None) -> None:
        """Save configuration to file.

        Args:
            config: Configuration to save. If None, saves current config.
        """
        self.ensure_config_dir()
        cfg = config or self._config or CLIConfig()

        with open(self.config_file, "w") as f:
            toml.dump(cfg.model_dump(), f)

        self._config = cfg

    def get_profile(self, profile_name: Optional[str] = None) -> ProfileConfig:
        """Get profile configuration.

        Args:
            profile_name: Profile name. If None, uses default profile.

        Returns:
            ProfileConfig instance

        Raises:
            ValueError: If profile not found
        """
        config = self.load()
        name = profile_name or config.settings.default_profile

        if name not in config.profiles:
            raise ValueError(f"Profile '{name}' not found")

        return config.profiles[name]

    def add_profile(
        self, name: str, base_url: str, api_key: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Add or update a profile.

        Args:
            name: Profile name
            base_url: API base URL
            api_key: Optional API key
            **kwargs: Additional profile settings
        """
        config = self.load()
        config.profiles[name] = ProfileConfig(
            base_url=base_url, api_key=api_key, **kwargs
        )
        self.save(config)

    def delete_profile(self, name: str) -> None:
        """Delete a profile.

        Args:
            name: Profile name

        Raises:
            ValueError: If profile not found or is default profile
        """
        config = self.load()

        if name not in config.profiles:
            raise ValueError(f"Profile '{name}' not found")

        if name == config.settings.default_profile:
            raise ValueError("Cannot delete default profile")

        del config.profiles[name]
        self.save(config)

    def set_default_profile(self, name: str) -> None:
        """Set default profile.

        Args:
            name: Profile name

        Raises:
            ValueError: If profile not found
        """
        config = self.load()

        if name not in config.profiles:
            raise ValueError(f"Profile '{name}' not found")

        config.settings.default_profile = name
        self.save(config)

    def list_profiles(self) -> Dict[str, ProfileConfig]:
        """List all profiles.

        Returns:
            Dictionary of profile names to configs
        """
        config = self.load()
        return config.profiles

    def initialize_default(self) -> None:
        """Initialize default configuration."""
        config = CLIConfig()
        config.profiles["default"] = ProfileConfig()
        self.save(config)


# Global config manager instance
config_manager = ConfigManager()
