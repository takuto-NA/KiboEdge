"""Responsibility: define shared dataclasses for tool calls, cases, and evaluation results."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ParsedToolCall:
    """One parsed tool call candidate from a model response."""

    tool_name: str
    arguments: dict[str, Any]
    source: str
    raw_payload: str


@dataclass(frozen=True)
class EvaluationCase:
    """A single evaluation scenario and expected tool-calling behavior."""

    case_identifier: str
    user_prompt: str
    expected_tool_name: str
    required_argument_keys: list[str]
    optional_argument_keys: list[str] = field(default_factory=list)
    should_call_tool: bool = True
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ToolValidationResult:
    """Validation result for one parsed tool call against a schema/case."""

    is_success: bool
    failure_reason: str | None
    matched_tool_name: str | None


@dataclass(frozen=True)
class EvaluationCaseResult:
    """Evaluation result of one case."""

    case_identifier: str
    is_success: bool
    failure_reason: str | None
    source: str
    expected_tool_name: str
    actual_tool_name: str | None


@dataclass(frozen=True)
class EvaluationSummary:
    """Aggregated evaluation metrics."""

    total_cases: int
    successful_cases: int
    strict_success_rate: float
    failure_counts_by_reason: dict[str, int]
