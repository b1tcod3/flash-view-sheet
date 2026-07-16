Guía para Contribuidores - Exportación Separada
===============================================

Esta guía está dirigida a desarrolladores que desean contribuir al proyecto de Exportación de Datos Separados.

Prerrequisitos
--------------

Requisitos Técnicos
~~~~~~~~~~~~~~~~~~

- **Python**: 3.7 o superior
- **Entorno de desarrollo**: Git, VSCode (recomendado)
- **Dependencias principales**: pandas, openpyxl, PySide6
- **Testing**: unittest, pytest (opcional)

Instalación del Entorno de Desarrollo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Clonar el repositorio**:
   .. code-block:: bash

      git clone <repository-url>
      cd flash-sheet

2. **Instalar dependencias de desarrollo**:
   .. code-block:: bash

      pip install -r requirements.txt
      pip install pytest pytest-cov  # Para testing avanzado

3. **Verificar instalación**:
   .. code-block:: bash

      python -c "import pandas, openpyxl, PySide6; print('✓ All dependencies installed')"

Estructura del Proyecto
----------------------

Estructura de Directorios
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   flash-sheet/
   ├── app/
   │   └── widgets/
   │       └── export_separated_dialog.py     # UI Principal
   ├── core/
   │   ├── data_handler.py                    # Core Logic
   │   ├── performance_optimizer.py           # Performance System
   │   └── loaders/                           # Data Loading
   ├── tests/
   │   ├── test_excel_template_splitter.py    # Unit Tests
   │   ├── test_integration_export_separated.py # Integration Tests
   │   └── test_performance_export_separated.py # Performance Tests
   ├── docs/                                  # Documentación
   │   ├── user_guide/
   │   ├── developer_guide/
   │   └── api/
   ├── separar/                               # Planning Documents
   └── examples/                              # Ejemplos de uso

Archivos Clave
~~~~~~~~~~~~

- **core/data_handler.py**: Lógica principal de separación
- **app/widgets/export_separated_dialog.py**: Interfaz de usuario
- **tests/**: Suite completa de testing
- **docs/**: Documentación completa

Convenciones de Código
--------------------

Estilo de Código
~~~~~~~~~~~~~~

**Python PEP 8**:
- Máximo 79 caracteres por línea
- Nombres de variables: `snake_case`
- Nombres de clases: `PascalCase`
- Constantes: `UPPER_CASE`

**Ejemplo**:
.. code-block:: python

   class ExcelTemplateSplitter:
       """Clase para separación de datos con plantillas Excel."""
       
       def __init__(self, df: pd.DataFrame, config: ExportSeparatedConfig):
           self.df = df
           self.config = config
           
       def separate_and_export(self) -> Dict[str, Any]:
           """Ejecutar separación completa."""
           return {}

Documentación de Código
~~~~~~~~~~~~~~~~~~~~

**Docstrings**:
- Usar formato Google/Napoleon
- Incluir parámetros, retornos y excepciones

.. code-block:: python

   def export_datos_separados(df: pd.DataFrame, config_dict: dict) -> dict:
       """
       Exportar DataFrame a archivos Excel separados usando plantillas.
       
       Args:
           df: DataFrame a separar
           config_dict: Configuración de separación que incluye:
               - separator_column: str - Columna para separar
               - template_path: str - Ruta a plantilla Excel
               - output_folder: str - Carpeta destino
               - file_template: str - Plantilla de nombre de archivo
       
       Returns:
           dict con resultado de exportación incluyendo:
               - success: bool - Estado de éxito
               - files_created: List[str] - Archivos generados
               - processing_time: float - Tiempo de procesamiento
       
       Raises:
           SeparationError: Si hay error en la separación
           TemplateError: Si hay problema con la plantilla Excel
       """

Manejo de Errores
~~~~~~~~~~~~~~~

**Jerarquía de Excepciones**:
.. code-block:: python

   class SeparationError(Exception):
       """Error base para separación de datos."""
       pass

   class TemplateError(SeparationError):
       """Error específico de plantilla Excel."""
       pass

   class ConfigurationError(SeparationError):
       """Error de configuración inválida."""
       pass

**Uso correcto**:
.. code-block:: python

   try:
       result = splitter.separate_and_export()
   except TemplateError as e:
       logger.error(f"Template error: {e}")
       raise
   except SeparationError as e:
       logger.warning(f"Separation error: {e}")
       return {'success': False, 'error': str(e)}

Testing Guidelines
-----------------

Ejecución de Tests
~~~~~~~~~~~~~~~~

**Tests completos**:
.. code-block:: bash

   # Ejecutar todos los tests
   python -m pytest tests/ -v

   # Tests específicos
   python -m pytest tests/test_excel_template_splitter.py -v

   # Con cobertura
   python -m pytest tests/ --cov=core.data_handler --cov-report=html

**Tests manuales**:
.. code-block:: bash

   # Test de rendimiento standalone
   python3 tests/test_performance_export_separated.py

Estructura de Tests
~~~~~~~~~~~~~~~~~

**Test básico**:
.. code-block:: python

   import unittest
   import pandas as pd
   from core.data_handler import ExcelTemplateSplitter, ExportSeparatedConfig

   class TestExcelTemplateSplitter(unittest.TestCase):
       
       def setUp(self):
           """Configurar datos de prueba."""
           self.df = pd.DataFrame({
               'category': ['A', 'B', 'C'] * 10,
               'value': range(30)
           })
           
           self.config = ExportSeparatedConfig(
               separator_column='category',
               template_path='test_template.xlsx',
               output_folder='test_output/'
           )
       
       def test_splitter_initialization(self):
           """Test de inicialización básica."""
           splitter = ExcelTemplateSplitter(self.df, self.config)
           self.assertIsNotNone(splitter)
           
       def test_configuration_validation(self):
           """Test de validación de configuración."""
           splitter = ExcelTemplateSplitter(self.df, self.config)
           result = splitter.validate_configuration()
           self.assertIsInstance(result, ValidationResult)

Escribir Nuevos Tests
~~~~~~~~~~~~~~~~~~

**Casos a cubrir**:
- Tests unitarios para nuevas funciones
- Tests de integración para flujos completos
- Tests de rendimiento para optimizaciones
- Tests de edge cases y manejo de errores

**Ejemplo de test de integración**:
.. code-block:: python

   def test_separation_with_template(self):
       """Test de separación completa con plantilla."""
       with tempfile.TemporaryDirectory() as temp_dir:
           config = ExportSeparatedConfig(
               separator_column='category',
               template_path=self.create_test_template(),
               output_folder=temp_dir,
               file_template='test_{valor}.xlsx'
           )
           
           result = exportar_datos_separados(self.df, config.__dict__)
           
           self.assertTrue(result['success'])
           self.assertGreater(len(result['files_created']), 0)

Performance Testing
~~~~~~~~~~~~~~~~~

**Benchmarks**:
- Usar `test_performance_export_separated.py` como referencia
- Medir tiempo y memoria con `measure_performance`
- Establecer objetivos de rendimiento claros

**Ejemplo**:
.. code-block:: python

   def test_performance_large_dataset(self):
       """Test de rendimiento para dataset grande."""
       df_large = self.create_large_test_dataframe(10000, 50)
       
       with measure_performance("Large Dataset Test", self.metrics):
           result = exportar_datos_separados(df_large, self.config)
           
       # Verificar que cumple objetivos de rendimiento
       self.assertLess(self.metrics.last_duration, 60)  # < 1 minuto
       self.assertLess(self.metrics.peak_memory_mb, 500)  # < 500MB

Proceso de Desarrollo
-------------------

Workflow Git
~~~~~~~~~~

1. **Crear branch**:
   .. code-block:: bash

      git checkout -b feature/nueva-funcionalidad

2. **Desarrollar y testear**:
   .. code-block:: bash

      # Hacer cambios
      python -m pytest tests/  # Verificar tests
      python -m pytest --cov=core.data_handler  # Verificar cobertura

3. **Commit con mensaje descriptivo**:
   .. code-block:: bash

      git add .
      git commit -m "feat: agregar nueva validación de plantillas Excel"

4. **Push y crear PR**:
   .. code-block:: bash

      git push origin feature/nueva-funcionalidad

Commits Convencionales
~~~~~~~~~~~~~~~~~~~

**Formato**: `tipo(scope): descripción`

**Tipos**:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `test`: Agregar/modificar tests
- `refactor`: Refactorización de código
- `perf`: Mejoras de rendimiento

**Ejemplos**:
.. code-block:: bash

   feat(ui): agregar preview de archivos en diálogo de configuración
   fix(core): corregir manejo de valores nulos en mapeo de columnas
   test(perf): agregar test de rendimiento para datasets grandes
   docs(api): actualizar documentación de ExcelTemplateSplitter

Añadir Nueva Funcionalidad
------------------------

Paso 1: Análisis
~~~~~~~~~~~~~~

1. **Definir requerimientos**
2. **Diseñar interfaz** (si aplica)
3. **Planificar tests**
4. **Considerar rendimiento**

Paso 2: Implementación
~~~~~~~~~~~~~~~~~~

**Estructura recomendada**:

1. **Core Logic** (si es nueva funcionalidad):
   .. code-block:: python

      # En core/data_handler.py o nuevo módulo
      class NuevaFuncionalidad:
          def __init__(self, data, config):
              self.data = data
              self.config = config
          
          def process(self):
              """Lógica principal."""
              pass

2. **UI Components** (si aplica):
   .. code-block:: python

      # En app/widgets/
      class NuevaFuncionalidadDialog(QDialog):
          def __init__(self, parent=None):
              super().__init__(parent)
              self.setup_ui()
          
          def setup_ui(self):
              """Configurar interfaz."""
              pass

3. **Integración**:
   .. code-block:: python

      # En main.py o lugar apropiado
      # Agregar al menú principal
      self.separar_menu.addAction("Nueva Funcionalidad", self.nueva_funcionalidad)

Paso 3: Testing
~~~~~~~~~~~~

**Tests requeridos**:
- Unit tests para lógica core
- Integration tests para flujos completos
- UI tests si aplica
- Performance tests si hay impacto

Paso 4: Documentación
~~~~~~~~~~~~~~~~~~

**Documentación requerida**:
- Docstrings para todas las funciones públicas
- Actualizar documentación de API si aplica
- Ejemplos de uso en documentación
- Actualizar changelog

Optimización de Rendimiento
---------------------------

Principio de Optimización
~~~~~~~~~~~~~~~~~~~~~~~

**"Medir antes de optimizar"**:
1. Identificar bottleneck con profiling
2. Implementar optimización específica
3. Verificar mejora con benchmarks
4. Mantener compatibilidad hacia atrás

Técnicas de Optimización
~~~~~~~~~~~~~~~~~~~~~~

**1. Chunking para datasets grandes**:
.. code-block:: python

   def process_large_dataset(self, df):
       if len(df) > self.config.chunk_threshold:
           return self._process_with_chunking(df)
       else:
           return self._process_direct(df)

**2. Cache de operaciones costosas**:
.. code-block:: python

   @lru_cache(maxsize=128)
   def expensive_operation(self, parameter):
       # Operación costosa cacheada
       pass

**3. Lazy loading**:
.. code-block:: python

   @property
   def heavy_computation(self):
       if not hasattr(self, '_cached_result'):
           self._cached_result = self._compute_expensive_result()
       return self._cached_result

Profiling y Medición
~~~~~~~~~~~~~~~~~

**Usar cProfile**:
.. code-block:: python

   import cProfile
   
   def profile_function():
       cProfile.run('result = function_to_profile()')

**Métricas importantes**:
- Tiempo de ejecución total
- Uso de memoria pico
- Throughput (filas/segundo)
- Número de operaciones I/O

Debugging
--------

Herramientas de Debug
~~~~~~~~~~~~~~~~~~~

**Python Debugger (pdb)**:
.. code-block:: python

   import pdb; pdb.set_trace()  # Breakpoint

**Logging detallado**:
.. code-block:: python

   import logging
   
   logger = logging.getLogger(__name__)
   logger.debug(f"Processing group: {group_name}")
   logger.info(f"Files created: {len(files)}")

**PyLint para calidad**:
.. code-block:: bash

   pylint core/data_handler.py

Debugging Común
~~~~~~~~~~~~~

**1. ImportError de dependencias**:
.. code-block:: python

   try:
       import openpyxl
   except ImportError:
       raise ImportError("openpyxl es requerido para esta funcionalidad")

**2. Problemas de memoria**:
.. code-block:: python

   import gc
   
   # Forzar garbage collection después de operaciones grandes
   del large_variable
   gc.collect()

**3. Problemas de rendimiento**:
- Usar chunking para datasets grandes
- Evitar loops anidados ineficientes
- Usar operaciones vectorizadas de pandas

Contribución de Documentación
----------------------------

Tipos de Documentación
~~~~~~~~~~~~~~~~~~~~

1. **API Documentation**: Docstrings y Sphinx
2. **User Guide**: Guía para usuarios finales
3. **Developer Guide**: Documentación técnica
4. **Architecture Documentation**: Diagramas y diseño

Convenciones para Documentación
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Markdown para User Guide**:
- Títulos con # ## ###
- Código con ``` blocks
- Listas con - y 1.
- Enlaces con [texto](url)

**reStructuredText para Sphinx**:
- Usar .. autoclass:: para APIs
- Incluir ejemplos de código
- Referenciar otras secciones con :doc:

Revisión de Código
----------------

Checklist de Revisión
~~~~~~~~~~~~~~~~~~

**Funcionalidad**:
- [ ] La funcionalidad hace lo que se espera
- [ ] Maneja casos edge correctamente
- [ ] No rompe funcionalidades existentes

**Código**:
- [ ] Sigue convenciones de estilo
- [ ] Incluye documentación adecuada
- [ ] Manejo de errores apropiado

**Testing**:
- [ ] Incluye tests unitarios
- [ ] Incluye tests de integración si aplica
- [ ] Tests pasan localmente

**Performance**:
- [ ] No degrada rendimiento existente
- [ ] Optimizaciones documentadas si son significativas

**Documentación**:
- [ ] Actualiza documentación relevante
- [ ] Ejemplos de uso incluidos

Proceso de Merge
~~~~~~~~~~~~~~

1. **Code Review**: Al menos 1 aprobador
2. **CI/CD Pass**: Todos los tests pasan
3. **Performance Check**: Sin regresiones significativas
4. **Documentation Review**: Documentación actualizada
5. **Merge**: Squash y merge a main branch

Recursos Adicionales
------------------

Herramientas Recomendadas
~~~~~~~~~~~~~~~~~~~~~~

- **IDE**: VSCode con Python extension
- **Linting**: PyLint, Black (formateador)
- **Testing**: pytest, coverage.py
- **Documentation**: Sphinx, MkDocs
- **Profiling**: cProfile, memory_profiler

Enlaces Útiles
~~~~~~~~~~~~

- **PEP 8**: https://pep8.org/
- **Google Style Guide**: https://google.github.io/styleguide/pyguide.html
- **Sphinx Documentation**: https://www.sphinx-doc.org/
- **PyTest Documentation**: https://docs.pytest.org/

Contacto
-------

Para preguntas sobre contribución:
- Crear issue en el repositorio
- Consultar documentación existente
- Revisar tests para ejemplos de uso

Gracias por contribuir al proyecto Flash Sheet - Exportación Separada!