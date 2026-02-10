"""
View Manager Module

Este módulo proporciona gestión centralizada de vistas para Flash View Sheet.

Componentes:
- ViewRegistry: Registro de vistas disponibles
- ViewSwitcher: Lógica de cambio entre vistas
- ViewCoordinator: Coordinator pattern para coordinación de estado
"""

from .view_registry import ViewRegistry
from .view_switcher import ViewSwitcher
from .view_coordinator import ViewCoordinator

__all__ = ['ViewRegistry', 'ViewSwitcher', 'ViewCoordinator']
