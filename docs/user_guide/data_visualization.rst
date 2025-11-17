Data Visualization Guide
========================

This guide covers the data visualization features in Flash Sheet, including table views, filtering, sorting, and data exploration tools.

Table View Features
-------------------

The main data table provides comprehensive viewing and manipulation capabilities.

Pagination
~~~~~~~~~~

For large datasets, Flash Sheet automatically paginates the data:

- **Page Size Options**: Choose from 10, 25, 50, 100, or 500 rows per page
- **Navigation Controls**: First, Previous, Next, Last page buttons
- **Page Jump**: Enter specific page numbers directly
- **Row Count Display**: Shows current range and total rows

Column Operations
~~~~~~~~~~~~~~~~~

- **Sorting**: Click column headers to sort ascending/descending
- **Multi-column Sort**: Hold Shift while clicking for secondary sorts
- **Column Resizing**: Drag column borders to adjust widths
- **Column Reordering**: Drag column headers to rearrange
- **Column Visibility**: Show/hide columns as needed

Filtering Data
--------------

Flash Sheet provides powerful filtering capabilities to focus on relevant data.

Global Search
~~~~~~~~~~~~~

- **Search Box**: Enter text to search across all visible columns
- **Real-time Filtering**: Results update as you type
- **Case Sensitivity**: Toggle case-sensitive search
- **Highlighting**: Matching text is highlighted in results

Column-specific Filters
~~~~~~~~~~~~~~~~~~~~~~

Apply filters to individual columns:

- **Text Filters**: Contains, starts with, ends with, exact match
- **Numeric Filters**: Greater than, less than, between, equals
- **Date Filters**: Before, after, between dates
- **Null Value Filters**: Show/hide null or empty values

Advanced Filtering
~~~~~~~~~~~~~~~~~~

- **Filter Combinations**: AND/OR logic between multiple filters
- **Filter Groups**: Create complex filter hierarchies
- **Saved Filters**: Save and reuse filter configurations
- **Filter History**: Access recently used filters

Data Exploration
----------------

Understanding Your Dataset
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flash Sheet provides tools to analyze your data structure:

Dataset Summary
^^^^^^^^^^^^^^^

- **Row Count**: Total number of records
- **Column Count**: Number of columns
- **Data Types**: Automatic detection of column types
- **Memory Usage**: Dataset size and memory consumption
- **Null Analysis**: Count of missing values per column

Column Statistics
^^^^^^^^^^^^^^^^^

For numeric columns:

- **Min/Max Values**: Range of values
- **Mean/Average**: Central tendency
- **Standard Deviation**: Data spread
- **Quartiles**: Distribution analysis

For text columns:

- **Unique Values**: Count of distinct values
- **Most Frequent**: Top occurring values
- **Length Statistics**: Text length analysis

Data Quality Checks
^^^^^^^^^^^^^^^^^^^

- **Duplicate Detection**: Identify duplicate rows
- **Consistency Checks**: Validate data patterns
- **Type Validation**: Ensure data type consistency
- **Range Validation**: Check for outliers

View Customization
------------------

Table Appearance
~~~~~~~~~~~~~~~~

- **Themes**: Light and dark theme options
- **Font Size**: Adjustable text size
- **Row Height**: Customize row spacing
- **Grid Lines**: Show/hide table grid

Exporting Views
~~~~~~~~~~~~~~~

- **Current View Export**: Export only filtered/visible data
- **Complete Dataset**: Export entire dataset regardless of filters
- **Custom Ranges**: Export specific row ranges
- **Format Options**: Choose export format and options

Performance Optimization
------------------------

For large datasets, Flash Sheet includes performance features:

- **Lazy Loading**: Load data on demand
- **Indexing**: Automatic indexing for fast searches
- **Caching**: Cache filtered results
- **Memory Management**: Efficient memory usage

Keyboard Shortcuts
------------------

- **Ctrl+F**: Focus search box
- **Ctrl+Shift+F**: Clear all filters
- **Ctrl+G**: Go to specific row
- **Ctrl+Home**: First page
- **Ctrl+End**: Last page
- **F3**: Repeat last search

Next Steps
----------

- :doc:`graphics` - Create visual charts and graphs
- :doc:`basic_export` - Export your visualized data
- :doc:`advanced_features` - Advanced visualization techniques