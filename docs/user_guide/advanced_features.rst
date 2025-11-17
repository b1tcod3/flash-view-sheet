Advanced Features Guide
======================

This guide covers the advanced functionality in Flash Sheet, including folder loading, data joins, separated exports, and pivot tables.

Folder Loading
--------------

Loading Multiple Files
~~~~~~~~~~~~~~~~~~~~~~

Folder loading allows you to consolidate data from multiple Excel files in a directory:

1. Click **"Archivo"** → **"Cargar Carpeta..."**
2. Select the folder containing your Excel files
3. Choose files to include in the consolidation
4. Configure column alignment (automatic or manual)
5. Review the preview and consolidate

Supported Formats
~~~~~~~~~~~~~~~~~

- **Excel Files**: .xlsx and .xls formats
- **Recursive Search**: Include files in subdirectories
- **File Filtering**: Select specific files or patterns
- **Metadata Preview**: View file information before loading

Column Alignment
~~~~~~~~~~~~~~~~

- **Automatic Alignment**: Match columns by position or name
- **Manual Alignment**: Drag and drop to realign columns
- **Column Renaming**: Customize consolidated column names
- **Type Handling**: Manage different data types across files

Data Joins (Merging)
--------------------

Join Operations
~~~~~~~~~~~~~~~

Flash Sheet supports SQL-like join operations to combine datasets:

Types of Joins
^^^^^^^^^^^^^^

- **Inner Join**: Only matching rows from both datasets
- **Left Join**: All rows from left dataset + matches from right
- **Right Join**: All rows from right dataset + matches from left
- **Cross Join**: Cartesian product of both datasets

Join Configuration
^^^^^^^^^^^^^^^^^^

1. Load the primary dataset
2. Click **"Datos"** → **"Cruzar Datos..."**
3. Load the secondary dataset
4. Select join type and matching columns
5. Configure additional options
6. Preview and execute the join

Advanced Join Options
^^^^^^^^^^^^^^^^^^^^^

- **Multiple Join Keys**: Join on multiple column combinations
- **Join Conditions**: Custom join logic beyond equality
- **Suffix Handling**: Manage duplicate column names
- **Null Handling**: Control how null values affect joins

Separated Exports
-----------------

Template-Based Exports
~~~~~~~~~~~~~~~~~~~~~~

Separated exports allow you to split data into multiple Excel files using templates:

1. Prepare your Excel template with formatting
2. Load the dataset with a separation column
3. Click **"Separar"** → **"Exportar Datos Separados..."**
4. Configure separation column and template
5. Set output options and export

Template Requirements
~~~~~~~~~~~~~~~~~~~~~

- **Excel Format**: .xlsx files (not .xls)
- **Header Row**: Column headers in first row
- **Data Area**: Designated area for data insertion
- **Formatting**: Preserve fonts, colors, formulas

Export Configuration
~~~~~~~~~~~~~~~~~~~~

- **Separation Column**: Column containing group identifiers
- **File Naming**: Templates for output filenames
- **Output Directory**: Destination folder for generated files
- **Column Mapping**: Map dataset columns to template columns

Pivot Tables
------------

Creating Pivot Tables
~~~~~~~~~~~~~~~~~~~~~

Pivot tables provide dynamic data summarization:

1. Load your dataset
2. Click **"Datos"** → **"Tabla Pivote..."**
3. Select row, column, and value fields
4. Configure aggregation functions
5. Generate the pivot table

Pivot Components
~~~~~~~~~~~~~~~~

- **Row Fields**: Categories for row grouping
- **Column Fields**: Categories for column grouping
- **Value Fields**: Numeric fields to aggregate
- **Filter Fields**: Fields for filtering the entire pivot

Aggregation Functions
~~~~~~~~~~~~~~~~~~~~~

- **Sum**: Total of values
- **Count**: Number of items
- **Average**: Mean of values
- **Min/Max**: Minimum or maximum values
- **Standard Deviation**: Statistical spread
- **Custom Functions**: User-defined aggregations

Advanced Pivot Features
~~~~~~~~~~~~~~~~~~~~~~~

- **Multiple Consolidation**: Combine multiple value fields
- **Calculated Fields**: Add computed columns
- **Grouping**: Group dates, numbers, or text values
- **Drill-down**: Expand pivot details

Combined Operations
-------------------

Workflow Integration
~~~~~~~~~~~~~~~~~~~~

Combine multiple advanced features in workflows:

- **Load Folder → Join → Export Separated**
- **Load Data → Create Pivot → Export to Multiple Formats**
- **Join Multiple Datasets → Apply Filters → Generate Reports**

Data Pipeline Examples
~~~~~~~~~~~~~~~~~~~~~~

**Sales Analysis Pipeline:**

1. Load monthly sales files from folder
2. Join with customer database
3. Create pivot table by region/product
4. Export separated reports by region
5. Generate summary charts

**Inventory Management Pipeline:**

1. Load inventory files from multiple warehouses
2. Join with product catalog
3. Apply filters for low stock items
4. Create pivot analysis by category
5. Export alerts and reports

Performance Optimization
------------------------

Large Dataset Handling
~~~~~~~~~~~~~~~~~~~~~~

- **Chunking**: Process data in manageable chunks
- **Memory Management**: Efficient memory usage
- **Indexing**: Automatic indexing for fast operations
- **Caching**: Cache intermediate results

Optimization Techniques
~~~~~~~~~~~~~~~~~~~~~~~

- **Data Type Optimization**: Use appropriate data types
- **Column Selection**: Work with only needed columns
- **Filtering Early**: Apply filters before complex operations
- **Parallel Processing**: Utilize multiple CPU cores

Error Handling and Recovery
---------------------------

Common Issues
~~~~~~~~~~~~~

- **Memory Errors**: For very large datasets
- **File Permission Issues**: Access rights problems
- **Data Type Conflicts**: Incompatible column types
- **Template Format Issues**: Invalid Excel templates

Recovery Options
~~~~~~~~~~~~~~~~

- **Automatic Recovery**: Resume interrupted operations
- **Partial Results**: Save completed portions
- **Error Logging**: Detailed error information
- **Rollback**: Undo problematic operations

Best Practices
--------------

Data Preparation
~~~~~~~~~~~~~~~~

- **Clean Data**: Handle missing values and outliers
- **Consistent Formats**: Standardize date and number formats
- **Validation**: Check data integrity before operations
- **Backup**: Keep original data safe

Workflow Planning
~~~~~~~~~~~~~~~~~

- **Plan Operations**: Design workflow before execution
- **Test with Samples**: Validate with small data samples
- **Monitor Resources**: Watch memory and disk usage
- **Document Processes**: Record successful workflows

Next Steps
----------

- :doc:`troubleshooting` - Solutions for advanced feature issues
- :doc:`getting_started` - Return to basic usage
- :doc:`../developer_guide/architecture` - Technical implementation details