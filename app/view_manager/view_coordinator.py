"""
View Coordinator

Coordinator pattern para coordinación de estado entre vistas.
Maneja la creación, actualización y coordinación de todas las vistas de la aplicación.
"""

from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QStackedWidget, QWidget
from .view_registry import ViewRegistry
from .view_switcher import ViewSwitcher
from typing import Any

class ViewCoordinator(QObject):
    """Coordinador de vistas - Maneja la creación y coordinación de todas las vistas"""
    
    # Señales para comunicar eventos a MainWindow
    view_created = Signal(int)  # Emitido cuando se crea una vista
    data_loaded = Signal(object)  # Emitido cuando se cargan datos
    filter_applied = Signal(str, str)  # (columna, termino)
    filter_cleared = Signal()
    
    def __init__(self, parent: QWidget | None = None) -> None:
        """Inicializar el coordinador de vistas
        
        Args:
            parent: Widget padre (típicamente MainWindow)
        """
        super().__init__(parent)
        self._parent = parent
        self._stacked_widget: QStackedWidget | None = None
        self._view_switcher: ViewSwitcher = ViewSwitcher()
        
        # Referencias a las vistas
        self._views: dict[int, Any] = {}
        
        # Referencias para coordinación de estado
        self._main_view: Any | None = None
        self._data_view: Any | None = None
        self._info_modal: Any | None = None
        self._graphics_view: Any | None = None
        self._joined_data_view: Any | None = None
        self._original_data: Any | None = None
    
    def create_views(self, parent_widget: QWidget) -> dict[int, Any]:
        """Crear todas las vistas y añadirlas al stacked widget
        
        Args:
            parent_widget: Widget padre para las vistas
            
        Returns:
            dict: Referencias a las vistas creadas
        """
        # Crear stacked widget si no existe
        if self._stacked_widget is None:
            self._stacked_widget = QStackedWidget(parent_widget)
        
        # Vista Principal (índice 0)
        self._main_view = self._create_main_view(parent_widget)
        self._stacked_widget.addWidget(self._main_view)
        self._views[ViewRegistry.VIEW_MAIN] = self._main_view
        
        # Vista de Tabla (índice 1) - DataView con paginación
        self._data_view = self._create_data_view(parent_widget)
        self._stacked_widget.addWidget(self._data_view)
        self._views[ViewRegistry.VIEW_DATA] = self._data_view
        
        # Vista de Gráficos (índice 3)
        self._graphics_view = self._create_graphics_view(parent_widget)
        self._stacked_widget.addWidget(self._graphics_view)
        self._views[ViewRegistry.VIEW_GRAPHICS] = self._graphics_view
        
        # Vista de Datos Cruzados (índice 4)
        self._joined_data_view = self._create_joined_data_view(parent_widget)
        self._stacked_widget.addWidget(self._joined_data_view)
        self._views[ViewRegistry.VIEW_JOIN] = self._joined_data_view
        
        # Configurar el switcher
        self._view_switcher.set_stacked_widget(self._stacked_widget)
        
        # Establecer vista inicial
        self._stacked_widget.setCurrentIndex(ViewRegistry.VIEW_MAIN)
        
        # Emitir señales de vistas creadas
        for idx in self._views.keys():
            self.view_created.emit(idx)
        
        return self._views
    
    def _create_main_view(self, parent: QWidget) -> Any:
        """Crear la vista principal"""
        from app.widgets.main_view import MainView
        view = MainView()
        return view
    
    def _create_data_view(self, parent: QWidget) -> Any:
        """Crear la vista de datos con paginación"""
        from paginacion.data_view import DataView
        view = DataView()
        return view
    
    def _create_graphics_view(self, parent: QWidget) -> Any:
        """Crear la vista de gráficos"""
        from app.widgets.graphics_view import GraphicsView
        view = GraphicsView()
        return view
    
    def _create_joined_data_view(self, parent: QWidget) -> Any:
        """Crear la vista de datos cruzados (join)"""
        from app.widgets.join.joined_data_view import JoinedDataView
        view = JoinedDataView()
        return view
    
    def get_stacked_widget(self) -> QStackedWidget:
        """Obtener el widget stacked"""
        return self._stacked_widget
    
    def get_view(self, view_id: int) -> Any | None:
        """Obtener referencia a una vista específica
        
        Args:
            view_id: ID de la vista (ViewRegistry.VIEW_*)
            
        Returns:
            La referencia a la vista o None
        """
        return self._views.get(view_id)
    
    def get_main_view(self) -> Any | None:
        """Obtener referencia a la vista principal"""
        return self._main_view
    
    def get_data_view(self) -> Any | None:
        """Obtener referencia a la vista de datos"""
        return self._data_view
    
    def get_graphics_view(self) -> Any | None:
        """Obtener referencia a la vista de gráficos"""
        return self._graphics_view
    
    def get_joined_data_view(self) -> Any | None:
        """Obtener referencia a la vista de join"""
        return self._joined_data_view
    
    def get_view_switcher(self) -> ViewSwitcher:
        """Obtener el switcher de vistas"""
        return self._view_switcher
    
    def switch_to(self, index: int) -> bool:
        """Cambiar a la vista especificada"""
        return self._view_switcher.switch_to(index)
    
    def switch_to_main(self) -> bool:
        """Cambiar a la vista principal"""
        return self._view_switcher.switch_to_main()
    
    def switch_to_data(self) -> bool:
        """Cambiar a la vista de datos"""
        return self._view_switcher.switch_to_data()
    
    def switch_to_graphics(self) -> bool:
        """Cambiar a la vista de gráficos"""
        return self._view_switcher.switch_to_graphics()
    
    def switch_to_join(self) -> bool:
        """Cambiar a la vista de join"""
        return self._view_switcher.switch_to_join()
    
    def get_current_view(self) -> int:
        """Obtener índice de la vista actual"""
        return self._view_switcher.get_current_view()
    
    def update_data_view(self, df: Any) -> None:
        """Actualizar la vista de datos con nuevos datos
        
        Args:
            df: DataFrame con los datos
        """
        if self._data_view:
            self._data_view.set_data(df)
    
    def update_graphics_view(self, df: Any) -> None:
        """Actualizar la vista de gráficos con nuevos datos
        
        Args:
            df: DataFrame con los datos
        """
        if self._graphics_view:
            self._graphics_view.update_data(df)
    
    def update_main_view(self, filepath: str) -> None:
        """Actualizar la vista principal con información del archivo
        
        Args:
            filepath: Ruta del archivo cargado
        """
        if self._main_view:
            self._main_view.set_file_info(filepath)
            self._main_view.show_options_button()
    
    def show_info_modal(self, df: Any, filename: str) -> None:
        """Mostrar el modal de información
        
        Args:
            df: DataFrame con los datos
            filename: Nombre del archivo
        """
        if self._info_modal is None and self._parent:
            from app.widgets.info_modal import InfoModal
            self._info_modal = InfoModal(self._parent)
        if self._info_modal:
            self._info_modal.update_info(df, filename)
            self._info_modal.exec()
    
    def set_join_result(self, result: Any, left_name: str, right_name: str) -> None:
        """Establecer el resultado de un join en la vista correspondiente
        
        Args:
            result: Resultado del join
            left_name: Nombre del dataset izquierdo
            right_name: Nombre del dataset derecho
        """
        if self._joined_data_view:
            self._joined_data_view.set_join_result(result, left_name, right_name)
    
    def on_datos_originales_cargados(self, df: Any) -> None:
        """Slot para reaccionar a la carga de datos originales
        
        Almacena los datos originales y actualiza MainView con los nombres de columnas.
        """
        self._original_data = df
        if df is not None and self._main_view:
            self._main_view.set_original_columns(df.columns.tolist())
    
    def on_datos_actualizados(self, df: Any) -> None:
        """Slot para reaccionar a la actualización de datos actuales
        
        Actualiza la vista de datos y la vista de gráficos con los nuevos datos.
        """
        if df is not None:
            self.update_data_view(df)
            self.update_graphics_view(df)

    def toggle_visualization(self, enabled: bool) -> None:
        """Habilitar o deshabilitar el panel de gráficos/visualización"""
        graphics = self.get_graphics_view()
        if graphics is not None and hasattr(graphics, 'setVisible'):
            graphics.setVisible(enabled)

    def set_column_visibility_enabled(self, enabled: bool) -> None:
        """Habilitar o deshabilitar la sección de visibilidad de columnas en DataView"""
        data_view = self.get_data_view()
        if data_view is not None and hasattr(data_view, 'column_visibility_group'):
            data_view.column_visibility_group.setVisible(enabled)
    
    def get_original_data(self) -> Any | None:
        """Obtener los datos originales"""
        return self._original_data
    
    def cleanup(self) -> None:
        """Destruye referencias a vistas y cierra modales pendientes."""
        # 1. Cerrar modal activo si existe
        if self._info_modal is not None:
            self._info_modal.close()
            self._info_modal.deleteLater()
            self._info_modal = None

        # 2. Romper referencias a vistas
        self._main_view = None
        self._data_view = None
        self._graphics_view = None
        self._joined_data_view = None
        self._original_data = None
        self._views.clear()
    
    def get_current_view_name(self) -> str:
        """Obtener nombre de la vista actual"""
        return self._view_switcher.get_view_name()
