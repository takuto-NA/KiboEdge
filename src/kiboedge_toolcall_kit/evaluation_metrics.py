"""Responsibility: aggregate strict-success metrics and reason-level failure statistics."""

from .models import EvaluationCaseResult, EvaluationSummary


def summarize_evaluation_results(evaluation_case_results: list[EvaluationCaseResult]) -> EvaluationSummary:
    total_cases = len(evaluation_case_results)
    successful_cases = len([result for result in evaluation_case_results if result.is_success])
    strict_success_rate = 0.0
    if total_cases > 0:
        strict_success_rate = successful_cases / total_cases

    failure_counts_by_reason: dict[str, int] = {}
    for evaluation_case_result in evaluation_case_results:
        if evaluation_case_result.is_success:
            continue
        failure_reason = evaluation_case_result.failure_reason or "unknown_failure"
        failure_counts_by_reason[failure_reason] = failure_counts_by_reason.get(failure_reason, 0) + 1

    return EvaluationSummary(
        total_cases=total_cases,
        successful_cases=successful_cases,
        strict_success_rate=strict_success_rate,
        failure_counts_by_reason=failure_counts_by_reason,
    )
