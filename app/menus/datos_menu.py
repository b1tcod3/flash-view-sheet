"""
Menú Datos para Flash View Sheet.
"""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMenuBar
from typing import Any


class DatosMenu:
    """Clase para crear y configurar el menú Datos."""

    @staticmethod
    def create(menu_bar: QMenuBar, cruzar_datos_action: QAction) -> QMenu:
        datos_menu = menu_bar.addMenu("&Datos")
        datos_menu.addAction(cruzar_datos_action)
        return datos_menu
