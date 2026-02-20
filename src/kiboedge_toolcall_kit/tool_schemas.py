"""Responsibility: define all tool schemas used for runtime and evaluation."""

from typing import Any


def build_tool_schemas() -> list[dict[str, Any]]:
    """Return OpenAI-compatible tool schema list."""
    return [
        _create_play_sound_effect_schema(),
        _create_calendar_create_schema(),
        _create_calendar_read_schema(),
        _create_todo_create_schema(),
        _create_todo_read_schema(),
        _create_weather_schema(),
        _create_news_schema(),
        _create_database_read_schema(),
        _create_database_write_schema(),
    ]


def _create_play_sound_effect_schema() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "play_sound_effect",
            "description": "Return a sound event to express emotion at appropriate timing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_name": {"type": "string"},
                    "intensity": {"type": "string", "enum": ["low", "medium", "high"]},
                },
                "required": ["event_name", "intensity"],
                "additionalProperties": False,
            },
        },
    }


def _create_calendar_create_schema() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Create a calendar event in the dummy calendar store.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "start_datetime": {"type": "string"},
                    "end_datetime": {"type": "string"},
                    "location": {"type": "string"},
                },
                "required": ["title", "start_datetime", "end_datetime"],
                "additionalProperties": False,
            },
        },
    }


def _create_calendar_read_schema() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "read_calendar_events",
            "description": "Read calendar events by date range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                },
                "required": ["start_date", "end_date"],
                "additionalProperties": False,
            },
        },
    }


def _create_todo_create_schema() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "create_todo_task",
            "description": "Create a task in the dummy todo store.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_title": {"type": "string"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "normal", "high"],
                    },
                    "due_date": {"type": "string"},
                },
                "required": ["task_title", "priority"],
                "additionalProperties": False,
            },
        },
    }


def _create_todo_read_schema() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "read_todo_tasks",
            "description": "Read tasks from the dummy todo store by filter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter_text": {"type": "string"},
                    "status": {"type": "string", "enum": ["open", "done", "all"]},
                },
                "required": ["status"],
                "additionalProperties": False,
            },
        },
    }


def _create_weather_schema() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Read weather from a dummy provider.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "date": {"type": "string"},
                },
                "required": ["location", "date"],
                "additionalProperties": False,
            },
        },
    }


def _create_news_schema() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Read news from a dummy provider.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "timeframe": {"type": "string"},
                },
                "required": ["topic", "timeframe"],
                "additionalProperties": False,
            },
        },
    }


def _create_database_read_schema() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "read_database_record",
            "description": "Read one record from a dummy key-value database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"},
                    "key": {"type": "string"},
                },
                "required": ["table_name", "key"],
                "additionalProperties": False,
            },
        },
    }


def _create_database_write_schema() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "write_database_record",
            "description": "Write one record into a dummy key-value database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"},
                    "key": {"type": "string"},
                    "payload": {"type": "object"},
                },
                "required": ["table_name", "key", "payload"],
                "additionalProperties": False,
            },
        },
    }
