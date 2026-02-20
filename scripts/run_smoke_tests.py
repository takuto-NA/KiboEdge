"""Responsibility: perform lightweight smoke tests for parser and schema validation logic."""

from kiboedge_toolcall_kit.lfm_tool_call_parser import LfmToolCallParser
from kiboedge_toolcall_kit.tool_schemas import build_tool_schemas
from kiboedge_toolcall_kit.tool_validation import validate_tool_call_against_schema


class DummyOpenAiFunction:
    """Simple shape-matching stub for OpenAI SDK function payload."""

    def __init__(self, name: str, arguments: str) -> None:
        self.name = name
        self.arguments = arguments


class DummyOpenAiToolCall:
    """Simple shape-matching stub for OpenAI SDK tool call payload."""

    def __init__(self, function_name: str, function_arguments: str) -> None:
        self.function = DummyOpenAiFunction(function_name, function_arguments)


class DummyOpenAiMessage:
    """Simple shape-matching stub for OpenAI SDK message payload."""

    def __init__(self, tool_calls: list[DummyOpenAiToolCall] | None = None, content: str | None = None) -> None:
        self.tool_calls = tool_calls
        self.content = content


def run_parser_smoke_tests() -> None:
    parser = LfmToolCallParser()

    tool_calls_message = DummyOpenAiMessage(
        tool_calls=[DummyOpenAiToolCall("get_weather", '{"location":"Tokyo","date":"tomorrow"}')]
    )
    parsed_tool_calls = parser.parse_from_message(tool_calls_message)
    assert len(parsed_tool_calls) == 1
    assert parsed_tool_calls[0].tool_name == "get_weather"

    xml_content_message = DummyOpenAiMessage(
        content='<tool_call>{"name":"get_news","arguments":{"topic":"ai","timeframe":"today"}}</tool_call>'
    )
    parsed_tool_calls = parser.parse_from_message(xml_content_message)
    assert len(parsed_tool_calls) == 1
    assert parsed_tool_calls[0].tool_name == "get_news"

    python_call_message = DummyOpenAiMessage(content='play_sound_effect(event_name="success", intensity="high")')
    parsed_tool_calls = parser.parse_from_message(python_call_message)
    assert len(parsed_tool_calls) == 1
    assert parsed_tool_calls[0].tool_name == "play_sound_effect"
    print("Parser smoke tests passed.")


def run_validation_smoke_tests() -> None:
    tool_schemas = build_tool_schemas()
    success_result = validate_tool_call_against_schema(
        tool_name="read_database_record",
        arguments={"table_name": "users", "key": "user_001"},
        tool_schemas=tool_schemas,
    )
    assert success_result.is_success

    failure_result = validate_tool_call_against_schema(
        tool_name="read_database_record",
        arguments={"table_name": "users"},
        tool_schemas=tool_schemas,
    )
    assert not failure_result.is_success
    assert failure_result.failure_reason == "missing_required"
    print("Validation smoke tests passed.")


def main() -> None:
    run_parser_smoke_tests()
    run_validation_smoke_tests()


if __name__ == "__main__":
    main()
