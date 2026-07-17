"""
AppCoordinator - Orquestador de la aplicación

Coordinador central que maneja la lógica de negocio y la orquestación
entre servicios, diálogos y vistas.
"""

from typing import Any, TYPE_CHECKING

import pandas as pd
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox, QFileDialog

from app.services import DataService, ExportService, PivotService
from app.view_manager import ViewCoordinator, ViewRegistry
from app.toolbar import ToolbarManager
from app.widgets import JoinDialog, SimplePivotDialog, PivotConfigDialog, FolderLoadDialog
from core.join.models import JoinResult, JoinConfig
from core.models.folder_load_config import FolderLoadConfig
from core.join.join_history import JoinHistory

if TYPE_CHECKING:
    from PySide6.QtWidgets import QMainWindow

class AppCoordinator(QObject):
    """
    Coordinador central de la aplicación.
    
    Responsabilidades:
    - Manejar callbacks de carga de datos
    - Coordinar diálogos de operaciones (join, pivote, exportación)
    - Actualizar estado de menús
    - Gestionar transiciones de vistas
    """
    
    # Señales para comunicar con MainWindow
    status_message = Signal(str)
    # Signal(pd.DataFrame)
    datos_originales_cargados = Signal(object)
    # Signal(pd.DataFrame)
    datos_actualizados = Signal(object)
    datos_disponibles = Signal(bool)
    
    def __init__(self, parent_window: 'QMainWindow', data_service: DataService, export_service: ExportService, 
                 pivot_service: PivotService, view_coordinator: ViewCoordinator, toolbar_manager: ToolbarManager, join_history: JoinHistory) -> None:
        """Inicializar el coordinador"""
        super().__init__(parent_window)
        
        self.parent = parent_window
        self.data_service = data_service
        self.export_service = export_service
        self.pivot_service = pivot_service
        self.view_coordinator = view_coordinator
        self.toolbar_manager = toolbar_manager
        self.join_history = join_history
    
    # ==================== CARGA DE ARCHIVO ====================

    def solicitar_apertura_archivo(self) -> None:
        """Muestra QFileDialog y arranca la carga si se selecciona un archivo."""
        filtro = self.data_service.get_file_filter()
        filepath, _ = QFileDialog.getOpenFileName(
            self.parent, "Abrir archivo de datos", "", filtro
        )
        if filepath:
            self.iniciar_carga_archivo(filepath, skip_rows=0, column_names={})

    def solicitar_carga_carpeta(self) -> None:
        """Muestra FolderLoadDialog y procesa la carga si se confirma."""
        dialog = FolderLoadDialog(self.parent)
        if dialog.exec():
            config = dialog.get_config()
            if config and config.folder_path:
                self.procesar_carga_carpeta(config)

    def iniciar_carga_archivo(self, filepath: str, skip_rows: int = 0, column_names: dict[str, str] | None = None, enable_vis: bool = True, enable_column_visibility: bool = True) -> None:
        """Inicia la carga de un archivo: valida extensión, muestra progreso, crea hilo y conecta resultados."""
        from pathlib import Path
        path = Path(filepath)
        extensiones = self.data_service.extensiones_permitidas()
        if path.suffix.lower() not in extensiones:
            self.status_message.emit(f"Formato no soportado: {path.suffix}")
            return

        progress = self.data_service.create_progress_dialog(
            "Cargando datos", "Cargando archivo..."
        )
        progress.setMinimumDuration(500)
        progress.show()

        try:
            thread = self.data_service.create_loader_thread(
                filepath, skip_rows, column_names or {}
            )
        except Exception as e:
            progress.close()
            self._on_error_carga(str(e))
            return

        self._pending_vis = enable_vis
        self._pending_col_vis = enable_column_visibility

        thread.data_loaded.connect(self._on_datos_cargados)
        thread.error_occurred.connect(self._on_error_carga)
        thread.finished.connect(progress.close)
        thread.start()

    # ==================== CALLBACKS DE DATOS ====================
    
    def _on_datos_cargados(self, df: pd.DataFrame) -> None:
        """Manejar datos cargados exitosamente"""
        self.data_service.set_original_data(df)
        self.data_service.set_current_data(df)
        
        # Actualizar MainView con info del archivo
        self.view_coordinator.update_main_view(self.data_service.get_filepath())
        
        # Actualizar estado UI
        self._actualizar_ui_post_carga()
        
        # Emitir señales para que las vistas reaccionen
        self.datos_originales_cargados.emit(self.data_service.datos_originales)
        self.datos_actualizados.emit(self.data_service.datos_actuales)
        self.datos_disponibles.emit(True)
        
        # Phase 6: apply pending enable_vis
        if hasattr(self, '_pending_vis'):
            self.view_coordinator.toggle_visualization(self._pending_vis)
            del self._pending_vis
        
        # Phase 6: apply pending column visibility
        if hasattr(self, '_pending_col_vis'):
            self.view_coordinator.set_column_visibility_enabled(self._pending_col_vis)
            del self._pending_col_vis
        
        # Cambiar a vista de datos
        self.view_coordinator.switch_to(ViewRegistry.VIEW_DATA)
        self.status_message.emit(f"Datos cargados: {self.data_service.get_filename()}")
    
    def _on_error_carga(self, error_message: str) -> None:
        """Manejar error de carga"""
        QMessageBox.critical(self.parent, "Error de carga", error_message)
        self.status_message.emit("Error al cargar archivo")
    
    def _actualizar_ui_post_carga(self) -> None:
        """Actualizar UI después de cargar datos"""
        main_view = self.view_coordinator.get_main_view()
        
        if main_view:
            main_view.set_file_info(self.data_service.get_filepath())
            main_view.show_options_button()
    
    # ==================== CARGA DE CARPETA ====================
    
    def procesar_carga_carpeta(self, config: FolderLoadConfig) -> None:
        """Procesar carga de carpeta en segundo plano"""
        progress = self.data_service.create_progress_dialog(
            "Cargando carpeta", "Escaneando archivos Excel..."
        )
        progress.setMinimumDuration(500)
        progress.show()

        try:
            thread = self.data_service.create_folder_loader_thread(
                config.folder_path, config
            )
        except Exception as e:
            progress.close()
            self._on_error_carga(str(e))
            return

        thread.data_loaded.connect(self._on_folder_data_loaded)
        thread.error_occurred.connect(self._on_error_carga)
        thread.finished.connect(progress.close)
        thread.progress_updated.connect(
            lambda current, total: progress.setValue(int(current / total * 100)) if total > 0 else None
        )
        thread.start()
    
    def _on_folder_data_loaded(self, df: pd.DataFrame) -> None:
        """Manejar datos de carpeta cargados exitosamente"""
        self.data_service.set_original_data(df)
        self.data_service.set_current_data(df)
        
        self.view_coordinator.switch_to(ViewRegistry.VIEW_DATA)
        
        self.datos_originales_cargados.emit(self.data_service.datos_originales)
        self.datos_actualizados.emit(self.data_service.datos_actuales)
        self.datos_disponibles.emit(True)
        
        rows, cols = df.shape
        QMessageBox.information(self.parent, "Éxito",
            f"Carpeta cargada exitosamente.\n\n"
            f"Filas: {rows}, Columnas: {cols}")
        
        self.status_message.emit("Carpeta cargada exitosamente")
    
    # ==================== OPERACIONES DE JOIN ====================
    
    def abrir_cruzar_datos(self) -> None:
        """Abrir diálogo para cruzar datos"""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No hay datos cargados para cruzar.")
            return
        
        dialog = JoinDialog(self.data_service.datos_actuales, self.parent)
        dialog.join_completed.connect(self._on_join_completed)
        dialog.exec()
    
    def _on_join_completed(self, result: JoinResult, right_file_path: str | None) -> None:
        """Manejar resultado de join"""
        try:
            left_name = self.data_service.get_filename()
            right_name = (right_file_path and 
                        self._basename(right_file_path) or "Dataset Derecho")
            
            self.view_coordinator.set_join_result(result, left_name, right_name)
            
            if result.success and result.config:
                self.join_history.add_entry(left_name, right_name, 
                                           result.config, result)
            
            self.toolbar_manager.set_view_buttons_enabled(True)
            self.view_coordinator.switch_to(ViewRegistry.VIEW_JOIN)
            self.status_message.emit(
                f"Cruce completado: {result.metadata.result_rows} filas")
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", 
                               f"Error procesando resultado del join: {str(e)}")
    
    def _basename(self, path: str) -> str:
        """Obtener nombre de archivo sin ruta"""
        from pathlib import Path
        return Path(path).name
    
    # ==================== OPERACIONES DE PIVOTE ====================
    
    def abrir_pivot_simple(self) -> None:
        """Abrir diálogo de pivote simple"""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No hay datos cargados.")
            return
        
        dialog = SimplePivotDialog(self.data_service.datos_actuales, self.parent)
        if dialog.exec() == QMessageBox.Accepted:
            config = dialog.get_config()
            if config:
                self._procesar_pivot_simple(config)
    
    def _procesar_pivot_simple(self, config: Any) -> None:
        """Procesar pivote simple"""
        result = self.pivot_service.execute_simple(
            self.data_service.datos_actuales, config)
        
        if result is not None and not result.empty:
            self.data_service.set_current_data(result)
            self.view_coordinator.switch_to(ViewRegistry.VIEW_DATA)
            self.datos_actualizados.emit(self.data_service.datos_actuales)
            self.status_message.emit(f"Pivote simple: {len(result)} filas")
            QMessageBox.information(self.parent, "Éxito",
                f"Tabla pivote creada.\n\n"
                f"Dimensiones: {len(result)} filas x {len(result.columns)} columnas")
        else:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No se pudo crear la tabla pivote.")
    
    def abrir_pivot_combinada(self) -> None:
        """Abrir diálogo de pivote combinada"""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No hay datos cargados.")
            return
        
        dialog = PivotConfigDialog(self.data_service.datos_actuales, self.parent)
        if dialog.exec() == QMessageBox.Accepted:
            config = dialog.get_config()
            if config:
                self._procesar_pivot_combinada(config)
    
    def _procesar_pivot_combinada(self, config: Any) -> None:
        """Procesar pivote combinada"""
        result = self.pivot_service.execute_combined(
            self.data_service.datos_actuales, config)
        
        if result is not None and not result.empty:
            self.data_service.set_current_data(result)
            self.view_coordinator.switch_to(ViewRegistry.VIEW_DATA)
            self.datos_actualizados.emit(self.data_service.datos_actuales)
            self.status_message.emit(f"Pivote combinada: {len(result)} filas")
            QMessageBox.information(self.parent, "Éxito",
                f"Tabla pivote combinada creada.\n\n"
                f"Dimensiones: {len(result)} filas x {len(result.columns)} columnas")
        else:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No se pudo crear la tabla pivote.")
    
    def exportar_resultado_pivote(self) -> None:
        """Exportar resultado de pivote"""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No hay datos para exportar.")
            return
        self.export_service.show_export_dialog(
            self.data_service.datos_actuales, "Resultado_Pivote", parent=self.parent)
    
    # ==================== EXPORTACIÓN ====================
    
    def mostrar_info(self) -> None:
        """Mostrar el modal de información del archivo cargado"""
        df = self.data_service.datos_originales
        if df is not None:
            self.view_coordinator.show_info_modal(
                df, self.data_service.get_filename())
        else:
            QMessageBox.warning(self.parent, "Advertencia",
                              "No hay datos cargados.")

    def exportar_a_pdf(self) -> None:
        """Exportar a PDF"""
        self.export_service.export_to_pdf(self.data_service.datos_actuales, parent=self.parent)
    
    def exportar_a_xlsx(self) -> None:
        """Exportar a Excel"""
        self.export_service.export_to_xlsx(self.data_service.datos_actuales, parent=self.parent)
    
    def exportar_a_csv(self) -> None:
        """Exportar a CSV"""
        self.export_service.export_to_csv(self.data_service.datos_actuales, parent=self.parent)
    
    def exportar_a_sql(self) -> None:
        """Exportar a SQL"""
        self.export_service.export_to_sql(self.data_service.datos_actuales, parent=self.parent)
    
    def exportar_a_imagen(self) -> None:
        """Exportar a imagen"""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No hay datos para exportar.")
            return
        self.export_service.show_export_dialog(
            self.data_service.datos_actuales, "Exportacion_Imagen", parent=self.parent)
    
    def exportar_datos_separados(self) -> None:
        """Exportar datos separados"""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No hay datos para exportar.")
            return
        self.export_service.show_export_dialog(
            self.data_service.datos_actuales, "Exportacion_Separada", parent=self.parent)
    
    # ==================== FILTROS ====================
    
    def on_filter_applied(self, column: str, term: str) -> None:
        """Manejar filtro aplicado"""
        self.status_message.emit(
            f"Filtro aplicado en '{column}': '{term}'")
        self.datos_actualizados.emit(self.data_service.datos_actuales)
    
    def on_filter_cleared(self) -> None:
        """Manejar filtro limpiado"""
        self.status_message.emit("Filtro limpiado")
        self.datos_actualizados.emit(self.data_service.datos_actuales)
    
    def on_data_updated(self) -> None:
        """Manejar datos actualizados"""
        graphics_view = self.view_coordinator.get_graphics_view()
        data_view = self.view_coordinator.get_data_view()
        
        if graphics_view and data_view:
            current_page_data = data_view.export_current_page()
            if not current_page_data.empty:
                graphics_view.update_data(current_page_data)

    # ==================== CLEANUP ====================

    def cleanup(self) -> None:
        """Limpieza profunda de recursos, señales e historial."""
        # 1. Desconectar señales de manera segura
        for sig in (self.status_message, self.datos_originales_cargados,
                    self.datos_actualizados, self.datos_disponibles):
            try:
                sig.disconnect()
            except RuntimeError:
                pass

        # 2. Liberar join_history
        self.join_history = None  # type: ignore[assignment]

        # 3. Liberar referencias a componentes
        self.view_coordinator = None  # type: ignore[assignment]
        self.toolbar_manager = None  # type: ignore[assignment]

        # 4. Limpiar tareas pendientes del ThreadPool global
        from PySide6.QtCore import QThreadPool
        pool = QThreadPool.globalInstance()
        if pool is not None:
            pool.clear()

# Exports
__all__ = ['AppCoordinator']
