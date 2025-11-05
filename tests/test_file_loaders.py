"""
Test suite for file loaders
Tests the new modular file loader system
"""

import pytest
import pandas as pd
import os
import tempfile
from core.loaders import (
    get_file_loader, 
    is_file_supported, 
    get_supported_formats,
    FileLoaderFactory
)
from core.loaders.csv_loader import CsvLoader
from core.loaders.json_loader import JsonLoader
from core.loaders.xml_loader import XmlLoader


class TestFileLoaderFactory:
    """Test the FileLoaderFactory"""

    def test_get_supported_formats(self):
        """Test getting supported formats"""
        formats = get_supported_formats()
        assert isinstance(formats, list)
        assert '.csv' in formats
        assert '.json' in formats
        assert '.xml' in formats
        assert '.parquet' in formats

    def test_is_file_supported(self):
        """Test checking if file format is supported"""
        # Supported formats
        assert is_file_supported('test.csv') == True
        assert is_file_supported('test.json') == True
        assert is_file_supported('test.parquet') == True
        
        # Unsupported formats
        assert is_file_supported('test.txt') == False
        assert is_file_supported('test.doc') == False

    def test_get_loader(self):
        """Test getting appropriate loader for file"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            loader = get_file_loader(tmp_path)
            assert isinstance(loader, CsvLoader)
        finally:
            os.unlink(tmp_path)

    def test_unsupported_format(self):
        """Test error for unsupported format"""
        with tempfile.NamedTemporaryFile(suffix='.unsupported', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                get_file_loader(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_nonexistent_file(self):
        """Test error for nonexistent file"""
        with pytest.raises(FileNotFoundError):
            get_file_loader('nonexistent_file.csv')


class TestCsvLoader:
    """Test CSV/TSV loader"""

    def setup_method(self):
        """Set up test data"""
        # Create test CSV file
        self.csv_content = "name,age,city\nAlice,25,NYC\nBob,30,LA\nCharlie,35,Chicago"
        self.csv_file = "test_data.csv"
        with open(self.csv_file, 'w') as f:
            f.write(self.csv_content)
        
        # Create test TSV file
        self.tsv_content = "name\tage\tcity\nAlice\t25\tNYC\nBob\t30\tLA\nCharlie\t35\tChicago"
        self.tsv_file = "test_data.tsv"
        with open(self.tsv_file, 'w') as f:
            f.write(self.tsv_content)

    def teardown_method(self):
        """Clean up test files"""
        for file in [self.csv_file, self.tsv_file]:
            if os.path.exists(file):
                os.unlink(file)

    def test_csv_loader_creation(self):
        """Test CSV loader creation"""
        loader = CsvLoader(self.csv_file)
        assert loader.get_supported_extensions() == ['.csv', '.tsv']

    def test_csv_load(self):
        """Test loading CSV file"""
        loader = CsvLoader(self.csv_file)
        df = loader.load()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ['name', 'age', 'city']

    def test_tsv_load(self):
        """Test loading TSV file"""
        loader = CsvLoader(self.tsv_file)
        df = loader.load()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ['name', 'age', 'city']

    def test_csv_skip_rows(self):
        """Test loading CSV with skip_rows"""
        loader = CsvLoader(self.csv_file)
        df = loader.load(skip_rows=1)
        assert len(df) == 2
        assert not any('Alice' in str(row) for row in df.values)

    def test_csv_column_rename(self):
        """Test loading CSV with column renaming"""
        loader = CsvLoader(self.csv_file)
        df = loader.load(column_names={'name': 'first_name', 'age': 'years'})
        assert 'first_name' in df.columns
        assert 'years' in df.columns
        assert 'name' not in df.columns

    def test_csv_file_info(self):
        """Test getting CSV file info"""
        loader = CsvLoader(self.csv_file)
        info = loader.get_file_info()
        assert info['format'] == 'CSV/TSV'
        assert 'delimiter' in info
        assert info['file_size_mb'] > 0

    def test_csv_chunk_loading(self):
        """Test CSV chunk loading support"""
        loader = CsvLoader(self.csv_file)
        assert loader.can_load_chunks() == True
        
        df = loader.load_in_chunks(chunk_size=1)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3


class TestJsonLoader:
    """Test JSON loader"""

    def setup_method(self):
        """Set up test data"""
        self.json_content = '[{"name": "Alice", "age": 25, "city": "NYC"}, {"name": "Bob", "age": 30, "city": "LA"}]'
        self.json_file = "test_data.json"
        with open(self.json_file, 'w') as f:
            f.write(self.json_content)

    def teardown_method(self):
        """Clean up test file"""
        if os.path.exists(self.json_file):
            os.unlink(self.json_file)

    def test_json_loader_creation(self):
        """Test JSON loader creation"""
        loader = JsonLoader(self.json_file)
        assert loader.get_supported_extensions() == ['.json']

    def test_json_load(self):
        """Test loading JSON file"""
        loader = JsonLoader(self.json_file)
        df = loader.load()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ['name', 'age', 'city']

    def test_json_file_info(self):
        """Test getting JSON file info"""
        loader = JsonLoader(self.json_file)
        info = loader.get_file_info()
        assert info['format'] == 'JSON'
        assert info['file_size_mb'] > 0

    def test_json_no_chunk_loading(self):
        """Test JSON doesn't support chunk loading"""
        loader = JsonLoader(self.json_file)
        assert loader.can_load_chunks() == False


class TestDataHandlerIntegration:
    """Test integration with data_handler.py"""

    def setup_method(self):
        """Set up test data"""
        self.csv_file = "test_integration.csv"
        with open(self.csv_file, 'w') as f:
            f.write("name,age\nAlice,25\nBob,30")

    def teardown_method(self):
        """Clean up test file"""
        if os.path.exists(self.csv_file):
            os.unlink(self.csv_file)

    def test_cargar_datos_integration(self):
        """Test cargar_datos function integration"""
        from core.data_handler import cargar_datos
        df = cargar_datos(self.csv_file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    def test_cargar_datos_con_opciones_integration(self):
        """Test cargar_datos_con_opciones function integration"""
        from core.data_handler import cargar_datos_con_opciones
        df = cargar_datos_con_opciones(self.csv_file, skip_rows=0, column_names={'name': 'nombre'})
        assert isinstance(df, pd.DataFrame)
        assert 'nombre' in df.columns
        assert 'name' not in df.columns

    def test_supported_formats_function(self):
        """Test get_supported_file_formats function"""
        from core.data_handler import get_supported_file_formats
        formats = get_supported_file_formats()
        assert isinstance(formats, list)
        assert '.csv' in formats

    def test_is_format_supported_function(self):
        """Test is_file_format_supported function"""
        from core.data_handler import is_file_format_supported
        assert is_file_format_supported(self.csv_file) == True
        assert is_file_format_supported('test.txt') == False


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])