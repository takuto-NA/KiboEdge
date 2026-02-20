"""Responsibility: run sequential prompt-variant iterations and report strict-success gains."""

import argparse
from dataclasses import asdict
import json

from kiboedge_toolcall_kit import EvaluationRunner, RuntimeConfiguration, ToolCallEngine
from kiboedge_toolcall_kit.lfm_tool_call_parser import LfmToolCallParser
from kiboedge_toolcall_kit.lmstudio_client import LmStudioChatClient
from kiboedge_toolcall_kit.prompt_templates import (
    build_strict_json_only_system_prompt,
    build_tool_call_system_prompt,
)
from kiboedge_toolcall_kit.tool_schemas import build_tool_schemas
from kiboedge_toolcall_kit.tools import DummyDataStores, build_tool_executor_map


def _run_with_prompt_variant(
    runtime_configuration: RuntimeConfiguration,
    system_prompt_text: str,
    max_cases: int | None,
) -> dict[str, object]:
    tool_schemas = build_tool_schemas()
    tool_executor_map = build_tool_executor_map(DummyDataStores())
    tool_call_engine = ToolCallEngine(
        runtime_configuration=runtime_configuration,
        chat_client=LmStudioChatClient(runtime_configuration),
        tool_schemas=tool_schemas,
        tool_executor_map=tool_executor_map,
        parser=LfmToolCallParser(),
        system_prompt_text=system_prompt_text,
    )
    evaluation_runner = EvaluationRunner(
        runtime_configuration=runtime_configuration,
        tool_call_engine=tool_call_engine,
    )
    evaluation_summary, _, result_file_path = evaluation_runner.run_evaluation(max_cases=max_cases)
    return {"summary": asdict(evaluation_summary), "result_file_path": result_file_path}


def main() -> None:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--max-cases",
        type=int,
        default=1,
        help="Use a smaller subset during rapid improvement loops.",
    )
    argument_parser.add_argument(
        "--request-timeout-seconds",
        type=float,
        default=12.0,
        help="Per-request timeout to avoid long stalls on local PC.",
    )
    command_line_arguments = argument_parser.parse_args()

    runtime_configuration = RuntimeConfiguration(
        request_timeout_seconds=command_line_arguments.request_timeout_seconds,
    )
    baseline_result = _run_with_prompt_variant(
        runtime_configuration=runtime_configuration,
        system_prompt_text=build_tool_call_system_prompt(),
        max_cases=command_line_arguments.max_cases,
    )
    strict_prompt_result = _run_with_prompt_variant(
        runtime_configuration=runtime_configuration,
        system_prompt_text=build_strict_json_only_system_prompt(),
        max_cases=command_line_arguments.max_cases,
    )

    print(
        json.dumps(
            {
                "baseline_prompt": baseline_result,
                "strict_json_prompt": strict_prompt_result,
            },
            ensure_ascii=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
