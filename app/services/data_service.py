"""
Servicio de Datos - DataService

Servicio centralizado para la gestión de carga, guardado y manipulación
de datos en Flash View Sheet.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import QProgressDialog, QMessageBox, QDialog
from core.data_handler import (
    cargar_datos, 
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
    
    def __init__(self, filepath: str, skip_rows: int = 0, column_names: Optional[Dict[str, str]] = None) -> None:
        super().__init__()
        self.filepath = filepath
        self.skip_rows = skip_rows
        self.column_names = column_names if column_names else {}
    
    def run(self) -> None:
        """Ejecutar la carga de datos"""
        try:
            if self.isInterruptionRequested():
                return
            df = cargar_datos_con_opciones(self.filepath, self.skip_rows, self.column_names)
            if not self.isInterruptionRequested():
                self.data_loaded.emit(df)
        except Exception as e:
            if not self.isInterruptionRequested():
                self.error_occurred.emit(str(e))


class FolderLoaderThread(QThread):
    """Hilo para cargar y consolidar archivos de una carpeta en segundo plano."""
    
    data_loaded = Signal(object)
    error_occurred = Signal(str)
    progress_updated = Signal(int, int)
    
    def __init__(self, folder_path: str, config: Optional[Any] = None) -> None:
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
        self.df_original: Optional[pd.DataFrame] = None
        self.df_vista_actual: Optional[pd.DataFrame] = None
        self.loading_thread: Optional[DataLoaderThread] = None
        self.folder_loading_thread: Optional[FolderLoaderThread] = None
        self.progress_dialog: Optional[QProgressDialog] = None
        
        # Formatos soportados
        self._format_descriptions: Dict[str, str] = {
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
    def datos_actuales(self) -> Optional[pd.DataFrame]:
        """Obtener los datos actuales"""
        return self.df_vista_actual
    
    @property
    def datos_originales(self) -> Optional[pd.DataFrame]:
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
    
    def create_loader_thread(self, filepath: str, skip_rows: int = 0, column_names: Optional[Dict[str, str]] = None) -> DataLoaderThread:
        """Crear un hilo de carga de datos"""
        self.loading_thread = DataLoaderThread(filepath, skip_rows, column_names)
        return self.loading_thread
    
    def create_folder_loader_thread(self, folder_path: str, config: Optional[Any] = None) -> FolderLoaderThread:
        """Crear un hilo de carga de carpeta"""
        self.folder_loading_thread = FolderLoaderThread(folder_path, config)
        return self.folder_loading_thread
    
    def create_progress_dialog(self, title: str = "Cargando datos", label: str = "Cargando archivo...") -> QProgressDialog:
        """Crear un diálogo de progreso"""
        self.progress_dialog = QProgressDialog(label, "Cancelar", 0, 100)
        self.progress_dialog.setWindowTitle(title)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        return self.progress_dialog
    
    def close_progress_dialog(self) -> None:
        """Cerrar el diálogo de progreso si existe"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
    
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Cargar datos desde un archivo"""
        try:
            self.df_original = cargar_datos(filepath)
            self.df_vista_actual = self.df_original.copy()
            return self.df_vista_actual
        except Exception as e:
            raise Exception(f"No se pudo cargar el archivo: {str(e)}")
    
    def load_data_with_options(self, filepath: str, skip_rows: int = 0, column_names: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """Cargar datos con opciones adicionales"""
        try:
            self.df_original = cargar_datos_con_opciones(filepath, skip_rows, column_names)
            self.df_vista_actual = self.df_original.copy()
            return self.df_vista_actual
        except Exception as e:
            raise Exception(f"No se pudo cargar el archivo: {str(e)}")
    
    def load_folder(self, folder_path: str, config: Optional[Any] = None) -> pd.DataFrame:
        """
        Cargar y consolidar archivos de una carpeta.
        
        Args:
            folder_path: Ruta de la carpeta
            config: Configuración de carga (opcional)
        
        Returns:
            DataFrame consolidado
        """
        try:
            folder_loader = FolderLoader(folder_path)
            
            # Obtener archivos
            all_metadata = folder_loader.get_all_metadata()
            
            if config and hasattr(config, 'should_include_file'):
                selected_files = [
                    meta['filepath'] for meta in all_metadata
                    if config.should_include_file(meta['filename'])
                ]
            else:
                selected_files = [meta['filepath'] for meta in all_metadata]
            
            if not selected_files:
                raise Exception("No se encontraron archivos válidos en la carpeta.")
            
            # Consolidar
            consolidator = ExcelConsolidator()
            
            if config and hasattr(config, 'column_rename_mapping') and config.column_rename_mapping:
                consolidator.set_column_mappings(config.column_rename_mapping)
            
            consolidated_df = consolidator.consolidate_chunked(
                selected_files,
                alignment_method='position',
                chunk_size=10
            )
            
            self.df_original = consolidated_df
            self.df_vista_actual = consolidated_df.copy()
            
            return consolidated_df
            
        except Exception as e:
            raise Exception(f"Error cargando carpeta: {str(e)}")
    
    def reset_to_original(self) -> Optional[pd.DataFrame]:
        """Restaurar datos originales"""
        if self.df_original is not None:
            self.df_vista_actual = self.df_original.copy()
            return self.df_vista_actual
        return None
    
    def set_current_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Establecer datos actuales"""
        self.df_vista_actual = df
        return df

    def set_original_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Establecer los datos originales (snapshot de referencia)"""
        self.df_original = df.copy()
        return self.df_original

    def extensiones_permitidas(self) -> List[str]:
        """Obtener lista de extensiones de archivo soportadas"""
        return get_supported_file_formats()
    
    def get_column_names(self) -> List[str]:
        """Obtener nombres de columnas"""
        if self.df_vista_actual is not None:
            return self.df_vista_actual.columns.tolist()
        return []
    
    def get_data_shape(self) -> Tuple[int, int]:
        """Obtener forma de los datos actuales"""
        if self.df_vista_actual is not None:
            return self.df_vista_actual.shape
        return (0, 0)
    
    def get_filepath(self) -> Optional[str]:
        """Obtener ruta del archivo cargado"""
        if self.loading_thread:
            return self.loading_thread.filepath
        return None
    
    def get_filename(self) -> str:
        """Obtener nombre del archivo cargado"""
        filepath = self.get_filepath()
        if filepath:
            return Path(filepath).name
        return "Archivo cargado"
    
    def cleanup(self) -> None:
        """Limpiar recursos del servicio de forma cooperativa"""
        for thread in (self.loading_thread, self.folder_loading_thread):
            if thread and thread.isRunning():
                thread.requestInterruption()
                thread.quit()
                if not thread.wait(2000):
                    thread.terminate()
                    thread.wait(1000)
        self.close_progress_dialog()
        self.df_original = None
        self.df_vista_actual = None
