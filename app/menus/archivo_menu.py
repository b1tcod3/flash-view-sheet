"""
Menú Archivo para Flash View Sheet.

Este módulo define la creación y configuración del menú Archivo.
"""

from PySide6.QtWidgets import QMenu


class ArchivoMenu:
    """
    Clase para crear y configurar el menú Archivo.
    """
    
    @staticmethod
    def create(menu_bar, actions, parent_window) -> QMenu:
        """
        Crear el menú Archivo.
        
        Args:
            menu_bar: QMenuBar donde se añadirá el menú
            actions: Lista de acciones (incluye separadores None)
            parent_window: Referencia a la ventana principal
            
        Returns:
            QMenu: El menú Archivo creado
        """
        archivo_menu = menu_bar.addMenu("&Archivo")
        
        for action in actions:
            if action is None:
                archivo_menu.addSeparator()
            else:
                archivo_menu.addAction(action)
        
        return archivo_menu
