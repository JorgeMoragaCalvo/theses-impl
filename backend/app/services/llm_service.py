import logging
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

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

    def _get_llm_with_overrides(self, temperature: float | None = None, max_tokens: int | None = None):
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

    @staticmethod
    def _execute_tool(tools: list[BaseTool], tool_name: str, tool_args: dict | str) -> str:
        """
        Execute a tool by name with given arguments.

        Args:
            tools: List of available tools
            tool_name: Name of the tool to execute
            tool_args: Arguments to pass to the tool

        Returns:
            Tool execution result as string
        """
        for tool in tools:
            if tool.name == tool_name:
                try:
                    # Handle both dict args and string args
                    if isinstance(tool_args, dict):
                        result = tool.run(tool_args)
                    else:
                        result = tool.run(tool_args)
                    logger.info(f"Tool '{tool_name}' executed successfully")
                    return str(result)
                except Exception as e:
                    logger.error(f"Tool '{tool_name}' execution error: {e}")
                    return f"Error executing tool '{tool_name}': {str(e)}"
        return f"Tool '{tool_name}' not found"

    def generate_response_with_tools(
        self,
        messages: list[dict[str, str]],
        tools: list[BaseTool],
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        max_tool_iterations: int = 3
    ) -> str:
        """
        Generate a response with tool calling support.

        The LLM can decide to call tools, and this method handles the
        tool execution loop until a final response is generated.

        Args:
            messages: Conversation history as list of dicts with 'role' and 'content'
            tools: List of LangChain tools to make available to the LLM
            system_prompt: Optional system prompt to prepend
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            max_tool_iterations: Maximum number of tool call iterations (default 3)

        Returns:
            Final generated response text after tool execution

        Raises:
            Exception: If LLM call fails
        """
        try:
            # Prepend the system message if provided
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages

            # Convert to LangChain messages
            langchain_messages = self._convert_message(messages)

            # Get LLM with overrides and bind tools
            llm = self._get_llm_with_overrides(temperature, max_tokens)
            llm_with_tools = llm.bind_tools(tools)

            # Tool execution loop
            for iteration in range(max_tool_iterations):
                response = llm_with_tools.invoke(langchain_messages)

                # Check if there are tool calls
                if not hasattr(response, 'tool_calls') or not response.tool_calls:
                    # No tool calls, return the content
                    logger.info(f"Generated response with tools (iteration {iteration + 1}): {len(response.content)} chars")
                    return response.content

                # Add AI message with tool calls to conversation
                langchain_messages.append(response)

                # Execute each tool call
                for tool_call in response.tool_calls:
                    tool_name = tool_call.get("name", "")
                    tool_args = tool_call.get("args", {})
                    tool_id = tool_call.get("id", "")

                    logger.info(f"Executing tool '{tool_name}' with args: {tool_args}")

                    # Execute the tool
                    tool_result = self._execute_tool(tools, tool_name, tool_args)

                    # Add tool result to messages
                    langchain_messages.append(
                        ToolMessage(content=tool_result, tool_call_id=tool_id)
                    )

            # Max iterations reached, get final response without tools
            logger.warning(f"Max tool iterations ({max_tool_iterations}) reached")
            final_response = llm.invoke(langchain_messages)
            return final_response.content

        except Exception as e:
            logger.error(f"Error in generate_response_with_tools: {str(e)}")
            raise

    async def a_generate_response_with_tools(
        self,
        messages: list[dict[str, str]],
        tools: list[BaseTool],
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        max_tool_iterations: int = 3
    ) -> str:
        """
        Async version of generate_response_with_tools.

        Args:
            messages: Conversation history
            tools: List of LangChain tools to make available
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            max_tool_iterations: Maximum tool call iterations

        Returns:
            Final generated response text after tool execution
        """
        try:
            # Prepend the system message if provided
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages

            # Convert to LangChain messages
            langchain_messages = self._convert_message(messages)

            # Get LLM with overrides and bind tools
            llm = self._get_llm_with_overrides(temperature, max_tokens)
            llm_with_tools = llm.bind_tools(tools)

            # Tool execution loop
            for iteration in range(max_tool_iterations):
                response = await llm_with_tools.ainvoke(langchain_messages)

                # Check if there are tool calls
                if not hasattr(response, 'tool_calls') or not response.tool_calls:
                    logger.info(f"Generated async response with tools (iteration {iteration + 1}): {len(response.content)} chars")
                    return response.content

                # Add AI message with tool calls to conversation
                langchain_messages.append(response)

                # Execute each tool call
                for tool_call in response.tool_calls:
                    tool_name = tool_call.get("name", "")
                    tool_args = tool_call.get("args", {})
                    tool_id = tool_call.get("id", "")

                    logger.info(f"Executing tool '{tool_name}' with args: {tool_args}")

                    # Execute the tool (tools are sync, but that's okay)
                    tool_result = self._execute_tool(tools, tool_name, tool_args)

                    # Add tool result to messages
                    langchain_messages.append(
                        ToolMessage(content=tool_result, tool_call_id=tool_id)
                    )

            # Max iterations reached
            logger.warning(f"Max tool iterations ({max_tool_iterations}) reached")
            final_response = await llm.ainvoke(langchain_messages)
            return final_response.content

        except Exception as e:
            logger.error(f"Error in a_generate_response_with_tools: {str(e)}")
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
