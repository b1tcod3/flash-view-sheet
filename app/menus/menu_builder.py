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


class MenuBuilder:
    """
    Builder para crear la barra de menús completa.
    
    Usage:
        builder = MenuBuilder(parent_window)
        menubar = builder.build()
    """
    
    def __init__(self, parent_window):
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
        
        # Conectar señales de acciones a slots del parent
        self._connect_actions()
        
        return self.menu_bar
    
    def _build_archivo_menu(self):
        """Construir el menú Archivo."""
        ArchivoMenu.create(
            self.menu_bar,
            MenuActions.get_archivo_actions(),
            self.parent_window
        )
    
    def _build_separar_menu(self):
        """Construir el menú Separar."""
        from PySide6.QtWidgets import QMenu
        
        self.separar_menu = self.menu_bar.addMenu("&Separar")
        self.separar_menu.addAction(MenuActions.EXPORTAR_SEPARADO)
        
    def _build_datos_menu(self):
        """Construir el menú Datos."""
        DatosMenu.create(self.menu_bar, self.parent_window)
    
    def _build_tabla_pivote_menu(self):
        """Construir el menú Tabla Pivote."""
        from PySide6.QtWidgets import QMenu
        
        self.tabla_pivote_menu = self.menu_bar.addMenu("&Tabla Pivote")
        
        self.tabla_pivote_menu.addAction(MenuActions.PIVOT_SIMPLE)
        self.tabla_pivote_menu.addAction(MenuActions.PIVOT_COMBINADA)
        self.tabla_pivote_menu.addSeparator()
        self.tabla_pivote_menu.addAction(MenuActions.EXPORTAR_PIVOTE)
    
    def _build_vista_menu(self):
        """Construir el menú Vista."""
        VistaMenu.create(
            self.menu_bar,
            MenuActions.get_vista_actions(),
            self.parent_window
        )
    
    def _build_ayuda_menu(self):
        """Construir el menú Ayuda."""
        from PySide6.QtWidgets import QMenu
        
        ayuda_menu = self.menu_bar.addMenu("&Ayuda")
        ayuda_menu.addAction(MenuActions.ACERCA_DE)
    
    def _connect_actions(self):
        """Conectar acciones a los slots del parent window."""
        # Archivo
        MenuActions.ABRIR.triggered.connect(self.parent_window.abrir_archivo)
        MenuActions.CARGAR_CARPETA.triggered.connect(self.parent_window.cargar_carpeta)
        MenuActions.EXPORTAR_PDF.triggered.connect(self.parent_window.exportar_a_pdf)
        MenuActions.EXPORTAR_IMAGEN.triggered.connect(self.parent_window.exportar_a_imagen)
        MenuActions.EXPORTAR_XLSX.triggered.connect(self.parent_window.exportar_a_xlsx)
        MenuActions.EXPORTAR_CSV.triggered.connect(self.parent_window.exportar_a_csv)
        MenuActions.EXPORTAR_SQL.triggered.connect(self.parent_window.exportar_a_sql)
        MenuActions.SALIR.triggered.connect(self.parent_window.close)
        
        # Separar
        MenuActions.EXPORTAR_SEPARADO.triggered.connect(
            self.parent_window.exportar_datos_separados
        )
        
        # Datos
        MenuActions.CRUZAR_DATOS.triggered.connect(self.parent_window.abrir_cruzar_datos)
        
        # Tabla Pivote
        MenuActions.PIVOT_SIMPLE.triggered.connect(self.parent_window.abrir_pivot_simple)
        MenuActions.PIVOT_COMBINADA.triggered.connect(
            self.parent_window.abrir_pivot_combinada
        )
        MenuActions.EXPORTAR_PIVOTE.triggered.connect(
            self.parent_window.exportar_resultado_pivote
        )
        
        # Vista
        MenuActions.VISTA_PRINCIPAL.triggered.connect(
            lambda: self.parent_window.switch_view(0)
        )
        MenuActions.VISTA_DATOS.triggered.connect(
            lambda: self.parent_window.switch_view(1)
        )
        MenuActions.VISTA_INFO.triggered.connect(self.parent_window.show_info_modal)
        MenuActions.VISTA_GRAFICOS.triggered.connect(
            lambda: self.parent_window.switch_view(2)
        )
        
        # Ayuda
        MenuActions.ACERCA_DE.triggered.connect(self.parent_window.mostrar_acerca_de)
    
    def update_data_menus(self, has_data: bool):
        """
        Actualizar estado de menús que requieren datos.
        
        Args:
            has_data: True si hay datos cargados
        """
        MenuActions.enable_data_actions(has_data)
    
    def get_menu_references(self) -> dict:
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
