"""Responsibility: execute strict-success evaluation cases and persist comparable results."""

from __future__ import annotations

from dataclasses import asdict
import time

from .config import RuntimeConfiguration
from .evaluation_metrics import summarize_evaluation_results
from .io_utils import build_timestamp_suffix, read_json_file, write_json_file
from .models import EvaluationCase, EvaluationCaseResult, EvaluationSummary
from .tool_orchestrator import ToolCallEngine
from .tool_validation import validate_case_expected_result


class EvaluationRunner:
    """Runs fixed evaluation case set and computes strict success rate."""

    def __init__(
        self,
        runtime_configuration: RuntimeConfiguration,
        tool_call_engine: ToolCallEngine,
    ) -> None:
        self._runtime_configuration = runtime_configuration
        self._tool_call_engine = tool_call_engine

    def run_evaluation(
        self,
        case_file_path: str | None = None,
        max_cases: int | None = None,
    ) -> tuple[EvaluationSummary, list[EvaluationCaseResult], str]:
        case_path = case_file_path or self._runtime_configuration.evaluation_case_file_path
        evaluation_cases = self._load_cases(case_path)
        if max_cases is not None:
            evaluation_cases = evaluation_cases[:max_cases]

        evaluation_case_results: list[EvaluationCaseResult] = []
        consecutive_request_error_count = 0
        for evaluation_case in evaluation_cases:
            evaluation_case_result = self._run_single_case(evaluation_case)
            evaluation_case_results.append(evaluation_case_result)

            if evaluation_case_result.failure_reason == "request_error":
                consecutive_request_error_count += 1
            else:
                consecutive_request_error_count = 0

            # Guard: stop early when request-level instability repeats.
            if (
                consecutive_request_error_count
                >= self._runtime_configuration.max_consecutive_request_errors
            ):
                break

            time.sleep(self._runtime_configuration.delay_between_evaluation_cases_seconds)

        evaluation_summary = summarize_evaluation_results(evaluation_case_results)
        result_file_path = self._write_result_file(evaluation_summary, evaluation_case_results)
        return evaluation_summary, evaluation_case_results, result_file_path

    def _load_cases(self, case_file_path: str) -> list[EvaluationCase]:
        raw_case_objects = read_json_file(case_file_path)
        return [
            EvaluationCase(
                case_identifier=raw_case_object["case_identifier"],
                user_prompt=raw_case_object["user_prompt"],
                expected_tool_name=raw_case_object["expected_tool_name"],
                required_argument_keys=raw_case_object["required_argument_keys"],
                optional_argument_keys=raw_case_object.get("optional_argument_keys", []),
                should_call_tool=raw_case_object.get("should_call_tool", True),
                tags=raw_case_object.get("tags", []),
            )
            for raw_case_object in raw_case_objects
        ]

    def _run_single_case(self, evaluation_case: EvaluationCase) -> EvaluationCaseResult:
        try:
            engine_result = self._tool_call_engine.run_tool_call_round(evaluation_case.user_prompt)
        except Exception:
            return EvaluationCaseResult(
                case_identifier=evaluation_case.case_identifier,
                is_success=False,
                failure_reason="request_error",
                source="exception",
                expected_tool_name=evaluation_case.expected_tool_name,
                actual_tool_name=None,
            )

        if not engine_result["is_success"]:
            return EvaluationCaseResult(
                case_identifier=evaluation_case.case_identifier,
                is_success=False,
                failure_reason=engine_result["failure_reason"],
                source=engine_result["source"],
                expected_tool_name=evaluation_case.expected_tool_name,
                actual_tool_name=engine_result["tool_name"],
            )

        expected_validation_result = validate_case_expected_result(
            expected_tool_name=evaluation_case.expected_tool_name,
            parsed_tool_name=engine_result["tool_name"],
        )
        if not expected_validation_result.is_success:
            return EvaluationCaseResult(
                case_identifier=evaluation_case.case_identifier,
                is_success=False,
                failure_reason=expected_validation_result.failure_reason,
                source=engine_result["source"],
                expected_tool_name=evaluation_case.expected_tool_name,
                actual_tool_name=engine_result["tool_name"],
            )

        missing_required_arguments = [
            required_argument_key
            for required_argument_key in evaluation_case.required_argument_keys
            if required_argument_key not in engine_result["arguments"]
        ]
        if missing_required_arguments:
            return EvaluationCaseResult(
                case_identifier=evaluation_case.case_identifier,
                is_success=False,
                failure_reason="missing_required",
                source=engine_result["source"],
                expected_tool_name=evaluation_case.expected_tool_name,
                actual_tool_name=engine_result["tool_name"],
            )

        return EvaluationCaseResult(
            case_identifier=evaluation_case.case_identifier,
            is_success=True,
            failure_reason=None,
            source=engine_result["source"],
            expected_tool_name=evaluation_case.expected_tool_name,
            actual_tool_name=engine_result["tool_name"],
        )

    def _write_result_file(
        self,
        evaluation_summary: EvaluationSummary,
        evaluation_case_results: list[EvaluationCaseResult],
    ) -> str:
        timestamp_suffix = build_timestamp_suffix()
        result_file_path = (
            f"{self._runtime_configuration.evaluation_result_directory_path}/evaluation_{timestamp_suffix}.json"
        )
        write_json_file(
            result_file_path,
            {
                "summary": asdict(evaluation_summary),
                "results": [asdict(evaluation_case_result) for evaluation_case_result in evaluation_case_results],
            },
        )
        return result_file_path
