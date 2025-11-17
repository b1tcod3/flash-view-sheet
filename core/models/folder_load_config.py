"""
Folder Load Configuration Model
Configuration for loading folders with Excel files
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class ColumnAlignmentStrategy(Enum):
    """Strategies for aligning columns"""
    BY_POSITION = "position"
    BY_NAME = "name"


@dataclass
class FolderLoadConfig:
    """
    Configuration for folder loading operations
    """
    folder_path: str
    included_files: List[str] = field(default_factory=list)
    excluded_files: List[str] = field(default_factory=list)
    included_columns: List[str] = field(default_factory=list)  # Column names to include (empty = all)
    excluded_columns: List[str] = field(default_factory=list)  # Column names to exclude
    alignment_strategy: ColumnAlignmentStrategy = ColumnAlignmentStrategy.BY_POSITION
    column_rename_mapping: Dict[str, str] = field(default_factory=dict)
    skip_rows: int = 0
    add_source_column: bool = True
    source_column_name: str = "__source__"

    def should_include_file(self, filename: str) -> bool:
        """
        Check if a file should be included based on configuration

        Args:
            filename: Name of the file

        Returns:
            True if file should be included
        """
        if self.excluded_files and filename in self.excluded_files:
            return False

        if self.included_files:
            return filename in self.included_files

        return True

    def should_include_column(self, column_name: str) -> bool:
        """
        Check if a column should be included based on configuration

        Args:
            column_name: Name of the column

        Returns:
            True if column should be included
        """
        if self.excluded_columns and column_name in self.excluded_columns:
            return False

        if self.included_columns:
            return column_name in self.included_columns

        return True

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'folder_path': self.folder_path,
            'included_files': self.included_files,
            'excluded_files': self.excluded_files,
            'included_columns': self.included_columns,
            'excluded_columns': self.excluded_columns,
            'alignment_strategy': self.alignment_strategy.value,
            'column_rename_mapping': self.column_rename_mapping,
            'skip_rows': self.skip_rows,
            'add_source_column': self.add_source_column,
            'source_column_name': self.source_column_name
        }