"""Tipos comunes reutilizables en todo el proyecto."""

from pathlib import Path
from typing import Union, Dict, Any, List, Optional
import pandas as pd

FilePath = Union[str, Path]
ColumnMapping = Dict[str, str]
ColumnNames = Dict[int, str]
DataFrameDict = Dict[str, Any]
