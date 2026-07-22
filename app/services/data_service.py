"""
Servicio de Datos - DataService

Servicio centralizado para la gestión de carga, guardado y manipulación
de datos en Flash View Sheet.
"""

from pathlib import Path
from typing import Any
import pandas as pd
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import QProgressDialog
from core.data_handler import (
    cargar_datos_con_opciones,
    get_supported_file_formats
)
from core.loaders.folder_loader import FolderLoader
from core.consolidation.excel_consolidator import ExcelConsolidator

class DataLoaderThread(QThread):
    """Hilo para cargar datos en segundo plano"""
    
    # Signal(pd.DataFrame)
    data_loaded = Signal(object)
    # Signal(str)
    error_occurred = Signal(str)
    # Signal(int, int) — (loaded, total) para barra de progreso
    progress_updated = Signal(int, int)
    
    def __init__(self, filepath: str, skip_rows: int = 0, column_names: dict[str, str] | None = None, separator: str | None = None, sheet_name: str | None = None) -> None:
        super().__init__()
        self.filepath = filepath
        self.skip_rows = skip_rows
        self.column_names = column_names if column_names else {}
        self.separator = separator
        self.sheet_name = sheet_name
    
    def run(self) -> None:
        """Ejecutar la carga de datos"""
        try:
            if self.isInterruptionRequested():
                return
            self.progress_updated.emit(0, 100)
            df = cargar_datos_con_opciones(self.filepath, self.skip_rows, self.column_names, separator=self.separator, sheet_name=self.sheet_name)
            if not self.isInterruptionRequested():
                self.progress_updated.emit(100, 100)
                self.data_loaded.emit(df)
        except Exception as e:
            if not self.isInterruptionRequested():
                self.error_occurred.emit(str(e))

class FolderLoaderThread(QThread):
    """Hilo para cargar y consolidar archivos de una carpeta en segundo plano."""
    
    data_loaded = Signal(object)
    error_occurred = Signal(str)
    progress_updated = Signal(int, int)
    
    def __init__(self, folder_path: str, config: Any | None = None) -> None:
        super().__init__()
        self.folder_path = folder_path
        self.config = config
    
    def run(self) -> None:
        try:
            if self.isInterruptionRequested():
                return
            
            folder_loader = FolderLoader(self.folder_path)
            all_metadata = folder_loader.get_all_metadata()
            
            if self.isInterruptionRequested():
                return
            
            if self.config and hasattr(self.config, 'should_include_file'):
                selected_files = [
                    meta['filepath'] for meta in all_metadata
                    if self.config.should_include_file(meta['filename'])
                ]
            else:
                selected_files = [meta['filepath'] for meta in all_metadata]
            
            if not selected_files:
                self.error_occurred.emit("No se encontraron archivos válidos en la carpeta.")
                return
            
            total_files = len(selected_files)
            self.progress_updated.emit(0, total_files)
            
            consolidator = ExcelConsolidator()
            
            if self.config and hasattr(self.config, 'column_rename_mapping') and self.config.column_rename_mapping:
                consolidator.set_column_mappings(self.config.column_rename_mapping)
            
            def _progress_callback(progress: float) -> None:
                if self.isInterruptionRequested():
                    raise InterruptedError("Thread interrupted")
                current = int(progress / 100 * total_files)
                self.progress_updated.emit(current, total_files)
            
            consolidated_df = consolidator.consolidate_chunked(
                selected_files,
                alignment_method='position',
                chunk_size=10,
                progress_callback=_progress_callback
            )
            
            self.progress_updated.emit(total_files, total_files)
            
            if not self.isInterruptionRequested():
                self.data_loaded.emit(consolidated_df)
        except Exception as e:
            if not self.isInterruptionRequested():
                self.error_occurred.emit(str(e))

class DataService:
    """
    Servicio unificado para operaciones de datos.
    
    Responsabilidades:
    - Carga de archivos (Excel, CSV, JSON, etc.)
    - Carga de carpetas con consolidación
    - Gestión del estado de datos
    """
    
    def __init__(self) -> None:
        """Inicializar el servicio de datos"""
        self.df_original: pd.DataFrame | None = None
        self.df_vista_actual: pd.DataFrame | None = None
        self.loading_thread: DataLoaderThread | None = None
        self.folder_loading_thread: FolderLoaderThread | None = None
        self.progress_dialog: QProgressDialog | None = None
        self._active_threads: list[DataLoaderThread] = []
        
        # Formatos soportados
        self._format_descriptions: dict[str, str] = {
            '.xlsx': 'Archivos de Excel',
            '.xls': 'Archivos de Excel Legacy',
            '.csv': 'Archivos CSV',
            '.tsv': 'Archivos TSV',
            '.json': 'Archivos JSON',
            '.xml': 'Archivos XML',
            '.parquet': 'Archivos Parquet',
            '.feather': 'Archivos Feather',
            '.hdf5': 'Archivos HDF5',
            '.h5': 'Archivos HDF5',
            '.pkl': 'Archivos Pickle',
            '.pickle': 'Archivos Pickle',
            '.db': 'Bases de Datos SQLite',
            '.sqlite': 'Bases de Datos SQLite',
            '.sqlite3': 'Bases de Datos SQLite',
            '.yaml': 'Archivos YAML',
            '.yml': 'Archivos YAML',
        }
    
    @property
    def has_data(self) -> bool:
        """Verificar si hay datos cargados"""
        return self.df_vista_actual is not None and not self.df_vista_actual.empty
    
    @property
    def datos_actuales(self) -> pd.DataFrame | None:
        """Obtener los datos actuales"""
        return self.df_vista_actual
    
    @property
    def datos_originales(self) -> pd.DataFrame | None:
        """Obtener los datos originales"""
        return self.df_original
    
    def get_file_filter(self) -> str:
        """Obtener filtro de archivos para diálogos de apertura"""
        supported_formats = get_supported_file_formats()
        
        format_filters = []
        for ext in supported_formats:
            if ext in self._format_descriptions:
                format_filters.append(f"{self._format_descriptions[ext]} (*{ext})")
        
        # Añadir filtro de "Todos los soportados"
        all_extensions = " ".join([f"*{ext}" for ext in supported_formats])
        all_formats = f"Todos los archivos soportados ({all_extensions})"
        format_filters.insert(0, all_formats)
        
        return ";;".join(format_filters)
    
    def create_loader_thread(self, filepath: str, skip_rows: int = 0, column_names: dict[str, str] | None = None, separator: str | None = None, sheet_name: str | None = None) -> DataLoaderThread:
        """Crear un hilo de carga de datos"""
        thread = DataLoaderThread(filepath, skip_rows, column_names, separator, sheet_name)
        self.loading_thread = thread
        self._active_threads.append(thread)
        thread.finished.connect(
            lambda t=thread: self._active_threads.remove(t) if t in self._active_threads else None
        )
        thread.finished.connect(
            lambda t=thread: setattr(self, 'loading_thread', None) if self.loading_thread is t else None
        )
        return thread
    
    def create_folder_loader_thread(self, folder_path: str, config: Any | None = None) -> FolderLoaderThread:
        """Crear un hilo de carga de carpeta"""
        self.folder_loading_thread = FolderLoaderThread(folder_path, config)
        return self.folder_loading_thread
    
    def create_progress_dialog(self, title: str = "Cargando datos", label: str = "Cargando archivo...") -> QProgressDialog:
        """Crear un diálogo de progreso"""
        self.close_progress_dialog()
        self.progress_dialog = QProgressDialog(label, "Cancelar", 0, 100)
        self.progress_dialog.setWindowTitle(title)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        return self.progress_dialog

    def close_progress_dialog(self) -> None:
        """Cerrar el diálogo de progreso si existe"""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
    
    def set_current_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Establecer datos actuales"""
        self.df_vista_actual = df
        return df

    def set_original_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Establecer los datos originales (snapshot de referencia)"""
        self.df_original = df.copy()
        return self.df_original

    def clear_data(self) -> None:
        """Reset data state without stopping threads or closing dialogs."""
        self.df_original = None
        self.df_vista_actual = None
        # TODO: Emitir señal (ej. datos_disponibles(False)) para deshabilitar menús/toolbar
        import gc
        gc.collect()

    def extensiones_permitidas(self) -> list[str]:
        """Obtener lista de extensiones de archivo soportadas"""
        return get_supported_file_formats()
    
    def get_column_names(self) -> list[str]:
        """Obtener nombres de columnas"""
        if self.df_vista_actual is not None:
            return self.df_vista_actual.columns.tolist()
        return []
    
    def get_data_shape(self) -> tuple[int, int]:
        """Obtener forma de los datos actuales"""
        if self.df_vista_actual is not None:
            return self.df_vista_actual.shape
        return (0, 0)
    
    def get_filepath(self) -> str | None:
        """Obtener ruta del archivo o carpeta cargada"""
        if self.loading_thread:
            return self.loading_thread.filepath
        if self.folder_loading_thread:
            return self.folder_loading_thread.folder_path
        return None
    
    def get_filename(self) -> str:
        """Obtener nombre del archivo cargado"""
        filepath = self.get_filepath()
        if filepath:
            return Path(filepath).name
        return "Archivo cargado"
    
    def cleanup(self) -> None:
        """Libera agresivamente la memoria de los DataFrames cargados."""
        # 1. Detener hilos activos
        for thread in self._active_threads[:]:
            if thread.isRunning():
                thread.requestInterruption()
                thread.quit()
                if not thread.wait(2000):
                    thread.terminate()
                    thread.wait(1000)
        self._active_threads.clear()

        for thread in (self.loading_thread, self.folder_loading_thread):
            if thread and thread.isRunning():
                thread.requestInterruption()
                thread.quit()
                if not thread.wait(2000):
                    thread.terminate()
                    thread.wait(1000)

        # 2. Cerrar diálogo de progreso
        self.close_progress_dialog()

        # 3. Sobrescribir DataFrames pesados
        self.df_original = None
        self.df_vista_actual = None

        # 4. Forzar recolección de basura
        import gc
        gc.collect()

        # 5. Liberar referencias a hilos
        self.loading_thread = None
        self.folder_loading_thread = None
