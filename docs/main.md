# main.py — Documentación Completa

Punto de entrada principal de la aplicación **Flash View Sheet**. Define `MainWindow` (la ventana principal Qt) y la función `main()` que arranca el event loop.

---

## Índice

1. [Visión General](#1-visión-general)
2. [Importaciones](#2-importaciones)
3. [Clase MainWindow](#3-clase-mainwindow)
   - [3.1 Constructor](#31-constructor)
   - [3.2 Métodos de Inicialización](#32-métodos-de-inicialización)
   - [3.3 Propiedades de Compatibilidad](#33-propiedades-de-compatibilidad)
   - [3.4 Métodos Delegados](#34-métodos-delegados)
   - [3.5 Gestión de Carga de Archivos](#35-gestión-de-carga-de-archivos)
   - [3.6 Carga de Carpeta](#36-carga-de-carpeta)
   - [3.7 Operaciones de Exportación](#37-operaciones-de-exportación)
   - [3.8 Acerca De](#38-acerca-de)
   - [3.9 Eventos](#39-eventos)
4. [Función main()](#4-función-main)
5. [Diagrama de Dependencias](#5-diagrama-de-dependencias)
6. [Flujo de Señales](#6-flujo-de-señales)

---

## 1. Visión General

`main.py` (298 líneas) actúa como **orquestador de componentes**. Su responsabilidad es:

- Crear la aplicación Qt (`QApplication`)
- Instantiar y conectar todos los subsistemas (servicios, coordinadores, vistas, menús, toolbar)
- Delegar toda la lógica de negocio a `AppCoordinator`
- Delegar la gestión de datos a `DataService`
- Delegar la navegación de vistas a `ViewCoordinator`

No contiene lógica de negocio propia. Sigue el patrón **Coordinator**: `MainWindow` es el punto de conexión central que integra servicios, vistas y coordinadores.

---

## 2. Importaciones

### Módulos estándar
| Módulo | Uso |
|--------|-----|
| `sys` | Acceso a `sys.argv` y `sys.exit()` |
| `os` | Rutas de archivos (`os.path.join`, `os.path.exists`) |

### PySide6 (Qt6)
| Símbolo | Módulo | Uso |
|---------|--------|-----|
| `QApplication` | `PySide6.QtWidgets` | Event loop de Qt |
| `QMainWindow` | `PySide6.QtWidgets` | Clase base de la ventana principal |
| `QStackedWidget` | `PySide6.QtWidgets` | Contenedor de vistas apiladas |
| `QFileDialog` | `PySide6.QtWidgets` | Diálogo de selección de archivos |
| `Signal` | `PySide6.QtCore` | Sistema de señales Qt |
| `QIcon` | `PySide6.QtGui` | Icono de la aplicación |

### Servicios de la aplicación
| Símbolo | Módulo | Responsabilidad |
|---------|--------|-----------------|
| `DataService` | `app.services` | Carga y estado de datos |
| `ExportService` | `app.services` | Todas las operaciones de exportación |
| `FilterService` | `app.services` | Filtrado de datos |
| `PivotService` | `app.services` | Tablas pivote |

### Componentes de UI
| Símbolo | Módulo | Responsabilidad |
|---------|--------|-----------------|
| `ToolbarManager` | `app.toolbar` | Gestión del toolbar principal |
| `ViewCoordinator` | `app.view_manager` | Coordinación de vistas y navegación |
| `AppCoordinator` | `app.app_coordinator` | Orquestador central de lógica de negocio |
| `FolderLoadDialog` | `app.widgets` | Diálogo de carga de carpetas |
| `InfoModal` | `app.widgets` | Modal de información del dataset |

### Importaciones lazy (dentro de métodos)
| Símbolo | Módulo | Cuándo se importa |
|---------|--------|-------------------|
| `JoinHistory` | `core.join.join_history` | `_init_coordinator()` |
| `MenuBuilder`, `MenuActions` | `app.menus` | `_create_menu_bar()` |
| `AboutDialog` | `app.widgets.about_dialog` | `mostrar_acerca_de()` |
| `QMessageBox` | `PySide6.QtWidgets` | `show_info_modal()` (rama de warning) |

---

## 3. Clase MainWindow

```python
class MainWindow(QMainWindow):
    """Ventana principal de la aplicación - Orquestador de componentes"""
```

Hereda de `QMainWindow` (Qt). Funciona como el orquestador central que conecta todos los subsistemas.

### Señales

| Señal | Tipo | Propósito |
|-------|------|-----------|
| `reload_with_options` | `Signal(str, int, dict)` | Re-exportada para compatibilidad con vistas existentes |

---

### 3.1 Constructor

```python
def __init__(self):
```

**Orden de inicialización:**

1. `super().__init__()` — Inicializa QMainWindow
2. `setWindowTitle()` — Título: "Flash View Sheet - Visor de Datos Tabulares"
3. `setMinimumSize(800, 600)` — Tamaño mínimo
4. `resize(1200, 800)` — Tamaño inicial
5. `_init_services()` — Crea los 4 servicios
6. `_init_toolbar()` — Crea el gestor del toolbar
7. `_init_coordinator()` — Crea coordinadores y JoinHistory
8. `_setup_ui()` — Construye la interfaz (widget central, vistas, menú, toolbar)
9. `_setup_connections()` — Conecta señales entre componentes

---

### 3.2 Métodos de Inicialización

#### `_init_services()`

```python
def _init_services(self):
    self.data_service = DataService()
    self.export_service = ExportService(self)
    self.filter_service = FilterService()
    self.pivot_service = PivotService()
```

Crea las 4 instancias de servicio. `ExportService` recibe `self` (la ventana) como referencia para diálogos modales.

#### `_init_toolbar()`

```python
def _init_toolbar(self):
    self.toolbar_manager = ToolbarManager(self)
```

Crea el gestor del toolbar, pasando la ventana como referencia.

#### `_init_coordinator()`

```python
def _init_coordinator(self):
```

Paso más complejo de la inicialización:

1. Crea `ViewCoordinator(self)` — gestiona las 4 vistas
2. Crea `AppCoordinator(...)` con 7 dependencias:
   - `parent_window=self`
   - `data_service`, `export_service`, `pivot_service`
   - `view_coordinator`, `toolbar_manager`
   - `join_history=None` (se inicializa después)
3. Importa y crea `JoinHistory()` (persiste historial en JSON)
4. Asigna `join_history` al coordinator
5. Conecta `coordinator.status_message` → `statusBar().showMessage`

#### `_setup_ui()`

```python
def _setup_ui(self):
    self._create_central_widget()
    self._create_views()
    self._create_menu_bar()
    self._add_toolbar()
    self.statusBar().showMessage("Listo para cargar datos")
```

Secuencia de construcción de la UI.

#### `_create_central_widget()`

```python
def _create_central_widget(self):
    self.stacked_widget = QStackedWidget()
    self.setCentralWidget(self.stacked_widget)
```

Crea el `QStackedWidget` que contendrá todas las vistas apiladas.

#### `_create_views()`

```python
def _create_views(self):
    self.view_coordinator.create_views(self.stacked_widget)
    self.stacked_widget.addWidget(self.view_coordinator.get_stacked_widget())
```

Delega la creación de vistas (MainView, DataView, GraphicsView, JoinedDataView) al `ViewCoordinator`.

#### `_create_menu_bar()`

```python
def _create_menu_bar(self):
```

1. Importa `MenuBuilder` y `MenuActions` (import lazy)
2. Crea `MenuBuilder(self)` y llama `build()`
3. Obtiene referencias a menús: `separar_menu`, `datos_menu`, `tabla_pivote_menu`
4. Obtiene acciones: `EXPORTAR_SEPARADO`, `CRUZAR_DATOS`, `PIVOT_SIMPLE`, `PIVOT_COMBINADA`, `EXPORTAR_PIVOTE`

#### `_add_toolbar()`

```python
def _add_toolbar(self):
    self.toolbar_manager.create_toolbar()
    self.addToolBar(self.toolbar_manager.get_toolbar())
```

Crea y añade el toolbar a la ventana.

#### `_setup_connections()`

```python
def _setup_connections(self):
```

Conecta señales de las vistas al coordinator:

| Señal | Conecta a |
|-------|-----------|
| `main_view.file_loaded` | `self._on_file_loaded` |
| `main_view.reload_with_options` | `self._on_reload_with_options` |
| `data_view.filter_applied` | `coordinator.on_filter_applied` |
| `data_view.filter_cleared` | `coordinator.on_filter_cleared` |
| `data_view.data_updated` | `coordinator.on_data_updated` |
| `joined_view.new_join_requested` | `coordinator.abrir_cruzar_datos` |

Cada conexión verifica que la vista no sea `None` antes de conectar.

---

### 3.3 Propiedades de Compatibilidad

Propiedades Python que actúan como wrappers sobre `DataService`:

#### `df_original`

```python
@property
def df_original(self):
    return self.data_service.datos_originales

@df_original.setter
def df_original(self, value):
    self.data_service.df_original = value
```

Acceso al DataFrame original (sin filtros). Getter lee de `data_service.datos_originales`, setter escribe en `data_service.df_original`.

#### `df_vista_actual`

```python
@property
def df_vista_actual(self):
    return self.data_service.datos_actuales

@df_vista_actual.setter
def df_vista_actual(self, value):
    self.data_service.datos_vista_actual = value
```

Acceso al DataFrame de la vista actual (con filtros aplicados).

**Nota:** Estas propiedades existen para mantener compatibilidad con código existente que accede directamente a `main_window.df_original`.

---

### 3.4 Métodos Delegados

Todos delegan directamente al `AppCoordinator` o `ViewCoordinator`:

| Método | Delega a | Descripción |
|--------|----------|-------------|
| `switch_view(index)` | `view_coordinator.switch_to(index)` | Cambiar vista activa |
| `show_info_modal()` | Crea `InfoModal` localmente | Mostrar info del dataset |
| `abrir_archivo()` | Flujo propio (ver 3.5) | Abrir diálogo de carga |
| `cargar_carpeta()` | Flujo propio (ver 3.6) | Abrir diálogo de carga de carpeta |
| `abrir_cruzar_datos()` | `coordinator.abrir_cruzar_datos()` | Abrir diálogo de join |
| `abrir_pivot_simple()` | `coordinator.abrir_pivot_simple()` | Abrir diálogo pivote simple |
| `abrir_pivot_combinada()` | `coordinator.abrir_pivot_combinada()` | Abrir diálogo pivote combinada |
| `exportar_resultado_pivote()` | `coordinator.exportar_resultado_pivote()` | Exportar pivote |
| `exportar_a_pdf()` | `coordinator.exportar_a_pdf()` | Exportar a PDF |
| `exportar_a_xlsx()` | `coordinator.exportar_a_xlsx()` | Exportar a Excel |
| `exportar_a_csv()` | `coordinator.exportar_a_csv()` | Exportar a CSV |
| `exportar_a_sql()` | `coordinator.exportar_a_sql()` | Exportar a SQL |
| `exportar_a_imagen()` | `coordinator.exportar_a_imagen()` | Exportar a imagen |
| `exportar_datos_separados()` | `coordinator.exportar_datos_separados()` | Exportar datos separados |
| `mostrar_acerca_de()` | `AboutDialog.show_about(self)` | Mostrar diálogo Acerca de |

---

### 3.5 Gestión de Carga de Archivos

#### `abrir_archivo()`

```python
def abrir_archivo(self):
    file_filter = self.data_service.get_file_filter()
    filepath, _ = QFileDialog.getOpenFileName(
        self, "Abrir archivo de datos", "", file_filter)
    if filepath:
        self._mostrar_loading_indicator(filepath)
```

**Flujo:**
1. Obtiene el filtro de archivos soportados desde `DataService`
2. Abre `QFileDialog` nativo del SO
3. Si el usuario selecciona un archivo, llama a `_mostrar_loading_indicator()`

#### `_on_file_loaded(filepath, skip_rows=0, column_names=None)`

Callback conectado a `main_view.file_loaded`. Reenvía a `_mostrar_loading_indicator()`.

#### `_on_reload_with_options(filepath, skip_rows, column_names, enable_vis)`

Callback conectado a `main_view.reload_with_options`. Reenvía a `_mostrar_loading_indicator()` (ignora `enable_vis`).

#### `_mostrar_loading_indicator(filepath, skip_rows=0, column_names=None)`

```python
def _mostrar_loading_indicator(self, filepath, skip_rows=0, column_names=None):
    progress = self.data_service.create_progress_dialog(
        "Cargando datos", "Cargando archivo...")
    progress.show()
    thread = self.data_service.create_loader_thread(filepath, skip_rows, column_names)
    thread.data_loaded.connect(self.coordinator.on_datos_cargados)
    thread.error_occurred.connect(self.coordinator.on_error_carga)
    thread.start()
```

**Flujo:**
1. Crea diálogo de progreso via `DataService`
2. Crea hilo de carga (`DataLoaderThread`) via `DataService`
3. Conecta `data_loaded` → `coordinator.on_datos_cargados`
4. Conecta `error_occurred` → `coordinator.on_error_carga`
5. Inicia el hilo

**Patrón:** Carga asíncrona en hilo separado para no bloquear la UI.

---

### 3.6 Carga de Carpeta

```python
def cargar_carpeta(self):
    dialog = FolderLoadDialog(self)
    if dialog.exec():
        config = dialog.get_config()
        if config and config.folder_path:
            self.coordinator.procesar_carga_carpeta(config)
```

**Flujo:**
1. Abre `FolderLoadDialog` como modal
2. Si el usuario acepta, obtiene la configuración (`FolderLoadConfig`)
3. Si hay ruta válida, delega al coordinator para procesar

---

### 3.7 Operaciones de Exportación

Todos los métodos de exportación siguen el mismo patrón: delegan directamente al `AppCoordinator`.

| Método | Formato | Servicio utilizado |
|--------|---------|-------------------|
| `exportar_a_pdf()` | PDF | `ExportService` (via reportlab) |
| `exportar_a_xlsx()` | Excel | `ExportService` (via openpyxl) |
| `exportar_a_csv()` | CSV | `ExportService` |
| `exportar_a_sql()` | SQL/SQLite | `ExportService` (via sqlalchemy) |
| `exportar_a_imagen()` | PNG/JPG | `ExportService` (via Qt pixmap) |
| `exportar_datos_separados()` | Excel separado | `ExportService` (ExcelTemplateSplitter) |
| `exportar_resultado_pivote()` | Variable | `PivotService` (via ExportService) |

---

### 3.8 Acerca De

```python
def mostrar_acerca_de(self):
    from app.widgets.about_dialog import AboutDialog
    AboutDialog.show_about(self)
```

Import lazy de `AboutDialog`. Método estático `show_about()` recibe la ventana padre.

---

### 3.9 Eventos

#### `closeEvent(event)`

```python
def closeEvent(self, event):
    self.data_service.cleanup()
    event.accept()
```

Se ejecuta al cerrar la ventana. Limpia recursos de `DataService` y acepta el evento de cierre.

---

## 4. Función main()

```python
def main():
    app = QApplication(sys.argv)
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.exists(logo_path):
        app.setWindowIcon(QIcon(logo_path))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

**Flujo de arranque:**

1. Crea `QApplication` con `sys.argv`
2. Busca `assets/logo.png` (relativo al directorio del script)
3. Si existe, lo establece como icono de la aplicación
4. Instancia `MainWindow()` (ejecuta toda la inicialización descrita arriba)
5. Muestra la ventana (`window.show()`)
6. Entra al event loop de Qt (`app.exec()`)
7. Cuando el event loop termina, llama a `sys.exit()`

**Punto de ejecución:**
```python
if __name__ == "__main__":
    main()
```

Solo se ejecuta `main()` si el archivo se ejecuta directamente (no si se importa como módulo).

---

## 5. Diagrama de Dependencias

```
main.py
├── app/
│   ├── services/          (DataService, ExportService, FilterService, PivotService)
│   ├── toolbar/           (ToolbarManager)
│   ├── view_manager/      (ViewCoordinator)
│   ├── app_coordinator.py (AppCoordinator)
│   ├── menus/             (MenuBuilder, MenuActions)
│   └── widgets/           (FolderLoadDialog, InfoModal, AboutDialog)
├── core/
│   └── join/              (JoinHistory)
└── assets/                (logo.png)
```

### Flujo de dependencias

```
MainWindow
 ├── DataService          ← Estado de datos, carga
 ├── ExportService        ← Exportaciones (PDF, XLSX, CSV, SQL, imagen)
 ├── FilterService        ← Filtrado
 ├── PivotService         ← Tablas pivote
 ├── ToolbarManager       ← Barra de herramientas
 ├── ViewCoordinator      ← Navegación entre vistas
 ├── AppCoordinator       ← Orquestador central
 │    ├── Usa: DataService, ExportService, PivotService
 │    ├── Usa: ViewCoordinator, ToolbarManager
 │    └── Usa: JoinHistory
 └── JoinHistory          ← Historial de joins (persistente en JSON)
```

---

## 6. Flujo de Señales

```
[Usuario] → MainWindow methods → AppCoordinator → Services
                                        ↓
                                  ViewCoordinator → Views
                                        ↓
                              StatusBar messages
```

### Conexiones activas

| Emisor | Señal | Receptor | Slot |
|--------|-------|----------|------|
| `main_view` | `file_loaded(str)` | `MainWindow` | `_on_file_loaded()` |
| `main_view` | `reload_with_options(str,int,dict)` | `MainWindow` | `_on_reload_with_options()` |
| `data_view` | `filter_applied(str,str)` | `AppCoordinator` | `on_filter_applied()` |
| `data_view` | `filter_cleared()` | `AppCoordinator` | `on_filter_cleared()` |
| `data_view` | `data_updated(DataFrame)` | `AppCoordinator` | `on_data_updated()` |
| `joined_view` | `new_join_requested()` | `AppCoordinator` | `abrir_cruzar_datos()` |
| `AppCoordinator` | `status_message(str)` | `MainWindow.statusBar()` | `showMessage()` |

---

## Resumen

| Aspecto | Detalle |
|---------|---------|
| **Líneas** | 298 |
| **Responsabilidad** | Orquestador de componentes, no contiene lógica de negocio |
| **Patrón** | Coordinator / Facade |
| **Servicios** | 4 (Data, Export, Filter, Pivot) |
| **Vistas** | 4 (Main, Data, Graphics, Joined) |
| **Coordinadores** | 2 (ViewCoordinator, AppCoordinator) |
| **Acciones de menú** | 17 |
| **Formatos de carga** | 16+ (CSV, Excel, JSON, XML, Parquet, etc.) |
| **Formatos de exportación** | 6 (PDF, XLSX, CSV, SQL, imagen, separado) |
