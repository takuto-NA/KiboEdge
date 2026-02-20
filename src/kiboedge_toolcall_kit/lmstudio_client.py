"""Responsibility: call LM Studio OpenAI-compatible Chat Completions endpoint."""

from typing import Any

from openai import OpenAI

from .config import RuntimeConfiguration


class LmStudioChatClient:
    """Small wrapper around OpenAI SDK configured for LM Studio."""

    def __init__(self, runtime_configuration: RuntimeConfiguration) -> None:
        self._runtime_configuration = runtime_configuration
        self._openai_client = OpenAI(
            base_url=runtime_configuration.base_url,
            api_key=runtime_configuration.api_key,
            timeout=runtime_configuration.request_timeout_seconds,
        )

    def create_chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_choice: str = "auto",
    ) -> Any:
        """Send one Chat Completions request to LM Studio."""
        return self._openai_client.chat.completions.create(
            model=self._runtime_configuration.model_name,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=self._runtime_configuration.response_temperature,
            max_tokens=self._runtime_configuration.max_generation_tokens,
        )
