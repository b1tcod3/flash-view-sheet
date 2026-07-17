"""Tipos comunes reutilizables en todo el proyecto."""

from pathlib import Path
from typing import Any
import pandas as pd

FilePath = str | Path
ColumnMapping = dict[str, str]
ColumnNames = dict[int, str]
DataFrameDict = dict[str, Any]
