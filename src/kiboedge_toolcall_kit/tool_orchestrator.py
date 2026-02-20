"""Responsibility: run tool-calling workflow sequentially with parser fallback and retries."""

from __future__ import annotations

import json
from typing import Any

from .config import RuntimeConfiguration
from .lfm_tool_call_parser import LfmToolCallParser
from .lmstudio_client import LmStudioChatClient
from .models import ParsedToolCall
from .prompt_templates import build_repair_prompt_for_parse_failure, build_tool_call_system_prompt
from .tool_validation import validate_tool_call_against_schema


class ToolCallEngine:
    """Sequential tool-calling engine that handles LFM dialect quirks."""

    def __init__(
        self,
        runtime_configuration: RuntimeConfiguration,
        chat_client: LmStudioChatClient,
        tool_schemas: list[dict[str, Any]],
        tool_executor_map: dict[str, Any],
        parser: LfmToolCallParser | None = None,
        system_prompt_text: str | None = None,
    ) -> None:
        self._runtime_configuration = runtime_configuration
        self._chat_client = chat_client
        self._tool_schemas = tool_schemas
        self._tool_executor_map = tool_executor_map
        self._parser = parser if parser is not None else LfmToolCallParser()
        self._system_prompt_text = system_prompt_text or build_tool_call_system_prompt()

    def run_tool_call_round(
        self,
        user_prompt: str,
    ) -> dict[str, Any]:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt_text},
            {"role": "user", "content": user_prompt},
        ]

        repair_attempt_count = 0
        executed_tool_calls: list[ParsedToolCall] = []
        for tool_call_round_index in range(self._runtime_configuration.max_tool_call_rounds_per_request):
            response = self._chat_client.create_chat_completion(
                messages=messages,
                tools=self._tool_schemas,
                tool_choice="auto",
            )
            message = response.choices[0].message
            parsed_tool_calls = self._parser.parse_from_message(message)

            # Guard: parse failure should trigger bounded repair retries.
            if not parsed_tool_calls:
                if repair_attempt_count >= self._runtime_configuration.max_repair_attempts:
                    return {
                        "is_success": False,
                        "failure_reason": "parse_failure",
                        "source": "none",
                        "tool_name": None,
                        "arguments": None,
                        "assistant_content": getattr(message, "content", None),
                    }

                messages.append(
                    {
                        "role": "user",
                        "content": build_repair_prompt_for_parse_failure(),
                    }
                )
                repair_attempt_count += 1
                continue

            executed_in_this_round = self._execute_parsed_tool_calls_sequentially(
                parsed_tool_calls=parsed_tool_calls,
                messages=messages,
                tool_call_round_index=tool_call_round_index,
            )
            if not executed_in_this_round["is_success"]:
                return executed_in_this_round

            executed_tool_calls.extend(executed_in_this_round["executed_tool_calls"])

            # Guard: after successful tool execution, ask model for final answer without tools.
            final_response = self._chat_client.create_chat_completion(messages=messages, tools=[], tool_choice="none")
            if not executed_tool_calls:
                continue
            last_tool_call = executed_tool_calls[-1]
            return {
                "is_success": True,
                "failure_reason": None,
                "source": last_tool_call.source,
                "tool_name": last_tool_call.tool_name,
                "arguments": last_tool_call.arguments,
                "assistant_content": final_response.choices[0].message.content,
            }

        return {
            "is_success": False,
            "failure_reason": "max_tool_round_exceeded",
            "source": "none",
            "tool_name": None,
            "arguments": None,
            "assistant_content": None,
        }

    def _execute_parsed_tool_calls_sequentially(
        self,
        parsed_tool_calls: list[ParsedToolCall],
        messages: list[dict[str, Any]],
        tool_call_round_index: int,
    ) -> dict[str, Any]:
        executed_tool_calls: list[ParsedToolCall] = []
        for tool_call_index, parsed_tool_call in enumerate(parsed_tool_calls):
            validation_result = validate_tool_call_against_schema(
                tool_name=parsed_tool_call.tool_name,
                arguments=parsed_tool_call.arguments,
                tool_schemas=self._tool_schemas,
            )
            if not validation_result.is_success:
                return {
                    "is_success": False,
                    "failure_reason": validation_result.failure_reason,
                    "source": parsed_tool_call.source,
                    "tool_name": parsed_tool_call.tool_name,
                    "arguments": parsed_tool_call.arguments,
                    "assistant_content": None,
                    "executed_tool_calls": executed_tool_calls,
                }

            tool_result_payload = self._execute_tool(parsed_tool_call)
            tool_call_identifier = self._build_tool_call_identifier(tool_call_round_index, tool_call_index)
            messages.append(self._build_assistant_tool_call_message(parsed_tool_call, tool_call_identifier))
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_identifier,
                    "content": json.dumps(tool_result_payload, ensure_ascii=True),
                }
            )
            executed_tool_calls.append(parsed_tool_call)

        return {
            "is_success": True,
            "failure_reason": None,
            "source": executed_tool_calls[-1].source if executed_tool_calls else "none",
            "tool_name": executed_tool_calls[-1].tool_name if executed_tool_calls else None,
            "arguments": executed_tool_calls[-1].arguments if executed_tool_calls else None,
            "assistant_content": None,
            "executed_tool_calls": executed_tool_calls,
        }

    def _execute_tool(self, parsed_tool_call: ParsedToolCall) -> dict[str, Any]:
        tool_name = parsed_tool_call.tool_name

        # Guard: only registered tools can be executed.
        if tool_name not in self._tool_executor_map:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}

        return self._tool_executor_map[tool_name](parsed_tool_call.arguments)

    def _build_assistant_tool_call_message(
        self,
        parsed_tool_call: ParsedToolCall,
        tool_call_identifier: str,
    ) -> dict[str, Any]:
        return {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": tool_call_identifier,
                    "type": "function",
                    "function": {
                        "name": parsed_tool_call.tool_name,
                        "arguments": json.dumps(parsed_tool_call.arguments, ensure_ascii=True),
                    },
                }
            ],
        }

    def _build_tool_call_identifier(self, tool_call_round_index: int, tool_call_index: int) -> str:
        return f"local-tool-call-{tool_call_round_index + 1}-{tool_call_index + 1}"
