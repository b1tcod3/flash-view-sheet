"""
Folder Loader
Handles loading and scanning of folders containing Excel files
"""

import os
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd


class FolderLoader:
    """
    Class for loading and managing Excel files from a folder
    """

    SUPPORTED_EXTENSIONS = ['.xlsx', '.xls']

    def __init__(self, folder_path: str):
        """
        Initialize folder loader

        Args:
            folder_path: Path to the folder containing Excel files
        """
        self.folder_path = Path(folder_path)
        self._validate_folder()
        self.excel_files = self._scan_excel_files()
        self._metadata_cache = {}  # Cache for file metadata

    def _validate_folder(self):
        """Validate that the folder exists"""
        if not self.folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {self.folder_path}")
        if not self.folder_path.is_dir():
            raise ValueError(f"Path is not a directory: {self.folder_path}")

    def _scan_excel_files(self) -> List[Path]:
        """
        Scan the folder for Excel files

        Returns:
            List of Path objects for Excel files
        """
        excel_files = []
        for file_path in self.folder_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                excel_files.append(file_path)
        return sorted(excel_files)

    def get_excel_files(self) -> List[str]:
        """
        Get list of Excel file paths as strings

        Returns:
            List of file paths
        """
        return [str(f) for f in self.excel_files]

    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Get metadata for a specific Excel file (with caching)

        Args:
            file_path: Path to the Excel file

        Returns:
            Dictionary with file metadata
        """
        # Check cache first
        cache_key = str(Path(file_path).resolve())
        if cache_key in self._metadata_cache:
            return self._metadata_cache[cache_key]

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Get basic file info
            stat = path.stat()
            file_size = stat.st_size

            # Get Excel-specific info
            excel_file = pd.ExcelFile(file_path)
            sheets = excel_file.sheet_names

            # Load first sheet to get column info (assuming first sheet is the main one)
            if sheets:
                df = pd.read_excel(file_path, sheet_name=0, nrows=0)  # Only headers
                columns = df.columns.tolist()
                num_columns = len(columns)
            else:
                columns = []
                num_columns = 0

            metadata = {
                'filename': path.name,
                'filepath': str(path),
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'sheets': sheets,
                'sheet_count': len(sheets),
                'columns': columns,
                'num_columns': num_columns,
                'num_rows': self._estimate_rows(file_path)
            }

            # Cache the result
            self._metadata_cache[cache_key] = metadata
            return metadata

        except Exception as e:
            error_metadata = {
                'filename': path.name,
                'filepath': str(path),
                'error': str(e)
            }
            # Cache error results too to avoid repeated failures
            self._metadata_cache[cache_key] = error_metadata
            return error_metadata

    def get_all_metadata(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all Excel files in the folder

        Returns:
            List of metadata dictionaries
        """
        metadata = []
        for file_path in self.excel_files:
            metadata.append(self.get_file_metadata(str(file_path)))
        return metadata

    def get_metadata_batch(self, start_idx: int = 0, batch_size: int = 10) -> List[Dict[str, Any]]:
        """
        Get metadata for a batch of Excel files (for performance optimization)

        Args:
            start_idx: Starting index in the excel_files list
            batch_size: Number of files to process in this batch

        Returns:
            List of metadata dictionaries for the batch
        """
        end_idx = min(start_idx + batch_size, len(self.excel_files))
        metadata = []

        for i in range(start_idx, end_idx):
            file_path = self.excel_files[i]
            metadata.append(self.get_file_metadata(str(file_path)))

        return metadata

    def get_metadata_count(self) -> int:
        """
        Get total number of Excel files (for batch processing)

        Returns:
            Number of Excel files
        """
        return len(self.excel_files)

    def _estimate_rows(self, file_path: str) -> int:
        """
        Estimate number of rows in Excel file (optimized)

        Args:
            file_path: Path to the Excel file

        Returns:
            Estimated number of rows
        """
        try:
            # Use a smaller sample for faster estimation
            df_sample = pd.read_excel(file_path, nrows=100)
            if len(df_sample) == 0:
                return 0

            file_size = os.path.getsize(file_path)

            # More accurate estimation based on file size and sample
            # Excel files have overhead, so we adjust the estimation
            avg_bytes_per_row = file_size / len(df_sample) * 0.1  # Conservative estimate
            estimated_rows = int(file_size / avg_bytes_per_row)

            # Cap at reasonable maximum to avoid unrealistic estimates
            return min(estimated_rows, 1000000)
        except:
            return 0

    def clear_metadata_cache(self):
        """Clear the metadata cache to free memory"""
        self._metadata_cache.clear()