"""Responsibility: validate parsed tool calls against available schemas and expectations."""

from typing import Any

from .models import ToolValidationResult


def validate_tool_call_against_schema(
    tool_name: str,
    arguments: dict[str, Any],
    tool_schemas: list[dict[str, Any]],
) -> ToolValidationResult:
    schema_by_name = _build_schema_by_name(tool_schemas)
    if tool_name not in schema_by_name:
        return ToolValidationResult(False, "hallucinated_tool", None)

    schema = schema_by_name[tool_name]
    if not isinstance(arguments, dict):
        return ToolValidationResult(False, "schema_mismatch", tool_name)

    required_argument_names: list[str] = schema["required"]
    properties: dict[str, Any] = schema["properties"]

    missing_required_argument_names = [
        required_argument_name
        for required_argument_name in required_argument_names
        if required_argument_name not in arguments
    ]
    if missing_required_argument_names:
        return ToolValidationResult(False, "missing_required", tool_name)

    if not schema.get("additionalProperties", True):
        unknown_argument_names = [argument_name for argument_name in arguments if argument_name not in properties]
        if unknown_argument_names:
            return ToolValidationResult(False, "schema_mismatch", tool_name)

    for argument_name, argument_value in arguments.items():
        if argument_name not in properties:
            continue

        expected_type_name = properties[argument_name].get("type")
        if not _is_argument_type_valid(argument_value, expected_type_name):
            return ToolValidationResult(False, "schema_mismatch", tool_name)

    return ToolValidationResult(True, None, tool_name)


def validate_case_expected_result(
    expected_tool_name: str,
    parsed_tool_name: str,
) -> ToolValidationResult:
    if expected_tool_name != parsed_tool_name:
        return ToolValidationResult(False, "wrong_tool_selected", parsed_tool_name)
    return ToolValidationResult(True, None, parsed_tool_name)


def _build_schema_by_name(tool_schemas: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        tool_schema["function"]["name"]: tool_schema["function"]["parameters"]
        for tool_schema in tool_schemas
    }


def _is_argument_type_valid(argument_value: Any, expected_type_name: str | None) -> bool:
    if expected_type_name is None:
        return True

    if expected_type_name == "string":
        return isinstance(argument_value, str)
    if expected_type_name == "object":
        return isinstance(argument_value, dict)
    if expected_type_name == "number":
        return isinstance(argument_value, (int, float))
    if expected_type_name == "integer":
        return isinstance(argument_value, int)
    if expected_type_name == "boolean":
        return isinstance(argument_value, bool)
    return True
