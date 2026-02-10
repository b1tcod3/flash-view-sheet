"""
Menú Vista para Flash View Sheet.

Este módulo define la creación y configuración del menú Vista.
"""

from PySide6.QtWidgets import QMenu


class VistaMenu:
    """
    Clase para crear y configurar el menú Vista.
    """
    
    @staticmethod
    def create(menu_bar, actions, parent_window) -> QMenu:
        """
        Crear el menú Vista.
        
        Args:
            menu_bar: QMenuBar donde se añadirá el menú
            actions: Lista de acciones (incluye separadores None)
            parent_window: Referencia a la ventana principal
            
        Returns:
            QMenu: El menú Vista creado
        """
        vista_menu = menu_bar.addMenu("&Vista")
        
        for action in actions:
            if action is None:
                vista_menu.addSeparator()
            else:
                vista_menu.addAction(action)
        
        return vista_menu
