"""
Test suite for folder loading functionality
Tests the folder loader, consolidator, and dialog components
"""

import pytest
import pandas as pd
import os
import tempfile
from pathlib import Path
from core.loaders.folder_loader import FolderLoader
from core.consolidation.excel_consolidator import ExcelConsolidator
from core.models.folder_load_config import FolderLoadConfig, ColumnAlignmentStrategy
from core.models.file_metadata import FileMetadata


class TestFolderLoader:
    """Test the FolderLoader class"""

    def setup_method(self):
        """Set up test data"""
        self.temp_dir = tempfile.mkdtemp()

        # Create test Excel files
        self.create_test_excel_file("file1.xlsx", [["Name", "Age"], ["Alice", 25], ["Bob", 30]])
        self.create_test_excel_file("file2.xlsx", [["Name", "City"], ["Charlie", "NYC"], ["David", "LA"]])
        self.create_test_excel_file("file3.xlsx", [["Name", "Score"], ["Eve", 95], ["Frank", 87]])

        # Create a non-Excel file
        self.non_excel_file = os.path.join(self.temp_dir, "notes.txt")
        with open(self.non_excel_file, 'w') as f:
            f.write("This is not an Excel file")

    def teardown_method(self):
        """Clean up test files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def create_test_excel_file(self, filename, data):
        """Create a test Excel file"""
        df = pd.DataFrame(data[1:], columns=data[0])
        filepath = os.path.join(self.temp_dir, filename)
        df.to_excel(filepath, index=False)

    def test_folder_loader_creation(self):
        """Test FolderLoader initialization"""
        loader = FolderLoader(self.temp_dir)
        assert loader.folder_path == Path(self.temp_dir)
        assert len(loader.excel_files) == 3  # Should find 3 Excel files

    def test_scan_excel_files(self):
        """Test scanning for Excel files"""
        loader = FolderLoader(self.temp_dir)
        excel_files = loader.get_excel_files()
        assert len(excel_files) == 3
        assert all(f.endswith('.xlsx') for f in excel_files)

    def test_get_file_metadata(self):
        """Test getting metadata for a file"""
        loader = FolderLoader(self.temp_dir)
        first_file = loader.get_excel_files()[0]
        metadata = loader.get_file_metadata(first_file)

        assert 'filename' in metadata
        assert 'filepath' in metadata
        assert metadata['num_columns'] > 0
        assert metadata['num_rows'] > 0
        assert metadata['file_size_mb'] >= 0

    def test_get_all_metadata(self):
        """Test getting metadata for all files"""
        loader = FolderLoader(self.temp_dir)
        all_metadata = loader.get_all_metadata()
        assert len(all_metadata) == 3
        for meta in all_metadata:
            assert 'filename' in meta
            assert meta['filename'].endswith('.xlsx')

    def test_invalid_folder(self):
        """Test error handling for invalid folder"""
        with pytest.raises(FileNotFoundError):
            FolderLoader("/nonexistent/folder")


class TestExcelConsolidator:
    """Test the ExcelConsolidator class"""

    def setup_method(self):
        """Set up test data"""
        self.consolidator = ExcelConsolidator()

        # Create test DataFrames
        self.df1 = pd.DataFrame({
            'Name': ['Alice', 'Bob'],
            'Age': [25, 30]
        })

        self.df2 = pd.DataFrame({
            'Name': ['Charlie', 'David'],
            'City': ['NYC', 'LA']
        })

        self.df3 = pd.DataFrame({
            'Name': ['Eve', 'Frank'],
            'Score': [95, 87]
        })

    def test_add_dataframe(self):
        """Test adding DataFrames to consolidator"""
        self.consolidator.add_dataframe(self.df1, "file1.xlsx")
        assert len(self.consolidator.dataframes) == 1
        assert self.consolidator.dataframes[0]['source'] == "file1.xlsx"

    def test_align_by_position(self):
        """Test alignment by position"""
        self.consolidator.add_dataframe(self.df1, "file1.xlsx")
        self.consolidator.add_dataframe(self.df2, "file2.xlsx")
        self.consolidator.add_dataframe(self.df3, "file3.xlsx")

        result = self.consolidator.align_by_position()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 6  # 2 + 2 + 2 rows
        assert '__source__' in result.columns

    def test_column_mappings(self):
        """Test column renaming"""
        self.consolidator.add_dataframe(self.df1, "file1.xlsx")
        self.consolidator.set_column_mappings({'Name': 'Full_Name', 'Age': 'Years'})

        result = self.consolidator.align_by_position()
        assert 'Full_Name' in result.columns
        assert 'Years' in result.columns
        assert 'Name' not in result.columns
        assert 'Age' not in result.columns

    def test_get_column_alignment_preview(self):
        """Test column alignment preview"""
        self.consolidator.add_dataframe(self.df1, "file1.xlsx")
        self.consolidator.add_dataframe(self.df2, "file2.xlsx")

        preview = self.consolidator.get_column_alignment_preview()
        assert isinstance(preview, list)
        assert len(preview) == 2  # Max columns between the two DataFrames

    def test_consolidate_method(self):
        """Test consolidate method"""
        self.consolidator.add_dataframe(self.df1, "file1.xlsx")
        result = self.consolidator.consolidate('position')
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_clear_method(self):
        """Test clearing consolidator"""
        self.consolidator.add_dataframe(self.df1, "file1.xlsx")
        self.consolidator.clear()
        assert len(self.consolidator.dataframes) == 0
        assert len(self.consolidator.column_mappings) == 0


class TestFolderLoadConfig:
    """Test the FolderLoadConfig model"""

    def test_config_creation(self):
        """Test creating a folder load config"""
        config = FolderLoadConfig(
            folder_path="/test/path",
            included_files=["file1.xlsx", "file2.xlsx"],
            excluded_files=["temp.xlsx"],
            alignment_strategy=ColumnAlignmentStrategy.BY_POSITION,
            column_rename_mapping={"old": "new"},
            skip_rows=1,
            add_source_column=True
        )

        assert config.folder_path == "/test/path"
        assert len(config.included_files) == 2
        assert len(config.excluded_files) == 1
        assert config.alignment_strategy == ColumnAlignmentStrategy.BY_POSITION

    def test_should_include_file(self):
        """Test file inclusion logic"""
        config = FolderLoadConfig(
            folder_path="/test/path",
            included_files=["file1.xlsx"],
            excluded_files=["file2.xlsx"]
        )

        assert config.should_include_file("file1.xlsx") == True
        assert config.should_include_file("file2.xlsx") == False
        assert config.should_include_file("file3.xlsx") == False  # Not in included list

        # Test with no specific includes/excludes
        config2 = FolderLoadConfig(folder_path="/test/path")
        assert config2.should_include_file("any.xlsx") == True

        # Test with no specific includes/excludes
        config2 = FolderLoadConfig(folder_path="/test/path")
        assert config2.should_include_file("any.xlsx") == True

    def test_config_to_dict(self):
        """Test converting config to dict"""
        config = FolderLoadConfig(folder_path="/test/path")
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict['folder_path'] == "/test/path"


class TestFileMetadata:
    """Test the FileMetadata model"""

    def test_metadata_creation(self):
        """Test creating file metadata"""
        metadata = FileMetadata(
            filename="test.xlsx",
            filepath="/path/test.xlsx",
            file_size_bytes=1024,
            file_size_mb=1.0,
            sheets=["Sheet1"],
            sheet_count=1,
            columns=["Name", "Age"],
            num_columns=2,
            num_rows=10
        )

        assert metadata.filename == "test.xlsx"
        assert metadata.num_columns == 2
        assert metadata.has_error == False

    def test_metadata_with_error(self):
        """Test metadata with error"""
        metadata = FileMetadata(
            filename="test.xlsx",
            filepath="/path/test.xlsx",
            file_size_bytes=1024,
            file_size_mb=1.0,
            sheets=[],
            sheet_count=0,
            columns=[],
            num_columns=0,
            num_rows=0,
            error="File corrupted"
        )

        assert metadata.has_error == True
        assert metadata.error == "File corrupted"

    def test_metadata_to_dict(self):
        """Test converting metadata to dict"""
        metadata = FileMetadata(
            filename="test.xlsx",
            filepath="/path/test.xlsx",
            file_size_bytes=1024,
            file_size_mb=1.0,
            sheets=["Sheet1"],
            sheet_count=1,
            columns=["Name"],
            num_columns=1,
            num_rows=5
        )

        meta_dict = metadata.to_dict()
        assert isinstance(meta_dict, dict)
        assert meta_dict['filename'] == "test.xlsx"
        assert meta_dict['num_rows'] == 5


class TestIntegration:
    """Test integration of folder loading components"""

    def setup_method(self):
        """Set up test data"""
        self.temp_dir = tempfile.mkdtemp()

        # Create test Excel files with different structures
        self.create_test_excel_file("sales_q1.xlsx", [["Product", "Q1_Sales"], ["A", 100], ["B", 200]])
        self.create_test_excel_file("sales_q2.xlsx", [["Product", "Q2_Sales"], ["A", 150], ["B", 250]])
        self.create_test_excel_file("inventory.xlsx", [["Product", "Stock"], ["A", 50], ["B", 75]])

    def teardown_method(self):
        """Clean up test files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def create_test_excel_file(self, filename, data):
        """Create a test Excel file"""
        df = pd.DataFrame(data[1:], columns=data[0])
        filepath = os.path.join(self.temp_dir, filename)
        df.to_excel(filepath, index=False)

    def test_full_folder_loading_workflow(self):
        """Test complete folder loading workflow"""
        # Create config
        config = FolderLoadConfig(
            folder_path=self.temp_dir,
            add_source_column=True,
            column_rename_mapping={"Q1_Sales": "Sales_Q1", "Q2_Sales": "Sales_Q2"}
        )

        # Load folder
        loader = FolderLoader(config.folder_path)
        files = loader.get_excel_files()
        assert len(files) == 3

        # Consolidate
        consolidator = ExcelConsolidator()
        for file_path in files:
            df = pd.read_excel(file_path)
            consolidator.add_dataframe(df, os.path.basename(file_path))

        consolidator.set_column_mappings(config.column_rename_mapping)
        result = consolidator.consolidate()

        # Verify results
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 6  # 2 + 2 + 2 rows
        assert '__source__' in result.columns

        # Check column renaming
        assert 'Sales_Q1' in result.columns or 'Sales_Q2' in result.columns


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])