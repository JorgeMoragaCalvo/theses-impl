from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

"""
Configuration management for the AI Tutoring System.
Loads environment variables and provides application settings.
"""

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # LLM Provider Configuration
    llm_provider: Literal["openai", "anthropic"] = "openai"

    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"

    # Anthropic Configuration
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost:5432/security"
    database_echo: bool = False

    # Chroma Vector Store Configuration
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "course_materials"

    # Application Configuration
    debug: bool = True
    log_level: str = "INFO"

    # Backend API Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # Frontend Configuration
    fronted_host: str = "localhost"
    frontend_port: int = 8501
    backend_url: str = f"http://localhost:{backend_port}"

    # Session Configuration
    secret_key: str = "secret"
    session_timeout_minutes: int = 60

    # LLM Configuration
    temperature: float = 0.4
    max_tokens: int = 1000

    @property
    def current_api_key(self) -> str:
        """Get the API key for the currently selected LLM provider."""
        if self.llm_provider == "openai":
            return self.openai_api_key
        return self.anthropic_api_key

    @property
    def current_model(self) -> str:
        """Get the model name for the currently selected LLM provider."""
        if self.llm_provider == "openai":
            return self.openai_model
        return self.anthropic_model

# Global settings instance
settings = Settings()