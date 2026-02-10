#!/usr/bin/env python3
"""
Flash View Sheet - Visor de Datos Tabulares
Punto de entrada principal de la aplicación
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, 
                               QFileDialog)
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon

# Importar servicios y gestores
from app.services import DataService, ExportService, FilterService, PivotService
from app.toolbar import ToolbarManager
from app.view_manager import ViewCoordinator

# Importar coordinador de aplicación
from app.app_coordinator import AppCoordinator

# Importar diálogos
from app.widgets import FolderLoadDialog, InfoModal


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación - Orquestador de componentes"""
    
    # Señales re-exportadas para compatibilidad
    reload_with_options = Signal(str, int, dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flash View Sheet - Visor de Datos Tabulares")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)
        
        # Inicializar servicios
        self._init_services()
        
        # Inicializar gestor de toolbar
        self._init_toolbar()
        
        # Inicializar coordinador de aplicación
        self._init_coordinator()
        
        # Configurar UI
        self._setup_ui()
        self._setup_connections()
        
        print(f"DEBUG: MainWindow initialized with size {self.size()}")
    
    # ==================== INICIALIZACIÓN ====================
    
    def _init_services(self):
        """Inicializar servicios centralizados"""
        self.data_service = DataService()
        self.export_service = ExportService(self)
        self.filter_service = FilterService()
        self.pivot_service = PivotService()
    
    def _init_toolbar(self):
        """Inicializar toolbar manager"""
        self.toolbar_manager = ToolbarManager(self)
    
    def _init_coordinator(self):
        """Inicializar coordinador de aplicación"""
        # View Coordinator
        self.view_coordinator = ViewCoordinator(self)
        
        # AppCoordinator con todas las dependencias
        self.coordinator = AppCoordinator(
            parent_window=self,
            data_service=self.data_service,
            export_service=self.export_service,
            pivot_service=self.pivot_service,
            view_coordinator=self.view_coordinator,
            toolbar_manager=self.toolbar_manager,
            join_history=None  # Se inicializa después
        )
        
        # Inicializar JoinHistory después del coordinator
        from core.join.join_history import JoinHistory
        self.join_history = JoinHistory
        self.coordinator.join_history = JoinHistory()
        
        # Conectar señales del coordinator
        self.coordinator.status_message.connect(self.statusBar().showMessage)
    
    def _setup_ui(self):
        """Configurar la interfaz de usuario"""
        self._create_central_widget()
        self._create_views()
        self._create_menu_bar()
        self._add_toolbar()
        self.statusBar().showMessage("Listo para cargar datos")
    
    def _create_central_widget(self):
        """Crear widget central con stacked widget"""
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
    
    def _create_views(self):
        """Delegar creación de vistas al ViewCoordinator"""
        self.view_coordinator.create_views(self.stacked_widget)
        self.stacked_widget.addWidget(self.view_coordinator.get_stacked_widget())
    
    def _create_menu_bar(self):
        """Crear barra de menús"""
        from app.menus import MenuBuilder, MenuActions
        
        menu_builder = MenuBuilder(self)
        menu_builder.build()
        
        refs = menu_builder.get_menu_references()
        self.separar_menu = refs.get('separar_menu')
        self.datos_menu = refs.get('datos_menu')
        self.tabla_pivote_menu = refs.get('tabla_pivote_menu')
        
        self.exportar_separado_action = MenuActions.EXPORTAR_SEPARADO
        self.cruzar_datos_action = MenuActions.CRUZAR_DATOS
        self.pivot_simple_action = MenuActions.PIVOT_SIMPLE
        self.pivot_combinada_action = MenuActions.PIVOT_COMBINADA
        self.export_pivot_action = MenuActions.EXPORTAR_PIVOTE
    
    def _add_toolbar(self):
        """Añadir toolbar"""
        self.toolbar_manager.create_toolbar()
        self.addToolBar(self.toolbar_manager.get_toolbar())
    
    def _setup_connections(self):
        """Configurar conexiones de señales"""
        main_view = self.view_coordinator.get_main_view()
        data_view = self.view_coordinator.get_data_view()
        joined_view = self.view_coordinator.get_joined_data_view()
        
        if main_view:
            main_view.file_loaded.connect(self._on_file_loaded)
            main_view.reload_with_options.connect(self._on_reload_with_options)
        
        if data_view:
            data_view.filter_applied.connect(self.coordinator.on_filter_applied)
            data_view.filter_cleared.connect(self.coordinator.on_filter_cleared)
            data_view.data_updated.connect(self.coordinator.on_data_updated)
        
        if joined_view:
            joined_view.new_join_requested.connect(self.coordinator.abrir_cruzar_datos)
    
    # ==================== PROPIEDADES DE COMPATIBILIDAD ====================
    
    @property
    def df_original(self):
        return self.data_service.datos_originales
    
    @df_original.setter
    def df_original(self, value):
        self.data_service.df_original = value
    
    @property
    def df_vista_actual(self):
        return self.data_service.datos_actuales
    
    @df_vista_actual.setter
    def df_vista_actual(self, value):
        self.data_service.datos_vista_actual = value
    
    # ==================== DELEGADOS ====================
    
    def switch_view(self, index):
        """Cambiar a la vista especificada"""
        return self.view_coordinator.switch_to(index)
    
    def show_info_modal(self):
        """Mostrar el modal de información"""
        if self.df_original is not None:
            info_modal = InfoModal(self)
            info_modal.update_info(self.df_original, self.data_service.get_filename())
            info_modal.exec()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Advertencia", "No hay datos cargados.")
    
    # ==================== GESTIÓN DE CARGA ====================
    
    def abrir_archivo(self):
        """Abrir diálogo para cargar archivo"""
        file_filter = self.data_service.get_file_filter()
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo de datos", "", file_filter)
        
        if filepath:
            self._mostrar_loading_indicator(filepath)
    
    def _on_file_loaded(self, filepath, skip_rows=0, column_names=None):
        """Manejar carga de archivo"""
        self._mostrar_loading_indicator(filepath, skip_rows, column_names or {})
    
    def _on_reload_with_options(self, filepath, skip_rows, column_names, enable_vis):
        """Manejar recarga con opciones"""
        self._mostrar_loading_indicator(filepath, skip_rows, column_names)
    
    def _mostrar_loading_indicator(self, filepath, skip_rows=0, column_names=None):
        """Mostrar indicador de carga"""
        progress = self.data_service.create_progress_dialog(
            "Cargando datos", "Cargando archivo..."
        )
        progress.show()
        
        thread = self.data_service.create_loader_thread(filepath, skip_rows, column_names)
        thread.data_loaded.connect(self.coordinator.on_datos_cargados)
        thread.error_occurred.connect(self.coordinator.on_error_carga)
        thread.start()
    
    # ==================== CARGA DE CARPETA ====================
    
    def cargar_carpeta(self):
        """Abrir diálogo para cargar carpeta"""
        dialog = FolderLoadDialog(self)
        if dialog.exec():
            config = dialog.get_config()
            if config and config.folder_path:
                self.coordinator.procesar_carga_carpeta(config)
    
    # ==================== OPERACIONES DELEGADAS ====================
    
    def abrir_cruzar_datos(self):
        """Abrir diálogo para cruzar datos"""
        self.coordinator.abrir_cruzar_datos()
    
    def abrir_pivot_simple(self):
        """Abrir diálogo de pivote simple"""
        self.coordinator.abrir_pivot_simple()
    
    def abrir_pivot_combinada(self):
        """Abrir diálogo de pivote combinada"""
        self.coordinator.abrir_pivot_combinada()
    
    def exportar_resultado_pivote(self):
        """Exportar resultado de pivote"""
        self.coordinator.exportar_resultado_pivote()
    
    def exportar_a_pdf(self):
        """Exportar a PDF"""
        self.coordinator.exportar_a_pdf()
    
    def exportar_a_xlsx(self):
        """Exportar a Excel"""
        self.coordinator.exportar_a_xlsx()
    
    def exportar_a_csv(self):
        """Exportar a CSV"""
        self.coordinator.exportar_a_csv()
    
    def exportar_a_sql(self):
        """Exportar a SQL"""
        self.coordinator.exportar_a_sql()
    
    def exportar_a_imagen(self):
        """Exportar a imagen"""
        self.coordinator.exportar_a_imagen()
    
    def exportar_datos_separados(self):
        """Exportar datos separados"""
        self.coordinator.exportar_datos_separados()
    
    # ==================== ACERCA DE ====================
    
    def mostrar_acerca_de(self):
        """Mostrar diálogo Acerca de"""
        from app.widgets.about_dialog import AboutDialog
        AboutDialog.show_about(self)
    
    # ==================== EVENTOS ====================
    
    def closeEvent(self, event):
        """Manejar cierre de aplicación"""
        self.data_service.cleanup()
        event.accept()


def main():
    """Función principal de la aplicación"""
    app = QApplication(sys.argv)
    
    # Configurar icono
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.exists(logo_path):
        app.setWindowIcon(QIcon(logo_path))
    
    # Crear y mostrar ventana
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
