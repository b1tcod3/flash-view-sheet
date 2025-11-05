"""
Excel File Loader
Handles Excel formats (.xlsx, .xls)
"""

import pandas as pd
import os
from typing import Optional, Dict, Any
from .base_loader import FileLoader


class ExcelLoader(FileLoader):
    """
    File loader for Excel formats
    """

    def get_supported_extensions(self) -> list:
        return ['.xlsx', '.xls']

    def load(self, skip_rows: int = 0, column_names: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Load Excel file into DataFrame
        
        Args:
            skip_rows: Number of rows to skip at the beginning
            column_names: Dictionary for renaming columns
            
        Returns:
            DataFrame with loaded data
        """
        try:
            # For Excel, use header=skip_rows to use the row after skipping as header
            if skip_rows > 0:
                df = pd.read_excel(self.filepath, header=skip_rows)
                df = df.reset_index(drop=True)
            else:
                df = pd.read_excel(self.filepath)
            
            # Apply column renaming if specified
            if column_names:
                df = df.rename(columns=column_names)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error loading Excel file {self.filepath}: {str(e)}")

    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the Excel file
        """
        try:
            file_size = os.path.getsize(self.filepath)
            extension = os.path.splitext(self.filepath)[1].lower()
            
            # Get basic sheet information
            try:
                excel_file = pd.ExcelFile(self.filepath)
                sheets = excel_file.sheet_names
                sheet_count = len(sheets)
            except:
                sheets = ['Default']
                sheet_count = 1
            
            return {
                'format': 'Excel',
                'extension': extension,
                'sheets': sheets,
                'sheet_count': sheet_count,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2)
            }
        except Exception as e:
            return {'error': str(e)}

    def can_load_chunks(self) -> bool:
        """
        Excel files do not support chunk loading directly
        """
        return False

    def _estimate_rows(self) -> int:
        """
        Estimate number of rows in Excel file
        """
        try:
            # Load a small sample to count rows
            df_sample = pd.read_excel(self.filepath, nrows=1000)
            file_size = os.path.getsize(self.filepath)
            
            # Rough estimation based on file size
            sample_size = 1000
            sample_estimated_size = len(df_sample) * len(df_sample.columns) * 10  # rough estimate
            if sample_estimated_size > 0:
                return int((file_size / sample_estimated_size) * sample_size)
            return 0
        except:
            return super()._estimate_rows()