#!/usr/bin/env python3
"""
Flash View Sheet - Visor de Datos Tabulares
Punto de entrada principal de la aplicación
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QToolBar

from core.join.join_history import JoinHistory

# Importar servicios y gestores
from app.services import DataService, ExportService, FilterService, PivotService
from app.toolbar import ToolbarManager
from app.view_manager import ViewCoordinator

# Importar coordinador de aplicación
from app.app_coordinator import AppCoordinator

# Importar menús
from app.menus import MenuActions


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación - Orquestador de componentes"""
    
    # Instance attributes
    data_service: DataService
    export_service: ExportService
    filter_service: FilterService
    pivot_service: PivotService
    toolbar_manager: ToolbarManager
    view_coordinator: ViewCoordinator
    coordinator: AppCoordinator
    join_history: Optional[JoinHistory]
    stacked_widget: QStackedWidget
    separar_menu: Optional[QObject]
    datos_menu: Optional[QObject]
    tabla_pivote_menu: Optional[QObject]
    exportar_separado_action: Optional[QAction]
    cruzar_datos_action: Optional[QAction]
    pivot_simple_action: Optional[QAction]
    pivot_combinada_action: Optional[QAction]
    export_pivot_action: Optional[QAction]
    
    def __init__(self) -> None:
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
    
    def _init_services(self) -> None:
        """Inicializar servicios centralizados"""
        self.data_service = DataService()
        self.export_service = ExportService(self)
        self.filter_service = FilterService()
        self.pivot_service = PivotService()
    
    def _init_toolbar(self) -> None:
        """Inicializar toolbar manager"""
        self.toolbar_manager = ToolbarManager(self)
    
    def _init_coordinator(self) -> None:
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
        self.join_history = JoinHistory()
        self.coordinator.join_history = self.join_history
        
        # Conectar señales del coordinator
        self.coordinator.status_message.connect(self.statusBar().showMessage)
    
    def _setup_ui(self) -> None:
        """Configurar la interfaz de usuario"""
        self._create_central_widget()
        self._create_views()
        self._create_menu_bar()
        self._add_toolbar()
        self.statusBar().showMessage("Listo para cargar datos")
    
    def _create_central_widget(self) -> None:
        """Crear widget central con stacked widget"""
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
    
    def _create_views(self) -> None:
        """Delegar creación de vistas al ViewCoordinator"""
        self.view_coordinator.create_views(self.stacked_widget)
        self.stacked_widget.addWidget(self.view_coordinator.get_stacked_widget())
    
    def _create_menu_bar(self) -> None:
        """Crear barra de menús"""
        from app.menus import MenuBuilder
        
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
    
    def _add_toolbar(self) -> None:
        """Añadir toolbar"""
        self.toolbar_manager.create_toolbar()
        self.addToolBar(self.toolbar_manager.get_toolbar())
    
    def _setup_connections(self) -> None:
        """Configurar conexiones de señales"""
        main_view = self.view_coordinator.get_main_view()
        data_view = self.view_coordinator.get_data_view()
        joined_view = self.view_coordinator.get_joined_data_view()
        
        if main_view:
            main_view.load_file_clicked.connect(self.coordinator.solicitar_apertura_archivo)
            main_view.reload_with_options.connect(self._on_reload_with_options)
        
        if data_view:
            data_view.filter_applied.connect(self.coordinator.on_filter_applied)
            data_view.filter_cleared.connect(self.coordinator.on_filter_cleared)
            data_view.data_updated.connect(self.coordinator.on_data_updated)
        
        if joined_view:
            joined_view.new_join_requested.connect(self.coordinator.abrir_cruzar_datos)
        
        # Conectar señales de datos del coordinator al ViewCoordinator
        self.coordinator.datos_originales_cargados.connect(
            self.view_coordinator.on_datos_originales_cargados)
        self.coordinator.datos_actualizados.connect(
            self.view_coordinator.on_datos_actualizados)
        
        # Conectar datos_disponibles a menús y toolbar (single source of truth)
        self.coordinator.datos_disponibles.connect(MenuActions.enable_data_actions)
        self.coordinator.datos_disponibles.connect(self.toolbar_manager.on_datos_disponibles)
    
    # ==================== DELEGADOS ====================
    
    def switch_view(self, index: int) -> bool:
        """Cambiar a la vista especificada"""
        return self.view_coordinator.switch_to(index)
    
    def show_info_modal(self) -> None:
        """Delegar modal de información al coordinador"""
        self.coordinator.mostrar_info()
    
    # ==================== GESTIÓN DE CARGA ====================
    
    def abrir_archivo(self) -> None:
        """Delegar apertura de archivo al coordinador"""
        self.coordinator.solicitar_apertura_archivo()
    
    def _on_reload_with_options(self, filepath: str, skip_rows: int, column_names: Dict[str, str], enable_column_visibility: bool = True) -> None:
        """Manejar recarga con opciones"""
        self.coordinator.iniciar_carga_archivo(filepath, skip_rows, column_names, enable_column_visibility=enable_column_visibility)
    
    # ==================== CARGA DE CARPETA ====================
    
    def cargar_carpeta(self) -> None:
        """Delegar carga de carpeta al coordinador"""
        self.coordinator.solicitar_carga_carpeta()
    
    # ==================== OPERACIONES DELEGADAS ====================
    
    def abrir_cruzar_datos(self) -> None:
        """Abrir diálogo para cruzar datos"""
        self.coordinator.abrir_cruzar_datos()
    
    def abrir_pivot_simple(self) -> None:
        """Abrir diálogo de pivote simple"""
        self.coordinator.abrir_pivot_simple()
    
    def abrir_pivot_combinada(self) -> None:
        """Abrir diálogo de pivote combinada"""
        self.coordinator.abrir_pivot_combinada()
    
    def exportar_resultado_pivote(self) -> None:
        """Exportar resultado de pivote"""
        self.coordinator.exportar_resultado_pivote()
    
    def exportar_a_pdf(self) -> None:
        """Exportar a PDF"""
        self.coordinator.exportar_a_pdf()
    
    def exportar_a_xlsx(self) -> None:
        """Exportar a Excel"""
        self.coordinator.exportar_a_xlsx()
    
    def exportar_a_csv(self) -> None:
        """Exportar a CSV"""
        self.coordinator.exportar_a_csv()
    
    def exportar_a_sql(self) -> None:
        """Exportar a SQL"""
        self.coordinator.exportar_a_sql()
    
    def exportar_a_imagen(self) -> None:
        """Exportar a imagen"""
        self.coordinator.exportar_a_imagen()
    
    def exportar_datos_separados(self) -> None:
        """Exportar datos separados"""
        self.coordinator.exportar_datos_separados()
    
    # ==================== ACERCA DE ====================
    
    def mostrar_acerca_de(self) -> None:
        """Mostrar diálogo Acerca de"""
        from app.widgets.about_dialog import AboutDialog
        AboutDialog.show_about(self)
    
    # ==================== EVENTOS ====================
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """Manejar cierre de aplicación con limpieza ordenada."""
        # 1. Detener threads y liberar DataFrames grandes
        self.data_service.cleanup()
        self.pivot_service.cleanup()
        
        # 2. Desconectar coordinator y liberar vistas
        self.coordinator.cleanup()
        self.view_coordinator.cleanup()
        
        event.accept()


def main() -> None:
    """Función principal de la aplicación"""
    app = QApplication(sys.argv)
    
    # Configurar icono
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    if logo_path.exists():
        app.setWindowIcon(QIcon(str(logo_path)))
    
    # Crear y mostrar ventana
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
