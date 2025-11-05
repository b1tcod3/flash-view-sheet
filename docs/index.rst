Flash Sheet - Sistema de Exportación de Datos Separados
=========================================================

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   user_guide/README
   user_guide/tutorial/basic_usage
   user_guide/tutorial/advanced_config
   user_guide/troubleshooting/common_issues

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide:

   developer_guide/architecture
   developer_guide/contributing
   developer_guide/testing
   developer_guide/deployment

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/overview
   api/classes
   api/configuration

.. toctree::
   :maxdepth: 2
   :caption: Releases:

   releases/v1.0.0/release_notes
   releases/v1.0.0/installation
   releases/v1.0.0/upgrade_guide

Overview
========

Flash Sheet es un sistema avanzado de análisis y exportación de datos que incluye una funcionalidad de **Exportación de Datos Separados con Plantillas Excel**. Esta funcionalidad permite:

- Separar un DataFrame en múltiples archivos Excel basado en una columna de separación
- Usar plantillas Excel personalizadas preservando formato original
- Mapeo flexible de columnas DataFrame ↔ Excel
- Optimización automática para datasets grandes
- Interfaz gráfica intuitiva para configuración

Key Features
============

- **Plantillas Excel**: Preservación completa del formato original
- **Mapeo Inteligente**: Conversión automática y manual de columnas
- **Optimización**: Chunking automático para datasets grandes
- **Interfaz Gráfica**: Configuración visual con validación en tiempo real
- **Robustez**: Manejo de casos especiales y recovery automático

Quick Start
===========

1. **Import your data** into Flash Sheet
2. **Navigate** to Menu → "Separar" → "Exportar Datos Separados"
3. **Configure** column separation, Excel template, and output settings
4. **Preview** the files that will be created
5. **Export** your separated data files

For detailed instructions, see the :doc:`user_guide/tutorial/basic_usage`.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Version Information
===================

- **Current Version**: 1.0.0
- **Release Date**: 2025-11-05
- **Python Support**: 3.7+
- **Dependencies**: pandas, openpyxl, PySide6

License
=======

This project is licensed under the MIT License.