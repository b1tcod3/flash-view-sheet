"""
Acciones de menú centralizadas para Flash View Sheet.

Este módulo define todas las acciones de menú que se utilizan
en la aplicación, permitiendo su reutilización y mantenimiento centralizado.
"""

from PySide6.QtGui import QAction
from PySide6.QtCore import Qt


class MenuActions:
    """
    Clase estática que proporciona acceso a todas las acciones de menú.
    
    Uso:
        action = MenuActions.ABRIR
        action.triggered.connect(callback)
    """
    
    # === Menú Archivo ===
    ABRIR = None
    CARGAR_CARPETA = None
    EXPORTAR_PDF = None
    EXPORTAR_IMAGEN = None
    EXPORTAR_XLSX = None
    EXPORTAR_CSV = None
    EXPORTAR_SQL = None
    SALIR = None
    
    # === Menú Separar ===
    EXPORTAR_SEPARADO = None
    
    # === Menú Datos ===
    CRUZAR_DATOS = None
    
    # === Menú Tabla Pivote ===
    PIVOT_SIMPLE = None
    PIVOT_COMBINADA = None
    EXPORTAR_PIVOTE = None
    
    # === Menú Vista ===
    VISTA_PRINCIPAL = None
    VISTA_DATOS = None
    VISTA_INFO = None
    VISTA_GRAFICOS = None
    
    # === Menú Ayuda ===
    ACERCA_DE = None
    
    @classmethod
    def initialize_actions(cls, parent_window):
        """
        Inicializar todas las acciones con referencias al ventana padre.
        
        Args:
            parent_window: Referencia a la ventana principal (MainWindow)
        """
        # === Menú Archivo ===
        cls.ABRIR = QAction("&Abrir...", parent_window)
        cls.ABRIR.setShortcut("Ctrl+O")
        cls.ABRIR.setStatusTip("Abrir archivo de datos")
        
        cls.CARGAR_CARPETA = QAction("&Cargar Carpeta...", parent_window)
        cls.CARGAR_CARPETA.setShortcut("Ctrl+Shift+O")
        cls.CARGAR_CARPETA.setStatusTip("Cargar y consolidar carpeta de archivos Excel")
        
        cls.EXPORTAR_PDF = QAction("&PDF...", parent_window)
        cls.EXPORTAR_PDF.setShortcut("Ctrl+P")
        cls.EXPORTAR_PDF.setStatusTip("Exportar datos a formato PDF")
        
        cls.EXPORTAR_IMAGEN = QAction("&Imagen...", parent_window)
        cls.EXPORTAR_IMAGEN.setShortcut("Ctrl+I")
        cls.EXPORTAR_IMAGEN.setStatusTip("Exportar vista actual como imagen")
        
        cls.EXPORTAR_XLSX = QAction("&XLSX...", parent_window)
        cls.EXPORTAR_XLSX.setShortcut("Ctrl+X")
        cls.EXPORTAR_XLSX.setStatusTip("Exportar datos a formato Excel")
        
        cls.EXPORTAR_CSV = QAction("&CSV...", parent_window)
        cls.EXPORTAR_CSV.setShortcut("Ctrl+C")
        cls.EXPORTAR_CSV.setStatusTip("Exportar datos a formato CSV")
        
        cls.EXPORTAR_SQL = QAction("&SQL...", parent_window)
        cls.EXPORTAR_SQL.setShortcut("Ctrl+S")
        cls.EXPORTAR_SQL.setStatusTip("Exportar datos a base de datos SQLite")
        
        cls.SALIR = QAction("&Salir", parent_window)
        cls.SALIR.setShortcut("Ctrl+Q")
        cls.SALIR.setStatusTip("Cerrar la aplicación")
        
        # === Menú Separar ===
        cls.EXPORTAR_SEPARADO = QAction("&Exportar Datos Separados...", parent_window)
        cls.EXPORTAR_SEPARADO.setShortcut("Ctrl+Shift+S")
        cls.EXPORTAR_SEPARADO.setStatusTip("Exportar datos separados por columna usando plantillas Excel")
        cls.EXPORTAR_SEPARADO.setEnabled(False)
        
        # === Menú Datos ===
        cls.CRUZAR_DATOS = QAction("&Cruzar Datos...", parent_window)
        cls.CRUZAR_DATOS.setShortcut("Ctrl+Shift+J")
        cls.CRUZAR_DATOS.setStatusTip("Cruzar datos con otro dataset usando operaciones de join")
        cls.CRUZAR_DATOS.setEnabled(False)
        
        # === Menú Tabla Pivote ===
        cls.PIVOT_SIMPLE = QAction("&Simple...", parent_window)
        cls.PIVOT_SIMPLE.setShortcut("Ctrl+Alt+S")
        cls.PIVOT_SIMPLE.setStatusTip("Crear tabla pivote simple")
        cls.PIVOT_SIMPLE.setEnabled(False)
        
        cls.PIVOT_COMBINADA = QAction("&Combinada...", parent_window)
        cls.PIVOT_COMBINADA.setShortcut("Ctrl+Alt+C")
        cls.PIVOT_COMBINADA.setStatusTip("Crear tabla pivote combinada")
        cls.PIVOT_COMBINADA.setEnabled(False)
        
        cls.EXPORTAR_PIVOTE = QAction("&Exportar Datos Actuales...", parent_window)
        cls.EXPORTAR_PIVOTE.setShortcut("Ctrl+Alt+E")
        cls.EXPORTAR_PIVOTE.setStatusTip("Exportar los datos que se muestran actualmente")
        cls.EXPORTAR_PIVOTE.setEnabled(False)
        
        # === Menú Vista ===
        cls.VISTA_PRINCIPAL = QAction("&Vista Principal", parent_window)
        cls.VISTA_PRINCIPAL.setShortcut("Ctrl+1")
        cls.VISTA_PRINCIPAL.setStatusTip("Cambiar a la vista principal")
        
        cls.VISTA_DATOS = QAction("&Vista de Datos", parent_window)
        cls.VISTA_DATOS.setShortcut("Ctrl+2")
        cls.VISTA_DATOS.setStatusTip("Cambiar a la vista de datos")
        
        cls.VISTA_INFO = QAction("&Ver Información del dataset", parent_window)
        cls.VISTA_INFO.setShortcut("Ctrl+I")
        cls.VISTA_INFO.setStatusTip("Mostrar información del dataset actual")
        
        cls.VISTA_GRAFICOS = QAction("&Vista Gráficos", parent_window)
        cls.VISTA_GRAFICOS.setShortcut("Ctrl+G")
        cls.VISTA_GRAFICOS.setStatusTip("Cambiar a la vista de gráficos")
        
        # === Menú Ayuda ===
        cls.ACERCA_DE = QAction("&Acerca de...", parent_window)
        cls.ACERCA_DE.setShortcut("F1")
        cls.ACERCA_DE.setStatusTip("Mostrar información sobre la aplicación")
    
    @classmethod
    def enable_data_actions(cls, enable: bool = True):
        """Habilitar/deshabilitar acciones que requieren datos cargados."""
        actions = [
            cls.EXPORTAR_SEPARADO,
            cls.CRUZAR_DATOS,
            cls.PIVOT_SIMPLE,
            cls.PIVOT_COMBINADA,
            cls.EXPORTAR_PIVOTE,
        ]
        for action in actions:
            if action:
                action.setEnabled(enable)
    
    @classmethod
    def get_archivo_actions(cls):
        """Obtener lista de acciones del menú Archivo."""
        return [
            cls.ABRIR,
            cls.CARGAR_CARPETA,
            None,  # Separador
            cls.EXPORTAR_PDF,
            cls.EXPORTAR_IMAGEN,
            cls.EXPORTAR_XLSX,
            cls.EXPORTAR_CSV,
            cls.EXPORTAR_SQL,
            None,  # Separador
            cls.SALIR,
        ]
    
    @classmethod
    def get_exportar_actions(cls):
        """Obtener lista de acciones del submenú Exportar."""
        return [
            cls.EXPORTAR_PDF,
            cls.EXPORTAR_IMAGEN,
            cls.EXPORTAR_XLSX,
            cls.EXPORTAR_CSV,
            cls.EXPORTAR_SQL,
        ]
    
    @classmethod
    def get_vista_actions(cls):
        """Obtener lista de acciones del menú Vista."""
        return [
            cls.VISTA_PRINCIPAL,
            cls.VISTA_DATOS,
            cls.VISTA_INFO,
            cls.VISTA_GRAFICOS,
        ]
