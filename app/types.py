"""Tipos comunes reutilizables en todo el proyecto."""

from pathlib import Path
from typing import Any

FilePath = str | Path
ColumnMapping = dict[str, str]
ColumnNames = dict[int, str]
DataFrameDict = dict[str, Any]
