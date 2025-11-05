"""
CSV/TSV File Loader
Handles Comma-Separated Values and Tab-Separated Values formats
"""

import pandas as pd
import os
from typing import Optional, Dict, Any
from .base_loader import FileLoader


class CsvLoader(FileLoader):
    """
    File loader for CSV and TSV formats
    """

    def get_supported_extensions(self) -> list:
        return ['.csv', '.tsv']

    def load(self, skip_rows: int = 0, column_names: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Load CSV/TSV file into DataFrame
        
        Args:
            skip_rows: Number of rows to skip at the beginning
            column_names: Dictionary for renaming columns
            
        Returns:
            DataFrame with loaded data
        """
        try:
            # Determine separator based on file extension
            sep = '\t' if self.filepath.lower().endswith('.tsv') else ','
            
            # Load with skip_rows if specified
            if skip_rows > 0:
                df = pd.read_csv(self.filepath, sep=sep, header=skip_rows)
                df = df.reset_index(drop=True)
            else:
                df = pd.read_csv(self.filepath, sep=sep)
            
            # Apply column renaming if specified
            if column_names:
                df = df.rename(columns=column_names)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error loading CSV/TSV file {self.filepath}: {str(e)}")

    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the CSV/TSV file
        """
        try:
            file_size = os.path.getsize(self.filepath)
            
            # Get first few lines to detect delimiter
            with open(self.filepath, 'r', encoding='utf-8', nrows=5) as f:
                first_line = f.readline().strip()
                delimiter = '\t' if self.filepath.lower().endswith('.tsv') else ','
                delimiter = delimiter if delimiter in first_line else ','
            
            return {
                'format': 'CSV/TSV',
                'delimiter': delimiter,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2)
            }
        except Exception as e:
            return {'error': str(e)}

    def can_load_chunks(self) -> bool:
        """
        CSV/TSV files support chunk loading
        """
        return True

    def load_in_chunks(self, chunk_size: int = 1000) -> pd.DataFrame:
        """
        Load CSV/TSV file in chunks for better memory management
        """
        try:
            sep = '\t' if self.filepath.lower().endswith('.tsv') else ','
            
            chunk_list = []
            for chunk in pd.read_csv(self.filepath, sep=sep, chunksize=chunk_size):
                chunk_list.append(chunk)
            
            return pd.concat(chunk_list, ignore_index=True)
            
        except Exception as e:
            raise Exception(f"Error loading CSV/TSV file in chunks: {str(e)}")

    def _estimate_rows(self) -> int:
        """
        Estimate number of rows in CSV/TSV file
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                # Count lines efficiently
                line_count = sum(1 for _ in f)
                return line_count - 1  # Subtract header row
        except:
            return super()._estimate_rows()