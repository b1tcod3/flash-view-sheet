"""
JSON File Loader
Handles JavaScript Object Notation format
"""

import pandas as pd
import os
from typing import Optional, Dict, Any
from .base_loader import FileLoader


class JsonLoader(FileLoader):
    """
    File loader for JSON format
    """

    def get_supported_extensions(self) -> list:
        return ['.json']

    def load(self, skip_rows: int = 0, column_names: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Load JSON file into DataFrame
        
        Args:
            skip_rows: Number of rows to skip at the beginning (not applicable for JSON, kept for interface compatibility)
            column_names: Dictionary for renaming columns
            
        Returns:
            DataFrame with loaded data
        """
        try:
            # Load JSON file
            df = pd.read_json(self.filepath)
            
            # Apply skip_rows if specified (for JSON, this means removing first n rows)
            if skip_rows > 0 and len(df) > skip_rows:
                df = df.iloc[skip_rows:].reset_index(drop=True)
            
            # Apply column renaming if specified
            if column_names:
                df = df.rename(columns=column_names)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error loading JSON file {self.filepath}: {str(e)}")

    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the JSON file
        """
        try:
            file_size = os.path.getsize(self.filepath)
            
            # Get basic JSON structure information
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # Read first 1KB to get structure
                    is_array = content.strip().startswith('[')
                    
            except:
                is_array = False
            
            return {
                'format': 'JSON',
                'is_array': is_array,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2)
            }
        except Exception as e:
            return {'error': str(e)}

    def can_load_chunks(self) -> bool:
        """
        JSON files do not support chunk loading
        """
        return False

    def _estimate_rows(self) -> int:
        """
        Estimate number of rows in JSON file
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Count objects in array (rough estimate)
                if content.strip().startswith('[') and content.strip().endswith(']'):
                    return content.count('{')  # Count objects
                return 1  # Single object
        except:
            return super()._estimate_rows()