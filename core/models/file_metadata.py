"""
File Metadata Model
Represents metadata for Excel files
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class FileMetadata:
    """
    Metadata for an Excel file
    """
    filename: str
    filepath: str
    file_size_bytes: int
    file_size_mb: float
    sheets: List[str]
    sheet_count: int
    columns: List[str]
    num_columns: int
    num_rows: int
    error: Optional[str] = None

    @property
    def has_error(self) -> bool:
        """Check if there's an error with this file"""
        return self.error is not None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'filename': self.filename,
            'filepath': self.filepath,
            'file_size_bytes': self.file_size_bytes,
            'file_size_mb': self.file_size_mb,
            'sheets': self.sheets,
            'sheet_count': self.sheet_count,
            'columns': self.columns,
            'num_columns': self.num_columns,
            'num_rows': self.num_rows,
            'error': self.error
        }