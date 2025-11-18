"""Configuration management for the digest agent."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Config:
    """Configuration loader and manager."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration.

        Args:
            config_path: Path to YAML configuration file

        Raises:
            FileNotFoundError: If config file not found
            ValueError: If config is invalid
        """
        # Load environment variables from .env
        load_dotenv()

        # Load YAML configuration
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                f"Please copy config.yaml.example to config.yaml and configure it."
            )

        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # Validate configuration
        self._validate()

        # Create necessary directories
        self._create_directories()

    def _validate(self):
        """Validate required configuration fields."""
        required_fields = [
            'research_profile.profile_file',
            'llm.provider',
            'llm.model',
            'email.smtp_server',
            'email.sender_email',
        ]

        for field_path in required_fields:
            value = self.get(field_path)
            if value is None:
                raise ValueError(
                    f"Required configuration field missing: {field_path}"
                )

    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        dirs = self.config.get('directories', {})
        for dir_path in dirs.values():
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation path.

        Args:
            key_path: Dot-separated path (e.g., 'llm.model')
            default: Default value if key not found

        Returns:
            Configuration value

        Example:
            >>> config = Config()
            >>> config.get('llm.model')
            'gpt-4o-mini'
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_api_key(self, env_var_name: str) -> str:
        """Get API key from environment variable.

        Args:
            env_var_name: Name of environment variable

        Returns:
            API key value

        Raises:
            ValueError: If environment variable not found
        """
        api_key = os.getenv(env_var_name)
        if not api_key:
            raise ValueError(
                f"Environment variable '{env_var_name}' not found.\n"
                f"Please set it in your .env file.\n"
                f"See .env.example for template."
            )
        return api_key

    @property
    def research_profile(self) -> str:
        """Get research profile content.

        Returns:
            Contents of research profile markdown file

        Raises:
            FileNotFoundError: If profile file not found
        """
        profile_file = self.get('research_profile.profile_file')
        profile_path = Path(profile_file)

        if not profile_path.exists():
            raise FileNotFoundError(
                f"Research profile file not found: {profile_file}\n"
                f"Please copy my_research.md.example to {profile_file} "
                f"and edit it with your research interests."
            )

        with open(profile_path, 'r', encoding='utf-8') as f:
            return f.read()

    @property
    def llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration including API key.

        Returns:
            Dictionary with LLM config
        """
        llm = self.config.get('llm', {})
        api_key_env = llm.get('api_key_env', 'OPENAI_API_KEY')

        return {
            'provider': llm.get('provider', 'openai'),
            'model': llm.get('model', 'gpt-4o-mini'),
            'api_key': self.get_api_key(api_key_env),
            'temperature': llm.get('temperature', 0.3),
            'max_tokens': llm.get('max_tokens', 3000),
        }

    @property
    def email_config(self) -> Dict[str, Any]:
        """Get email configuration including credentials.

        Returns:
            Dictionary with email config
        """
        email = self.config.get('email', {})
        password_env = email.get('sender_password_env', 'GMAIL_APP_PASSWORD')

        return {
            'smtp_server': email.get('smtp_server'),
            'smtp_port': email.get('smtp_port', 587),
            'sender_email': email.get('sender_email'),
            'sender_password': self.get_api_key(password_env),
            'recipient_email': email.get('recipient_email'),
            'subject_prefix': email.get('subject_prefix', '[LLM Digest]'),
            'template': email.get('template', 'modern'),
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"Config(llm={self.get('llm.model')}, template={self.get('email.template')})"
