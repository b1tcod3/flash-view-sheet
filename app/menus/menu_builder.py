"""
Constructor de menús para Flash View Sheet.

Este módulo proporciona una interfaz unificada para construir
la barra de menús completa de la aplicación.
"""

from PySide6.QtWidgets import QMenuBar
from .menu_actions import MenuActions
from .archivo_menu import ArchivoMenu
from .datos_menu import DatosMenu
from .vista_menu import VistaMenu
from .exportar_menu import ExportarMenu
from typing import Any

class MenuBuilder:
    """
    Builder para crear la barra de menús completa.
    
    Usage:
        builder = MenuBuilder(parent_window)
        menubar = builder.build()
    """
    
    def __init__(self, parent_window: Any) -> None:
        """
        Inicializar el constructor de menús.
        
        Args:
            parent_window: Referencia a la ventana principal
        """
        self.parent_window = parent_window
        self.menu_bar = None
        
        # Referencias a menús para actualización posterior
        self.separar_menu = None
        self.datos_menu = None
        self.tabla_pivote_menu = None
        
    def build(self) -> QMenuBar:
        """
        Construir la barra de menús completa.
        
        Returns:
            QMenuBar: La barra de menús configurada
        """
        # Inicializar acciones
        MenuActions.initialize_actions(self.parent_window)
        
        # Crear barra de menús
        self.menu_bar = QMenuBar()
        
        # Construir cada menú
        self._build_archivo_menu()
        self._build_separar_menu()
        self._build_datos_menu()
        self._build_tabla_pivote_menu()
        self._build_vista_menu()
        self._build_ayuda_menu()
        
        # Conectar señales de acciones directamente a coordinator
        self._connect_actions(
            self.parent_window.coordinator,
            self.parent_window.view_coordinator,
        )
        
        return self.menu_bar
    
    def _build_archivo_menu(self) -> None:
        """Construir el menú Archivo."""
        ArchivoMenu.create(
            self.menu_bar,
            MenuActions.get_archivo_actions(),
            self.parent_window
        )
    
    def _build_separar_menu(self) -> None:
        """Construir el menú Separar."""
        from PySide6.QtWidgets import QMenu
        
        self.separar_menu = self.menu_bar.addMenu("&Separar")
        self.separar_menu.addAction(MenuActions.EXPORTAR_SEPARADO)
        
    def _build_datos_menu(self) -> None:
        """Construir el menú Datos."""
        DatosMenu.create(self.menu_bar, self.parent_window)
    
    def _build_tabla_pivote_menu(self) -> None:
        """Construir el menú Tabla Pivote."""
        from PySide6.QtWidgets import QMenu
        
        self.tabla_pivote_menu = self.menu_bar.addMenu("&Tabla Pivote")
        
        self.tabla_pivote_menu.addAction(MenuActions.PIVOT_SIMPLE)
        self.tabla_pivote_menu.addAction(MenuActions.PIVOT_COMBINADA)
        self.tabla_pivote_menu.addSeparator()
        self.tabla_pivote_menu.addAction(MenuActions.EXPORTAR_PIVOTE)
    
    def _build_vista_menu(self) -> None:
        """Construir el menú Vista."""
        VistaMenu.create(
            self.menu_bar,
            MenuActions.get_vista_actions(),
            self.parent_window
        )
    
    def _build_ayuda_menu(self) -> None:
        """Construir el menú Ayuda."""
        from PySide6.QtWidgets import QMenu
        
        ayuda_menu = self.menu_bar.addMenu("&Ayuda")
        ayuda_menu.addAction(MenuActions.ACERCA_DE)
    
    def _connect_actions(self, coordinator: Any, view_coordinator: Any) -> None:
        # Archivo
        MenuActions.ABRIR.triggered.connect(coordinator.solicitar_apertura_archivo)
        MenuActions.CARGAR_CARPETA.triggered.connect(coordinator.solicitar_carga_carpeta)
        MenuActions.EXPORTAR_PDF.triggered.connect(coordinator.exportar_a_pdf)
        MenuActions.EXPORTAR_IMAGEN.triggered.connect(coordinator.exportar_a_imagen)
        MenuActions.EXPORTAR_XLSX.triggered.connect(coordinator.exportar_a_xlsx)
        MenuActions.EXPORTAR_CSV.triggered.connect(coordinator.exportar_a_csv)
        MenuActions.EXPORTAR_SQL.triggered.connect(coordinator.exportar_a_sql)
        MenuActions.SALIR.triggered.connect(self.parent_window.close)

        # Separar
        MenuActions.EXPORTAR_SEPARADO.triggered.connect(coordinator.exportar_datos_separados)

        # Datos
        MenuActions.CRUZAR_DATOS.triggered.connect(coordinator.abrir_cruzar_datos)

        # Tabla Pivote
        MenuActions.PIVOT_SIMPLE.triggered.connect(coordinator.abrir_pivot_simple)
        MenuActions.PIVOT_COMBINADA.triggered.connect(coordinator.abrir_pivot_combinada)
        MenuActions.EXPORTAR_PIVOTE.triggered.connect(coordinator.exportar_resultado_pivote)

        # Vista
        MenuActions.VISTA_PRINCIPAL.triggered.connect(lambda: view_coordinator.switch_to(0))
        MenuActions.VISTA_DATOS.triggered.connect(lambda: view_coordinator.switch_to(1))
        MenuActions.VISTA_GRAFICOS.triggered.connect(lambda: view_coordinator.switch_to(2))
        MenuActions.VISTA_INFO.triggered.connect(coordinator.mostrar_info)

        # Ayuda
        MenuActions.ACERCA_DE.triggered.connect(self.parent_window.mostrar_acerca_de)
    
    def update_data_menus(self, has_data: bool) -> None:
        """
        Actualizar estado de menús que requieren datos.
        
        Args:
            has_data: True si hay datos cargados
        """
        MenuActions.enable_data_actions(has_data)
    
    def get_menu_references(self) -> dict[str, Any]:
        """
        Obtener referencias a los menús para uso externo.
        
        Returns:
            dict con referencias a los menús
        """
        return {
            'separar_menu': self.separar_menu,
            'datos_menu': self.datos_menu,
            'tabla_pivote_menu': self.tabla_pivote_menu,
        }
