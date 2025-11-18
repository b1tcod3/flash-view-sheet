Flash Sheet - Herramienta de Análisis y Exportación de Datos
=============================================

Flash Sheet es una aplicación completa para análisis de datos, visualización y exportación con características avanzadas para manipulación de datos e informes.

.. toctree::
    :maxdepth: 2
    :caption: Guía del Usuario:

    user_guide/getting_started
    user_guide/basic_usage
    user_guide/data_visualization
    user_guide/graphics
    user_guide/basic_export
    user_guide/advanced_features
    user_guide/troubleshooting

.. toctree::
    :maxdepth: 2
    :caption: Guía del Desarrollador:

    developer_guide/architecture
    developer_guide/code_walkthrough/main_window
    developer_guide/code_walkthrough/data_handler
    developer_guide/code_walkthrough/views_system
    developer_guide/code_walkthrough/advanced_features
    developer_guide/api_reference
    developer_guide/development_guide

.. toctree::
    :maxdepth: 2
    :caption: Versiones:

    releases/installation_guide
    releases/v1.0.0/release_notes
    releases/v1.0.0/installation_guide
    releases/v1.1.0/release_notes
    releases/v1.1.0/installation_guide

Resumen
========

Flash Sheet es un sistema avanzado de análisis y exportación de datos que incluye una funcionalidad de **Exportación de Datos Separados con Plantillas Excel**. Esta funcionalidad permite:

- Separar un DataFrame en múltiples archivos Excel basado en una columna de separación
- Usar plantillas Excel personalizadas preservando formato original
- Mapeo flexible de columnas DataFrame ↔ Excel
- Optimización automática para datasets grandes
- Interfaz gráfica intuitiva para configuración

Características Principales
===========================

- **Plantillas Excel**: Preservación completa del formato original
- **Mapeo Inteligente**: Conversión automática y manual de columnas
- **Optimización**: Chunking automático para datasets grandes
- **Interfaz Gráfica**: Configuración visual con validación en tiempo real
- **Robustez**: Manejo de casos especiales y recovery automático

Inicio Rápido
=============

1. **Importa tus datos** en Flash Sheet
2. **Navega** al Menú → "Separar" → "Exportar Datos Separados"
3. **Configura** la separación de columnas, plantilla Excel y ajustes de salida
4. **Previsualiza** los archivos que se crearán
5. **Exporta** tus archivos de datos separados

Para instrucciones detalladas, consulta :doc:`user_guide/basic_usage`.

Índices y tablas
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Información de Versión
======================

- **Versión Actual**: 1.0.0
- **Fecha de Lanzamiento**: 2025-11-05
- **Soporte de Python**: 3.7+
- **Dependencias**: pandas, openpyxl, PySide6

Licencia
=======

Este proyecto está licenciado bajo la Licencia MIT.