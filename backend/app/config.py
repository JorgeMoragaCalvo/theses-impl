import logging
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

"""
Configuration management for the AI Tutoring System.
Loads environment variables and provides application settings.
"""

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # LLM Provider Configuration
    llm_provider: Literal["gemini", "google", "openai", "anthropic"] = "gemini"

    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"

    # Anthropic Configuration
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Gemini Configuration
    google_api_key: str = ""
    google_model: str = "gemini-2.5-flash-lite"

    # Database Configuration
    # database_url: str = "postgresql://postgres:postgres123@localhost:5432/security"
    database_url: str
    database_echo: bool = False # True prints all SQL queries to console

    # Chroma Vector Store Configuration
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "course_materials"

    # Application Configuration
    version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"

    # Backend API Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # Frontend Configuration
    frontend_host: str = "localhost"
    frontend_port: int = 8501
    backend_url: str = f"http://localhost:{backend_port}"

    # Session and Authentication Configuration
    secret_key: str = "your-secret-key-change-this-in-production-min-32-chars"  # Must be changed in .env
    session_timeout_minutes: int = 60
    access_token_expire_days: int = 7  # JWT token expiration

    # LLM Configuration
    temperature: float = 0.4
    max_tokens: int = 2000

    @property
    def current_api_key(self) -> str:
        """Get the API key for the currently selected LLM provider."""
        if self.llm_provider == "gemini" or self.llm_provider == "google":
            return self.google_api_key
        elif self.llm_provider == "openai":
            return self.openai_api_key
        return self.anthropic_api_key

    @property
    def current_model(self) -> str:
        """Get the model name for the currently selected LLM provider."""
        if self.llm_provider == "gemini" or self.llm_provider == "google":
            return self.google_model
        elif self.llm_provider == "openai":
            return self.openai_model
        return self.anthropic_model

    def model_post_init(self, __context):
        """Validate settings after initialization."""
        # Log the loaded SECRET_KEY (first/last 4 chars only for security)
        if len(self.secret_key) >= 8:
            masked_key = f"{self.secret_key[:4]}...{self.secret_key[-4:]}"
        else:
            masked_key = "***"
        logger.info(f"Loaded SECRET_KEY: {masked_key}")

        # Warn if using a default/insecure key
        if self.secret_key in [
            "secret",
            "your_secret_key_here",
            "your-secret-key-change-this-in-production-min-32-chars"
        ]:
            logger.warning(
                "⚠️  WARNING: Using default SECRET_KEY! "
                "This is INSECURE for production. "
                "Generate a secure key: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )


# Global settings instance
settings = Settings()
