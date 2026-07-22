"""
Flash View Sheet - Paquete Principal de la Aplicación

Este módulo export los componentes principales de la aplicación.
"""

# Menús
from app.menus import MenuBuilder

# Toolbar
from app.toolbar import ToolbarManager

# Servicios
from app.services import (
    DataService,
    ExportService,
    FilterService,
    PivotService,
)

# Widgets
from app.widgets import (
    MainView,
    InfoModal,
    DataView,
)

__version__ = "1.1.0"

__all__ = [
    # Menús
    'MenuBuilder',
    
    # Toolbar
    'ToolbarManager',
    
    # Servicios
    'DataService',
    'ExportService',
    'FilterService',
    'PivotService',
    
    # Widgets
    'MainView',
    'InfoModal',
    'DataView',
]
