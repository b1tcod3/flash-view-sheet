"""
AppCoordinator - Orquestador de la aplicación

Coordinador central que maneja la lógica de negocio y la orquestación
entre servicios, diálogos y vistas.
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox

from app.services import DataService, ExportService, PivotService
from app.view_manager import ViewCoordinator, ViewRegistry
from app.toolbar import ToolbarManager
from app.widgets import JoinDialog, SimplePivotDialog, PivotConfigDialog


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
    data_loaded = Signal(object)
    
    def __init__(self, parent_window, data_service, export_service, 
                 pivot_service, view_coordinator, toolbar_manager, join_history):
        """Inicializar el coordinador"""
        super().__init__(parent_window)
        
        self.parent = parent_window
        self.data_service = data_service
        self.export_service = export_service
        self.pivot_service = pivot_service
        self.view_coordinator = view_coordinator
        self.toolbar_manager = toolbar_manager
        self.join_history = join_history
    
    # ==================== CALLBACKS DE DATOS ====================
    
    def on_datos_cargados(self, df):
        """Manejar datos cargados exitosamente"""
        self.data_service.close_progress_dialog()
        self.data_service.set_current_data(df)
        
        # Actualizar vistas
        self.view_coordinator.update_data_view(df)
        self.view_coordinator.update_graphics_view(df)
        self.view_coordinator.update_main_view(self.data_service.get_filepath())
        
        # Actualizar estado UI
        self._actualizar_ui_post_carga()
        self._actualizar_menus()
        
        # Cambiar a vista de datos
        self.view_coordinator.switch_to(ViewRegistry.VIEW_DATA)
        self.status_message.emit(f"Datos cargados: {self.data_service.get_filename()}")
    
    def on_error_carga(self, error_message):
        """Manejar error de carga"""
        self.data_service.close_progress_dialog()
        QMessageBox.critical(self.parent, "Error", 
                           f"No se pudo cargar el archivo: {error_message}")
    
    def _actualizar_ui_post_carga(self):
        """Actualizar UI después de cargar datos"""
        data_view = self.view_coordinator.get_data_view()
        main_view = self.view_coordinator.get_main_view()
        
        if data_view:
            data_view.set_data(self.data_service.datos_actuales)
        if main_view:
            main_view.set_file_info(self.data_service.get_filepath())
            main_view.show_options_button()
    
    def _actualizar_menus(self):
        """Actualizar estado de menús"""
        enabled = self.data_service.has_data
        parent = self.parent
        
        if hasattr(parent, 'exportar_separado_action') and parent.exportar_separado_action:
            parent.exportar_separado_action.setEnabled(enabled)
        if hasattr(parent, 'cruzar_datos_action') and parent.cruzar_datos_action:
            parent.cruzar_datos_action.setEnabled(enabled)
        if hasattr(parent, 'pivot_simple_action') and parent.pivot_simple_action:
            parent.pivot_simple_action.setEnabled(enabled)
        if hasattr(parent, 'pivot_combinada_action') and parent.pivot_combinada_action:
            parent.pivot_combinada_action.setEnabled(enabled)
        if hasattr(parent, 'export_pivot_action') and parent.export_pivot_action:
            parent.export_pivot_action.setEnabled(enabled)
    
    # ==================== CARGA DE CARPETA ====================
    
    def procesar_carga_carpeta(self, config):
        """Procesar carga de carpeta"""
        try:
            df = self.data_service.load_folder(config.folder_path, config)
            
            self.view_coordinator.update_data_view(df)
            self.view_coordinator.update_graphics_view(df)
            self._actualizar_menus()
            self.view_coordinator.switch_to(ViewRegistry.VIEW_DATA)
            
            QMessageBox.information(self.parent, "Éxito",
                f"Carpeta cargada exitosamente.\n\n"
                f"Archivos procesados: {self.data_service.get_data_shape()[0]}\n"
                f"Filas: {len(df)}, Columnas: {len(df.columns)}")
                
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", 
                               f"Error procesando carga de carpeta: {str(e)}")
    
    # ==================== OPERACIONES DE JOIN ====================
    
    def abrir_cruzar_datos(self):
        """Abrir diálogo para cruzar datos"""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No hay datos cargados para cruzar.")
            return
        
        dialog = JoinDialog(self.data_service.datos_actuales, self.parent)
        dialog.join_completed.connect(self._on_join_completed)
        dialog.exec()
    
    def _on_join_completed(self, result, right_file_path):
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
    
    def _basename(self, path):
        """Obtener nombre de archivo sin ruta"""
        import os
        return os.path.basename(path)
    
    # ==================== OPERACIONES DE PIVOTE ====================
    
    def abrir_pivot_simple(self):
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
    
    def _procesar_pivot_simple(self, config):
        """Procesar pivote simple"""
        result = self.pivot_service.execute_simple(
            self.data_service.datos_actuales, config)
        
        if result is not None and not result.empty:
            self.data_service.set_current_data(result)
            self.view_coordinator.update_data_view(result)
            self.view_coordinator.switch_to(ViewRegistry.VIEW_DATA)
            self.status_message.emit(f"Pivote simple: {len(result)} filas")
            QMessageBox.information(self.parent, "Éxito",
                f"Tabla pivote creada.\n\n"
                f"Dimensiones: {len(result)} filas x {len(result.columns)} columnas")
        else:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No se pudo crear la tabla pivote.")
    
    def abrir_pivot_combinada(self):
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
    
    def _procesar_pivot_combinada(self, config):
        """Procesar pivote combinada"""
        result = self.pivot_service.execute_combined(
            self.data_service.datos_actuales, config)
        
        if result is not None and not result.empty:
            self.data_service.set_current_data(result)
            self.view_coordinator.update_data_view(result)
            self.view_coordinator.switch_to(ViewRegistry.VIEW_DATA)
            self.status_message.emit(f"Pivote combinada: {len(result)} filas")
            QMessageBox.information(self.parent, "Éxito",
                f"Tabla pivote combinada creada.\n\n"
                f"Dimensiones: {len(result)} filas x {len(result.columns)} columnas")
        else:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No se pudo crear la tabla pivote.")
    
    def exportar_resultado_pivote(self):
        """Exportar resultado de pivote"""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No hay datos para exportar.")
            return
        self.export_service.show_export_dialog(
            self.data_service.datos_actuales, "Resultado_Pivote")
    
    # ==================== EXPORTACIÓN ====================
    
    def exportar_a_pdf(self):
        """Exportar a PDF"""
        self.export_service.export_to_pdf(self.data_service.datos_actuales)
    
    def exportar_a_xlsx(self):
        """Exportar a Excel"""
        self.export_service.export_to_xlsx(self.data_service.datos_actuales)
    
    def exportar_a_csv(self):
        """Exportar a CSV"""
        self.export_service.export_to_csv(self.data_service.datos_actuales)
    
    def exportar_a_sql(self):
        """Exportar a SQL"""
        self.export_service.export_to_sql(self.data_service.datos_actuales)
    
    def exportar_a_imagen(self):
        """Exportar a imagen"""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No hay datos para exportar.")
            return
        self.export_service.show_export_dialog(
            self.data_service.datos_actuales, "Exportacion_Imagen")
    
    def exportar_datos_separados(self):
        """Exportar datos separados"""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent, "Advertencia", 
                              "No hay datos para exportar.")
            return
        self.export_service.show_export_dialog(
            self.data_service.datos_actuales, "Exportacion_Separada")
    
    # ==================== FILTROS ====================
    
    def on_filter_applied(self, column, term):
        """Manejar filtro aplicado"""
        self.status_message.emit(
            f"Filtro aplicado en '{column}': '{term}'")
    
    def on_filter_cleared(self):
        """Manejar filtro limpiado"""
        self.status_message.emit("Filtro limpiado")
    
    def on_data_updated(self):
        """Manejar datos actualizados"""
        graphics_view = self.view_coordinator.get_graphics_view()
        data_view = self.view_coordinator.get_data_view()
        
        if graphics_view and data_view:
            current_page_data = data_view.export_current_page()
            if not current_page_data.empty:
                graphics_view.update_data(current_page_data)


# Exports
__all__ = ['AppCoordinator']
