API Reference - Classes
=======================

This section provides detailed documentation for all classes in the Exportación Separada module.

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