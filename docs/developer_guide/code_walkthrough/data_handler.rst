Data Handler System
===================

The DataHandler class is the core component responsible for data loading, processing, validation, and management in Flash Sheet.

Architecture Overview
---------------------

DataHandler serves as the central data management hub, implementing a facade pattern over various data sources and formats.

Key Components
~~~~~~~~~~~~~~

- **Format Detectors**: Automatic format recognition
- **Parsers**: Format-specific data parsing
- **Validators**: Data integrity and type checking
- **Transformers**: Data manipulation and cleaning
- **Exporters**: Multi-format data export
- **Cache Manager**: Performance optimization through caching

Core Responsibilities
~~~~~~~~~~~~~~~~~~~~~

- **Data Loading**: Support for multiple file formats and sources
- **Type Inference**: Automatic data type detection
- **Data Validation**: Integrity checking and error handling
- **Memory Management**: Efficient handling of large datasets
- **Format Conversion**: Data transformation between formats
- **Export Coordination**: Unified export interface

Data Loading Pipeline
---------------------

File Format Detection
~~~~~~~~~~~~~~~~~~~~~

Automatic format detection based on file extensions and content analysis:

.. code-block:: python

    def detect_format(self, file_path):
        extension = Path(file_path).suffix.lower()

        format_map = {
            '.csv': 'csv',
            '.xlsx': '.xls': 'excel',
            '.json': 'json',
            '.parquet': 'parquet',
            '.h5': '.hdf5': 'hdf5',
            '.sql': 'sql'
        }

        return format_map.get(extension, 'unknown')

Parser Selection and Execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dynamic parser selection based on detected format:

.. code-block:: python

    def load_file(self, file_path, **options):
        format_type = self.detect_format(file_path)

        parser = self.get_parser(format_type)
        if not parser:
            raise UnsupportedFormatError(f"Unsupported format: {format_type}")

        try:
            data = parser.parse(file_path, **options)
            validated_data = self.validate_data(data)
            return self.optimize_data(validated_data)
        except Exception as e:
            self.logger.error(f"Failed to load {file_path}: {str(e)}")
            raise

Supported Formats Implementation
--------------------------------

CSV Format Handling
~~~~~~~~~~~~~~~~~~~

Comprehensive CSV parsing with encoding detection:

.. code-block:: python

    class CSVParser:
        def parse(self, file_path, encoding=None, delimiter=None):
            encodings_to_try = [encoding, 'utf-8', 'iso-8859-1', 'cp1252']

            for enc in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        sample = f.read(1024)
                        detected_delim = self.detect_delimiter(sample)

                        df = pd.read_csv(
                            file_path,
                            encoding=enc,
                            delimiter=delimiter or detected_delim,
                            na_values=['', 'NA', 'N/A', 'null']
                        )
                        return df
                except UnicodeDecodeError:
                    continue

            raise EncodingError("Could not determine file encoding")

Excel Format Handling
~~~~~~~~~~~~~~~~~~~~~

Multi-sheet Excel file support with sheet selection:

.. code-block:: python

    class ExcelParser:
        def parse(self, file_path, sheet_name=None, header_row=0):
            xl = pd.ExcelFile(file_path)

            if sheet_name:
                df = xl.parse(sheet_name, header=header_row)
            else:
                # Use first sheet or prompt user
                df = xl.parse(xl.sheet_names[0], header=header_row)

            # Clean column names
            df.columns = df.columns.str.strip()

            return df

JSON and Structured Data
~~~~~~~~~~~~~~~~~~~~~~~~

Flexible JSON parsing with multiple structures:

.. code-block:: python

    class JSONParser:
        def parse(self, file_path, orient=None):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                if orient == 'records':
                    df = pd.DataFrame(data)
                elif orient == 'index':
                    df = pd.DataFrame.from_dict(data, orient='index')
                else:
                    # Try to infer structure
                    df = pd.json_normalize(data)
            else:
                raise ValueError("Unsupported JSON structure")

            return df

Database Connectivity
~~~~~~~~~~~~~~~~~~~~~

SQL database integration with connection pooling:

.. code-block:: python

    class SQLParser:
        def parse(self, connection_string, query):
            engine = create_engine(connection_string)

            try:
                df = pd.read_sql(query, engine)
                return df
            finally:
                engine.dispose()

Data Validation and Cleaning
----------------------------

Type Inference Engine
~~~~~~~~~~~~~~~~~~~~~

Automatic data type detection and conversion:

.. code-block:: python

    def infer_types(self, df):
        for col in df.columns:
            # Try to convert to numeric
            try:
                pd.to_numeric(df[col])
                df[col] = df[col].astype('float64')
                continue
            except (ValueError, TypeError):
                pass

            # Try to convert to datetime
            try:
                pd.to_datetime(df[col])
                df[col] = pd.to_datetime(df[col])
                continue
            except (ValueError, TypeError):
                pass

            # Default to string
            df[col] = df[col].astype('string')

        return df

Data Quality Validation
~~~~~~~~~~~~~~~~~~~~~~~

Comprehensive data quality checks:

.. code-block:: python

    def validate_data(self, df):
        validation_results = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'null_counts': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict()
        }

        # Check for critical issues
        if df.empty:
            raise ValidationError("Dataset is empty")

        if df.columns.duplicated().any():
            raise ValidationError("Duplicate column names found")

        return df, validation_results

Memory Optimization
-------------------

Large Dataset Handling
~~~~~~~~~~~~~~~~~~~~~~

Memory-efficient processing for big data:

.. code-block:: python

    def optimize_memory(self, df):
        # Downcast numeric types
        for col in df.select_dtypes(include=['int64']):
            df[col] = pd.to_numeric(df[col], downcast='integer')

        for col in df.select_dtypes(include=['float64']):
            df[col] = pd.to_numeric(df[col], downcast='float')

        # Convert object columns to category if appropriate
        for col in df.select_dtypes(include=['object']):
            if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique
                df[col] = df[col].astype('category')

        return df

Chunked Processing
~~~~~~~~~~~~~~~~~~

Process large files in chunks to manage memory:

.. code-block:: python

    def load_large_file(self, file_path, chunk_size=10000):
        chunks = []
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            processed_chunk = self.process_chunk(chunk)
            chunks.append(processed_chunk)

        return pd.concat(chunks, ignore_index=True)

Export System
-------------

Unified Export Interface
~~~~~~~~~~~~~~~~~~~~~~~~

Consistent export API across all formats:

.. code-block:: python

    def export_data(self, df, format_type, destination, **options):
        exporter = self.get_exporter(format_type)
        return exporter.export(df, destination, **options)

Format-Specific Exporters
~~~~~~~~~~~~~~~~~~~~~~~~~

Specialized export classes for each format:

.. code-block:: python

    class CSVExporter:
        def export(self, df, destination, **options):
            df.to_csv(
                destination,
                index=options.get('index', False),
                encoding=options.get('encoding', 'utf-8'),
                sep=options.get('delimiter', ',')
            )

    class ExcelExporter:
        def export(self, df, destination, **options):
            with pd.ExcelWriter(destination, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=options.get('sheet_name', 'Sheet1'), index=False)

Caching and Performance
-----------------------

Data Caching Strategy
~~~~~~~~~~~~~~~~~~~~~

Intelligent caching for improved performance:

.. code-block:: python

    class DataCache:
        def __init__(self, max_size=100):
            self.cache = {}
            self.access_order = []
            self.max_size = max_size

        def get(self, key):
            if key in self.cache:
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]
            return None

        def put(self, key, data):
            if key in self.cache:
                self.access_order.remove(key)
            elif len(self.cache) >= self.max_size:
                # Remove least recently used
                lru_key = self.access_order.pop(0)
                del self.cache[lru_key]

            self.cache[key] = data
            self.access_order.append(key)

Error Handling and Recovery
---------------------------

Comprehensive Error Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robust error handling with recovery options:

.. code-block:: python

    class DataHandlerError(Exception):
        pass

    class UnsupportedFormatError(DataHandlerError):
        pass

    class ValidationError(DataHandlerError):
        pass

    def handle_error(self, error, context):
        self.logger.error(f"DataHandler error in {context}: {str(error)}")

        # Attempt recovery strategies
        if isinstance(error, MemoryError):
            self.free_memory()
            # Retry with smaller chunk size
        elif isinstance(error, ValidationError):
            # Try automatic data cleaning
            pass

Integration with Application
---------------------------

Signal-Based Communication
~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration with the main application through signals:

.. code-block:: python

    # Signals emitted by DataHandler
    data_loaded = Signal(DataFrame)  # Emitted when data is successfully loaded
    progress_updated = Signal(int)   # Progress percentage for long operations
    error_occurred = Signal(str)     # Error messages

Threading and Concurrency
~~~~~~~~~~~~~~~~~~~~~~~~~

Background processing for non-blocking operations:

.. code-block:: python

    def load_file_async(self, file_path):
        self.thread_pool.start(lambda: self._load_file_background(file_path))

    def _load_file_background(self, file_path):
        try:
            data = self.load_file(file_path)
            self.data_loaded.emit(data)
        except Exception as e:
            self.error_occurred.emit(str(e))

Testing and Quality Assurance
-----------------------------

Unit Testing Framework
~~~~~~~~~~~~~~~~~~~~~~

Comprehensive test coverage:

.. code-block:: python

    def test_csv_parsing(self):
        # Test various CSV formats
        test_files = [
            'simple.csv',
            'quoted.csv',
            'multiline.csv',
            'encoding_test.csv'
        ]

        for test_file in test_files:
            df = self.load_file(f'test_data/{test_file}')
            self.assertIsInstance(df, pd.DataFrame)
            self.assertGreater(len(df), 0)

Performance Benchmarking
~~~~~~~~~~~~~~~~~~~~~~~~

Performance testing and optimization:

.. code-block:: python

    def benchmark_loading(self, file_path, iterations=5):
        times = []
        for _ in range(iterations):
            start_time = time.time()
            df = self.load_file(file_path)
            end_time = time.time()
            times.append(end_time - start_time)

        avg_time = sum(times) / len(times)
        self.logger.info(f"Average load time for {file_path}: {avg_time:.2f}s")
        return avg_time

Future Enhancements
-------------------

Planned Improvements
~~~~~~~~~~~~~~~~~~~~

- **Streaming Processing**: Real-time data processing
- **Cloud Integration**: Direct loading from cloud storage
- **Advanced Parsing**: Support for complex file formats
- **Machine Learning**: Automatic data quality improvement
- **Plugin Architecture**: Third-party parser extensions