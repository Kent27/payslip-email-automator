from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterable, Set

from app.config import HOLIDAYS_FILE


def _parse_dates(values: Iterable[str]) -> Set[date]:
    parsed: Set[date] = set()
    for value in values:
        try:
            parsed.add(date.fromisoformat(value))
        except ValueError:
            continue
    return parsed


def load_holidays(holidays_file: Path | None = None) -> Set[date]:
    file_path = holidays_file or HOLIDAYS_FILE
    if not file_path.exists():
        return set()
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()

    holidays: Set[date] = set()
    if isinstance(data, dict):
        for year_values in data.values():
            if isinstance(year_values, list):
                holidays.update(_parse_dates(year_values))
    elif isinstance(data, list):
        holidays.update(_parse_dates(data))
    return holidays


def get_holidays_for_year(year: int, holidays_file: Path | None = None) -> Set[date]:
    file_path = holidays_file or HOLIDAYS_FILE
    if not file_path.exists():
        return set()
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()

    if isinstance(data, dict):
        year_values = data.get(str(year), [])
        if isinstance(year_values, list):
            return _parse_dates(year_values)
    return set()
