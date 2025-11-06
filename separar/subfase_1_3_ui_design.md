# Subfase 1.3: Diseño de Interfaz de Usuario
## Diseño Completo de UI para Configuración de Exportación Separada con Plantillas Excel

### 1. Diseño General del Diálogo Modal

#### 1.1 Estructura Principal del Diálogo
**Clase**: `ExportSeparatedDialog(QDialog)`

**Dimensiones**: 800x600 píxeles (escalable hasta 1000x800)
**Ventana Modal**: Bloquea interacción con ventana principal
**Icono**: 💾 (consistente con funciones de exportación)

**Layout Principal**:
```
+----------------------------------------------------------------------------------+
| 💾 Configurar Exportación Separada con Plantillas Excel                 [?] [X] |
+----------------------------------------------------------------------------------+
|  +------------------------------------------------------------------------------+ |
|  | 📊 Datos                             🔧 Configuración     📁 Destino          | |
|  | +------------------------------------+ +------------------+ +----------------+ | |
|  | | 1. Columna de Separación           | | 2. Plantilla     | | 3. Nombres     | | |
|  | |                                    | |    Excel         | |    de Archivos | | |
|  | | [ComboBox: Seleccionar columna ▼]  | |                  | |                | | |
|  | |                                    | | [Seleccionar]    | | [Plantilla:    | | |
|  | | Preview de valores:                | | [plantilla.xlsx] | |  {valor}_{fecha}| | |
|  | | • Norte (1,250 filas)              | |                  | | ]              | | |
|  | | • Sur (980 filas)                  | | [ComboBox: Hoja  | |                | | |
|  | | • Este (1,100 filas)               | |          ▼]      | | Preview:        | | |
|  | | • Oeste (750 filas)                | |                  | | • Norte_2025... | | |
|  | |                                    | | 2.1 Celda inicial| | • Sur_2025...   | | |
|  | | ✓ Validación: 4 grupos encontrados | | [A5 ▼] [Campo:   | | • Este_2025...  | | |
|  | |                                    | |      A5]         | | • Oeste_2025... | | |
|  | +------------------------------------+ +------------------+ +----------------+ | |
|  +------------------------------------------------------------------------------+ |
|  +------------------------------------------------------------------------------+ |
|  | 📋 Mapeo de Columnas                                                             | |
|  | +-------------------+----------+-------------------+---------------------------+ |
|  | | DataFrame Column  | → Excel  | Excel Column      | Preview (primeras 3 filas) | |
|  | +-------------------+----------+-------------------+---------------------------+ |
|  | | Región           | → [A    ▼] | Column A          | Norte | Sur  | Este | |
|  | | Producto         | → [B    ▼] | Column B          | A     | B    | C    | |
|  | | Ventas           | → [C    ▼] | Column C          | 1250  | 980  | 1100 | |
|  | | Fecha            | → [D    ▼] | Column D          | 2025- | 2025-| 2025-| |
|  +-------------------+----------+-------------------+---------------------------+ |
|  | [+ Añadir Columna] [- Eliminar] [Auto-mapear] [Vista Previa Completa]          | |
|  +------------------------------------------------------------------------------+ |
|  +------------------------------------------------------------------------------+ |
|  | 📁 Carpeta de Destino: C:\Datos\Exportacion\ [Cambiar...] ✓ Permisos OK       | |
|  +------------------------------------------------------------------------------+ |
|  | ⚠️ Validación: • 4 archivos se generarán • ~15MB espacio requerido             | |
|  +------------------------------------------------------------------------------+ |
|                    [Vista Previa] [Validar] [Cancelar] [Exportar]                |
+----------------------------------------------------------------------------------+
```

#### 1.2 Estados del Diálogo
**Estado Inicial** (sin datos):
```
• Mensaje: "Cargue datos primero desde el menú Archivo > Abrir"
• Botón "Exportar" deshabilitado
• Todos los campos bloqueados
```

**Estado con Datos**:
```
• Todos los campos habilitados
• Validación automática en tiempo real
• Preview generado automáticamente
```

**Estado con Errores**:
```
• Campos con errores marcados en rojo
• Tooltips explicativos al pasar el mouse
• Botón "Exportar" deshabilitado hasta resolver errores
```

### 2. Secciones Detalladas de la Interfaz

#### 2.1 Sección 1: Datos (Columna de Separación)
**Ubicación**: Panel izquierdo superior
**Dimensiones**: 300x200 píxeles

**Componentes**:
```python
# ComboBox para seleccionar columna
self.columna_separacion_combo = QComboBox()
self.columna_separacion_combo.setPlaceholderText("Seleccionar columna para separar")

# Label para información de columna
self.info_columna_label = QLabel()
self.info_columna_label.setWordWrap(True)
self.info_columna_label.setStyleSheet("color: #666; font-size: 11px;")

# Preview de valores únicos
self.valores_preview_list = QListWidget()
self.valores_preview_list.setMaximumHeight(100)
self.valores_preview_list.setStyleSheet("""
    QListWidget {
        border: 1px solid #ccc;
        border-radius: 3px;
        background-color: #fafafa;
    }
""")

# Checkbox para incluir nulos
self.incluir_nulos_check = QCheckBox("Incluir valores nulos como grupo separado")
```

**Funcionalidades**:
- **Carga Dinámica**: ComboBox se llena con columnas del DataFrame actual
- **Preview Automático**: Al seleccionar columna, mostrar valores únicos con conteo
- **Validación**: Verificar que hay al menos 2 valores únicos
- **Tooltips**: Mostrar tipo de dato y valores de ejemplo

#### 2.2 Sección 2: Configuración (Plantilla Excel)
**Ubicación**: Panel central superior
**Dimensiones**: 300x200 píxeles

**Componentes**:
```python
# Botón y campo para seleccionar plantilla
self.seleccionar_plantilla_btn = QPushButton("Seleccionar Plantilla Excel")
self.plantilla_path_label = QLabel("No hay plantilla seleccionada")
self.plantilla_path_label.setWordWrap(True)

# ComboBox para seleccionar hoja
self.hoja_combo = QComboBox()
self.hoja_combo.setEnabled(False)  # Habilitado solo con plantilla válida

# Selector de celda inicial
self.celda_inicial_combo = QComboBox()
self.celda_inicial_combo.addItems(["A1", "A2", "A5", "B1", "B2", "Personalizado"])
self.celda_personalizada_edit = QLineEdit()
self.celda_personalizada_edit.setPlaceholderText("Ej: C10")
self.celda_personalizada_edit.setMaximumWidth(80)
```

**Validaciones**:
- **Plantilla**: Verificar que es archivo .xlsx válido y accesible
- **Hoja**: Verificar que la hoja existe en el workbook
- **Celda**: Validar formato Excel (letras+números) y rango válido

#### 2.3 Sección 3: Nombres de Archivos
**Ubicación**: Panel derecho superior
**Dimensiones**: 300x200 píxeles

**Componentes**:
```python
# Campo de plantilla con validación
self.plantilla_nombre_edit = QLineEdit()
self.plantilla_nombre_edit.setPlaceholderText("Ej: {valor}_{fecha}.xlsx")

# Lista de placeholders disponibles
self.placeholders_list = QListWidget()
self.placeholders_list.setMaximumHeight(80)
self.placeholders_list.addItems([
    "{valor} - Valor de la columna de separación",
    "{fecha} - Fecha actual (YYYY-MM-DD)",
    "{hora} - Hora actual (HHMMSS)",
    "{contador} - Número secuencial",
    "{columna_nombre} - Nombre de columna",
    "{total_filas} - Filas en el grupo"
])

# Preview de nombres generados
self.nombres_preview_list = QListWidget()
self.nombres_preview_list.setMaximumHeight(60)
```

**Funcionalidades**:
- **Validación en Tiempo Real**: Verificar plantilla mientras usuario escribe
- **Preview Dinámico**: Actualizar nombres mostrados al cambiar configuración
- **Placeholders Interactivos**: Click en placeholder lo inserta en campo de texto

#### 2.4 Sección 4: Mapeo de Columnas
**Ubicación**: Panel inferior ancho
**Dimensiones**: 760x150 píxeles

**Componentes Principales**:
```python
# Tabla de mapeo
self.mapeo_tabla = QTableWidget()
self.mapeo_tabla.setColumnCount(4)
self.mapeo_tabla.setHorizontalHeaderLabels([
    "Columna DataFrame", "→", "Columna Excel", "Vista Previa"
])

# Configuración de tabla
header = self.mapeo_tabla.horizontalHeader()
header.setStretchLastSection(True)
self.mapeo_tabla.setAlternatingRowColors(True)

# Botones de acción
self.agregar_columna_btn = QPushButton("+ Añadir Columna")
self.eliminar_columna_btn = QPushButton("- Eliminar")
self.auto_mapear_btn = QPushButton("Auto-mapear")
self.vista_previa_btn = QPushButton("Vista Previa Completa")
```

**Funcionalidades de Tabla**:
- **Fila por Columna**: Una fila por cada columna del DataFrame
- **ComboBox Excel**: Dropdown con letras A-Z, AA-ZZ, etc.
- **Preview en Vivo**: Mostrar primeras 3 filas de datos mapeados
- **Drag & Drop**: Permitir reordenar filas para cambiar orden de inserción

#### 2.5 Sección 5: Configuración de Destino
**Ubicación**: Panel inferior
**Dimensiones**: 760x50 píxeles

**Componentes**:
```python
# Selector de carpeta
self.carpeta_label = QLabel("No se ha seleccionado carpeta de destino")
self.cambiar_carpeta_btn = QPushButton("Cambiar...")

# Indicador de estado
self.estado_permisos_label = QLabel()
self.estado_permisos_label.setStyleSheet("color: #666; font-size: 11px;")
```

### 3. Interfaz de Validación y Preview

#### 3.1 Sistema de Validación en Tiempo Real
**Implementación**:
```python
class ValidationManager:
    def __init__(self, dialog):
        self.dialog = dialog
        self.errores = []
        self.advertencias = []
        
    def validar_configuracion_completa(self):
        """Validar toda la configuración y actualizar UI"""
        self.errores.clear()
        self.advertencias.clear()
        
        # Validaciones en orden de prioridad
        self._validar_datos_cargados()
        self._validar_columna_separacion()
        self._validar_plantilla_excel()
        self._validar_mapeo_columnas()
        self._validar_destino()
        
        self._actualizar_ui_validacion()
        
    def _actualizar_ui_validacion(self):
        """Actualizar indicadores visuales de validación"""
        if not self.errores:
            self.dialog.validacion_label.setText("✅ Configuración válida")
            self.dialog.validacion_label.setStyleSheet("color: green;")
            self.dialog.exportar_btn.setEnabled(True)
        else:
            self.dialog.validacion_label.setText(f"❌ {len(self.errores)} error(es) encontrado(s)")
            self.dialog.validacion_label.setStyleSheet("color: red;")
            self.dialog.exportar_btn.setEnabled(False)
```

**Indicadores Visuales**:
- **Verde (✅)**: Campo válido, configuración completa
- **Amarillo (⚠️)**: Advertencia, funciona pero con limitaciones
- **Rojo (❌)**: Error, bloquea exportación
- **Gris (⏸️)**: Campo deshabilitado, esperando configuración previa

#### 3.2 Vista Previa de Archivos a Generar
**Diálogo Separado**: `FilePreviewDialog(QDialog)`

**Contenido**:
```
+----------------------------------------------------------------------------------+
| Vista Previa de Archivos a Generar                                       [X] |
+----------------------------------------------------------------------------------+
| Filtros: [Todos ▼] [Buscar...]                                                  |
+----------------------------------------------------------------------------------+
| Nombre Archivo                   | Grupo     | Filas | Tamaño | Estado        |
+----------------------------------+-----------+-------+--------+--------------+
| Norte_2025-11-04.xlsx           | Norte     | 1,250 | ~45KB  | ✅ Listo      |
| Sur_2025-11-04.xlsx             | Sur       | 980   | ~35KB  | ✅ Listo      |
| Este_2025-11-04.xlsx            | Este      | 1,100 | ~40KB  | ✅ Listo      |
| Oeste_2025-11-04.xlsx           | Oeste     | 750   | ~28KB  | ✅ Listo      |
+----------------------------------+-----------+-------+--------+--------------+
| Resumen: 4 archivos • Total estimado: ~148KB • Espacio disponible: 2.1GB      |
+----------------------------------------------------------------------------------+
| [Exportar esta lista a CSV] [Cerrar]                                          |
+----------------------------------------------------------------------------------+
```

**Funcionalidades**:
- **Filtros**: Por estado (Todos, Listos, Errores, Advertencias)
- **Búsqueda**: Por nombre de archivo o grupo
- **Ordenamiento**: Por cualquier columna
- **Export**: Guardar preview como CSV para revisión externa

### 4. Interfaz de Selección de Plantilla Excel

#### 4.1 Diálogo de Selección
**Clase**: `ExcelTemplateSelectionDialog(QDialog)`

**Componentes**:
```python
# Área de selección de archivo
self.archivo_edit = QLineEdit()
self.seleccionar_btn = QPushButton("Explorar...")

# Información del archivo seleccionado
self.info_archivo_label = QLabel()
self.vista_previa_label = QLabel("Vista Previa de Plantilla:")

# Tabla de preview (primeras 10 filas)
self.preview_tabla = QTableWidget()
self.preview_tabla.setMaximumHeight(200)

# Selector de hoja si hay múltiples
self.hoja_combo = QComboBox()
```

**Funcionalidades**:
- **Drag & Drop**: Arrastrar archivo Excel directamente al diálogo
- **Preview**: Mostrar primeras 10 filas para verificar estructura
- **Validación**: Verificar que el archivo no esté abierto en Excel
- **Información**: Mostrar tamaño, fecha modificación, número de hojas

#### 4.2 Validación de Plantilla
**Checks Automáticos**:
1. **Formato**: Verificar que es archivo .xlsx válido
2. **Accesibilidad**: Verificar permisos de lectura
3. **Contenido**: Verificar que tiene al menos 1 fila y 1 columna
4. **Formato Excel**: Verificar que las celdas tienen formato apropiado
5. **Hojas**: Listar todas las hojas disponibles

### 5. Interfaz Avanzada de Mapeo de Columnas

#### 5.1 Tabla de Mapeo Expandida
**Columnas Adicionales**:
```python
# Columna 1: Nombre de columna DataFrame (readonly)
# Columna 2: Flecha (readonly) 
# Columna 3: ComboBox para columna Excel
# Columna 4: Vista previa de datos
# Columna 5: Tipo de dato (readonly)
# Columna 6: Acción (botón eliminar)
```

**Funcionalidades Avanzadas**:
```python
class ColumnMappingManager:
    def __init__(self, tabla):
        self.tabla = tabla
        self.setup_context_menu()
        
    def setup_context_menu(self):
        """Menú contextual en tabla"""
        self.tabla.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, position):
        """Mostrar menú contextual"""
        menu = QMenu()
        
        # Acciones del menú
        mapear_automatico = menu.addAction("Mapear automáticamente")
        invertir_mapeo = menu.addAction("Invertir mapeo")
        mapear_por_nombre = menu.addAction("Mapear por nombre similar")
        menu.addSeparator()
        agregar_columna = menu.addAction("Agregar columna")
        eliminar_seleccionadas = menu.addAction("Eliminar seleccionadas")
        
        action = menu.exec(self.tabla.mapToGlobal(position))
        
    def auto_map_by_position(self):
        """Mapear automáticamente por posición"""
        for row in range(self.tabla.rowCount()):
            excel_col = self.index_to_excel_column(row)
            combo = self.tabla.cellWidget(row, 2)  # ComboBox
            combo.setCurrentText(excel_col)
            
    def auto_map_by_name(self):
        """Mapear automáticamente por nombre de columna"""
        # Buscar coincidencias entre nombres de columnas
        # DataFrame: "Region", Excel: "región", "REGION", etc.
        pass
```

#### 5.2 Presets de Mapeo Comunes
**Sistema de Presets**:
```python
PRESETS_MAPEO = {
    "Estándar_DataFrame": {
        "description": "Mapear DataFrame por posición (A, B, C...)",
        "mapping": "position"
    },
    "Científico": {
        "description": "Mapeo para datos científicos (muestra, valor, error)",
        "mapping": {
            "Muestra": "A",
            "Valor": "B", 
            "Error": "C",
            "Fecha": "D"
        }
    },
    "Financiero": {
        "description": "Mapeo para datos financieros (fecha, concepto, importe)",
        "mapping": {
            "Fecha": "A",
            "Concepto": "B",
            "Importe": "C",
            "Categoría": "D"
        }
    }
}
```

**Interface de Presets**:
- **ComboBox**: Selector de preset en toolbar de la tabla
- **Aplicar**: Botón para aplicar preset seleccionado
- **Personalizado**: Opción para guardar mapeo actual como preset

### 6. Integración con Sistema de Temas

#### 6.1 Consistencia Visual
**Paleta de Colores** (consistente con aplicación):
```python
# Colores principales
COLOR_PRIMARY = "#4a90e2"      # Azul principal (botones)
COLOR_SECONDARY = "#6c757d"     # Gris secundario
COLOR_SUCCESS = "#28a745"       # Verde (validación)
COLOR_WARNING = "#ffc107"       # Amarillo (advertencias)
COLOR_ERROR = "#dc3545"         # Rojo (errores)
COLOR_BACKGROUND = "#f8f9fa"    # Fondo de paneles
COLOR_BORDER = "#dee2e6"        # Bordes de campos
```

**Estilos CSS**:
```css
/* Panel principal */
QGroupBox {
    font-weight: bold;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    margin-top: 1ex;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
}

/* Campos de entrada */
QLineEdit {
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 6px;
    font-size: 12px;
}

QLineEdit:focus {
    border-color: #4a90e2;
}

/* Botones */
QPushButton {
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #357abd;
}

QPushButton:disabled {
    background-color: #6c757d;
    color: #adb5bd;
}

/* Tabla */
QTableWidget {
    border: 1px solid #dee2e6;
    border-radius: 4px;
    gridline-color: #e9ecef;
    selection-background-color: #e3f2fd;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #e3f2fd;
    color: #000;
}

/* Validación visual */
.valid-field {
    border-left: 4px solid #28a745;
}

.warning-field {
    border-left: 4px solid #ffc107;
}

.error-field {
    border-left: 4px solid #dc3545;
    background-color: #f8d7da;
}
```

#### 6.2 Soporte para Temas Dark/Light
**Configuración Dinámica**:
```python
def apply_theme(self, is_dark_theme=False):
    """Aplicar tema dark o light"""
    if is_dark_theme:
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QGroupBox {
                border-color: #555555;
                color: #ffffff;
            }
            QLineEdit, QComboBox, QTableWidget {
                background-color: #3d3d3d;
                color: #ffffff;
                border-color: #555555;
            }
        """)
    else:
        # Tema light (por defecto)
        self.setStyleSheet("")
```

### 7. Accesibilidad y Usabilidad

#### 7.1 Navegación por Teclado
**Shortcuts Definidos**:
```python
# Shortcuts globales del diálogo
self.setShortcut(Qt.Key_Escape, self.reject)           # ESC: Cancelar
self.setShortcut(Qt.Key_Return, self.accept)           # Enter: Aceptar
self.setShortcut(Qt.Key_F1, self.show_help)            # F1: Ayuda
self.setShortcut(Qt.Key_F5, self.refresh_preview)      # F5: Actualizar preview

# Shortcuts para secciones
self.columna_separacion_combo.setShortcut(Qt.Alt + 1)  # Alt+1: Ir a columna
self.seleccionar_plantilla_btn.setShortcut(Qt.Alt + 2) # Alt+2: Ir a plantilla
self.mapeo_tabla.setShortcut(Qt.Alt + 3)               # Alt+3: Ir a mapeo
```

#### 7.2 Ayuda Contextual
**Tooltips Informativos**:
```python
# Tooltips para campos principales
self.columna_separacion_combo.setToolTip(
    "Selecciona la columna que determinará cómo se separarán los datos.\n"
    "Cada valor único creará un archivo Excel separado.\n\n"
    "Ejemplo: Si seleccionas 'Región', se creará un archivo por cada región."
)

self.plantilla_nombre_edit.setToolTip(
    "Define el nombre de los archivos usando placeholders:\n"
    "{valor} - Valor de la columna de separación\n"
    "{fecha} - Fecha actual (YYYY-MM-DD)\n"
    "{contador} - Número secuencial\n\n"
    "Ejemplo: 'Reporte_{valor}_{fecha}.xlsx'"
)
```

#### 7.3 Mensajes de Estado
**Barra de Estado del Diálogo**:
```python
# Status bar en la parte inferior del diálogo
self.status_bar = QStatusBar()
layout.addWidget(self.status_bar)

def update_status(self, message, message_type="info"):
    """Actualizar mensaje de estado"""
    if message_type == "error":
        self.status_bar.setStyleSheet("color: red;")
    elif message_type == "warning":
        self.status_bar.setStyleSheet("color: orange;")
    else:
        self.status_bar.setStyleSheet("color: green;")
    
    self.status_bar.showMessage(message, 5000)  # Auto-hide en 5 segundos
```

### 8. Integración con Flujo de Trabajo

#### 8.1 Secuencia de Interacción
**Flujo Típico del Usuario**:
```
1. Usuario carga datos → Menú "Separar" se habilita
2. Usuario hace click "Separar > Exportar Datos Separados"
3. Diálogo se abre con DataFrame ya cargado
4. Usuario selecciona columna de separación
5. Sistema genera preview automático de valores únicos
6. Usuario selecciona plantilla Excel
7. Usuario configura celda inicial y mapeo de columnas
8. Usuario define plantilla de nombres y carpeta destino
9. Sistema valida configuración completa
10. Usuario hace click "Vista Previa" para revisar
11. Usuario confirma con "Exportar"
12. Proceso de exportación inicia con progress feedback
```

#### 8.2 Persistencia de Configuración
**Guardar Preferencias del Usuario**:
```python
import json
from pathlib import Path

class ConfiguracionManager:
    def __init__(self):
        self.config_path = Path.home() / ".flash-sheet" / "export-separation.json"
        
    def guardar_configuracion(self, config):
        """Guardar configuración para uso futuro"""
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
    def cargar_configuracion(self):
        """Cargar configuración guardada"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}
        
    def aplicar_configuracion_guardada(self, dialog):
        """Aplicar configuración guardada al diálogo"""
        config = self.cargar_configuracion()
        if config.get('plantilla_nombre'):
            dialog.plantilla_nombre_edit.setText(config['plantilla_nombre'])
        if config.get('carpeta_destino'):
            dialog.carpeta_destino = config['carpeta_destino']
```

#### 8.3 Integración con Sistema de Log
**Logging de Acciones del Usuario**:
```python
import logging

class UIActionLogger:
    def __init__(self):
        self.logger = logging.getLogger('ui.export_separation')
        
    def log_configuracion_iniciada(self, dataframe_info):
        self.logger.info(f"Usuario inició configuración - DataFrame: {dataframe_info}")
        
    def log_columna_seleccionada(self, columna, valores_unicos):
        self.logger.info(f"Columna seleccionada: {columna} - Valores únicos: {valores_unicos}")
        
    def log_plantilla_seleccionada(self, plantilla_path, hojas):
        self.logger.info(f"Plantilla seleccionada: {plantilla_path} - Hojas: {hojas}")
        
    def log_exportacion_completada(self, archivos_generados, tiempo_procesamiento):
        self.logger.info(f"Exportación completada - Archivos: {archivos_generados} - Tiempo: {tiempo_procesamiento}s")
```

### 9. Métricas de Usabilidad

#### 9.1 Objetivos de Diseño UX
- **Tiempo de Configuración**: < 2 minutos para casos simples
- **Curva de Aprendizaje**: Usuario nuevo puede configurar sin documentación
- **Tasa de Error**: < 5% de configuraciones que resultan en errores
- **Satisfacción**: > 4/5 en pruebas de usabilidad

#### 9.2 Testing de Usabilidad
**Casos de Prueba UX**:
1. **Usuario Novato**: Primera vez usando la funcionalidad
2. **Usuario Intermedio**: Ha usado funciones de exportación antes
3. **Usuario Avanzado**: Usuario técnico que entiende Excel y DataFrames
4. **Usuario con Limitaciones**: Accesibilidad (vision, motor skills)

#### 9.3 Métricas de Rendimiento UI
- **Tiempo de Respuesta**: < 100ms para interacciones simples
- **Actualización de Preview**: < 500ms después de cambios
- **Tiempo de Carga**: < 2 segundos para abrir diálogo con datos grandes
- **Memoria UI**: < 50MB adicionales para el diálogo completo

---

**Estado**: ✅ COMPLETADO - Subfase 1.3
**Resultado**: Diseño completo de UI para funcionalidad de separación con plantillas Excel
**Próximo**: Completar Fase 1 con resumen ejecutivo
**Fecha**: 2025-11-04