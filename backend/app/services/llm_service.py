import logging
from typing import Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from ..config import settings

"""
LLM Service - Abstraction layer for different LLM providers.
Supports both Gemini, OpenAI and Anthropic with easy switching via configuration.
"""

logger = logging.getLogger(__name__)

class LLMService:
    """
    Service for interacting with LLM providers.
    Provides a unified interface for OpenAI and Anthropic.
    """

    def __init__(self):
        """Initialize LLM service with configured provider."""
        self.provider = settings.llm_provider
        self.llm = self._initialize_llm()
        logger.info(f"LLMService initialized with provider: {self.provider}")

    def _initialize_llm(self):
        """
        Initialize the appropriate LLM based on configuration.

        Returns:
            LLM instance (ChatGoogleGenerativeAI, ChatOpenAI, or ChatAnthropic)

        Raises:
            ValueError: If the provider is not supported, or the API key is missing
        """
        if self.provider == "gemini" or self.provider == "google":
            if not settings.google_api_key:
                raise ValueError("Google API key not configured. Please set GOOGLE_API_KEY in .env file.")

            return ChatGoogleGenerativeAI(
                model=settings.google_model,
                temperature=settings.temperature,
                max_output_tokens=settings.max_tokens,
                google_api_key=settings.google_api_key
            )

        elif self.provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in .env file.")

            return ChatOpenAI(
                tiktoken_model_name=settings.openai_model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                openai_api_key=settings.openai_api_key
            )

        elif self.provider == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic model not configured. Please set ANTHROPIC_API_KEY in .env file.")

            return ChatAnthropic(
                model=settings.anthropic_model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                anthropic_api_key=settings.anthropic_api_key
            )
        else:
            raise ValueError(
                f"Unsupported LLM provider: {self.provider}. "
                f"Please set LLM_PROVIDER in .env file to 'gemini', 'openai' or 'anthropic'."
            )

    def _get_llm_with_overrides(self, temperature: Optional[float] = None, max_tokens: int | None = None):
        """
        Get LLM instance with optional parameter overrides.

        Args:
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override

        Returns:
            LLM instance with overrides applied if provided, else default
        """
        if temperature is not None or max_tokens is not None:
            if self.provider == "gemini" or self.provider == "google":
                return ChatGoogleGenerativeAI(
                    model=settings.google_model,
                    temperature=temperature or settings.temperature,
                    max_output_tokens=max_tokens or settings.max_tokens,
                    google_api_key=settings.google_api_key
                )
            elif self.provider == "openai":
                return ChatOpenAI(
                    tiktoken_model_name=settings.openai_model,
                    temperature=temperature or settings.temperature,
                    max_tokens=max_tokens or settings.max_tokens,
                    openai_api_key=settings.openai_api_key
                )
            else:
                return ChatAnthropic(
                    model=settings.anthropic_model,
                    temperature=temperature or settings.temperature,
                    max_tokens=max_tokens or settings.max_tokens,
                    anthropic_api_key=settings.anthropic_api_key
                )
        else:
            return self.llm

    @staticmethod
    def _convert_message(messages: list[dict[str, str]]) -> list:
        """
        Convert message dictionaries to LangChain message objects.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            List of LangChain message objects
        """
        langchain_messages = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else: # user or any other role
                langchain_messages.append(HumanMessage(content=content))

        return langchain_messages

    def generate_response(self, messages: list[dict[str, str]],
                          system_prompt: str | None = None,
                          temperature: float | None= None,
                          max_tokens: int | None = None) -> str:
        """
        Generate a response from the LLM.

        Args:
            messages: Conversation history as the list of dicts with 'role' and 'content'
            system_prompt: Optional system prompt to prepend
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override

        Returns:
            Generated response text

        Raises:
            Exception: If LLM call fails
        """
        try:
            # Prepend the system message if provided
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages

            # Convert to LangChain messages
            langchain_messages = self._convert_message(messages)

            # Update LLM parameters if overrides provided
            llm = self._get_llm_with_overrides(temperature, max_tokens)

            # Generate response
            response = llm.invoke(langchain_messages)

            # Extract content
            response_text = response.content

            logger.info(f"Generated response with {self.provider}: {len(response_text)} characters")
            return response_text
        except Exception as e:
            logger.error(f"Error generating response with {self.provider}: {str(e)}")
            raise

    async def a_generate_response(self, messages: list[dict[str, str]],
                                  system_prompt: str | None = None,
                                  temperature: float | None= None,
                                  max_tokens: int | None = None) -> str:
        """
        Async version of generate_response.

        Args:
            messages: Conversation history
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override

        Returns:
            Generated response text
        """
        try:
            # Prepend the system message if provided
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages

            # Convert to LangChain messages
            langchain_messages = self._convert_message(messages)

            # Update LLM parameters if overrides provided
            llm = self._get_llm_with_overrides(temperature, max_tokens)

            # Generate response asynchronously
            response = await llm.ainvoke(langchain_messages)
            response_text = response.content

            logger.info(f"Generated async response with {self.provider}: {len(response_text)} characters")
            return response_text
        except Exception as e:
            logger.error(f"Error generating async response with {self.provider}: {str(e)}")
            raise

    def get_provider_info(self) -> dict[str, Any]:
        """
        Get information about the current LLM provider.

        Returns:
            Dictionary with provider information
        """
        return {
            "provider": self.provider,
            "model": settings.current_model,
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens
        }

# Global LLM service instance
_llm_service: LLMService | None = None

def get_llm_service() -> LLMService:
    """
    Get or create the global LLM service instance.

    Returns:
        LLMService instance
    """
    global _llm_service

    if _llm_service is None:
        _llm_service = LLMService()

    return _llm_service
