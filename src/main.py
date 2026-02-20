"""Responsibility: provide a simple CLI entry point for one-shot tool-calling checks."""

from kiboedge_toolcall_kit import RuntimeConfiguration, ToolCallEngine
from kiboedge_toolcall_kit.lfm_tool_call_parser import LfmToolCallParser
from kiboedge_toolcall_kit.lmstudio_client import LmStudioChatClient
from kiboedge_toolcall_kit.tool_schemas import build_tool_schemas
from kiboedge_toolcall_kit.tools import DummyDataStores, build_tool_executor_map


def main() -> None:
    runtime_configuration = RuntimeConfiguration()
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

    user_prompt = "明日の東京の天気を確認して。"
    engine_result = tool_call_engine.run_tool_call_round(user_prompt)
    print(engine_result)


if __name__ == "__main__":
    main()
