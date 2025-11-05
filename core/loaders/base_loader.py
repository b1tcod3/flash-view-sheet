"""
Base File Loader Class
Abstract base class for all file format loaders
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd
import os


class FileLoader(ABC):
    """
    Abstract base class for file loaders
    All specific file loaders should inherit from this class
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self._validate_file()

    def _validate_file(self):
        """Validate that the file exists and has the correct format"""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")
        
        extension = os.path.splitext(self.filepath)[1].lower()
        if extension not in self.get_supported_extensions():
            raise ValueError(
                f"File format '{extension}' not supported by {self.__class__.__name__}. "
                f"Supported formats: {self.get_supported_extensions()}"
            )

    @abstractmethod
    def get_supported_extensions(self) -> list:
        """
        Get list of supported file extensions
        
        Returns:
            List of file extensions (e.g., ['.csv', '.tsv'])
        """
        pass

    @abstractmethod
    def load(self, skip_rows: int = 0, column_names: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Load the file into a pandas DataFrame
        
        Args:
            skip_rows: Number of rows to skip at the beginning
            column_names: Dictionary for renaming columns {old_name: new_name}
            
        Returns:
            DataFrame with the loaded data
        """
        pass

    @abstractmethod
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the file
        
        Returns:
            Dictionary with file information (size, format, etc.)
        """
        pass

    def can_load_chunks(self) -> bool:
        """
        Check if the loader supports loading in chunks for large files
        
        Returns:
            True if chunk loading is supported
        """
        return False

    def load_in_chunks(self, chunk_size: int = 1000) -> pd.DataFrame:
        """
        Load file in chunks for better memory management
        
        Args:
            chunk_size: Number of rows per chunk
            
        Returns:
            DataFrame with all chunks concatenated
        """
        raise NotImplementedError(
            f"Chunk loading not supported by {self.__class__.__name__}"
        )

    def get_memory_usage_info(self) -> Dict[str, Any]:
        """
        Get memory usage information for the file
        
        Returns:
            Dictionary with memory usage details
        """
        try:
            file_size = os.path.getsize(self.filepath)
            return {
                'file_size_bytes': file_size,
                'file_size_mb': file_size / (1024 * 1024),
                'estimated_data_rows': self._estimate_rows(),
                'supports_chunked_loading': self.can_load_chunks()
            }
        except Exception as e:
            return {'error': str(e)}

    def _estimate_rows(self) -> int:
        """
        Estimate the number of rows in the file (for text-based formats)
        
        Returns:
            Estimated number of rows
        """
        # This is a rough estimation, can be overridden by specific loaders
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                file_size = os.path.getsize(self.filepath)
                line_length = 100  # Rough estimate
                return file_size // line_length
        except:
            return 0