"""Centralized Qwen API configuration and management.

This module provides a centralized configuration system for Qwen API integration,
separating text and vision models to avoid configuration inconsistencies.

Usage:
    from app.core.qwen_config import qwen_config

    # For text conversations
    model = qwen_config.QWEN_CHAT_MODEL

    # For image recognition
    model = qwen_config.QWEN_VISION_MODEL

    # For API calls
    headers = qwen_config.get_headers()
    url = qwen_config.QWEN_API_URL
"""

from typing import Dict, Any
import os

# Import the main settings
from app.core.config import settings


class QwenConfig:
    """Centralized Qwen API configuration with separate text and vision models.

    This is a simple wrapper around the main settings to provide Qwen-specific
    configuration without conflicting with the main settings.
    """

    # API Credentials - read from main settings
    QWEN_API_KEY: str = settings.QWEN_API_KEY or ""

    # Base URLs
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_API_URL: str = f"{QWEN_BASE_URL}/chat/completions"

    # Model Configuration - read from main settings
    QWEN_TEXT_MODEL: str = settings.QWEN_TEXT_MODEL
    QWEN_VISION_MODEL: str = settings.QWEN_VISION_MODEL
    QWEN_CHAT_MODEL: str = "qwen-plus"  # Regular conversation model (fallback)
    QWEN_TURBO_MODEL: str = "qwen-turbo"  # Fast response model (same as text)

    # Timeout Settings (seconds)
    CHAT_TIMEOUT: float = 30.0
    VISION_TIMEOUT: float = 60.0

    # Retry Settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0

    # Temperature Settings
    CHAT_TEMPERATURE: float = 0.7
    VISION_TEMPERATURE: float = 0.3

    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Qwen API requests."""
        if not self.QWEN_API_KEY:
            raise ValueError(
                "QWEN_API_KEY is not set. Please configure it in .env file."
            )

        return {
            "Authorization": f"Bearer {self.QWEN_API_KEY}",
            "Content-Type": "application/json",
        }

    def get_model_for_purpose(self, purpose: str = "text") -> str:
        """Get the appropriate model for a given purpose.

        Args:
            purpose: One of "text", "chat", "vision", "turbo"

        Returns:
            Model name string

        Raises:
            ValueError: If purpose is not recognized
        """
        purpose = purpose.lower()
        if purpose == "text" or purpose == "chat":
            return self.QWEN_TEXT_MODEL
        elif purpose == "vision":
            return self.QWEN_VISION_MODEL
        elif purpose == "turbo":
            return self.QWEN_TURBO_MODEL
        else:
            raise ValueError(
                f"Unknown purpose: {purpose}. Use 'text', 'vision', or 'turbo'."
            )

    def get_timeout_for_model(self, model: str) -> float:
        """Get appropriate timeout for a model.

        Args:
            model: Model name

        Returns:
            Timeout in seconds
        """
        if "vl" in model.lower() or "vision" in model.lower():
            return self.VISION_TIMEOUT
        return self.CHAT_TIMEOUT

    def get_temperature_for_model(self, model: str) -> float:
        """Get appropriate temperature for a model.

        Args:
            model: Model name

        Returns:
            Temperature value
        """
        if "vl" in model.lower() or "vision" in model.lower():
            return self.VISION_TEMPERATURE
        return self.CHAT_TEMPERATURE

    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the configuration and return status.

        Returns:
            Dictionary with validation results
        """
        validation = {
            "api_key_configured": bool(self.QWEN_API_KEY),
            "chat_model": self.QWEN_CHAT_MODEL,
            "vision_model": self.QWEN_VISION_MODEL,
            "turbo_model": self.QWEN_TURBO_MODEL,
            "base_url": self.QWEN_BASE_URL,
            "api_url": self.QWEN_API_URL,
            "status": "valid" if bool(self.QWEN_API_KEY) else "missing_api_key",
        }

        return validation

    def __str__(self) -> str:
        """String representation of configuration (hides API key)."""
        return (
            f"QwenConfig("
            f"chat_model={self.QWEN_CHAT_MODEL}, "
            f"vision_model={self.QWEN_VISION_MODEL}, "
            f"turbo_model={self.QWEN_TURBO_MODEL}, "
            f"api_key_configured={bool(self.QWEN_API_KEY)}, "
            f"base_url={self.QWEN_BASE_URL})"
        )


# Singleton instance for application-wide use
qwen_config = QwenConfig()


def get_qwen_config() -> QwenConfig:
    """Get the singleton Qwen configuration instance.

    Returns:
        QwenConfig instance
    """
    return qwen_config


if __name__ == "__main__":
    # Test the configuration
    config = get_qwen_config()
    print("Qwen API Configuration:")
    print(f"  Chat Model: {config.QWEN_CHAT_MODEL}")
    print(f"  Vision Model: {config.QWEN_VISION_MODEL}")
    print(f"  Turbo Model: {config.QWEN_TURBO_MODEL}")
    print(f"  API Key Configured: {bool(config.QWEN_API_KEY)}")
    print(f"  Base URL: {config.QWEN_BASE_URL}")

    validation = config.validate_configuration()
    print("\nValidation Results:")
    for key, value in validation.items():
        print(f"  {key}: {value}")
