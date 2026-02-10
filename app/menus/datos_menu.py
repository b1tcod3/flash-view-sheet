"""
Menú Datos para Flash View Sheet.

Este módulo define la creación y configuración del menú Datos.
"""

from PySide6.QtWidgets import QMenu
from .menu_actions import MenuActions


class DatosMenu:
    """
    Clase para crear y configurar el menú Datos.
    """
    
    @staticmethod
    def create(menu_bar, parent_window) -> QMenu:
        """
        Crear el menú Datos.
        
        Args:
            menu_bar: QMenuBar donde se añadirá el menú
            parent_window: Referencia a la ventana principal
            
        Returns:
            QMenu: El menú Datos creado
        """
        datos_menu = menu_bar.addMenu("&Datos")
        datos_menu.addAction(MenuActions.CRUZAR_DATOS)
        
        return datos_menu
