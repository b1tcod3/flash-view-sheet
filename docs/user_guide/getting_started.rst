Guía de Inicio Rápido de Flash Sheet (Tutorial de 10 Minutos)
============================================================

¡Bienvenido a Flash Sheet! Este tutorial de 10 minutos te pondrá en funcionamiento con operaciones básicas de carga de datos, visualización y exportación. Al final, habrás cargado datos, creado un gráfico simple y exportado resultados.

.. note::
   **Tiempo Estimado**: 10 minutos
   **Prerrequisitos**: Flash Sheet instalado y ejecutándose
   **Datos de Muestra**: Usaremos un conjunto de datos de ventas simple

Qué Aprenderás
--------------

- Cargar datos desde un archivo CSV
- Navegar y filtrar datos
- Crear un gráfico básico
- Exportar datos y visualizaciones

Paso 1: Iniciar Flash Sheet y Cargar Datos (2 minutos)
-----------------------------------------------------

1. **Lanzar la Aplicación**
   - Haz doble clic en el ícono de Flash Sheet en tu escritorio
   - O lanza desde tu menú de aplicaciones

   .. figure:: ../_static/screenshots/main_interface.png
      :alt: Interfaz principal de Flash Sheet
      :width: 600px

      La interfaz principal de Flash Sheet mostrando el área de carga de datos.

2. **Cargar Datos de Muestra**
   - Haz clic en **"Archivo"** → **"Cargar Archivo"**
   - Navega a tu archivo de datos de muestra (ej. ``sales_data.csv``)
   - Selecciona el archivo y haz clic en **"Abrir"**

   **Contenido CSV de Muestra**::

       Date,Product,Region,Sales,Quantity
       2024-01-01,Laptop,North,1200,5
       2024-01-01,Mouse,North,50,10
       2024-01-02,Laptop,South,2400,10
       2024-01-02,Keyboard,South,150,8
       2024-01-03,Laptop,East,1800,7

3. **Verificar Carga de Datos**
   - Los datos aparecen en la vista de tabla principal
   - Verifica la barra de estado para conteos de filas/columnas
   - Observa la detección automática de tipos de datos

Paso 2: Explorar y Filtrar Datos (3 minutos)
--------------------------------------------

1. **Navegar la Tabla de Datos**
   - Usa **controles de paginación** para navegar a través de filas
   - Haz clic en encabezados de columna para **ordenar** datos (prueba haciendo clic en "Sales")
   - **Redimensiona columnas** arrastrando bordes de columna

2. **Aplicar Filtros Básicos**
   - Haz clic en la **caja de búsqueda** y escribe "Laptop" para filtrar productos
   - Prueba filtrar por región usando el menú desplegable de filtro de columna
   - Limpia filtros usando el botón **"X"**

   .. figure:: ../_static/screenshots/data_filtering.png
      :alt: Interfaz de filtrado de datos
      :width: 600px

      Filtrando datos por nombre de producto y región.

3. **Ver Información del Conjunto de Datos**
   - Haz clic en **"Vista"** → **"Ver Información del dataset"**
   - Revisa tipos de columna, valores nulos y estadísticas básicas

Paso 3: Crear Tu Primer Gráfico (3 minutos)
-------------------------------------------

1. **Cambiar a Vista de Gráficos**
   - Haz clic en la pestaña **"Gráficos"** en la parte superior de la ventana

2. **Crear un Gráfico de Barras**
   - Selecciona **"Barras"** del menú desplegable de tipo de gráfico
   - Elige **"Product"** para eje X y **"Sales"** para eje Y
   - Haz clic en **"Generar Gráfico"**

   .. figure:: ../_static/screenshots/basic_chart.png
      :alt: Gráfico de barras básico
      :width: 600px

      Un gráfico de barras simple mostrando ventas por producto.

3. **Personalizar el Gráfico**
   - Agrega un título: "Ventas por Producto"
   - Cambia colores usando el selector de color
   - Prueba diferentes tipos de gráfico (Línea, Torta)

Paso 4: Exportar Resultados (2 minutos)
---------------------------------------

1. **Exportar los Datos Filtrados**
   - Regresa a la pestaña **"Datos"**
   - Haz clic en **"Exportar"** → **"Exportar Excel"**
   - Elige nombre de archivo y ubicación
   - Haz clic en **"Exportar"**

2. **Exportar el Gráfico**
   - Cambia de vuelta a la pestaña **"Gráficos"**
   - Haz clic en **"Exportar"** → **"Exportar Imagen"**
   - Selecciona formato PNG y guarda

   .. figure:: ../_static/screenshots/export_dialog.png
      :alt: Diálogo de exportación
      :width: 600px

      Diálogo de exportación mostrando opciones de formato.

¡Felicitaciones! 🎉
------------------

Has completado el tutorial de inicio rápido de Flash Sheet. Ahora sabes cómo:

- ✅ Cargar datos desde archivos
- ✅ Navegar y filtrar conjuntos de datos
- ✅ Crear visualizaciones básicas
- ✅ Exportar datos y gráficos

¿Qué Sigue?
-----------

Ahora que conoces lo básico, explora estas características avanzadas:

- :doc:`basic_usage` - Resumen completo de características
- :doc:`data_visualization` - Operaciones avanzadas de tabla
- :doc:`graphics` - Creación profesional de gráficos
- :doc:`basic_export` - Todos los formatos de exportación
- :doc:`advanced_features` - Uniones, tablas pivote y plantillas

Para ayuda con cualquier problema, consulta :doc:`troubleshooting`.

Requisitos del Sistema
----------------------

- **Sistema Operativo**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python**: 3.7 o superior
- **Memoria**: Mínimo 4GB RAM (8GB recomendado)
- **Almacenamiento**: 500MB de espacio libre

Instalación
-----------

Para instrucciones detalladas de instalación, consulta :doc:`../releases/installation_guide`.