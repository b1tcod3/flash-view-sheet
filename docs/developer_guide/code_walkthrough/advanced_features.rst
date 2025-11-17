Advanced Features Implementation
==============================

This document covers the implementation details of Flash Sheet's advanced features including folder loading, data joins, separated exports, and pivot tables.

Folder Loading Implementation
-----------------------------

FolderLoader Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~

The FolderLoader handles batch processing of multiple Excel files:

.. code-block:: python

    class FolderLoader:
        def __init__(self, data_handler):
            self.data_handler = data_handler
            self.logger = logging.getLogger(__name__)

        def load_folder(self, folder_path, **options):
            """
            Load and consolidate multiple Excel files from a folder.

            Args:
                folder_path: Path to folder containing Excel files
                options: Configuration options for loading

            Returns:
                Consolidated DataFrame
            """
            excel_files = self.discover_excel_files(folder_path)
            file_metadata = self.analyze_files(excel_files)

            if options.get('interactive_alignment', True):
                alignment_config = self.get_user_alignment_config(file_metadata)
            else:
                alignment_config = self.auto_align_columns(file_metadata)

            consolidated_data = self.consolidate_files(
                excel_files, alignment_config, options
            )

            return consolidated_data

File Discovery and Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Automatic detection and metadata extraction:

.. code-block:: python

    def discover_excel_files(self, folder_path):
        """Find all Excel files in the specified folder."""
        excel_files = []
        for file_path in Path(folder_path).rglob('*'):
            if file_path.suffix.lower() in ['.xlsx', '.xls']:
                excel_files.append(file_path)

        return sorted(excel_files)

    def analyze_files(self, file_paths):
        """Extract metadata from each Excel file."""
        metadata = []
        for file_path in file_paths:
            try:
                xl = pd.ExcelFile(file_path)
                file_info = {
                    'path': file_path,
                    'sheets': xl.sheet_names,
                    'columns': {},
                    'row_counts': {}
                }

                # Analyze each sheet
                for sheet_name in xl.sheet_names:
                    df = xl.parse(sheet_name, nrows=5)  # Sample first 5 rows
                    file_info['columns'][sheet_name] = df.columns.tolist()
                    file_info['row_counts'][sheet_name] = len(df)

                metadata.append(file_info)
            except Exception as e:
                self.logger.warning(f"Failed to analyze {file_path}: {e}")

        return metadata

Column Alignment System
~~~~~~~~~~~~~~~~~~~~~~~

Interactive and automatic column alignment:

.. code-block:: python

    class ColumnAlignmentDialog(QDialog):
        def __init__(self, file_metadata):
            super().__init__()
            self.file_metadata = file_metadata
            self.alignment_config = {}
            self.setup_ui()

        def setup_ui(self):
            layout = QVBoxLayout()

            # File selector
            self.file_combo = QComboBox()
            self.file_combo.addItems([str(f['path']) for f in self.file_metadata])
            layout.addWidget(self.file_combo)

            # Alignment table
            self.alignment_table = QTableWidget()
            self.setup_alignment_table()
            layout.addWidget(self.alignment_table)

            # Control buttons
            button_layout = QHBoxLayout()
            self.auto_align_btn = QPushButton("Auto Align")
            self.manual_align_btn = QPushButton("Manual Align")
            self.ok_btn = QPushButton("OK")

            button_layout.addWidget(self.auto_align_btn)
            button_layout.addWidget(self.manual_align_btn)
            button_layout.addStretch()
            button_layout.addWidget(self.ok_btn)

            layout.addLayout(button_layout)
            self.setLayout(layout)

            self.connect_signals()

Data Join Implementation
------------------------

DataJoinManager Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Comprehensive join operations management:

.. code-block:: python

    class DataJoinManager:
        def __init__(self):
            self.join_history = []
            self.logger = logging.getLogger(__name__)

        def perform_join(self, left_df, right_df, join_config):
            """
            Perform join operation between two DataFrames.

            Args:
                left_df: Left DataFrame
                right_df: Right DataFrame
                join_config: Join configuration dictionary

            Returns:
                Join result DataFrame
            """
            join_type = join_config['type']
            left_keys = join_config['left_keys']
            right_keys = join_config['right_keys']

            try:
                result = self.execute_join(
                    left_df, right_df, join_type, left_keys, right_keys
                )

                # Apply additional options
                if join_config.get('suffixes'):
                    result = self.apply_suffixes(result, join_config['suffixes'])

                if join_config.get('indicator'):
                    result = self.add_merge_indicator(result, join_config['indicator'])

                # Store in history
                self.join_history.append({
                    'timestamp': datetime.now(),
                    'config': join_config,
                    'result_shape': result.shape
                })

                return result

            except Exception as e:
                self.logger.error(f"Join failed: {e}")
                raise

Join Execution Engine
~~~~~~~~~~~~~~~~~~~~~

Optimized join execution with multiple strategies:

.. code-block:: python

    def execute_join(self, left_df, right_df, join_type, left_keys, right_keys):
        """Execute the actual join operation."""

        # Validate join keys
        self.validate_join_keys(left_df, right_df, left_keys, right_keys)

        # Choose join strategy based on data size
        if len(left_df) * len(right_df) > 1000000:  # Large join
            result = self.perform_chunked_join(
                left_df, right_df, join_type, left_keys, right_keys
            )
        else:
            result = self.perform_direct_join(
                left_df, right_df, join_type, left_keys, right_keys
            )

        return result

    def perform_direct_join(self, left_df, right_df, join_type, left_keys, right_keys):
        """Perform standard pandas join."""
        join_params = {
            'how': join_type.lower(),
            'left_on': left_keys,
            'right_on': right_keys
        }

        return left_df.merge(right_df, **join_params)

Join Validation and Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data validation and performance optimization:

.. code-block:: python

    def validate_join_keys(self, left_df, right_df, left_keys, right_keys):
        """Validate join key compatibility."""
        for left_key, right_key in zip(left_keys, right_keys):
            if left_key not in left_df.columns:
                raise ValueError(f"Left key '{left_key}' not found in left DataFrame")
            if right_key not in right_df.columns:
                raise ValueError(f"Right key '{right_key}' not found in right DataFrame")

            # Check type compatibility
            left_type = left_df[left_key].dtype
            right_type = right_df[right_key].dtype

            if not self.types_compatible(left_type, right_type):
                self.logger.warning(f"Type mismatch: {left_type} vs {right_type}")

    def types_compatible(self, type1, type2):
        """Check if data types are compatible for joining."""
        compatible_pairs = [
            (np.dtype('int64'), np.dtype('float64')),
            (np.dtype('float64'), np.dtype('int64')),
            (np.dtype('object'), np.dtype('string')),
            # Add more compatibility rules
        ]

        return (type1, type2) in compatible_pairs or type1 == type2

Separated Export Implementation
------------------------------

ExcelTemplateSplitter Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Template-based separated exports:

.. code-block:: python

    class ExcelTemplateSplitter:
        def __init__(self):
            self.template_cache = {}
            self.logger = logging.getLogger(__name__)

        def split_by_template(self, df, separation_column, template_path, output_dir, **options):
            """
            Split DataFrame and export using Excel template.

            Args:
                df: Input DataFrame
                separation_column: Column to split by
                template_path: Path to Excel template
                output_dir: Output directory
                options: Export configuration options
            """
            # Validate inputs
            self.validate_inputs(df, separation_column, template_path)

            # Load and cache template
            template = self.load_template(template_path)

            # Get unique values for separation
            unique_values = df[separation_column].unique()

            # Process each group
            results = []
            for value in unique_values:
                group_df = df[df[separation_column] == value]
                output_path = self.generate_output_path(
                    output_dir, value, options.get('filename_template', '{value}.xlsx')
                )

                try:
                    self.export_group(group_df, template, output_path, options)
                    results.append({
                        'value': value,
                        'output_path': output_path,
                        'row_count': len(group_df)
                    })
                except Exception as e:
                    self.logger.error(f"Failed to export group {value}: {e}")

            return results

Template Processing
~~~~~~~~~~~~~~~~~~~

Excel template handling and data insertion:

.. code-block:: python

    def load_template(self, template_path):
        """Load and analyze Excel template."""
        if template_path in self.template_cache:
            return self.template_cache[template_path]

        try:
            wb = openpyxl.load_workbook(template_path)
            template_info = {
                'workbook': wb,
                'sheets': {},
                'data_ranges': {}
            }

            # Analyze each worksheet
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                template_info['sheets'][sheet_name] = ws

                # Find data insertion areas (look for placeholders or empty ranges)
                data_range = self.find_data_range(ws)
                if data_range:
                    template_info['data_ranges'][sheet_name] = data_range

            self.template_cache[template_path] = template_info
            return template_info

        except Exception as e:
            raise TemplateLoadError(f"Failed to load template: {e}")

Data Insertion Logic
~~~~~~~~~~~~~~~~~~~~

Intelligent data insertion into templates:

.. code-block:: python

    def export_group(self, group_df, template_info, output_path, options):
        """Export a data group using the template."""
        wb = copy.deepcopy(template_info['workbook'])

        # Get target sheet
        sheet_name = options.get('sheet_name', wb.active.title)
        ws = wb[sheet_name]

        # Determine insertion point
        start_row = options.get('start_row', 2)  # Default to row 2
        start_col = options.get('start_col', 1)  # Default to column A

        # Insert data
        for row_idx, (_, row) in enumerate(group_df.iterrows()):
            for col_idx, value in enumerate(row):
                cell = ws.cell(row=start_row + row_idx, column=start_col + col_idx)
                cell.value = value

        # Apply formatting if specified
        if options.get('preserve_formatting', True):
            self.apply_formatting(ws, start_row, start_col, len(group_df), len(group_df.columns))

        # Save the file
        wb.save(output_path)

Pivot Table Implementation
--------------------------

PivotTableManager Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dynamic pivot table creation and management:

.. code-block:: python

    class PivotTableManager:
        def __init__(self):
            self.pivot_history = []
            self.logger = logging.getLogger(__name__)

        def create_pivot(self, df, pivot_config):
            """
            Create pivot table from DataFrame.

            Args:
                df: Input DataFrame
                pivot_config: Pivot configuration dictionary

            Returns:
                Pivot table DataFrame
            """
            try:
                pivot = pd.pivot_table(
                    df,
                    values=pivot_config.get('values'),
                    index=pivot_config.get('index'),
                    columns=pivot_config.get('columns'),
                    aggfunc=pivot_config.get('aggfunc', 'sum'),
                    fill_value=pivot_config.get('fill_value', 0),
                    margins=pivot_config.get('margins', False)
                )

                # Store in history
                self.pivot_history.append({
                    'timestamp': datetime.now(),
                    'config': pivot_config,
                    'result_shape': pivot.shape
                })

                return pivot

            except Exception as e:
                self.logger.error(f"Pivot creation failed: {e}")
                raise

Advanced Pivot Features
~~~~~~~~~~~~~~~~~~~~~~~

Enhanced pivot table capabilities:

.. code-block:: python

    def create_multi_level_pivot(self, df, config):
        """Create pivot with multiple index/column levels."""
        pivot = pd.pivot_table(
            df,
            values=config['values'],
            index=config['index'],  # Can be list for multi-level
            columns=config['columns'],  # Can be list for multi-level
            aggfunc=config.get('aggfunc', 'sum')
        )

        return pivot

    def add_calculated_fields(self, pivot_df, calculations):
        """Add calculated fields to pivot table."""
        for calc_name, calc_func in calculations.items():
            pivot_df[calc_name] = pivot_df.apply(calc_func, axis=1)

        return pivot_df

Performance Optimization
------------------------

Memory Management
~~~~~~~~~~~~~~~~~

Efficient processing for large datasets:

.. code-block:: python

    def optimize_for_large_data(self, operation_type, data_size):
        """Apply optimizations based on data size and operation type."""
        if data_size > 1000000:  # 1M rows
            if operation_type == 'join':
                return {
                    'chunk_size': 50000,
                    'use_low_memory': True,
                    'parallel_processing': True
                }
            elif operation_type == 'pivot':
                return {
                    'use_sparse': True,
                    'chunk_processing': True
                }

        return {}  # Default settings

Chunked Processing
~~~~~~~~~~~~~~~~~~

Process large operations in manageable chunks:

.. code-block:: python

    def process_in_chunks(self, operation_func, data, chunk_size=10000):
        """Process data in chunks to manage memory."""
        results = []

        for i in range(0, len(data), chunk_size):
            chunk = data.iloc[i:i + chunk_size]
            chunk_result = operation_func(chunk)
            results.append(chunk_result)

        # Combine results
        if isinstance(results[0], pd.DataFrame):
            return pd.concat(results, ignore_index=True)
        else:
            return results

Error Handling and Recovery
---------------------------

Robust Error Management
~~~~~~~~~~~~~~~~~~~~~~~

Comprehensive error handling for advanced operations:

.. code-block:: python

    class AdvancedFeatureError(Exception):
        pass

    class JoinError(AdvancedFeatureError):
        pass

    class ExportError(AdvancedFeatureError):
        pass

    class PivotError(AdvancedFeatureError):
        pass

Recovery Strategies
~~~~~~~~~~~~~~~~~~~

Automatic recovery and user guidance:

.. code-block:: python

    def handle_operation_error(self, error, operation_type, context):
        """Handle errors with appropriate recovery strategies."""

        if isinstance(error, MemoryError):
            # Suggest memory optimization
            suggestion = "Try processing in smaller chunks or use less data"
            self.show_recovery_dialog(suggestion)

        elif isinstance(error, JoinError):
            # Check join key validity
            if 'key not found' in str(error):
                suggestion = "Verify join keys exist in both datasets"
            else:
                suggestion = "Check data types compatibility"

        elif isinstance(error, ExportError):
            # Check file permissions and disk space
            suggestion = "Check file permissions and available disk space"

        self.logger.error(f"{operation_type} failed in {context}: {error}")
        self.show_error_dialog(str(error), suggestion)

Testing and Validation
----------------------

Comprehensive Testing
~~~~~~~~~~~~~~~~~~~~~

Test coverage for advanced features:

.. code-block:: python

    def test_folder_loading(self):
        """Test folder loading functionality."""
        # Create test files
        test_files = self.create_test_excel_files()

        # Test loading
        loader = FolderLoader(self.data_handler)
        result = loader.load_folder(self.test_folder)

        # Validate results
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)

        # Check consolidation
        expected_columns = set()
        for file_info in test_files:
            expected_columns.update(file_info['columns'])
        self.assertTrue(expected_columns.issubset(set(result.columns)))

Integration Testing
~~~~~~~~~~~~~~~~~~~

End-to-end testing of feature combinations:

.. code-block:: python

    def test_complete_workflow(self):
        """Test complete data processing workflow."""
        # Load folder
        consolidated = self.folder_loader.load_folder('test_data/')

        # Perform join
        joined = self.join_manager.perform_join(
            consolidated, self.reference_data, self.join_config
        )

        # Create pivot
        pivot = self.pivot_manager.create_pivot(joined, self.pivot_config)

        # Export separated
        results = self.excel_splitter.split_by_template(
            pivot, 'category', 'template.xlsx', 'output/'
        )

        # Validate final results
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertTrue(Path(result['output_path']).exists())

Future Enhancements
-------------------

Planned Improvements
~~~~~~~~~~~~~~~~~~~~

- **Machine Learning Integration**: Auto-detect optimal join keys and operations
- **Real-time Processing**: Streaming data processing capabilities
- **Cloud Integration**: Direct processing of cloud-stored data
- **Advanced Analytics**: Built-in statistical analysis and modeling
- **Collaboration Features**: Multi-user simultaneous operations
- **Performance Monitoring**: Real-time performance metrics and optimization