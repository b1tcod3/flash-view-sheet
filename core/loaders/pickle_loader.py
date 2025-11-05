"""
Pickle File Loader
Handles Python Pickle format
"""

import pandas as pd
import os
from typing import Optional, Dict, Any
from .base_loader import FileLoader


class PickleLoader(FileLoader):
    """
    File loader for Pickle format
    """

    def get_supported_extensions(self) -> list:
        return ['.pkl', '.pickle']

    def load(self, skip_rows: int = 0, column_names: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Load Pickle file into DataFrame
        
        Args:
            skip_rows: Number of rows to skip at the beginning (not applicable for pickle, kept for interface compatibility)
            column_names: Dictionary for renaming columns
            
        Returns:
            DataFrame with loaded data
        """
        try:
            # Load Pickle file
            df = pd.read_pickle(self.filepath)
            
            # Ensure it's a DataFrame
            if not isinstance(df, pd.DataFrame):
                raise ValueError("Pickle file does not contain a DataFrame")
            
            # Apply skip_rows if specified
            if skip_rows > 0 and len(df) > skip_rows:
                df = df.iloc[skip_rows:].reset_index(drop=True)
            
            # Apply column renaming if specified
            if column_names:
                df = df.rename(columns=column_names)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error loading Pickle file {self.filepath}: {str(e)}")

    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the Pickle file
        """
        try:
            file_size = os.path.getsize(self.filepath)
            extension = os.path.splitext(self.filepath)[1].lower()
            
            return {
                'format': 'Pickle',
                'extension': extension,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'note': 'Binary Python format - use with trusted sources only'
            }
        except Exception as e:
            return {'error': str(e)}

    def can_load_chunks(self) -> bool:
        """
        Pickle files do not support chunk loading
        """
        return False

    def _estimate_rows(self) -> int:
        """
        Estimate number of rows in Pickle file
        """
        try:
            # Load a sample to count rows
            df_sample = pd.read_pickle(self.filepath)
            if isinstance(df_sample, pd.DataFrame):
                return len(df_sample)
            return 0
        except:
            return super()._estimate_rows()