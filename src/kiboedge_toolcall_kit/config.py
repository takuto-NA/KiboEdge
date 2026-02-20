"""Responsibility: centralize runtime constants and user-tunable configuration values."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeConfiguration:
    """Configuration values used across runtime and evaluation."""

    base_url: str = "http://127.0.0.1:1234/v1"
    api_key: str = "lm-studio"
    model_name: str = "lfm2-2.6b-exp"
    request_timeout_seconds: float = 12.0
    response_temperature: float = 0.1
    max_generation_tokens: int = 256
    max_tool_call_rounds_per_request: int = 3
    max_repair_attempts: int = 2
    sequential_execution_only: bool = True
    delay_between_evaluation_cases_seconds: float = 2.0
    max_consecutive_request_errors: int = 2
    log_directory_path: str = "logs"
    evaluation_result_directory_path: str = "logs/evaluations"
    evaluation_case_file_path: str = "tests/fixtures/tool_call_cases_30.json"


DEFAULT_RUNTIME_CONFIGURATION = RuntimeConfiguration()
