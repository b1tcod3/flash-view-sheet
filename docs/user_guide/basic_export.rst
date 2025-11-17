Basic Export Guide
==================

Flash Sheet provides comprehensive export capabilities to save your data and visualizations in various formats for use in other applications.

Supported Export Formats
------------------------

Data Export Formats
~~~~~~~~~~~~~~~~~~~

- **CSV (Comma-Separated Values)**: Universal spreadsheet format
- **Excel (.xlsx)**: Microsoft Excel format with formatting
- **JSON**: Structured data format for web applications
- **Parquet**: Columnar format for big data
- **HDF5**: Scientific data format
- **SQL**: Database insert statements

Visualization Export Formats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **PDF**: Portable document format for reports
- **PNG**: High-quality image format
- **SVG**: Scalable vector graphics
- **JPEG**: Compressed image format

Exporting Data Tables
---------------------

CSV Export
~~~~~~~~~~

1. Click **"Exportar"** → **"Exportar CSV"**
2. Choose the destination folder and filename
3. Configure options:
   - **Delimiter**: Comma, semicolon, tab, or custom
   - **Encoding**: UTF-8, ISO-8859-1, or other
   - **Include Headers**: Include column names as first row
   - **Quote Character**: Character for enclosing fields
4. Click **"Export"**

Excel Export
~~~~~~~~~~~~

1. Click **"Exportar"** → **"Exportar Excel"**
2. Select destination and filename
3. Choose options:
   - **Sheet Name**: Name for the Excel worksheet
   - **Include Formatting**: Preserve table formatting
   - **Auto-fit Columns**: Adjust column widths automatically
   - **Freeze Headers**: Keep column headers visible when scrolling
4. Click **"Export"**

JSON Export
~~~~~~~~~~~

1. Click **"Exportar"** → **"Exportar JSON"**
2. Configure format options:
   - **Pretty Print**: Formatted JSON with indentation
   - **Compact**: Minified JSON for smaller files
   - **Array Format**: Export as JSON array of objects
   - **Object Format**: Export as single JSON object

SQL Export
~~~~~~~~~~

1. Click **"Exportar"** → **"Exportar SQL"**
2. Select database type (MySQL, PostgreSQL, SQLite, etc.)
3. Configure options:
   - **Table Name**: Name for the database table
   - **Create Table**: Include CREATE TABLE statement
   - **Drop Table**: Include DROP TABLE IF EXISTS
   - **Insert Method**: Single INSERT or bulk INSERT
4. Click **"Export"**

Exporting Charts and Visualizations
-----------------------------------

PDF Export
~~~~~~~~~~

1. Switch to **Graphics View**
2. Select the chart to export
3. Click **"Exportar"** → **"Exportar PDF"**
4. Configure:
   - **Page Size**: A4, Letter, Legal, Custom
   - **Orientation**: Portrait or Landscape
   - **Margins**: Page margins in inches/cm
   - **Quality**: Resolution settings

Image Export
~~~~~~~~~~~~

1. Select the chart in Graphics View
2. Click **"Exportar"** → **"Exportar Imagen"**
3. Choose format (PNG, JPEG, SVG)
4. Configure:
   - **Resolution**: DPI (72, 150, 300, custom)
   - **Size**: Width and height in pixels
   - **Background**: Transparent or solid color
   - **Quality**: Compression level (for JPEG)

Export Options and Settings
---------------------------

Data Range Selection
~~~~~~~~~~~~~~~~~~~~

- **All Data**: Export the complete dataset
- **Current View**: Export only visible/filtered data
- **Selected Rows**: Export only selected rows
- **Custom Range**: Specify row range to export

Column Selection
~~~~~~~~~~~~~~~~

- **All Columns**: Export all columns
- **Visible Columns**: Only currently visible columns
- **Selected Columns**: Choose specific columns
- **Custom Order**: Rearrange column order for export

File Naming and Organization
----------------------------

Automatic Naming
~~~~~~~~~~~~~~~~

- **Timestamp**: Include date/time in filename
- **Dataset Name**: Use original dataset name
- **Export Type**: Include format in filename
- **Sequential Numbers**: For multiple exports

Custom Templates
~~~~~~~~~~~~~~~~

Use placeholders for dynamic naming:

- `{date}`: Current date (YYYY-MM-DD)
- `{time}`: Current time (HHMMSS)
- `{dataset}`: Dataset name
- `{type}`: Export format
- `{counter}`: Sequential number

Batch Export
~~~~~~~~~~~~

- **Multiple Formats**: Export to several formats simultaneously
- **Split Files**: Divide large datasets into multiple files
- **Template Application**: Apply different settings per format

Performance Considerations
--------------------------

Large Dataset Handling
~~~~~~~~~~~~~~~~~~~~~~

- **Chunking**: Automatically split large exports
- **Memory Management**: Efficient processing for big data
- **Progress Tracking**: Monitor export progress
- **Cancellation**: Stop long-running exports

Optimization Tips
~~~~~~~~~~~~~~~~~

- **Filter First**: Apply filters before exporting to reduce size
- **Select Columns**: Export only needed columns
- **Choose Format**: Select appropriate format for your use case
- **Compression**: Use compressed formats when possible

Troubleshooting Export Issues
-----------------------------

Common Problems
~~~~~~~~~~~~~~~

- **File Locked**: Close file if open in another application
- **Permission Denied**: Check write permissions on destination folder
- **Disk Space**: Ensure sufficient space for export
- **Encoding Issues**: Choose appropriate text encoding

Error Recovery
~~~~~~~~~~~~~~

- **Partial Exports**: Resume interrupted exports
- **Backup Creation**: Automatic backup of existing files
- **Validation**: Check export integrity
- **Log Files**: Review detailed error logs

Next Steps
----------

- :doc:`advanced_features` - Advanced export techniques
- :doc:`troubleshooting` - Export-related issues
- :doc:`getting_started` - Basic usage overview