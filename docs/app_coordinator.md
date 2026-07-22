# app/app_coordinator.py — Documentacion Completa

Coordinador central de la aplicacion. Orquesta toda la logica de negocio: carga de datos, join, pivote, exportacion, filtros y gestion de hilos. Emite senales para notificar cambios de estado a las vistas.

---

## Indice

1. [Vision General](#1-vision-general)
2. [Importaciones](#2-importaciones)
3. [Clase AppCoordinator](#3-clase-appcoordinator)
   - [3.1 Senales](#31-senales)
   - [3.2 Constructor](#32-constructor)
   - [3.3 Carga de Archivo](#33-carga-de-archivo)
   - [3.4 Callbacks de Datos](#34-callbacks-de-datos)
   - [3.5 Carga de Carpeta](#35-carga-de-carpeta)
   - [3.6 Operaciones de Join](#36-operaciones-de-join)
   - [3.7 Operaciones de Pivote](#37-operaciones-de-pivote)
   - [3.8 Exportacion](#38-exportacion)
   - [3.9 Filtros y Data Updated](#39-filtros-y-data-updated)
   - [3.10 Acerca De](#310-acerca-de)
   - [3.11 Thread Cleanup](#311-thread-cleanup)
   - [3.12 Cleanup General](#312-cleanup-general)
4. [Diagrama de Dependencias](#4-diagrama-de-dependencias)
5. [Flujo de Senales](#5-flujo-de-senales)
6. [Resumen](#6-resumen)

---

## 1. Vision General

`app_coordinator.py` (440 lineas) es el **corazon de la logica de negocio**. Su responsabilidad es:

- Recibir acciones del usuario (via `MainWindow`) y traducirlas en operaciones sobre servicios
- Coordinar dialogos (join, pivote, exportacion, carga de carpeta)
- Gestionar el ciclo de vida de hilos de carga (`DataLoaderThread`, `FolderLoaderThread`)
- Em senales para notificar a las vistas sobre cambios de datos
- Aplicar filtros pendientes (`enable_vis`, `enable_column_visibility`) despues de cargar

No contiene UI propia. Hereda de `QObject` para poder definir y emitir senales Qt.

---

## 2. Importaciones

### Modulos estandar
| Simbolo | Modulo | Uso |
|---------|--------|-----|
| `Any` | `typing` | Tipado generico para configs de pivote |
| `pd` | `pandas` | Tipo `pd.DataFrame` en firmas de metodos |

### PySide6 (Qt6)
| Simbolo | Modulo | Uso |
|---------|--------|-----|
| `QObject` | `PySide6.QtCore` | Clase base (requerida para definir `Signal`) |
| `Signal` | `PySide6.QtCore` | Declaracion de senales personalizadas |
| `QMessageBox` | `PySide6.QtWidgets` | Dialogos de error/aviso/exito |
| `QFileDialog` | `PySide6.QtWidgets` | Selector de archivos |

### Servicios de la aplicacion
| Simbolo | Modulo | Responsabilidad |
|---------|--------|-----------------|
| `DataService` | `app.services` | Estado y carga de datos |
| `ExportService` | `app.services` | Todas las operaciones de exportacion |
| `PivotService` | `app.services` | Tablas pivote |

### Hilos
| Simbolo | Modulo | Responsabilidad |
|---------|--------|-----------------|
| `DataLoaderThread` | `app.services.data_service` | Hilo de carga de archivos individuales |
| `FolderLoaderThread` | `app.services.data_service` | Hilo de carga y consolidacion de carpetas |

### Coordinadores y vistas
| Simbolo | Modulo | Responsabilidad |
|---------|--------|-----------------|
| `ViewCoordinator` | `app.view_manager` | Navegacion y gestion de vistas |
| `ViewRegistry` | `app.view_manager` | Constantes de indices de vistas |
| `ToolbarManager` | `app.toolbar` | Barra de herramientas |

### Widgets (dialogos)
| Simbolo | Modulo | Responsabilidad |
|---------|--------|-----------------|
| `JoinDialog` | `app.widgets` | Dialogo de cruzamiento de datos |
| `SimplePivotDialog` | `app.widgets` | Dialogo de pivote simple |
| `PivotConfigDialog` | `app.widgets` | Dialogo de pivote combinada |
| `FolderLoadDialog` | `app.widgets` | Dialogo de carga de carpeta |

### Modelos del dominio
| Simbolo | Modulo | Responsabilidad |
|---------|--------|-----------------|
| `JoinResult` | `core.join.models` | Resultado de un join |
| `JoinConfig` | `core.join.models` | Configuracion de un join |
| `FolderLoadConfig` | `core.models.folder_load_config` | Configuracion de carga de carpeta |
| `JoinHistory` | `core.join.join_history` | Historial persistente de joins |

### Importaciones condicionales
| Simbolo | Modulo | Cuando se importa |
|---------|--------|-------------------|
| `QMainWindow` | `PySide6.QtWidgets` | Solo bajo `TYPE_CHECKING` (para type hints) |

---

## 3. Clase AppCoordinator

```python
class AppCoordinator(QObject):
    """Coordinador central de la aplicacion."""
```

Hereda de `QObject` para poder definir senales Qt. Es instanciada una sola vez por `MainWindow._init_coordinator()`.

---

### 3.1 Senales

| Senal | Tipo | Descripcion |
|-------|------|-------------|
| `status_message` | `Signal(str)` | Mensaje para la barra de estado |
| `datos_originales_cargados` | `Signal(object)` | DataFrame original recien cargado |
| `datos_actualizados` | `Signal(object)` | DataFrame actual (puede ser resultado de pivote/filtro) |
| `datos_disponibles` | `Signal(bool)` | `True` cuando hay datos cargados, habilita menus y toolbar |

Las senales `datos_originales_cargados` y `datos_actualizados` llevan un `pd.DataFrame` como argumento (embebido como `object` porque PySide6 `Signal` no soporta generics).

---

### 3.2 Constructor

```python
def __init__(self, parent_window: QMainWindow, data_service: DataService,
             export_service: ExportService, pivot_service: PivotService,
             view_coordinator: ViewCoordinator, toolbar_manager: ToolbarManager,
             join_history: JoinHistory) -> None:
```

**7 dependencias inyectadas:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `parent_window` | `QMainWindow` | Ventana padre para dialogos modales |
| `data_service` | `DataService` | Estado y carga de datos |
| `export_service` | `ExportService` | Exportaciones (PDF, XLSX, CSV, SQL, imagen) |
| `pivot_service` | `PivotService` | Tablas pivote |
| `view_coordinator` | `ViewCoordinator` | Navegacion entre vistas |
| `toolbar_manager` | `ToolbarManager` | Barra de herramientas |
| `join_history` | `JoinHistory` | Historial persistente de joins |

**Atributos de instancia:**

| Atributo | Tipo | Descripcion |
|----------|------|-------------|
| `parent` | `QMainWindow` | Ventana padre (para dialogos) |
| `data_service` | `DataService` | Servicio de datos |
| `export_service` | `ExportService` | Servicio de exportacion |
| `pivot_service` | `PivotService` | Servicio de pivote |
| `view_coordinator` | `ViewCoordinator` | Coordinador de vistas |
| `toolbar_manager` | `ToolbarManager` | Gestor del toolbar |
| `join_history` | `JoinHistory \| None` | Historial de joins (se libera en `cleanup()`) |
| `_loader_thread` | `DataLoaderThread \| None` | Hilo activo de carga de archivo |
| `_folder_thread` | `FolderLoaderThread \| None` | Hilo activo de carga de carpeta |
| `_pending_vis` | `bool` | Visibilidad pendiente de aplicar post-carga |
| `_pending_col_vis` | `bool` | Visibilidad de columnas pendiente de aplicar post-carga |

---

### 3.3 Carga de Archivo

#### `solicitar_apertura_archivo()`

Abre `QFileDialog` para seleccionar un archivo. Si se selecciona uno, llama a `iniciar_carga_archivo()`.

#### `iniciar_carga_archivo(filepath, skip_rows, column_names, enable_vis, enable_column_visibility)`

Flujo de carga de un archivo individual:

1. Valida extension contra `data_service.extensiones_permitidas()`
2. Cancela hilo anterior si existe (`_cancel_thread`)
3. Crea `QProgressDialog` con modalidad `WindowModal`
4. Crea `DataLoaderThread` via `data_service.create_loader_thread()`
5. Almacena referencia en `self._loader_thread` (evita GC premature)
6. Guarda `enable_vis` y `enable_column_visibility` como pendientes
7. Conecta senales del hilo:

| Senal del hilo | Conecta a | Proposito |
|----------------|-----------|-----------|
| `data_loaded(DataFrame)` | `_on_datos_cargados()` | Procesar datos exitosos |
| `error_occurred(str)` | `_on_error_carga()` | Mostrar error |
| `finished()` | `progress.close()` | Cerrar dialogo de progreso |
| `finished()` | `_on_loader_finished()` | Liberar referencia al hilo |

8. Inicia el hilo con `thread.start()`

---

### 3.4 Callbacks de Datos

#### `_on_datos_cargados(df: pd.DataFrame)`

Se ejecuta cuando un `DataLoaderThread` termina exitosamente:

1. Almacena el DataFrame en `data_service` (original y actual)
2. Actualiza `MainView` con info del archivo
3. Muestra boton de opciones en `MainView`
4. Emite las 3 senales de estado:

| Senal | Dato | Proposito |
|-------|------|-----------|
| `datos_originales_cargados` | DataFrame original | ViewCoordinator actualiza columnas en MainView |
| `datos_actualizados` | DataFrame actual | ViewCoordinator actualiza DataView y GraphicsView |
| `datos_disponibles` | `True` | Habilita menus y toolbar |

5. Aplica `enable_vis` y `enable_column_visibility` pendientes
6. Cambia a vista de datos (`VIEW_DATA`)
7. Actualiza barra de estado

#### `_on_error_carga(error_message: str)`

Muestra `QMessageBox.critical` con el mensaje de error y actualiza la barra de estado.

#### `_actualizar_ui_post_carga()`

Actualiza `MainView` con la ruta del archivo y muestra el boton de opciones.

---

### 3.5 Carga de Carpeta

#### `procesar_carga_carpeta(config: FolderLoadConfig)`

Flujo similar a `iniciar_carga_archivo` pero para carpetas:

1. Cancela hilo anterior de carpeta si existe
2. Crea `QProgressDialog`
3. Crea `FolderLoaderThread` via `data_service.create_folder_loader_thread()`
4. Almacena referencia en `self._folder_thread`
5. Conecta senales:

| Senal del hilo | Conecta a |
|----------------|-----------|
| `data_loaded(DataFrame)` | `_on_folder_data_loaded()` |
| `error_occurred(str)` | `_on_error_carga()` |
| `finished()` | `progress.close()` |
| `finished()` | `_on_folder_finished()` |
| `progress_updated(int, int)` | Lambda que actualiza `progress.setValue()` |

6. Inicia el hilo

#### `_on_folder_data_loaded(df: pd.DataFrame)`

Similar a `_on_datos_cargados` pero ademas muestra `QMessageBox.information` con filas y columnas.

---

### 3.6 Operaciones de Join

#### `abrir_cruzar_datos()`

1. Verifica `data_service.has_data`
2. Abre `JoinDialog` con los datos actuales
3. Conecta `join_completed` a `_on_join_completed()`

#### `_on_join_completed(result: JoinResult, right_file_path: str | None)`

1. Obtiene nombres de archivos izquierdo y derecho
2. Envia resultado al `ViewCoordinator` (`set_join_result`)
3. Guarda en `join_history` si el join fue exitoso
4. Habilita botones de vista y cambia a `VIEW_JOIN`
5. Actualiza barra de estado

---

### 3.7 Operaciones de Pivote

#### `abrir_pivot_simple()`

1. Verifica `data_service.has_data`
2. Abre `SimplePivotDialog`
3. Si se acepta, llama a `_procesar_pivot_simple(config)`

#### `_procesar_pivot_simple(config)`

1. Ejecuta `pivot_service.execute_simple()`
2. Si hay resultado: actualiza datos, cambia a `VIEW_DATA`, emite `datos_actualizados`
3. Si no: muestra advertencia

#### `abrir_pivot_combinada()` / `_procesar_pivot_combinada(config)`

Mismo patron que pivote simple pero usando `pivot_service.execute_combined()` y `PivotConfigDialog`.

#### `exportar_resultado_pivote()`

Delega a `mostrar_dialogo_exportacion()` con prefijo "Resultado_Pivote".

---

### 3.8 Exportacion

Todos los metodos verifican `data_service.has_data` y delegan a `export_service` via `_exportar_con_dialogo()`:

| Metodo | Formato | Metodo de ExportService |
|--------|---------|------------------------|
| `exportar_a_pdf()` | PDF | `export_to_pdf()` |
| `exportar_a_xlsx()` | Excel | `export_to_xlsx()` |
| `exportar_a_csv()` | CSV | `export_to_csv()` |
| `exportar_a_sql()` | SQL/SQLite | `export_to_sql()` |
| `exportar_a_imagen()` | PNG/JPG | `mostrar_dialogo_exportacion()` (TODO) |
| `exportar_datos_separados()` | Excel separado | `mostrar_dialogo_exportacion()` (TODO) |

#### `mostrar_info()`

Muestra el modal de informacion del dataset original via `view_coordinator.show_info_modal()`.

---

### 3.9 Filtros y Data Updated

#### `on_filter_applied(column: str, term: str)`

Slot conectado a `data_view.filter_applied`. Emite `status_message` con el filtro aplicado y `datos_actualizados` para que las vistas se refresquen.

#### `on_filter_cleared()`

Slot conectado a `data_view.filter_cleared`. Emite `status_message` y `datos_actualizados`.

#### `on_data_updated(df: pd.DataFrame)`

Slot conectado a `data_view.data_updated`. Recibe el DataFrame filtrado completo y lo reenvia a `GraphicsView.update_data()`. Flujo unidireccional:

```
DataView.update_view()
  → data_updated.emit(filtered_df)
    → AppCoordinator.on_data_updated(df)
      → GraphicsView.update_data(df)
```

---

### 3.10 Acerca De

#### `mostrar_acerca_de()`

Import lazy de `AboutDialog`. Delega a `AboutDialog.show_about(self.parent)`.

---

### 3.11 Thread Cleanup

#### `_cancel_thread(thread: DataLoaderThread | FolderLoaderThread | None)`

Detiene un hilo de forma segura:

1. Si el hilo es `None` o no esta corriendo, retorna
2. `requestInterruption()` — senial cooperativa (el hilo revisa `isInterruptionRequested()`)
3. `quit()` — intenta salir del event loop (seguridad)
4. `wait(2000)` — espera hasta 2 segundos
5. Si sigue corriendo: `terminate()` + `wait(1000)` (killa forzado)

#### `_on_loader_finished()`

Slot conectado a `thread.finished`. Pone `self._loader_thread = None`.

#### `_on_folder_finished()`

Slot conectado a `thread.finished`. Pone `self._folder_thread = None`.

---

### 3.12 Cleanup General

#### `cleanup()`

Limpieza profunda invocada por `MainWindow.closeEvent()`:

1. **Detiene hilos activos**: `_cancel_thread` para ambos hilos, nula referencias
2. **Desconecta senales**: `disconnect()` en las 4 senales (con `try/except RuntimeError`)
3. **Libera join_history**: `self.join_history = None`
4. **Libera referencias**: `view_coordinator = None`, `toolbar_manager = None`
5. **Limpia ThreadPool**: `QThreadPool.globalInstance().clear()`

---

## 4. Diagrama de Dependencias

```
AppCoordinator
├── DataService          ← Estado de datos, carga de archivos
│    ├── DataLoaderThread     ← Hilo de carga individual
│    └── FolderLoaderThread   ← Hilo de carga de carpetas
├── ExportService        ← Exportaciones (PDF, XLSX, CSV, SQL, imagen)
├── PivotService         ← Tablas pivote
├── ViewCoordinator      ← Navegacion entre vistas
│    ├── MainView
│    ├── DataView           ← Emite data_updated con DataFrame
│    ├── GraphicsView       ← Recibe DataFrame via on_data_updated
│    └── JoinedDataView
├── ToolbarManager       ← Barra de herramientas
├── JoinHistory          ← Historial de joins (persistente en JSON)
└── Dialogos (creados bajo demanda)
     ├── JoinDialog
     ├── SimplePivotDialog
     ├── PivotConfigDialog
     ├── FolderLoadDialog
     └── AboutDialog
```

---

## 5. Flujo de Senales

### Senales emitidas por AppCoordinator

```
AppCoordinator
 ├── datos_originales_cargados(DataFrame)  → ViewCoordinator → MainView
 ├── datos_actualizados(DataFrame)         → ViewCoordinator → DataView + GraphicsView
 ├── datos_disponibles(bool)               → MenuBuilder + ToolbarManager
 └── status_message(str)                   → MainWindow.statusBar()
```

### Conexiones de entrada (slots)

| Emisor | Senal | Slot en AppCoordinator |
|--------|-------|----------------------|
| `MainView` | `load_file_clicked()` | `solicitar_apertura_archivo()` |
| `MainView` | `reload_with_options(str,int,dict,bool)` | `iniciar_carga_archivo()` (via MainWindow) |
| `DataView` | `filter_applied(str,str)` | `on_filter_applied()` |
| `DataView` | `filter_cleared()` | `on_filter_cleared()` |
| `DataView` | `data_updated(DataFrame)` | `on_data_updated()` |
| `JoinedView` | `new_join_requested()` | `abrir_cruzar_datos()` |
| `DataLoaderThread` | `data_loaded(DataFrame)` | `_on_datos_cargados()` |
| `DataLoaderThread` | `error_occurred(str)` | `_on_error_carga()` |
| `DataLoaderThread` | `finished()` | `_on_loader_finished()` |
| `FolderLoaderThread` | `data_loaded(DataFrame)` | `_on_folder_data_loaded()` |
| `FolderLoaderThread` | `error_occurred(str)` | `_on_error_carga()` |
| `FolderLoaderThread` | `finished()` | `_on_folder_finished()` |
| `FolderLoaderThread` | `progress_updated(int,int)` | Lambda → `progress.setValue()` |
| `JoinDialog` | `join_completed(JoinResult,str)` | `_on_join_completed()` |

### Flujo de carga de archivo (completo)

```
Usuario clickea "Abrir"
  → MainView.load_file_clicked
    → AppCoordinator.solicitar_apertura_archivo()
      → QFileDialog → AppCoordinator.iniciar_carga_archivo()
        → DataService.create_loader_thread()
        → thread.start()
          [hilo en segundo plano]
            → DataLoaderThread.run() → cargar_datos_con_opciones()
            → data_loaded.emit(df)
              → AppCoordinator._on_datos_cargados(df)
                → data_service.set_original_data(df)
                → data_service.set_current_data(df)
                → datos_originales_cargados.emit(df)
                → datos_actualizados.emit(df)
                → datos_disponibles.emit(True)
                → view_coordinator.switch_to(VIEW_DATA)
            → finished.emit()
              → progress.close()
              → _on_loader_thread_finished()
```

---

## 6. Resumen

| Aspecto | Detalle |
|---------|---------|
| **Lineas** | 440 |
| **Responsabilidad** | Orquestador central de logica de negocio |
| **Patron** | Coordinator |
| **Herencia** | `QObject` (requerido para senales Qt) |
| **Senales emitidas** | 4 (`status_message`, `datos_originales_cargados`, `datos_actualizados`, `datos_disponibles`) |
| **Dependencias** | 7 inyectadas (3 servicios + ViewCoordinator + ToolbarManager + JoinHistory + parent_window) |
| **Metodos publicos** | 17 |
| **Metodos privados** | 10 |
| **Hilos gestionados** | 2 (`_loader_thread`, `_folder_thread`) |
| **Dialogos creados** | 5 (JoinDialog, SimplePivotDialog, PivotConfigDialog, FolderLoadDialog, AboutDialog) |
| **Formatos de exportacion** | 6 (PDF, XLSX, CSV, SQL, imagen, separado) |
| **Operaciones de pivote** | 2 (simple, combinada) |
