"""
View Switcher

Maneja la lógica de cambio entre vistas.
Provides methods to switch between different views in the application.
"""

from PySide6.QtCore import Signal, QObject
from .view_registry import ViewRegistry


class ViewSwitcher(QObject):
    """Manejador de cambio de vistas"""
    
    # Señales
    view_changed = Signal(int)  # Emitido cuando cambia la vista
    view_about_to_change = Signal(int, int)  # (vista_actual, vista_nueva)
    
    def __init__(self, stacked_widget=None):
        """Inicializar el switcher de vistas
        
        Args:
            stacked_widget: QStackedWidget que contiene las vistas
        """
        super().__init__()
        self._stacked_widget = stacked_widget
        self._current_view = ViewRegistry.VIEW_MAIN
        self._view_history = []
    
    def set_stacked_widget(self, stacked_widget):
        """Establecer el widget stacked
        
        Args:
            stacked_widget: QStackedWidget que contiene las vistas
        """
        self._stacked_widget = stacked_widget
        if stacked_widget:
            self._current_view = stacked_widget.currentIndex()
    
    def get_current_view(self) -> int:
        """Obtener índice de la vista actual"""
        if self._stacked_widget:
            return self._stacked_widget.currentIndex()
        return self._current_view
    
    def switch_to(self, index: int) -> bool:
        """Cambiar a la vista especificada
        
        Args:
            index: Índice de la vista a mostrar
            
        Returns:
            bool: True si el cambio fue exitoso
        """
        if not self._stacked_widget:
            return False
        
        if not ViewRegistry.is_valid_view(index):
            return False
        
        # Emitir señal antes del cambio
        self.view_about_to_change.emit(self._current_view, index)
        
        # Realizar el cambio
        self._stacked_widget.setCurrentIndex(index)
        self._current_view = index
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
    
    def switch_to_graphics(self) -> bool:
        """Cambiar a la vista de gráficos"""
        return self.switch_to(ViewRegistry.VIEW_GRAPHICS)
    
    def switch_to_join(self) -> bool:
        """Cambiar a la vista de join"""
        return self.switch_to(ViewRegistry.VIEW_JOIN)
    
    def get_view_name(self) -> str:
        """Obtener nombre de la vista actual"""
        return ViewRegistry.get_view_name(self._current_view)
    
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
