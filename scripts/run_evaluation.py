"""Responsibility: run the 30-case strict-success evaluation from the command line."""

import argparse
from dataclasses import asdict
import json

from kiboedge_toolcall_kit import EvaluationRunner, RuntimeConfiguration, ToolCallEngine
from kiboedge_toolcall_kit.lfm_tool_call_parser import LfmToolCallParser
from kiboedge_toolcall_kit.lmstudio_client import LmStudioChatClient
from kiboedge_toolcall_kit.tool_schemas import build_tool_schemas
from kiboedge_toolcall_kit.tools import DummyDataStores, build_tool_executor_map


def main() -> None:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--max-cases",
        type=int,
        default=1,
        help="Limit number of evaluation cases for faster iteration.",
    )
    argument_parser.add_argument(
        "--request-timeout-seconds",
        type=float,
        default=12.0,
        help="Per-request timeout to avoid heavy hangs on local PC.",
    )
    command_line_arguments = argument_parser.parse_args()

    runtime_configuration = RuntimeConfiguration(
        request_timeout_seconds=command_line_arguments.request_timeout_seconds,
    )
    tool_schemas = build_tool_schemas()
    dummy_data_stores = DummyDataStores()
    tool_executor_map = build_tool_executor_map(dummy_data_stores)

    tool_call_engine = ToolCallEngine(
        runtime_configuration=runtime_configuration,
        chat_client=LmStudioChatClient(runtime_configuration),
        tool_schemas=tool_schemas,
        tool_executor_map=tool_executor_map,
        parser=LfmToolCallParser(),
    )
    evaluation_runner = EvaluationRunner(
        runtime_configuration=runtime_configuration,
        tool_call_engine=tool_call_engine,
    )

    evaluation_summary, _, result_file_path = evaluation_runner.run_evaluation(
        max_cases=command_line_arguments.max_cases,
    )
    print(json.dumps(asdict(evaluation_summary), ensure_ascii=True, indent=2))
    print(f"result_file_path={result_file_path}")


if __name__ == "__main__":
    main()
