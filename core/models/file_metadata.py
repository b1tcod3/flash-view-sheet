"""
File Metadata Model
Represents metadata for Excel files
"""

from dataclasses import dataclass

@dataclass
class FileMetadata:
    """
    Metadata for an Excel file
    """
    filename: str
    filepath: str
    file_size_bytes: int
    file_size_mb: float
    sheets: list[str]
    sheet_count: int
    columns: list[str]
    num_columns: int
    num_rows: int
    error: str | None = None

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