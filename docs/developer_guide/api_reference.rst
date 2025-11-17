API Reference
=============

This section provides comprehensive documentation of Flash Sheet's public APIs, classes, methods, and interfaces.

Core Classes
------------

DataHandler
~~~~~~~~~~~

The central data management component.

**Class Signature:**

.. code-block:: python

    class DataHandler(QObject):
        # Signals
        data_loaded = Signal(DataFrame)
        progress_updated = Signal(int)
        error_occurred = Signal(str)

**Key Methods:**

.. py:method:: load_file(file_path: str, **options) -> DataFrame

    Load data from a file.

    :param file_path: Path to the data file
    :param options: Loading options (encoding, delimiter, etc.)
    :returns: Loaded DataFrame
    :raises: FileNotFoundError, UnsupportedFormatError

.. py:method:: load_folder(folder_path: str, **options) -> DataFrame

    Load and consolidate multiple files from a folder.

    :param folder_path: Path to folder containing data files
    :param options: Consolidation options
    :returns: Consolidated DataFrame

.. py:method:: export_data(data: DataFrame, format: str, destination: str, **options)

    Export data to specified format.

    :param data: DataFrame to export
    :param format: Export format ('csv', 'excel', 'json', etc.)
    :param destination: Output file path
    :param options: Export-specific options

MainWindow
~~~~~~~~~~

Main application window and coordinator.

**Class Signature:**

.. code-block:: python

    class MainWindow(QMainWindow):
        def __init__(self)

**Key Methods:**

.. py:method:: switch_to_view(view_name: str)

    Switch to specified application view.

    :param view_name: Name of view to activate

.. py:method:: load_file()

    Open file dialog and load data file.

.. py:method:: export_data(format: str)

    Export current data in specified format.

View Classes
------------

BaseView
~~~~~~~~

Abstract base class for all application views.

**Class Signature:**

.. code-block:: python

    class BaseView(QWidget):
        # Signals
        data_changed = Signal()
        export_requested = Signal(str)

**Abstract Methods:**

.. py:method:: setup_ui()

    Initialize the view's user interface.

.. py:method:: update_display()

    Refresh the visual display with current data.

**Concrete Methods:**

.. py:method:: set_data(data: DataFrame)

    Load data into the view.

    :param data: DataFrame to display

.. py:method:: get_data() -> DataFrame

    Retrieve current data from the view.

    :returns: Current DataFrame

DataView
~~~~~~~~

Primary data table display view.

**Class Signature:**

.. code-block:: python

    class DataView(BaseView):
        def __init__(self, parent=None)

**Key Methods:**

.. py:method:: apply_filter(filter_config: dict)

    Apply filtering to the displayed data.

    :param filter_config: Filter configuration dictionary

.. py:method:: sort_by_column(column: int, order: Qt.SortOrder)

    Sort data by specified column.

    :param column: Column index to sort by
    :param order: Sort order (Ascending/Descending)

.. py:method:: set_pagination_enabled(enabled: bool, page_size: int = 100)

    Enable or disable data pagination.

    :param enabled: Whether to enable pagination
    :param page_size: Number of rows per page

GraphicsView
~~~~~~~~~~~~

Chart creation and visualization view.

**Class Signature:**

.. code-block:: python

    class GraphicsView(BaseView):
        def __init__(self, parent=None)

**Key Methods:**

.. py:method:: create_chart(chart_type: str, config: dict) -> QChart

    Create a chart of specified type.

    :param chart_type: Type of chart ('bar', 'line', 'pie', etc.)
    :param config: Chart configuration dictionary
    :returns: Created QChart object

.. py:method:: export_chart(format: str, destination: str)

    Export current chart to file.

    :param format: Export format ('png', 'svg', 'pdf')
    :param destination: Output file path

Advanced Feature Classes
------------------------

DataJoinManager
~~~~~~~~~~~~~~~

Manages data join operations between datasets.

**Class Signature:**

.. code-block:: python

    class DataJoinManager:
        def __init__(self)

**Key Methods:**

.. py:method:: perform_join(left_df: DataFrame, right_df: DataFrame, config: dict) -> DataFrame

    Perform join operation between two DataFrames.

    :param left_df: Left DataFrame
    :param right_df: Right DataFrame
    :param config: Join configuration
    :returns: Joined DataFrame

**Join Configuration:**

.. code-block:: python

    join_config = {
        'type': 'inner',  # 'inner', 'left', 'right', 'cross'
        'left_keys': ['id'],  # Column names for left DataFrame
        'right_keys': ['customer_id'],  # Column names for right DataFrame
        'suffixes': ('_left', '_right'),  # Suffixes for duplicate columns
        'indicator': False  # Add merge indicator column
    }

ExcelTemplateSplitter
~~~~~~~~~~~~~~~~~~~~~

Handles template-based separated exports.

**Class Signature:**

.. code-block:: python

    class ExcelTemplateSplitter:
        def __init__(self)

**Key Methods:**

.. py:method:: split_by_template(df: DataFrame, separation_column: str, template_path: str, output_dir: str, **options) -> list

    Split DataFrame and export using Excel template.

    :param df: Input DataFrame
    :param separation_column: Column to split by
    :param template_path: Path to Excel template
    :param output_dir: Output directory
    :param options: Export options
    :returns: List of export results

**Export Options:**

.. code-block:: python

    export_options = {
        'filename_template': '{value}_{date}.xlsx',  # Output filename pattern
        'sheet_name': 'Data',  # Target sheet in template
        'start_row': 2,  # Starting row for data insertion
        'start_col': 1,  # Starting column for data insertion
        'preserve_formatting': True  # Maintain template formatting
    }

PivotTableManager
~~~~~~~~~~~~~~~~~

Manages pivot table creation and operations.

**Class Signature:**

.. code-block:: python

    class PivotTableManager:
        def __init__(self)

**Key Methods:**

.. py:method:: create_pivot(df: DataFrame, config: dict) -> DataFrame

    Create pivot table from DataFrame.

    :param df: Input DataFrame
    :param config: Pivot configuration
    :returns: Pivot table DataFrame

**Pivot Configuration:**

.. code-block:: python

    pivot_config = {
        'values': ['sales', 'quantity'],  # Value columns to aggregate
        'index': ['region', 'product'],  # Row grouping columns
        'columns': ['month'],  # Column grouping columns
        'aggfunc': 'sum',  # Aggregation function
        'fill_value': 0,  # Fill missing values
        'margins': True  # Add totals
    }

Utility Classes
---------------

DataValidator
~~~~~~~~~~~~~

Data validation and quality checking utilities.

**Class Signature:**

.. code-block:: python

    class DataValidator:
        @staticmethod
        def validate_dataframe(df: DataFrame) -> dict

**Validation Results:**

.. code-block:: python

    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'statistics': {
            'total_rows': 1000,
            'total_columns': 5,
            'null_counts': {'col1': 10, 'col2': 0},
            'data_types': {'col1': 'int64', 'col2': 'object'}
        }
    }

FileFormatDetector
~~~~~~~~~~~~~~~~~~

Automatic file format detection.

**Class Signature:**

.. code-block:: python

    class FileFormatDetector:
        @staticmethod
        def detect_format(file_path: str) -> str

**Supported Formats:**

- 'csv': Comma-separated values
- 'excel': Microsoft Excel (.xlsx, .xls)
- 'json': JavaScript Object Notation
- 'parquet': Apache Parquet
- 'hdf5': Hierarchical Data Format
- 'sql': SQL database connection

TypeInferer
~~~~~~~~~~~

Automatic data type inference and conversion.

**Class Signature:**

.. code-block:: python

    class TypeInferer:
        @staticmethod
        def infer_types(df: DataFrame) -> DataFrame

**Type Inference Rules:**

- Numeric strings → int64/float64
- Date strings → datetime64
- Consistent categories → category
- Mixed types → object

Exceptions
----------

Custom exception classes for error handling.

DataHandlerError
~~~~~~~~~~~~~~~~

Base exception for data handling operations.

.. code-block:: python

    class DataHandlerError(Exception):
        pass

FileOperationError
~~~~~~~~~~~~~~~~~~

File-related operation errors.

.. code-block:: python

    class FileOperationError(DataHandlerError):
        def __init__(self, file_path, operation, message):
            self.file_path = file_path
            self.operation = operation
            super().__init__(message)

UnsupportedFormatError
~~~~~~~~~~~~~~~~~~~~~~

Unsupported file format errors.

.. code-block:: python

    class UnsupportedFormatError(DataHandlerError):
        def __init__(self, format_type):
            self.format_type = format_type
            super().__init__(f"Unsupported format: {format_type}")

ValidationError
~~~~~~~~~~~~~~~

Data validation failures.

.. code-block:: python

    class ValidationError(DataHandlerError):
        def __init__(self, issues):
            self.issues = issues
            super().__init__(f"Validation failed: {issues}")

JoinError
~~~~~~~~~

Join operation errors.

.. code-block:: python

    class JoinError(DataHandlerError):
        def __init__(self, message, left_keys=None, right_keys=None):
            self.left_keys = left_keys
            self.right_keys = right_keys
            super().__init__(message)

ExportError
~~~~~~~~~~~

Export operation errors.

.. code-block:: python

    class ExportError(DataHandlerError):
        def __init__(self, format_type, destination, message):
            self.format_type = format_type
            self.destination = destination
            super().__init__(message)

Configuration
-------------

Application Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration management for application settings.

**Configuration File Structure:**

.. code-block:: yaml

    application:
      theme: 'light'  # 'light' or 'dark'
      language: 'en'  # Language code
      max_memory: '2GB'  # Memory limit

    data:
      default_encoding: 'utf-8'
      chunk_size: 10000
      cache_enabled: true

    export:
      default_format: 'csv'
      compression: true
      template_dir: './templates'

**Configuration Access:**

.. code-block:: python

    from config import get_config

    config = get_config()
    theme = config.get('application.theme', 'light')

Signals and Events
------------------

Qt Signal Reference
~~~~~~~~~~~~~~~~~~~

**DataHandler Signals:**

- ``data_loaded(DataFrame)``: Emitted when data is successfully loaded
- ``progress_updated(int)``: Progress percentage for long operations (0-100)
- ``error_occurred(str)``: Error messages with context

**View Signals:**

- ``data_changed()``: Emitted when view data is modified
- ``export_requested(str)``: Request to export data in specified format
- ``view_closed()``: Emitted when view is closed

**MainWindow Signals:**

- ``view_switched(str)``: Emitted when active view changes
- ``operation_started(str)``: Long operation started
- ``operation_completed(str)``: Long operation completed

Event Handling Examples
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Connecting to DataHandler signals
    data_handler.data_loaded.connect(self.on_data_loaded)
    data_handler.progress_updated.connect(self.update_progress_bar)
    data_handler.error_occurred.connect(self.show_error_message)

    # Handling view signals
    current_view.data_changed.connect(self.update_window_title)
    current_view.export_requested.connect(self.handle_export_request)

Constants and Enums
-------------------

Data Types
~~~~~~~~~~

.. code-block:: python

    class DataType:
        STRING = 'string'
        INTEGER = 'int64'
        FLOAT = 'float64'
        DATETIME = 'datetime64'
        BOOLEAN = 'bool'
        CATEGORY = 'category'

Join Types
~~~~~~~~~~

.. code-block:: python

    class JoinType:
        INNER = 'inner'
        LEFT = 'left'
        RIGHT = 'right'
        OUTER = 'outer'
        CROSS = 'cross'

Export Formats
~~~~~~~~~~~~~~

.. code-block:: python

    class ExportFormat:
        CSV = 'csv'
        EXCEL = 'excel'
        JSON = 'json'
        PARQUET = 'parquet'
        HDF5 = 'hdf5'
        SQL = 'sql'
        PDF = 'pdf'
        PNG = 'png'
        SVG = 'svg'

Chart Types
~~~~~~~~~~~

.. code-block:: python

    class ChartType:
        BAR = 'bar'
        LINE = 'line'
        PIE = 'pie'
        SCATTER = 'scatter'
        HISTOGRAM = 'histogram'
        BOX = 'box'
        AREA = 'area'
        HEATMAP = 'heatmap'

Performance Metrics
-------------------

Memory Usage Tracking
~~~~~~~~~~~~~~~~~~~~~

Monitor application memory consumption:

.. code-block:: python

    class MemoryMonitor:
        @staticmethod
        def get_memory_usage() -> dict:
            """Get current memory usage statistics."""
            process = psutil.Process()
            memory_info = process.memory_info()

            return {
                'rss': memory_info.rss,  # Resident Set Size
                'vms': memory_info.vms,  # Virtual Memory Size
                'percent': process.memory_percent()
            }

Operation Timing
~~~~~~~~~~~~~~~~

Performance timing for operations:

.. code-block:: python

    class PerformanceTimer:
        def __init__(self, operation_name):
            self.operation_name = operation_name
            self.start_time = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            if self.start_time:
                duration = time.time() - self.start_time
                logger.info(f"{self.operation_name} completed in {duration:.2f}s")
                return duration

**Context Manager Usage:**

.. code-block:: python

    with PerformanceTimer("data_loading"):
        data = data_handler.load_file(file_path)

Extension Points
----------------

Plugin Architecture
~~~~~~~~~~~~~~~~~~~

Extensible plugin system for custom functionality:

.. code-block:: python

    class PluginInterface(ABC):
        @abstractmethod
        def initialize(self, main_window):
            """Initialize plugin with main window reference."""
            pass

        @abstractmethod
        def get_menu_items(self) -> list:
            """Return menu items to add to application menu."""
            pass

Custom Data Sources
~~~~~~~~~~~~~~~~~~~

Add support for new data sources:

.. code-block:: python

    class CustomDataSource(ABC):
        @abstractmethod
        def can_handle(self, source_spec) -> bool:
            """Check if this source can handle the specification."""
            pass

        @abstractmethod
        def load_data(self, source_spec) -> DataFrame:
            """Load data from the custom source."""
            pass

**Registration:**

.. code-block:: python

    # Register custom data source
    data_handler.register_data_source(CustomDataSource())

Custom Export Formats
~~~~~~~~~~~~~~~~~~~~~

Add new export format support:

.. code-block:: python

    class CustomExporter(ABC):
        @abstractmethod
        def get_format_name(self) -> str:
            """Return the format name."""
            pass

        @abstractmethod
        def export(self, data: DataFrame, destination: str, **options):
            """Export data to custom format."""
            pass

**Registration:**

.. code-block:: python

    # Register custom exporter
    data_handler.register_exporter(CustomExporter())

Migration Guide
---------------

Version Compatibility
~~~~~~~~~~~~~~~~~~~~~

**API Changes by Version:**

- **v1.0.0**: Initial API release
- **v1.1.0**: Added async operations, improved error handling

**Backward Compatibility:**

- All public APIs maintain backward compatibility
- Deprecated methods issue warnings before removal
- Migration guides provided for major version changes

Deprecation Notices
~~~~~~~~~~~~~~~~~~~

**Deprecated Methods:**

.. code-block:: python

    # Deprecated in v1.1.0
    @deprecated("Use load_file() instead")
    def loadDataFile(self, file_path):
        return self.load_file(file_path)

**Migration Path:**

1. Update method calls to use new signatures
2. Replace deprecated classes with current implementations
3. Update configuration files to new format
4. Test with new version before production deployment