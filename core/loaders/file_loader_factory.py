"""
File Loader Factory
Factory pattern for creating appropriate file loaders based on file extension
"""

from typing import Dict, Type, Optional
import os
from .base_loader import FileLoader
from .csv_loader import CsvLoader
from .excel_loader import ExcelLoader
from .json_loader import JsonLoader
from .xml_loader import XmlLoader
from .parquet_loader import ParquetLoader
from .feather_loader import FeatherLoader
from .hdf5_loader import Hdf5Loader
from .pickle_loader import PickleLoader
from .sqlite_loader import SqliteLoader
from .yaml_loader import YamlLoader


class FileLoaderFactory:
    """
    Factory class for creating file loaders
    Maps file extensions to their corresponding loader classes
    """

    def __init__(self):
        # Map file extensions to loader classes
        self._loader_mapping: Dict[str, Type[FileLoader]] = {
            # Existing formats
            '.csv': CsvLoader,
            '.tsv': CsvLoader,  # TSV is handled by CSV loader
            '.xlsx': ExcelLoader,
            '.xls': ExcelLoader,
            '.json': JsonLoader,
            '.xml': XmlLoader,
            
            # New formats to be implemented
            '.parquet': ParquetLoader,
            '.feather': FeatherLoader,
            '.hdf5': Hdf5Loader,
            '.pkl': PickleLoader,
            '.pickle': PickleLoader,
            '.db': SqliteLoader,
            '.sqlite': SqliteLoader,
            '.yaml': YamlLoader,
            '.yml': YamlLoader,
        }

    def get_loader(self, filepath: str) -> FileLoader:
        """
        Get the appropriate file loader for a given file path
        
        Args:
            filepath: Path to the file
            
        Returns:
            FileLoader instance for the file type
            
        Raises:
            ValueError: If the file format is not supported
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        extension = os.path.splitext(filepath)[1].lower()
        
        if extension not in self._loader_mapping:
            supported_formats = list(self._loader_mapping.keys())
            raise ValueError(
                f"Unsupported file format: '{extension}'. "
                f"Supported formats: {supported_formats}"
            )
        
        loader_class = self._loader_mapping[extension]
        return loader_class(filepath)

    def is_supported(self, filepath: str) -> bool:
        """
        Check if a file format is supported
        
        Args:
            filepath: Path to the file
            
        Returns:
            True if the file format is supported
        """
        extension = os.path.splitext(filepath)[1].lower()
        return extension in self._loader_mapping

    def get_supported_extensions(self) -> list:
        """
        Get list of all supported file extensions
        
        Returns:
            List of supported file extensions
        """
        return list(self._loader_mapping.keys())

    def get_loader_info(self, filepath: str) -> Dict[str, str]:
        """
        Get information about the loader for a given file
        
        Args:
            filepath: Path to the file
            
        Returns:
            Dictionary with loader information
        """
        if not self.is_supported(filepath):
            return {"error": "Unsupported file format"}
        
        extension = os.path.splitext(filepath)[1].lower()
        loader_class = self._loader_mapping[extension]
        loader = loader_class(filepath)
        
        return {
            "extension": extension,
            "loader_class": loader_class.__name__,
            "supports_chunks": loader.can_load_chunks(),
            "file_info": loader.get_file_info(),
            "memory_info": loader.get_memory_usage_info()
        }

    def register_loader(self, extension: str, loader_class: Type[FileLoader]):
        """
        Register a new loader for a file extension (for extensibility)
        
        Args:
            extension: File extension (e.g., '.custom')
            loader_class: Class that inherits from FileLoader
        """
        if not issubclass(loader_class, FileLoader):
            raise ValueError("Loader class must inherit from FileLoader")
        
        self._loader_mapping[extension.lower()] = loader_class

    def get_format_description(self, extension: str) -> str:
        """
        Get description of a file format
        
        Args:
            extension: File extension
            
        Returns:
            Description of the format
        """
        descriptions = {
            '.csv': 'Comma-Separated Values - Text format with comma delimiters',
            '.tsv': 'Tab-Separated Values - Text format with tab delimiters',
            '.xlsx': 'Excel Workbook - Microsoft Excel format',
            '.xls': 'Excel Spreadsheet - Legacy Microsoft Excel format',
            '.json': 'JavaScript Object Notation - Structured text format',
            '.xml': 'eXtensible Markup Language - Structured markup format',
            '.parquet': 'Apache Parquet - Columnar storage format for big data',
            '.feather': 'Feather Format - Fast columnar storage format',
            '.hdf5': 'HDF5 - Hierarchical Data Format for scientific data',
            '.pkl': 'Pickle Format - Python serialized objects',
            '.pickle': 'Pickle Format - Python serialized objects',
            '.db': 'SQLite Database - Lightweight SQL database',
            '.sqlite': 'SQLite Database - Lightweight SQL database',
            '.yaml': 'YAML Format - Human-readable data serialization',
            '.yml': 'YAML Format - Human-readable data serialization',
        }
        
        return descriptions.get(extension.lower(), f"Unknown format: {extension}")


# Global factory instance
_global_factory = FileLoaderFactory()


def get_file_loader(filepath: str) -> FileLoader:
    """
    Get file loader for a given file path (convenience function)
    
    Args:
        filepath: Path to the file
        
    Returns:
        FileLoader instance for the file type
    """
    return _global_factory.get_loader(filepath)


def is_file_supported(filepath: str) -> bool:
    """
    Check if a file format is supported (convenience function)
    
    Args:
        filepath: Path to the file
        
    Returns:
        True if the file format is supported
    """
    return _global_factory.is_supported(filepath)


def get_supported_formats() -> list:
    """
    Get list of all supported file formats (convenience function)
    
    Returns:
        List of supported file extensions
    """
    return _global_factory.get_supported_extensions()