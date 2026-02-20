"""Responsibility: provide prompt templates that stabilize LFM tool-call formatting."""


def build_tool_call_system_prompt() -> str:
    """Return deterministic system prompt optimized for strict JSON tool calls."""
    return (
        "You are a reliable tool-calling assistant.\n"
        "Output function calls as JSON.\n"
        "Rules:\n"
        "1) Call only tools from the provided tools list.\n"
        "2) Include all required arguments and use correct argument names.\n"
        "3) Do not invent unknown tools.\n"
        "4) If a tool call is needed, return only the tool call, without extra prose.\n"
        "5) If no tool is needed, answer normally.\n"
    )


def build_repair_prompt_for_parse_failure() -> str:
    """Return retry instruction for malformed tool-call outputs."""
    return (
        "Your previous tool call format was invalid.\n"
        "Retry and output a single valid JSON function call with required arguments only."
    )


def build_strict_json_only_system_prompt() -> str:
    """Return stronger prompt variant for iteration experiments."""
    return (
        "You are a deterministic function router.\n"
        "Output function calls as JSON.\n"
        "If a tool call is needed, return exactly this shape and nothing else:\n"
        '{"name":"tool_name","arguments":{"required_key":"value"}}\n'
        "Do not include markdown, XML tags, or explanatory text.\n"
        "Use only available tools and include all required arguments.\n"
    )
