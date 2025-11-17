API Reference - Classes
=======================

This section provides detailed documentation for all classes in the Flash Sheet modules, including Exportación Separada and Cruce de Datos (Join) functionalities.

Core Classes
------------

ExcelTemplateSplitter
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: core.data_handler.ExcelTemplateSplitter
   :members:
   :undoc-members:
   :show-inheritance:

ExportSeparatedConfig
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: core.data_handler.ExportSeparatedConfig
   :members:
   :undoc-members:
   :show-inheritance:

ValidationResult
~~~~~~~~~~~~~~~

.. autoclass:: core.data_handler.ValidationResult
   :members:
   :undoc-members:
   :show-inheritance:

ExportResult
~~~~~~~~~~~

.. autoclass:: core.data_handler.ExportResult
   :members:
   :undoc-members:
   :show-inheritance:

Exception Classes
-----------------

SeparationError
~~~~~~~~~~~~~~~

.. autoclass:: core.data_handler.SeparationError
   :members:
   :undoc-members:
   :show-inheritance:

TemplateError
~~~~~~~~~~~~~

.. autoclass:: core.data_handler.TemplateError
   :members:
   :undoc-members:
   :show-inheritance:

ConfigurationError
~~~~~~~~~~~~~~~~~~

.. autoclass:: core.data_handler.ConfigurationError
   :members:
   :undoc-members:
   :show-inheritance:

MemoryError
~~~~~~~~~~~

.. autoclass:: core.data_handler.MemoryError
   :members:
   :undoc-members:
   :show-inheritance:

UI Classes
----------

ExportSeparatedDialog
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: app.widgets.export_separated_dialog.ExportSeparatedDialog
   :members:
   :undoc-members:
   :show-inheritance:

ColumnMappingWidget
~~~~~~~~~~~~~~~~~~~

.. autoclass:: app.widgets.export_separated_dialog.ColumnMappingWidget
   :members:
   :undoc-members:
   :show-inheritance:

ExcelTemplateDialog
~~~~~~~~~~~~~~~~~~~

.. autoclass:: app.widgets.export_separated_dialog.ExcelTemplateDialog
   :members:
   :undoc-members:
   :show-inheritance:

FilePreviewDialog
~~~~~~~~~~~~~~~~~

.. autoclass:: app.widgets.export_separated_dialog.FilePreviewDialog
    :members:
    :undoc-members:
    :show-inheritance:

Join (Cruce de Datos) Classes
-----------------------------

DataJoinManager
~~~~~~~~~~~~~~~

.. autoclass:: core.join.data_join_manager.DataJoinManager
    :members:
    :undoc-members:
    :show-inheritance:

JoinConfig
~~~~~~~~~~

.. autoclass:: core.join.models.JoinConfig
    :members:
    :undoc-members:
    :show-inheritance:

JoinResult
~~~~~~~~~~

.. autoclass:: core.join.models.JoinResult
    :members:
    :undoc-members:
    :show-inheritance:

JoinMetadata
~~~~~~~~~~~~

.. autoclass:: core.join.models.JoinMetadata
    :members:
    :undoc-members:
    :show-inheritance:

ValidationResult (Join)
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: core.join.models.ValidationResult
    :members:
    :undoc-members:
    :show-inheritance:

JoinHistory
~~~~~~~~~~~

.. autoclass:: core.join.join_history.JoinHistory
    :members:
    :undoc-members:
    :show-inheritance:

JoinHistoryEntry
~~~~~~~~~~~~~~~~

.. autoclass:: core.join.join_history.JoinHistoryEntry
    :members:
    :undoc-members:
    :show-inheritance:

Join Exception Classes
~~~~~~~~~~~~~~~~~~~~~~

JoinError
^^^^^^^^^

.. autoclass:: core.join.exceptions.JoinError
    :members:
    :undoc-members:
    :show-inheritance:

JoinValidationError
^^^^^^^^^^^^^^^^^^^

.. autoclass:: core.join.exceptions.JoinValidationError
    :members:
    :undoc-members:
    :show-inheritance:

JoinExecutionError
^^^^^^^^^^^^^^^^^^

.. autoclass:: core.join.exceptions.JoinExecutionError
    :members:
    :undoc-members:
    :show-inheritance:

MemoryLimitExceededError
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: core.join.exceptions.MemoryLimitExceededError
    :members:
    :undoc-members:
    :show-inheritance:

UnsupportedJoinError
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: core.join.exceptions.UnsupportedJoinError
    :members:
    :undoc-members:
    :show-inheritance:

Join UI Classes
~~~~~~~~~~~~~~~

JoinDialog
^^^^^^^^^^

.. autoclass:: app.widgets.join.join_dialog.JoinDialog
    :members:
    :undoc-members:
    :show-inheritance:

JoinedDataView
^^^^^^^^^^^^^^

.. autoclass:: app.widgets.join.joined_data_view.JoinedDataView
    :members:
    :undoc-members:
    :show-inheritance:

Function Reference
-----------------

Main Export Function
~~~~~~~~~~~~~~~~~~~

.. autofunction:: core.data_handler.exportar_datos_separados

Helper Functions
~~~~~~~~~~~~~~~

.. autofunction:: core.data_handler.cargar_datos

.. autofunction:: core.data_handler.obtener_metadata

.. autofunction:: core.data_handler.limpiar_datos

DataFrame Processing
~~~~~~~~~~~~~~~~~~

.. autofunction:: core.data_handler.aplicar_filtro

.. autofunction:: core.data_handler.aplicar_transformacion

.. autofunction:: core.data_handler.obtener_estadisticas

Export Functions
~~~~~~~~~~~~~~

.. autofunction:: core.data_handler.exportar_a_pdf

.. autofunction:: core.data_handler.exportar_a_sql

.. autofunction:: core.data_handler.exportar_a_imagen

Usage Examples
--------------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   from core.data_handler import exportar_datos_separados, ExportSeparatedConfig
   
   # Load your data
   df = pd.read_csv('your_data.csv')
   
   # Configure separation
   config = {
       'separator_column': 'category',
       'template_path': 'template.xlsx',
       'output_folder': 'output/',
       'file_template': '{valor}_report.xlsx'
   }
   
   # Export separated data
   result = exportar_datos_separados(df, config)
   print(f"Files created: {result['files_created']}")

Advanced Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from core.data_handler import ExportSeparatedConfig, ExcelTemplateSplitter
   
   # Create detailed configuration
   config = ExportSeparatedConfig(
       separator_column='region',
       template_path='corporate_template.xlsx',
       output_folder='regional_reports/',
       file_template='{valor}_Q4_2025.xlsx',
       column_mapping={'sales': 'B', 'product': 'C'},
       start_cell='A5',
       handle_duplicates='overwrite',
       enable_chunking=True,
       max_memory_mb=2048
   )
   
   # Execute with advanced options
   splitter = ExcelTemplateSplitter(df, config)
   result = splitter.separate_and_export()

Error Handling
~~~~~~~~~~~~~

.. code-block:: python

   from core.data_handler import SeparationError, TemplateError
   
   try:
       result = exportar_datos_separados(df, config)
   except TemplateError as e:
       print(f"Template error: {e}")
   except SeparationError as e:
       print(f"Separation error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

Join Usage Examples
~~~~~~~~~~~~~~~~~~~

Basic Join Usage
^^^^^^^^^^^^^^^^

.. code-block:: python

   import pandas as pd
   from core.join.data_join_manager import DataJoinManager
   from core.join.models import JoinConfig, JoinType

   # Load your datasets
   sales_df = pd.read_csv('sales_2023.csv')
   customers_df = pd.read_csv('customers.csv')

   # Create join manager
   join_manager = DataJoinManager(sales_df, customers_df)

   # Configure join
   config = JoinConfig(
       join_type=JoinType.LEFT,
       left_keys=['customer_id'],
       right_keys=['id'],
       suffixes=('_sales', '_customer')
   )

   # Execute join
   result = join_manager.execute_join(config)

   if result.success:
       print(f"Join completed successfully!")
       print(f"Result has {result.metadata.result_rows} rows")
       print(f"Processing time: {result.metadata.processing_time_seconds:.2f}s")
   else:
       print(f"Join failed: {result.error_message}")

Advanced Join Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from core.join.models import JoinConfig, JoinType
   from core.join.data_join_manager import DataJoinManager

   # Advanced configuration with validation and indicators
   config = JoinConfig(
       join_type=JoinType.INNER,
       left_keys=['customer_id', 'product_id'],
       right_keys=['id', 'product_code'],
       suffixes=('_left', '_right'),
       validate_integrity=True,
       sort_results=True,
       indicator=True  # Add _merge column
   )

   # Get preview before executing
   preview = join_manager.get_join_preview(config, max_rows=50)
   print("Preview of results:")
   print(preview.head())

   # Validate configuration
   validation = join_manager.validate_join(config)
   if validation.is_valid:
       result = join_manager.execute_join(config)
   else:
       print("Validation errors:", validation.errors)

Join History Management
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from core.join.join_history import JoinHistory

   # Initialize history manager
   history = JoinHistory(max_entries=100)

   # Add completed join to history
   history.add_entry(
       left_name="sales_2023.csv",
       right_name="customers.csv",
       config=config,
       result=result
   )

   # Retrieve recent joins
   recent_joins = history.get_entries(limit=10)

   # Export history
   history.export_history("join_history_backup.json")

   # Import history from file
   history.import_history("join_history_backup.json")

Error Handling in Joins
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from core.join.exceptions import (
       JoinValidationError,
       JoinExecutionError,
       MemoryLimitExceededError,
       UnsupportedJoinError
   )

   try:
       result = join_manager.execute_join(config)
       if not result.success:
           print(f"Join failed: {result.error_message}")
   except JoinValidationError as e:
       print(f"Configuration validation error: {e}")
       print(f"Details: {e.details}")
   except JoinExecutionError as e:
       print(f"Execution error during join: {e}")
   except MemoryLimitExceededError as e:
       print(f"Memory limit exceeded: {e}")
       print("Try using smaller datasets or enable chunking")
   except UnsupportedJoinError as e:
       print(f"Unsupported join type: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")