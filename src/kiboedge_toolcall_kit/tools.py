"""Responsibility: provide dummy tool implementations for local deterministic evaluation."""

from dataclasses import dataclass, field
from typing import Any, Callable


ToolFunction = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass
class DummyDataStores:
    """In-memory stores used by dummy tool implementations."""

    calendar_events: list[dict[str, Any]] = field(default_factory=list)
    todo_tasks: list[dict[str, Any]] = field(default_factory=list)
    database_tables: dict[str, dict[str, Any]] = field(default_factory=dict)


def build_tool_executor_map(dummy_data_stores: DummyDataStores) -> dict[str, ToolFunction]:
    """Create executable tool map."""
    return {
        "play_sound_effect": _execute_play_sound_effect,
        "create_calendar_event": lambda arguments: _execute_create_calendar_event(arguments, dummy_data_stores),
        "read_calendar_events": lambda arguments: _execute_read_calendar_events(arguments, dummy_data_stores),
        "create_todo_task": lambda arguments: _execute_create_todo_task(arguments, dummy_data_stores),
        "read_todo_tasks": lambda arguments: _execute_read_todo_tasks(arguments, dummy_data_stores),
        "get_weather": _execute_get_weather,
        "get_news": _execute_get_news,
        "read_database_record": lambda arguments: _execute_read_database_record(arguments, dummy_data_stores),
        "write_database_record": lambda arguments: _execute_write_database_record(arguments, dummy_data_stores),
    }


def _execute_play_sound_effect(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "ok",
        "event_name": arguments["event_name"],
        "intensity": arguments["intensity"],
        "playback_mode": "event_only",
    }


def _execute_create_calendar_event(arguments: dict[str, Any], dummy_data_stores: DummyDataStores) -> dict[str, Any]:
    calendar_event = {
        "title": arguments["title"],
        "start_datetime": arguments["start_datetime"],
        "end_datetime": arguments["end_datetime"],
        "location": arguments.get("location", ""),
    }
    dummy_data_stores.calendar_events.append(calendar_event)
    return {"status": "ok", "created_event": calendar_event}


def _execute_read_calendar_events(arguments: dict[str, Any], dummy_data_stores: DummyDataStores) -> dict[str, Any]:
    return {
        "status": "ok",
        "start_date": arguments["start_date"],
        "end_date": arguments["end_date"],
        "events": dummy_data_stores.calendar_events,
    }


def _execute_create_todo_task(arguments: dict[str, Any], dummy_data_stores: DummyDataStores) -> dict[str, Any]:
    todo_task = {
        "task_title": arguments["task_title"],
        "priority": arguments["priority"],
        "due_date": arguments.get("due_date", ""),
        "status": "open",
    }
    dummy_data_stores.todo_tasks.append(todo_task)
    return {"status": "ok", "created_task": todo_task}


def _execute_read_todo_tasks(arguments: dict[str, Any], dummy_data_stores: DummyDataStores) -> dict[str, Any]:
    task_status = arguments["status"]
    filter_text = arguments.get("filter_text", "").strip().lower()
    if task_status == "all":
        candidate_tasks = dummy_data_stores.todo_tasks
    else:
        candidate_tasks = [
            todo_task for todo_task in dummy_data_stores.todo_tasks if todo_task["status"] == task_status
        ]

    if not filter_text:
        return {"status": "ok", "tasks": candidate_tasks}

    filtered_tasks = [
        todo_task for todo_task in candidate_tasks if filter_text in todo_task["task_title"].lower()
    ]
    return {"status": "ok", "tasks": filtered_tasks}


def _execute_get_weather(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "ok",
        "location": arguments["location"],
        "date": arguments["date"],
        "forecast": "sunny",
        "temperature_celsius": 22,
    }


def _execute_get_news(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "ok",
        "topic": arguments["topic"],
        "timeframe": arguments["timeframe"],
        "headlines": [
            f"Dummy headline about {arguments['topic']} (1)",
            f"Dummy headline about {arguments['topic']} (2)",
        ],
    }


def _execute_read_database_record(arguments: dict[str, Any], dummy_data_stores: DummyDataStores) -> dict[str, Any]:
    table_name = arguments["table_name"]
    key = arguments["key"]
    if table_name not in dummy_data_stores.database_tables:
        return {"status": "not_found", "table_name": table_name, "key": key, "payload": None}

    payload = dummy_data_stores.database_tables[table_name].get(key)
    if payload is None:
        return {"status": "not_found", "table_name": table_name, "key": key, "payload": None}

    return {"status": "ok", "table_name": table_name, "key": key, "payload": payload}


def _execute_write_database_record(arguments: dict[str, Any], dummy_data_stores: DummyDataStores) -> dict[str, Any]:
    table_name = arguments["table_name"]
    key = arguments["key"]
    payload = arguments["payload"]

    if table_name not in dummy_data_stores.database_tables:
        dummy_data_stores.database_tables[table_name] = {}

    dummy_data_stores.database_tables[table_name][key] = payload
    return {"status": "ok", "table_name": table_name, "key": key}
