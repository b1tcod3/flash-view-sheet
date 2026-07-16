# main.py — Documentacion Completa

Punto de entrada principal de la aplicacion **Flash View Sheet**. Define `MainWindow` (la ventana principal Qt) y la funcion `main()` que arranca el event loop.

---

## Indice

1. [Vision General](#1-vision-general)
2. [Importaciones](#2-importaciones)
3. [Clase MainWindow](#3-clase-mainwindow)
   - [3.1 Constructor](#31-constructor)
   - [3.2 Metodos de Inicializacion](#32-metodos-de-inicializacion)
   - [3.3 Metodos Delegados](#33-metodos-delegados)
   - [3.4 Gestion de Carga de Archivos](#34-gestion-de-carga-de-archivos)
   - [3.5 Carga de Carpeta](#35-carga-de-carpeta)
   - [3.6 Operaciones de Exportacion](#36-operaciones-de-exportacion)
   - [3.7 Acerca De](#37-acerca-de)
   - [3.8 Eventos](#38-eventos)
4. [Funcion main()](#4-funcion-main)
5. [Diagrama de Dependencias](#5-diagrama-de-dependencias)
6. [Flujo de Senales](#6-flujo-de-senales)

---

## 1. Vision General

`main.py` (285 lineas) actua como **orquestador de componentes**. Su responsabilidad es:

- Crear la aplicacion Qt (`QApplication`)
- Instantiar y conectar todos los subsistemas (servicios, coordinadores, vistas, menus, toolbar)
- Delegar toda la logica de negocio a `AppCoordinator`
- Delegar la gestion de datos a `DataService`
- Delegar la navegacion de vistas a `ViewCoordinator`

No contiene logica de negocio propia. Sigue el patron **Coordinator**: `MainWindow` es el punto de conexion central que integra servicios, vistas y coordinadores.

---

## 2. Importaciones

### Modulos estandar
| Modulo | Uso |
|--------|-----|
| `sys` | Acceso a `sys.argv` y `sys.exit()` |
| `pathlib.Path` | Rutas de archivos (reemplaza `os.path`) |

### PySide6 (Qt6)
| Simbolo | Modulo | Uso |
|---------|--------|-----|
| `QApplication` | `PySide6.QtWidgets` | Event loop de Qt |
| `QMainWindow` | `PySide6.QtWidgets` | Clase base de la ventana principal |
| `QStackedWidget` | `PySide6.QtWidgets` | Contenedor de vistas apiladas |
| `QObject` | `PySide6.QtCore` | Base para atributos de tipo QObject |
| `QAction` | `PySide6.QtGui` | Acciones de menu |
| `QCloseEvent` | `PySide6.QtGui` | Evento de cierre de ventana |
| `QIcon` | `PySide6.QtGui` | Icono de la aplicacion |

### Servicios de la aplicacion
| Simbolo | Modulo | Responsabilidad |
|---------|--------|-----------------|
| `DataService` | `app.services` | Carga y estado de datos |
| `ExportService` | `app.services` | Todas las operaciones de exportacion |
| `FilterService` | `app.services` | Filtrado de datos |
| `PivotService` | `app.services` | Tablas pivote |

### Componentes de UI
| Simbolo | Modulo | Responsabilidad |
|---------|--------|-----------------|
| `ToolbarManager` | `app.toolbar` | Gestion del toolbar principal |
| `ViewCoordinator` | `app.view_manager` | Coordinacion de vistas y navegacion |
| `AppCoordinator` | `app.app_coordinator` | Orquestador central de logica de negocio |
| `MenuActions` | `app.menus` | Acciones de menu compartidas (single source of truth) |

### Importaciones lazy (dentro de metodos)
| Simbolo | Modulo | Cuando se importa |
|---------|--------|-------------------|
| `JoinHistory` | `core.join.join_history` | `_init_coordinator()` |
| `MenuBuilder` | `app.menus` | `_create_menu_bar()` |
| `AboutDialog` | `app.widgets.about_dialog` | `mostrar_acerca_de()` |

---

## 3. Clase MainWindow

```python
class MainWindow(QMainWindow):
    """Ventana principal de la aplicacion - Orquestador de componentes"""
```

Hereda de `QMainWindow` (Qt). Funciona como el orquestador central que conecta todos los subsistemas.

### Atributos de instancia

| Atributo | Tipo | Descripcion |
|----------|------|-------------|
| `data_service` | `DataService` | Estado y carga de datos |
| `export_service` | `ExportService` | Exportaciones |
| `filter_service` | `FilterService` | Filtrado |
| `pivot_service` | `PivotService` | Tablas pivote |
| `toolbar_manager` | `ToolbarManager` | Barra de herramientas |
| `view_coordinator` | `ViewCoordinator` | Navegacion entre vistas |
| `coordinator` | `AppCoordinator` | Orquestador central |
| `join_history` | `Optional[JoinHistory]` | Historial de joins |
| `stacked_widget` | `QStackedWidget` | Contenedor de vistas |
| `separar_menu` | `Optional[QObject]` | Referencia al menu Separar |
| `datos_menu` | `Optional[QObject]` | Referencia al menu Datos |
| `tabla_pivote_menu` | `Optional[QObject]` | Referencia al menu Tabla Pivote |

---

### 3.1 Constructor

```python
def __init__(self) -> None:
```

**Orden de inicializacion:**

1. `super().__init__()` — Inicializa QMainWindow
2. `setWindowTitle()` — Titulo: "Flash View Sheet - Visor de Datos Tabulares"
3. `setMinimumSize(800, 600)` — Tamano minimo
4. `resize(1200, 800)` — Tamano inicial
5. `_init_services()` — Crea los 4 servicios
6. `_init_toolbar()` — Crea el gestor del toolbar
7. `_init_coordinator()` — Crea coordinadores y JoinHistory
8. `_setup_ui()` — Construye la interfaz (widget central, vistas, menu, toolbar)
9. `_setup_connections()` — Conecta senales entre componentes

---

### 3.2 Metodos de Inicializacion

#### `_init_services()`

```python
def _init_services(self) -> None:
    self.data_service = DataService()
    self.export_service = ExportService(self)
    self.filter_service = FilterService()
    self.pivot_service = PivotService()
```

Crea las 4 instancias de servicio. `ExportService` recibe `self` (la ventana) como referencia para dialogos modales.

#### `_init_toolbar()`

```python
def _init_toolbar(self) -> None:
    self.toolbar_manager = ToolbarManager(self)
```

Crea el gestor del toolbar, pasando la ventana como referencia.

#### `_init_coordinator()`

```python
def _init_coordinator(self) -> None:
```

Paso mas complejo de la inicializacion:

1. Crea `ViewCoordinator(self)` — gestiona las 4 vistas
2. Crea `AppCoordinator(...)` con 7 dependencias:
   - `parent_window=self`
   - `data_service`, `export_service`, `pivot_service`
   - `view_coordinator`, `toolbar_manager`
   - `join_history=None` (se inicializa despues)
3. Importa y crea `JoinHistory()` (persiste historial en JSON)
4. Asigna `join_history` al coordinator
5. Conecta `coordinator.status_message` → `statusBar().showMessage`

#### `_setup_ui()`

```python
def _setup_ui(self) -> None:
    self._create_central_widget()
    self._create_views()
    self._create_menu_bar()
    self._add_toolbar()
    self.statusBar().showMessage("Listo para cargar datos")
```

Secuencia de construccion de la UI.

#### `_create_central_widget()`

```python
def _create_central_widget(self) -> None:
    self.stacked_widget = QStackedWidget()
    self.setCentralWidget(self.stacked_widget)
```

Crea el `QStackedWidget` que contendra todas las vistas apiladas.

#### `_create_views()`

```python
def _create_views(self) -> None:
    self.view_coordinator.create_views(self.stacked_widget)
    self.stacked_widget.addWidget(self.view_coordinator.get_stacked_widget())
```

Delega la creacion de vistas (MainView, DataView, GraphicsView, JoinedDataView) al `ViewCoordinator`.

#### `_create_menu_bar()`

```python
def _create_menu_bar(self) -> None:
```

1. Importa `MenuBuilder` y `MenuActions` (import lazy)
2. Crea `MenuBuilder(self)` y llama `build()`
3. Obtiene referencias a menus: `separar_menu`, `datos_menu`, `tabla_pivote_menu`
4. Obtiene acciones: `EXPORTAR_SEPARADO`, `CRUZAR_DATOS`, `PIVOT_SIMPLE`, `PIVOT_COMBINADA`, `EXPORTAR_PIVOTE`

#### `_add_toolbar()`

```python
def _add_toolbar(self) -> None:
    self.toolbar_manager.create_toolbar()
    self.addToolBar(self.toolbar_manager.get_toolbar())
```

Crea y anade el toolbar a la ventana.

#### `_setup_connections()`

```python
def _setup_connections(self) -> None:
```

Conecta senales de las vistas al coordinator:

| Senal | Conecta a |
|-------|-----------|
| `main_view.load_file_clicked` | `coordinator.solicitar_apertura_archivo` |
| `main_view.reload_with_options` | `MainWindow._on_reload_with_options` |
| `data_view.filter_applied` | `coordinator.on_filter_applied` |
| `data_view.filter_cleared` | `coordinator.on_filter_cleared` |
| `data_view.data_updated` | `coordinator.on_data_updated` |
| `joined_view.new_join_requested` | `coordinator.abrir_cruzar_datos` |
| `coordinator.datos_originales_cargados` | `view_coordinator.on_datos_originales_cargados` |
| `coordinator.datos_actualizados` | `view_coordinator.on_datos_actualizados` |
| `coordinator.datos_disponibles` | `MenuActions.enable_data_actions` |
| `coordinator.datos_disponibles` | `toolbar_manager.on_datos_disponibles` |

Cada conexion verifica que la vista no sea `None` antes de conectar.

---

### 3.3 Metodos Delegados

Todos delegan directamente al `AppCoordinator` o `ViewCoordinator`:

| Metodo | Delega a | Descripcion |
|--------|----------|-------------|
| `switch_view(index)` | `view_coordinator.switch_to(index)` | Cambiar vista activa |
| `show_info_modal()` | `coordinator.mostrar_info()` | Mostrar info del dataset |
| `abrir_archivo()` | `coordinator.solicitar_apertura_archivo()` | Abrir dialogo de carga |
| `cargar_carpeta()` | `coordinator.solicitar_carga_carpeta()` | Abrir dialogo de carga de carpeta |
| `abrir_cruzar_datos()` | `coordinator.abrir_cruzar_datos()` | Abrir dialogo de join |
| `abrir_pivot_simple()` | `coordinator.abrir_pivot_simple()` | Abrir dialogo pivote simple |
| `abrir_pivot_combinada()` | `coordinator.abrir_pivot_combinada()` | Abrir dialogo pivote combinada |
| `exportar_resultado_pivote()` | `coordinator.exportar_resultado_pivote()` | Exportar pivote |
| `exportar_a_pdf()` | `coordinator.exportar_a_pdf()` | Exportar a PDF |
| `exportar_a_xlsx()` | `coordinator.exportar_a_xlsx()` | Exportar a Excel |
| `exportar_a_csv()` | `coordinator.exportar_a_csv()` | Exportar a CSV |
| `exportar_a_sql()` | `coordinator.exportar_a_sql()` | Exportar a SQL |
| `exportar_a_imagen()` | `coordinator.exportar_a_imagen()` | Exportar a imagen |
| `exportar_datos_separados()` | `coordinator.exportar_datos_separados()` | Exportar datos separados |
| `mostrar_acerca_de()` | `AboutDialog.show_about(self)` | Mostrar dialogo Acerca de |

**Nota:** `MainWindow` no contiene logica de negocio. Todos los metodos son delegaciones unidireccionales al `AppCoordinator`.

---

### 3.4 Gestion de Carga de Archivos

#### `abrir_archivo()`

```python
def abrir_archivo(self) -> None:
    self.coordinator.solicitar_apertura_archivo()
```

Delega al coordinador, quien abre `QFileDialog`, valida la extension y arranca el hilo de carga.

#### `_on_reload_with_options(filepath, skip_rows, column_names, enable_column_visibility)`

```python
def _on_reload_with_options(self, filepath, skip_rows, column_names, enable_column_visibility=True):
    self.coordinator.iniciar_carga_archivo(filepath, skip_rows, column_names, enable_column_visibility=enable_column_visibility)
```

Callback conectado a `main_view.reload_with_options`. Reenvia al coordinador con el parametro `enable_column_visibility`.

---

### 3.5 Carga de Carpeta

```python
def cargar_carpeta(self) -> None:
    self.coordinator.solicitar_carga_carpeta()
```

Delega al coordinador, quien abre `FolderLoadDialog`, obtiene la configuracion y procesa la carga en hilo separado.

---

### 3.6 Operaciones de Exportacion

Todos los metodos de exportacion siguen el mismo patron: delegan directamente al `AppCoordinator`.

| Metodo | Formato | Servicio utilizado |
|--------|---------|-------------------|
| `exportar_a_pdf()` | PDF | `ExportService` (via reportlab) |
| `exportar_a_xlsx()` | Excel | `ExportService` (via openpyxl) |
| `exportar_a_csv()` | CSV | `ExportService` |
| `exportar_a_sql()` | SQL/SQLite | `ExportService` (via sqlalchemy) |
| `exportar_a_imagen()` | PNG/JPG | `ExportService` (via Qt pixmap) |
| `exportar_datos_separados()` | Excel separado | `ExportService` (ExcelTemplateSplitter) |
| `exportar_resultado_pivote()` | Variable | `PivotService` (via ExportService) |

---

### 3.7 Acerca De

```python
def mostrar_acerca_de(self) -> None:
    from app.widgets.about_dialog import AboutDialog
    AboutDialog.show_about(self)
```

Import lazy de `AboutDialog`. Metodo estatico `show_about()` recibe la ventana padre.

---

### 3.8 Eventos

#### `closeEvent(event)`

```python
def closeEvent(self, event: QCloseEvent) -> None:
    # 1. Detener threads y liberar DataFrames grandes
    self.data_service.cleanup()
    self.pivot_service.cleanup()
    
    # 2. Desconectar coordinator y liberar vistas
    self.coordinator.cleanup()
    self.view_coordinator.cleanup()
    
    event.accept()
```

**Flujo de limpieza ordenada (4 pasos):**

1. `data_service.cleanup()` — Detiene hilos de carga, libera DataFrames
2. `pivot_service.cleanup()` — Libera resultado y configuracion de pivote
3. `coordinator.cleanup()` — Desconecta senales, libera referencias
4. `view_coordinator.cleanup()` — Libera todas las referencias a vistas

El orden importa: primero los servicios (liberan datos), luego los coordinadores (liberan referencias).

---

## 4. Funcion main()

```python
def main() -> None:
    app = QApplication(sys.argv)
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    if logo_path.exists():
        app.setWindowIcon(QIcon(str(logo_path)))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

**Flujo de arranque:**

1. Crea `QApplication` con `sys.argv`
2. Busca `assets/logo.png` usando `pathlib.Path` (relativo al directorio del script)
3. Si existe, lo establece como icono de la aplicacion
4. Instancia `MainWindow()` (ejecuta toda la inicializacion descrita arriba)
5. Muestra la ventana (`window.show()`)
6. Entra al event loop de Qt (`app.exec()`)
7. Cuando el event loop termina, llama a `sys.exit()`

**Punto de ejecucion:**
```python
if __name__ == "__main__":
    main()
```

Solo se ejecuta `main()` si el archivo se ejecuta directamente (no si se importa como modulo).

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
│   └── widgets/           (AboutDialog)
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
 ├── ViewCoordinator      ← Navegacion entre vistas
 ├── AppCoordinator       ← Orquestador central
 │    ├── Usa: DataService, ExportService, PivotService
 │    ├── Usa: ViewCoordinator, ToolbarManager
 │    ├── Crea: FolderLoadDialog, JoinDialog, PivotConfigDialog
 │    └── Usa: JoinHistory
 └── JoinHistory          ← Historial de joins (persistente en JSON)
```

---

## 6. Flujo de Senales

```
[Usuario] → MainWindow methods → AppCoordinator → Services
                                        ↓
                                  ViewCoordinator → Views
                                        ↓
                              StatusBar messages (via status_message signal)
```

### Conexiones activas

| Emisor | Senal | Receptor | Slot |
|--------|-------|----------|------|
| `main_view` | `load_file_clicked()` | `AppCoordinator` | `solicitar_apertura_archivo()` |
| `main_view` | `reload_with_options(str,int,dict,bool)` | `MainWindow` | `_on_reload_with_options()` |
| `data_view` | `filter_applied(str,str)` | `AppCoordinator` | `on_filter_applied()` |
| `data_view` | `filter_cleared()` | `AppCoordinator` | `on_filter_cleared()` |
| `data_view` | `data_updated(DataFrame)` | `AppCoordinator` | `on_data_updated()` |
| `joined_view` | `new_join_requested()` | `AppCoordinator` | `abrir_cruzar_datos()` |
| `AppCoordinator` | `status_message(str)` | `MainWindow.statusBar()` | `showMessage()` |
| `AppCoordinator` | `datos_originales_cargados(DataFrame)` | `ViewCoordinator` | `on_datos_originales_cargados()` |
| `AppCoordinator` | `datos_actualizados(DataFrame)` | `ViewCoordinator` | `on_datos_actualizados()` |
| `AppCoordinator` | `datos_disponibles(bool)` | `MenuActions` | `enable_data_actions()` |
| `AppCoordinator` | `datos_disponibles(bool)` | `ToolbarManager` | `on_datos_disponibles()` |

---

## Resumen

| Aspecto | Detalle |
|---------|---------|
| **Lineas** | 285 |
| **Responsabilidad** | Orquestador de componentes, no contiene logica de negocio |
| **Patron** | Coordinator / Facade |
| **Servicios** | 4 (Data, Export, Filter, Pivot) |
| **Vistas** | 4 (Main, Data, Graphics, Joined) |
| **Coordinadores** | 2 (ViewCoordinator, AppCoordinator) |
| **Acciones de menu** | 17 |
| **Formatos de carga** | 16+ (CSV, Excel, JSON, XML, Parquet, etc.) |
| **Formatos de exportacion** | 6 (PDF, XLSX, CSV, SQL, imagen, separado) |
| **Senales del coordinator** | 4 (status_message, datos_originales_cargados, datos_actualizados, datos_disponibles) |
