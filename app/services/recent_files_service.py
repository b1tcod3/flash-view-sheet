"""
Recent Files Service

Persistencia de archivos recientes en disco.
Guarda hasta 10 archivos cargados en ~/.flashsheet/recent_files.json
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


_MAX_RECENT = 10


def _config_dir() -> Path:
    d = Path.home() / ".flashsheet"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _recent_file() -> Path:
    return _config_dir() / "recent_files.json"


def _relative_time(ts: float) -> str:
    diff = time.time() - ts
    if diff < 60:
        return "ahora mismo"
    if diff < 3600:
        m = int(diff // 60)
        return f"hace {m} min" if m != 1 else "hace 1 min"
    if diff < 86400:
        h = int(diff // 3600)
        return f"hace {h} h" if h != 1 else "hace 1 h"
    if diff < 604800:
        d = int(diff // 86400)
        return f"hace {d} días" if d != 1 else "hace 1 día"
    import datetime
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime("%d/%m/%Y")


class RecentFilesService:
    """Servicio de archivos recientes persistidos en disco"""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        path = _recent_file()
        if not path.exists():
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self._entries = data
        except (json.JSONDecodeError, OSError):
            self._entries = []

    def _save(self) -> None:
        try:
            with open(_recent_file(), "w", encoding="utf-8") as f:
                json.dump(self._entries, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def add(self, filepath: str) -> None:
        path = Path(filepath)
        filename = path.name
        resolved = str(path.resolve())

        self._entries = [
            e for e in self._entries
            if e.get("filepath") != resolved
        ]

        self._entries.insert(0, {
            "filepath": resolved,
            "filename": filename,
            "loaded_at": time.time(),
        })

        if len(self._entries) > _MAX_RECENT:
            self._entries = self._entries[:_MAX_RECENT]

        self._save()

    def get_recent(self, limit: int = _MAX_RECENT) -> list[dict[str, Any]]:
        result = []
        for entry in self._entries[:limit]:
            p = Path(entry.get("filepath", ""))
            if p.exists():
                result.append({
                    "filepath": entry["filepath"],
                    "filename": entry.get("filename", p.name),
                    "loaded_at": entry.get("loaded_at", 0),
                    "relative_time": _relative_time(entry.get("loaded_at", 0)),
                })
        return result

    def remove(self, filepath: str) -> None:
        resolved = str(Path(filepath).resolve())
        self._entries = [
            e for e in self._entries
            if e.get("filepath") != resolved
        ]
        self._save()

    def clear(self) -> None:
        self._entries.clear()
        self._save()
