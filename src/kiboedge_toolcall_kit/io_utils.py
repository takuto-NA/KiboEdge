"""Responsibility: provide file I/O helpers for structured runtime and evaluation logs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def ensure_directory(directory_path: str) -> None:
    """Create a directory recursively when needed."""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def write_json_file(file_path: str, payload: dict[str, Any]) -> None:
    """Write JSON payload with UTF-8 encoding."""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with Path(file_path).open(mode="w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, ensure_ascii=True, indent=2)


def read_json_file(file_path: str) -> Any:
    """Read JSON file and return decoded value."""
    with Path(file_path).open(mode="r", encoding="utf-8") as input_file:
        return json.load(input_file)


def build_timestamp_suffix() -> str:
    """Build an ISO-like filesystem-safe timestamp suffix."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
