Basic Usage Guide
==================

This guide covers the fundamental operations in Flash Sheet, including loading data, navigating the interface, and performing basic data operations.

Loading Data Files
------------------

Flash Sheet supports multiple data formats for loading:

Supported Formats
~~~~~~~~~~~~~~~~~

- **CSV**: Comma-separated values (.csv)
- **Excel**: Microsoft Excel files (.xlsx, .xls)
- **JSON**: JavaScript Object Notation (.json)
- **Parquet**: Columnar storage format (.parquet)
- **HDF5**: Hierarchical Data Format (.h5)
- **SQL Databases**: Direct connection to databases

Loading a Single File
~~~~~~~~~~~~~~~~~~~~~

1. Click **"Archivo"** → **"Cargar Archivo"** in the main menu
2. Navigate to your data file
3. Select the file and click **"Open"**
4. The data will be loaded and displayed in the main table view

File Loading Options
~~~~~~~~~~~~~~~~~~~~

- **Encoding Selection**: Choose the appropriate text encoding (UTF-8, ISO-8859-1, etc.)
- **Delimiter Detection**: Automatic detection of CSV delimiters
- **Header Row**: Specify which row contains column headers
- **Data Types**: Automatic type detection for columns

Navigating the Interface
------------------------

Main Interface Components
~~~~~~~~~~~~~~~~~~~~~~~~~

The Flash Sheet interface consists of several key areas:

- **Menu Bar**: Access to all application functions
- **Toolbar**: Quick access to common operations
- **Data View**: Main table displaying loaded data
- **Status Bar**: Information about current dataset and operations

View Navigation
~~~~~~~~~~~~~~~

Flash Sheet provides multiple views for different purposes:

- **Data View**: Primary table view with data manipulation tools
- **Graphics View**: Chart and visualization tools
- **Joined Data View**: Results of data join operations

Switching between views using the tab system or menu options.

Data Table Operations
---------------------

Viewing Data
~~~~~~~~~~~~

- **Pagination**: Navigate through large datasets using page controls
- **Column Sorting**: Click column headers to sort data
- **Column Resizing**: Drag column borders to adjust widths
- **Row Selection**: Click rows to select them for operations

Filtering and Searching
~~~~~~~~~~~~~~~~~~~~~~~

- **Global Search**: Use the search box to find specific values
- **Column Filters**: Apply filters to individual columns
- **Advanced Filters**: Combine multiple filter conditions
- **Filter Persistence**: Save and reuse filter configurations

Dataset Information
~~~~~~~~~~~~~~~~~~~

View comprehensive information about your loaded data:

- **Row Count**: Total number of records
- **Column Count**: Number of columns
- **Data Types**: Type information for each column
- **Memory Usage**: Dataset size information
- **Null Values**: Count of missing values per column

Basic Data Export
-----------------

Flash Sheet supports multiple export formats:

Export to CSV
~~~~~~~~~~~~~

1. Click **"Exportar"** → **"Exportar CSV"**
2. Choose the destination folder
3. Configure export options (delimiter, encoding, etc.)
4. Click **"Export"**

Export to Excel
~~~~~~~~~~~~~~~

1. Click **"Exportar"** → **"Exportar Excel"**
2. Select the destination and filename
3. Choose whether to include formatting
4. Click **"Export"**

Other Export Options
~~~~~~~~~~~~~~~~~~~~

- **PDF Export**: Generate formatted PDF reports
- **SQL Export**: Create SQL INSERT statements
- **Image Export**: Save charts and visualizations as images

Keyboard Shortcuts
------------------

Common keyboard shortcuts for efficient operation:

- **Ctrl+O**: Open file
- **Ctrl+S**: Save/export current view
- **Ctrl+F**: Focus search box
- **Ctrl+R**: Refresh data view
- **F5**: Reload dataset
- **Esc**: Cancel current operation

Next Steps
----------

Once comfortable with basic operations, explore:

- :doc:`data_visualization` - Advanced data viewing techniques
- :doc:`graphics` - Creating charts and visualizations
- :doc:`basic_export` - Comprehensive export options
- :doc:`advanced_features` - Advanced data manipulation