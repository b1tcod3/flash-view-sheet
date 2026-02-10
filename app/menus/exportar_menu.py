"""
Submenú Exportar para Flash View Sheet.

Este módulo define la creación y configuración del submenú Exportar.
"""

from PySide6.QtWidgets import QMenu


class ExportarMenu:
    """
    Clase para crear y configurar el submenú Exportar.
    """
    
    @staticmethod
    def create(parent_menu, actions) -> QMenu:
        """
        Crear el submenú Exportar.
        
        Args:
            parent_menu: Menú padre donde se añadirá el submenú
            actions: Lista de acciones (incluye separadores None)
            
        Returns:
            QMenu: El submenú Exportar creado
        """
        exportar_menu = parent_menu.addMenu("&Exportar como...")
        
        for action in actions:
            if action is None:
                exportar_menu.addSeparator()
            else:
                exportar_menu.addAction(action)
        
        return exportar_menu
