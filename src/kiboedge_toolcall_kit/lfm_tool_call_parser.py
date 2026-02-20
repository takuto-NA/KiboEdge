"""Responsibility: parse tool calls robustly across LM Studio and LFM output dialects."""

from __future__ import annotations

import ast
import json
import re
from typing import Any

from .models import ParsedToolCall

TOOL_CALL_XML_PATTERN = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)
LFM_TOOL_CALL_BLOCK_PATTERN = re.compile(
    r"<\|tool_call_start\|>\s*(.*?)\s*<\|tool_call_end\|>",
    re.DOTALL,
)
GENERIC_JSON_OBJECT_PATTERN = re.compile(r"\{.*\}", re.DOTALL)
PYTHON_STYLE_CALL_PATTERN = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)", re.DOTALL)


class LfmToolCallParser:
    """Parser that prefers structured tool_calls and falls back to content parsing."""

    def parse_from_message(self, message: Any) -> list[ParsedToolCall]:
        if hasattr(message, "tool_calls") and message.tool_calls:
            parsed_from_tool_calls = self._parse_openai_tool_calls(message.tool_calls)
            if parsed_from_tool_calls:
                return parsed_from_tool_calls

        content_text = getattr(message, "content", None)
        if not content_text:
            return []

        parsed_from_xml_tag = self._parse_from_tool_call_xml(content_text)
        if parsed_from_xml_tag:
            return parsed_from_xml_tag

        parsed_from_lfm_tokens = self._parse_from_lfm_special_tokens(content_text)
        if parsed_from_lfm_tokens:
            return parsed_from_lfm_tokens

        parsed_from_generic_json = self._parse_from_generic_json(content_text)
        if parsed_from_generic_json:
            return parsed_from_generic_json

        parsed_from_python_style = self._parse_from_python_style_call(content_text)
        if parsed_from_python_style:
            return parsed_from_python_style

        return []

    def _parse_openai_tool_calls(self, tool_calls: list[Any]) -> list[ParsedToolCall]:
        parsed_tool_calls: list[ParsedToolCall] = []
        for tool_call in tool_calls:
            raw_arguments = tool_call.function.arguments
            parsed_arguments = self._try_parse_json_object(raw_arguments)

            # Guard: arguments must be a JSON object.
            if parsed_arguments is None:
                continue

            parsed_tool_calls.append(
                ParsedToolCall(
                    tool_name=tool_call.function.name,
                    arguments=parsed_arguments,
                    source="message_tool_calls",
                    raw_payload=raw_arguments,
                )
            )
        return parsed_tool_calls

    def _parse_from_tool_call_xml(self, content_text: str) -> list[ParsedToolCall]:
        matches = TOOL_CALL_XML_PATTERN.findall(content_text)
        return self._parse_json_payload_matches(matches, "content_tool_call_xml")

    def _parse_from_lfm_special_tokens(self, content_text: str) -> list[ParsedToolCall]:
        blocks = LFM_TOOL_CALL_BLOCK_PATTERN.findall(content_text)
        normalized_blocks: list[str] = []
        for block in blocks:
            normalized_blocks.append(block.strip())
        return self._parse_json_payload_matches(normalized_blocks, "content_lfm_special_tokens")

    def _parse_from_generic_json(self, content_text: str) -> list[ParsedToolCall]:
        candidate_json = GENERIC_JSON_OBJECT_PATTERN.search(content_text)
        if candidate_json is None:
            return []

        return self._parse_json_payload_matches([candidate_json.group(0)], "content_generic_json")

    def _parse_json_payload_matches(self, payload_matches: list[str], source: str) -> list[ParsedToolCall]:
        parsed_tool_calls: list[ParsedToolCall] = []
        for payload_text in payload_matches:
            parsed_payload = self._try_parse_json_object(payload_text)
            if parsed_payload is None:
                continue

            parsed_tool_call = self._build_parsed_tool_call_from_json_payload(
                parsed_payload=parsed_payload,
                payload_text=payload_text,
                source=source,
            )
            if parsed_tool_call is None:
                continue

            parsed_tool_calls.append(parsed_tool_call)
        return parsed_tool_calls

    def _build_parsed_tool_call_from_json_payload(
        self,
        parsed_payload: dict[str, Any],
        payload_text: str,
        source: str,
    ) -> ParsedToolCall | None:
        tool_name = parsed_payload.get("name")
        arguments_value = parsed_payload.get("arguments")

        # Guard: payload must include a valid tool name.
        if not isinstance(tool_name, str) or not tool_name.strip():
            return None

        # Guard: arguments should resolve to an object.
        if isinstance(arguments_value, str):
            parsed_arguments = self._try_parse_json_object(arguments_value)
            if parsed_arguments is None:
                return None
            return ParsedToolCall(
                tool_name=tool_name.strip(),
                arguments=parsed_arguments,
                source=source,
                raw_payload=payload_text,
            )

        if isinstance(arguments_value, dict):
            return ParsedToolCall(
                tool_name=tool_name.strip(),
                arguments=arguments_value,
                source=source,
                raw_payload=payload_text,
            )

        return None

    def _parse_from_python_style_call(self, content_text: str) -> list[ParsedToolCall]:
        match = PYTHON_STYLE_CALL_PATTERN.search(content_text.strip())
        if match is None:
            return []

        tool_name = match.group(1)
        raw_argument_string = match.group(2).strip()

        # Guard: empty argument list is valid and should produce an empty object.
        if raw_argument_string == "":
            return [ParsedToolCall(tool_name=tool_name, arguments={}, source="content_python_style", raw_payload=content_text)]

        parsed_arguments = self._try_parse_python_keyword_arguments(raw_argument_string)
        if parsed_arguments is None:
            return []

        return [
            ParsedToolCall(
                tool_name=tool_name,
                arguments=parsed_arguments,
                source="content_python_style",
                raw_payload=content_text,
            )
        ]

    def _try_parse_json_object(self, payload_text: str) -> dict[str, Any] | None:
        try:
            parsed_value = json.loads(payload_text)
        except json.JSONDecodeError:
            return None

        if not isinstance(parsed_value, dict):
            return None
        return parsed_value

    def _try_parse_python_keyword_arguments(self, raw_argument_string: str) -> dict[str, Any] | None:
        # Guard: only parse pure keyword argument forms.
        if "=" not in raw_argument_string:
            return None

        argument_segments = [segment.strip() for segment in raw_argument_string.split(",") if segment.strip()]
        parsed_arguments: dict[str, Any] = {}
        for argument_segment in argument_segments:
            if "=" not in argument_segment:
                return None

            key_text, value_text = argument_segment.split("=", 1)
            key_name = key_text.strip()
            try:
                parsed_value = ast.literal_eval(value_text.strip())
            except (ValueError, SyntaxError):
                return None
            parsed_arguments[key_name] = parsed_value
        return parsed_arguments
