"""
Servicio de Datos - DataService

Servicio centralizado para la gestión de carga, guardado y manipulación
de datos en Flash View Sheet.
"""

import os
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
    
    data_loaded = Signal(object)
    error_occurred = Signal(str)
    
    def __init__(self, filepath, skip_rows=0, column_names=None):
        super().__init__()
        self.filepath = filepath
        self.skip_rows = skip_rows
        self.column_names = column_names if column_names else {}
    
    def run(self):
        """Ejecutar la carga de datos"""
        try:
            df = cargar_datos_con_opciones(self.filepath, self.skip_rows, self.column_names)
            self.data_loaded.emit(df)
        except Exception as e:
            self.error_occurred.emit(str(e))


class DataService:
    """
    Servicio unificado para operaciones de datos.
    
    Responsabilidades:
    - Carga de archivos (Excel, CSV, JSON, etc.)
    - Carga de carpetas con consolidación
    - Gestión del estado de datos
    """
    
    def __init__(self):
        """Inicializar el servicio de datos"""
        self.df_original = None
        self.df_vista_actual = None
        self.loading_thread = None
        self.progress_dialog = None
        
        # Formatos soportados
        self._format_descriptions = {
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
    def has_data(self):
        """Verificar si hay datos cargados"""
        return self.df_vista_actual is not None and not self.df_vista_actual.empty
    
    @property
    def datos_actuales(self):
        """Obtener los datos actuales"""
        return self.df_vista_actual
    
    @property
    def datos_originales(self):
        """Obtener los datos originales"""
        return self.df_original
    
    def get_file_filter(self):
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
    
    def create_loader_thread(self, filepath, skip_rows=0, column_names=None):
        """Crear un hilo de carga de datos"""
        self.loading_thread = DataLoaderThread(filepath, skip_rows, column_names)
        return self.loading_thread
    
    def create_progress_dialog(self, title="Cargando datos", label="Cargando archivo..."):
        """Crear un diálogo de progreso"""
        self.progress_dialog = QProgressDialog(label, "Cancelar", 0, 100)
        self.progress_dialog.setWindowTitle(title)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        return self.progress_dialog
    
    def close_progress_dialog(self):
        """Cerrar el diálogo de progreso si existe"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
    
    def load_data(self, filepath):
        """Cargar datos desde un archivo"""
        try:
            self.df_original = cargar_datos(filepath)
            self.df_vista_actual = self.df_original.copy()
            return self.df_vista_actual
        except Exception as e:
            raise Exception(f"No se pudo cargar el archivo: {str(e)}")
    
    def load_data_with_options(self, filepath, skip_rows=0, column_names=None):
        """Cargar datos con opciones adicionales"""
        try:
            self.df_original = cargar_datos_con_opciones(filepath, skip_rows, column_names)
            self.df_vista_actual = self.df_original.copy()
            return self.df_vista_actual
        except Exception as e:
            raise Exception(f"No se pudo cargar el archivo: {str(e)}")
    
    def load_folder(self, folder_path, config=None):
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
    
    def reset_to_original(self):
        """Restaurar datos originales"""
        if self.df_original is not None:
            self.df_vista_actual = self.df_original.copy()
            return self.df_vista_actual
        return None
    
    def set_current_data(self, df):
        """Establecer datos actuales"""
        self.df_vista_actual = df
        return df
    
    def get_column_names(self):
        """Obtener nombres de columnas"""
        if self.df_vista_actual is not None:
            return self.df_vista_actual.columns.tolist()
        return []
    
    def get_data_shape(self):
        """Obtener forma de los datos actuales"""
        if self.df_vista_actual is not None:
            return self.df_vista_actual.shape
        return (0, 0)
    
    def get_filepath(self):
        """Obtener ruta del archivo cargado"""
        if self.loading_thread:
            return self.loading_thread.filepath
        return None
    
    def get_filename(self):
        """Obtener nombre del archivo cargado"""
        filepath = self.get_filepath()
        if filepath:
            return os.path.basename(filepath)
        return "Archivo cargado"
    
    def cleanup(self):
        """Limpiar recursos del servicio"""
        if self.loading_thread and self.loading_thread.isRunning():
            self.loading_thread.terminate()
            self.loading_thread.wait()
        self.close_progress_dialog()
