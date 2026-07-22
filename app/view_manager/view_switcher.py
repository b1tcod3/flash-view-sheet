"""
View Switcher

Maneja la lógica de cambio entre vistas.
Provides methods to switch between different views in the application.
"""

from PySide6.QtCore import Signal, QObject


class ViewSwitcher(QObject):
    """Manejador de cambio de vistas"""
    
    # Señales
    view_changed = Signal(int)  # Emitido cuando cambia la vista
    view_about_to_change = Signal(int, int)  # (vista_actual, vista_nueva)
    
    def __init__(self, stacked_widget=None):
        super().__init__()
        self._stacked_widget = stacked_widget
        self._current_view = 0
        self._current_registry_id = 0
        self._view_history = []
        self._index_to_registry: dict[int, int] = {}
    
    def set_stacked_widget(self, stacked_widget):
        """Establecer el widget stacked"""
        self._stacked_widget = stacked_widget
        if stacked_widget:
            self._current_view = stacked_widget.currentIndex()
    
    def set_index_mapping(self, index_to_registry: dict[int, int]) -> None:
        """Establecer mapeo de stacked index → ViewRegistry ID"""
        self._index_to_registry = index_to_registry
    
    def get_current_view(self) -> int:
        """Obtener índice de la vista actual"""
        if self._stacked_widget:
            return self._stacked_widget.currentIndex()
        return self._current_view
    
    def switch_to(self, index: int) -> bool:
        """Cambiar a la vista especificada
        
        Args:
            index: Índice del stacked widget a mostrar
            
        Returns:
            bool: True si el cambio fue exitoso
        """
        if not self._stacked_widget:
            return False
        
        if index < 0 or index >= self._stacked_widget.count():
            return False
        
        # Emitir señal antes del cambio
        self.view_about_to_change.emit(self._current_view, index)
        
        # Realizar el cambio
        self._stacked_widget.setCurrentIndex(index)
        self._current_view = index
        self._current_registry_id = self._index_to_registry.get(index, 0)
        self._view_history.append(index)
        
        # Limitar historial a 20 elementos
        if len(self._view_history) > 20:
            self._view_history.pop(0)
        
        # Emitir señal después del cambio
        self.view_changed.emit(index)
        
        return True
    
    def switch_to_main(self) -> bool:
        """Cambiar a la vista principal"""
        return self.switch_to(ViewRegistry.VIEW_MAIN)
    
    def switch_to_data(self) -> bool:
        """Cambiar a la vista de datos"""
        return self.switch_to(ViewRegistry.VIEW_DATA)
    
    def switch_to_join(self) -> bool:
        """Cambiar a la vista de join"""
        return self.switch_to(ViewRegistry.VIEW_JOIN)
    
    def switch_to_pivot(self) -> bool:
        """Cambiar a la vista de pivote"""
        return self.switch_to(ViewRegistry.VIEW_PIVOT)
    
    def get_view_name(self) -> str:
        """Obtener nombre de la vista actual"""
        from .view_registry import ViewRegistry
        return ViewRegistry.get_view_name(self._current_registry_id)
    
    def get_view_history(self) -> list:
        """Obtener historial de vistas visitadas"""
        return self._view_history.copy()
    
    def can_go_back(self) -> bool:
        """Verificar si se puede volver a la vista anterior"""
        return len(self._view_history) > 1
    
    def go_back(self) -> bool:
        """Volver a la vista anterior
        
        Returns:
            bool: True si se pudo volver
        """
        if not self.can_go_back():
            return False
        
        # Remover el actual del historial
        self._view_history.pop()
        # La vista anterior es el último elemento
        previous_view = self._view_history[-1]
        return self.switch_to(previous_view)
