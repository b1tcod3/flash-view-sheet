# app/services/data_service.py — Documentacion Completa

Servicio centralizado para la gestion de carga, estado y manipulacion de datos en Flash View Sheet. Define los hilos de carga en segundo plano y la clase `DataService` que gestiona el ciclo de vida de los DataFrames.

---

## Indice

1. [Vision General](#1-vision-general)
2. [Importaciones](#2-importaciones)
3. [Clase DataLoaderThread](#3-clase-dataloaderthread)
   - [3.1 Senales](#31-senales)
   - [3.2 Constructor](#32-constructor)
   - [3.3 Metodo run](#33-metodo-run)
4. [Clase FolderLoaderThread](#4-clase-folderloaderthread)
   - [4.1 Senales](#41-senales)
   - [4.2 Constructor](#42-constructor)
   - [4.3 Metodo run](#43-metodo-run)
5. [Clase DataService](#5-clase-dataservice)
   - [5.1 Constructor](#51-constructor)
   - [5.2 Propiedades](#52-propiedades)
   - [5.3 Thread Factory](#53-thread-factory)
   - [5.4 Progress Dialog](#54-progress-dialog)
   - [5.5 Carga Sincrona](#55-carga-sincrona)
   - [5.6 Gestion de Estado](#56-gestion-de-estado)
   - [5.7 Consultas](#57-consultas)
   - [5.8 Cleanup](#58-cleanup)
6. [Diagrama de Dependencias](#6-diagrama-de-dependencias)
7. [Flujo de Senales](#7-flujo-de-senales)
8. [Resumen](#8-resumen)

---

## 1. Vision General

`data_service.py` (303 lineas) es el **servicio de datos** de la aplicacion. Contiene tres clases:

- **`DataLoaderThread`** — Hilo QThread para cargar archivos individuales en segundo plano
- **`FolderLoaderThread`** — Hilo QThread para cargar y consolidar archivos de una carpeta
- **`DataService`** — Clase principal que gestiona el estado de datos, crea hilos, muestra dialogos de progreso y proporciona metadatos

Responsabilidades clave:
- Carga de archivos (Excel, CSV, JSON, XML, Parquet, Feather, HDF5, Pickle, SQLite, YAML)
- Carga y consolidacion de carpetas via `FolderLoaderThread`
- Gestion del estado de datos (`df_original`, `df_vista_actual`)
- Creacion y control de hilos de carga
- Dialogos de progreso para operaciones largas
- Consultas sobre metadatos (nombre de archivo, forma, columnas)

**Diseno:**
- Los hilos usan `isInterruptionRequested()` para cancelacion limpia (3 checks en `DataLoaderThread`, 4 en `FolderLoaderThread`)
- `DataService` no contiene UI propia excepto `QProgressDialog` para la barra de progreso
- `get_filepath()` soporta tanto carga de archivo como de carpeta
- `cleanup()` es agresivo (detiene hilos, libera memoria). `clear_data()` es liviano (solo resetea DataFrames)

---

## 2. Importaciones

### Modulos estandar
| Simbolo | Modulo | Uso |
|---------|--------|-----|
| `Path` | `pathlib` | Obtener nombre de archivo via `Path(filepath).name` |
| `Any` | `typing` | Tipo generico para config de FolderLoaderThread |

### Pandas
| Simbolo | Modulo | Uso |
|---------|--------|-----|
| `pd` | `pandas` | Tipo `pd.DataFrame` en firmas de metodos y atributos |

### PySide6 (Qt6)
| Simbolo | Modulo | Uso |
|---------|--------|-----|
| `QThread` | `PySide6.QtCore` | Clase base para hilos de carga |
| `Signal` | `PySide6.QtCore` | Declaracion de senales personalizadas |
| `Qt` | `PySide6.QtCore` | `Qt.WindowModal` para dialogos de progreso |
| `QProgressDialog` | `PySide6.QtWidgets` | Dialogo de progreso modal |

### Core (logica de negocio)
| Simbolo | Modulo | Uso |
|---------|--------|-----|
| `cargar_datos` | `core.data_handler` | Carga sincrona de archivos |
| `cargar_datos_con_opciones` | `core.data_handler` | Carga con skip_rows y column_names |
| `get_supported_file_formats` | `core.data_handler` | Lista de formatos soportados |
| `FolderLoader` | `core.loaders.folder_loader` | Metadata de archivos en carpeta |
| `ExcelConsolidator` | `core.consolidation.excel_consolidator` | Consolidacion chunked de DataFrames |

---

## 3. Clase DataLoaderThread

Hilo QThread para cargar archivos individuales en segundo plano.

### 3.1 Senales

| Senal | Tipo | Descripcion |
|-------|------|-------------|
| `data_loaded` | `Signal(object)` | Emite el DataFrame cargado (`pd.DataFrame`) |
| `error_occurred` | `Signal(str)` | Emite el mensaje de error si la carga falla |

### 3.2 Constructor

```python
def __init__(self, filepath: str, skip_rows: int = 0, column_names: dict[str, str] | None = None) -> None:
```

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `filepath` | `str` | requerido | Ruta al archivo a cargar |
| `skip_rows` | `int` | `0` | Filas a saltar al inicio |
| `column_names` | `dict[str, str] \| None` | `None` | Renombrado de columnas `{original: nuevo}` |

### 3.3 Metodo run

```python
def run(self) -> None:
```

Flujo:
1. Verifica `isInterruptionRequested()` antes de iniciar → aborta si fue cancelado
2. Llama a `cargar_datos_con_opciones(filepath, skip_rows, column_names)`
3. Verifica `isInterruptionRequested()` antes de emitir `data_loaded`
4. En caso de excepcion, verifica `isInterruptionRequested()` antes de emitir `error_occurred`

**Patron de cancelacion:** 3 puntos de verificacion de `isInterruptionRequested()` en el metodo `run()`. Si el hilo fue cancelado en cualquier punto, se aborta silenciosamente sin emitir senales.

---

## 4. Clase FolderLoaderThread

Hilo QThread para cargar y consolidar archivos de una carpeta en segundo plano.

### 4.1 Senales

| Senal | Tipo | Descripcion |
|-------|------|-------------|
| `data_loaded` | `Signal(object)` | Emite el DataFrame consolidado |
| `error_occurred` | `Signal(str)` | Emite el mensaje de error |
| `progress_updated` | `Signal(int, int)` | Emite `(current, total)` archivos procesados |

### 4.2 Constructor

```python
def __init__(self, folder_path: str, config: Any | None = None) -> None:
```

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `folder_path` | `str` | requerido | Ruta a la carpeta |
| `config` | `Any \| None` | `None` | Configuracion de carga (opcional). Puede tener `should_include_file()` y `column_rename_mapping` |

### 4.3 Metodo run

```python
def run(self) -> None:
```

Flujo:
1. Verifica `isInterruptionRequested()` → aborta si cancelado
2. Crea `FolderLoader(folder_path)` y obtiene metadata de archivos
3. Verifica `isInterruptionRequested()` → aborta si cancelado
4. Filtra archivos segun `config.should_include_file()` (si config lo provee)
5. Emite `progress_updated(0, total_files)`
6. Crea `ExcelConsolidator()` y aplica mapeo de columnas (si config lo provee)
7. Define `_progress_callback` que:
   - Verifica `isInterruptionRequested()` y lanza `InterruptedError` si cancelado
   - Emite `progress_updated(current, total)` por cada chunk
8. Llama a `consolidator.consolidate_chunked()` con el callback
9. Emite `progress_updated(total, total)` al completar
10. Verifica `isInterruptionRequested()` antes de emitir `data_loaded`

**Patron de cancelacion:** 4 puntos de verificacion. El `_progress_callback` lanza `InterruptedError` que rompe el loop de `consolidate_chunked()`, capturado por el `except` externo que no emite si el hilo fue cancelado.

---

## 5. Clase DataService

Clase principal del servicio de datos. No hereda de QObject (no necesita senales propias).

### 5.1 Constructor

```python
def __init__(self) -> None:
```

Atributos de estado:

| Atributo | Tipo | Inicial | Descripcion |
|----------|------|---------|-------------|
| `df_original` | `pd.DataFrame \| None` | `None` | Datos originales (snapshot de referencia) |
| `df_vista_actual` | `pd.DataFrame \| None` | `None` | Datos actuales (puede estar filtrado) |
| `loading_thread` | `DataLoaderThread \| None` | `None` | Hilo de carga de archivo activo |
| `folder_loading_thread` | `FolderLoaderThread \| None` | `None` | Hilo de carga de carpeta activo |
| `progress_dialog` | `QProgressDialog \| None` | `None` | Dialogo de progreso actual |
| `_format_descriptions` | `dict[str, str]` | 16 entradas | Descripciones de formatos para el filtro de archivos |

### 5.2 Propiedades

| Propiedad | Tipo retorno | Descripcion |
|-----------|-------------|-------------|
| `has_data` | `bool` | `True` si `df_vista_actual` no es None y no esta vacio |
| `datos_actuales` | `pd.DataFrame \| None` | Getter de solo lectura para `df_vista_actual` |
| `datos_originales` | `pd.DataFrame \| None` | Getter de solo lectura para `df_original` |

### 5.3 Thread Factory

| Metodo | Parametros | Retorna | Descripcion |
|--------|-----------|---------|-------------|
| `create_loader_thread` | `filepath, skip_rows=0, column_names=None` | `DataLoaderThread` | Crea y almacena un hilo de carga de archivo |
| `create_folder_loader_thread` | `folder_path, config=None` | `FolderLoaderThread` | Crea y almacena un hilo de carga de carpeta |

Ambos metodos guardan referencia al hilo en el atributo correspondiente (`loading_thread` o `folder_loading_thread`).

### 5.4 Progress Dialog

| Metodo | Parametros | Retorna | Descripcion |
|--------|-----------|---------|-------------|
| `create_progress_dialog` | `title="Cargando datos", label="Cargando archivo..."` | `QProgressDialog` | Cierra dialogo previo, crea uno nuevo modal |
| `close_progress_dialog` | (ninguno) | `None` | Cierra y libera el dialogo si existe |

**Nota:** `create_progress_dialog()` llama a `close_progress_dialog()` al inicio para evitar dialogos huérfanos.

### 5.5 Carga Sincrona

| Metodo | Parametros | Retorna | Descripcion |
|--------|-----------|---------|-------------|
| `load_data` | `filepath: str` | `pd.DataFrame` | Carga sincrona simple (sin opciones) |
| `load_data_with_options` | `filepath, skip_rows=0, column_names=None` | `pd.DataFrame` | Carga sincrona con skip_rows y renombrado |

Ambos metodos actualizan `df_original` y `df_vista_actual`. Lanzan `Exception` en caso de error.

**Nota:** Estos metodos son sincrónicos y bloqueantes. Para uso en la app, se recomienda usar los hilos (`DataLoaderThread`) en su lugar.

### 5.6 Gestion de Estado

| Metodo | Parametros | Retorna | Descripcion |
|--------|-----------|---------|-------------|
| `set_current_data` | `df: pd.DataFrame` | `pd.DataFrame` | Establece `df_vista_actual` (sin copia) |
| `set_original_data` | `df: pd.DataFrame` | `pd.DataFrame` | Establece `df_original` (con `.copy()`) |
| `reset_to_original` | (ninguno) | `pd.DataFrame \| None` | Restaura `df_vista_actual` desde `df_original` |
| `clear_data` | (ninguno) | `None` | Resetea ambos DataFrames a None + gc.collect() |

**Diferencia entre `clear_data()` y `cleanup()`:**
- `clear_data()`: Liviano. Solo resetea DataFrames y fuerza GC. No toca hilos ni dialogos.
- `cleanup()`: Agresivo. Detiene hilos, cierra dialogos, libera todo. Usar solo en cierre de app.

**Known limitation:** `clear_data()` tiene un `# TODO` para emitir `datos_disponibles(False)` cuando se implemente el cierre de archivo.

### 5.7 Consultas

| Metodo | Parametros | Retorna | Descripcion |
|--------|-----------|---------|-------------|
| `get_file_filter` | (ninguno) | `str` | Filtro para `QFileDialog` con todos los formatos soportados |
| `extensiones_permitidas` | (ninguno) | `list[str]` | Lista de extensiones soportadas (ej. `['.xlsx', '.csv', ...]`) |
| `get_column_names` | (ninguno) | `list[str]` | Nombres de columnas del DataFrame actual |
| `get_data_shape` | (ninguno) | `tuple[int, int]` | Forma `(filas, columnas)` del DataFrame actual |
| `get_filepath` | (ninguno) | `str \| None` | Ruta del archivo o carpeta cargada |
| `get_filename` | (ninguno) | `str` | Nombre del archivo/carpeta (sin ruta) |

**`get_filepath()` logica dual:**
1. Primero verifica `loading_thread.filepath` (carga de archivo)
2. Luego verifica `folder_loading_thread.folder_path` (carga de carpeta)
3. Retorna `None` si ninguno existe

**`get_filename()` fallback:** Retorna `"Archivo cargado"` si `get_filepath()` retorna None.

### 5.8 Cleanup

```python
def cleanup(self) -> None:
```

Proceso de limpieza agresiva (ejecutar solo en cierre de aplicacion):

1. **Detener hilos activos:** `requestInterruption()` → `quit()` → `wait(2000)` → `terminate()` si no responde
2. **Cerrar dialogo de progreso:** `close_progress_dialog()`
3. **Sobrescribir DataFrames:** `df_original = None`, `df_vista_actual = None`
4. **Forzar GC:** `gc.collect()`
5. **Liberar referencias:** `loading_thread = None`, `folder_loading_thread = None`

---

## 6. Diagrama de Dependencias

```
AppCoordinator
  └── DataService
        ├── create_loader_thread()
        │     └── DataLoaderThread(QThread)
        │           └── core.data_handler.cargar_datos_con_opciones()
        │                 └── core.loaders.* (CSVLoader, ExcelLoader, ...)
        │
        ├── create_folder_loader_thread()
        │     └── FolderLoaderThread(QThread)
        │           ├── core.loaders.folder_loader.FolderLoader
        │           └── core.consolidation.excel_consolidator.ExcelConsolidator
        │
        ├── create_progress_dialog()
        │     └── QProgressDialog
        │
        └── load_data() / load_data_with_options()
              └── core.data_handler.cargar_datos[_con_opciones]()
```

---

## 7. Flujo de Senales

### Carga de archivo (via DataLoaderThread)

```
AppCoordinator.iniciar_carga_archivo()
  → DataService.create_loader_thread(filepath, skip_rows, column_names)
  → DataService.create_progress_dialog(title, label)
  → thread.start()
    [hilo en segundo plano]
      → DataLoaderThread.run()
        → isInterruptionRequested()? → return
        → cargar_datos_con_opciones(filepath, skip_rows, column_names)
        → isInterruptionRequested()? → return
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
          → _on_loader_finished() → self._loader_thread = None
```

### Carga de carpeta (via FolderLoaderThread)

```
AppCoordinator.iniciar_carga_carpeta()
  → DataService.create_folder_loader_thread(folder_path, config)
  → DataService.create_progress_dialog(title, label)
  → thread.start()
    [hilo en segundo plano]
      → FolderLoaderThread.run()
        → isInterruptionRequested()? → return
        → FolderLoader.get_all_metadata()
        → isInterruptionRequested()? → return
        → Filtrar archivos segun config
        → ExcelConsolidator.consolidate_chunked(files, progress_callback)
          [por cada chunk]
            → _progress_callback()
              → isInterruptionRequested()? → raise InterruptedError
              → progress_updated.emit(current, total)
        → isInterruptionRequested()? → return
        → data_loaded.emit(consolidated_df)
          → AppCoordinator._on_folder_data_loaded(df)
            → (mismo flujo que carga de archivo)
        → finished.emit()
          → progress.close()
          → _on_folder_finished() → self._folder_thread = None
```

### Senales de consulta (sin hilos)

```
DataService
  ├── has_data          → bool (consultado por AppCoordinator, ToolbarManager)
  ├── datos_actuales    → DataFrame (consultado por AppCoordinator para export/filtros)
  ├── datos_originales  → DataFrame (consultado por AppCoordinator para historial)
  ├── get_filename()    → str (consultado por AppCoordinator para UI y historial)
  ├── get_column_names() → list[str] (consultado por DataView para filtros)
  └── get_data_shape()  → tuple[int, int] (consultado por MainView para info)
```

---

## 8. Resumen

| Aspecto | Detalle |
|---------|---------|
| **Lineas** | 303 |
| **Clases** | 3 (`DataLoaderThread`, `FolderLoaderThread`, `DataService`) |
| **Responsabilidad** | Carga, estado y metadatos de datos |
| **Patron** | Service (sin UI propia, excepto QProgressDialog) |
| **Herencia** | `DataLoaderThread` y `FolderLoaderThread` heredan de `QThread`. `DataService` no hereda |
| **Senales en hilos** | 5 (`data_loaded` x2, `error_occurred` x2, `progress_updated` x1) |
| **Metodos DataService** | 18 (3 properties + 15 metodos) |
| **Formatos soportados** | 16 extensiones (Excel, CSV, JSON, XML, Parquet, Feather, HDF5, Pickle, SQLite, YAML) |
| **Hilos** | 2 tipos (`DataLoaderThread`, `FolderLoaderThread`) |
| **Cancelacion limpia** | `isInterruptionRequested()` en 3+ puntos por hilo |
| **Cleanup** | 2 niveles: `clear_data()` (liviano) y `cleanup()` (agresivo) |
| **Known TODO** | `clear_data()` necesita emitir `datos_disponibles(False)` para deshabilitar UI |
