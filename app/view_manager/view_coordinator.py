"""
View Coordinator

Coordinator pattern para coordinación de estado entre vistas.
Maneja la creación, actualización y coordinación de todas las vistas de la aplicación.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from collections.abc import Mapping

from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QStackedWidget, QWidget
from .view_registry import ViewRegistry
from .view_switcher import ViewSwitcher

if TYPE_CHECKING:
    import pandas as pd
    from app.widgets.main_view import MainView
    from app.widgets.data_view import DataView
    from app.widgets.join.joined_data_view import JoinedDataView
    from app.widgets.info_modal import InfoModal
    from app.widgets.pivot_results_view import PivotResultsView


class ViewCoordinator(QObject):
    """Coordinador de vistas - Maneja la creación y coordinación de todas las vistas"""

    view_created = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._parent = parent
        self._stacked_widget: QStackedWidget | None = None
        self._view_switcher: ViewSwitcher = ViewSwitcher()

        self._views: dict[int, QWidget] = {}
        self._id_to_index: dict[int, int] = {}
        self._main_view: MainView | None = None
        self._data_view: DataView | None = None
        self._joined_data_view: JoinedDataView | None = None
        self._pivot_view: PivotResultsView | None = None
        self._info_modal: InfoModal | None = None

        self._view_factories: dict[int, Callable[[QWidget], QWidget]] = {
            ViewRegistry.VIEW_MAIN: self._create_main_view,
            ViewRegistry.VIEW_DATA: self._create_data_view,
            ViewRegistry.VIEW_JOIN: self._create_joined_data_view,
            ViewRegistry.VIEW_PIVOT: self._create_pivot_view,
        }

    # ==================== CREACIÓN DE VISTAS ====================

    def create_views(self, parent_widget: QWidget) -> dict[int, QWidget]:
        if self._stacked_widget is None:
            self._stacked_widget = QStackedWidget(parent_widget)

        stacked_index = 0
        for view_id, factory in self._view_factories.items():
            view = factory(parent_widget)
            self._stacked_widget.addWidget(view)
            self._views[view_id] = view
            self._id_to_index[view_id] = stacked_index
            stacked_index += 1

            if view_id == ViewRegistry.VIEW_MAIN:
                self._main_view = view  # type: ignore[assignment]
            elif view_id == ViewRegistry.VIEW_DATA:
                self._data_view = view  # type: ignore[assignment]
            elif view_id == ViewRegistry.VIEW_JOIN:
                self._joined_data_view = view  # type: ignore[assignment]
            elif view_id == ViewRegistry.VIEW_PIVOT:
                self._pivot_view = view  # type: ignore[assignment]

            self.view_created.emit(view_id)

        self._view_switcher.set_stacked_widget(self._stacked_widget)
        reverse_mapping = {v: k for k, v in self._id_to_index.items()}
        self._view_switcher.set_index_mapping(reverse_mapping)
        self._stacked_widget.setCurrentIndex(0)
        return self._views

    def _create_main_view(self, parent: QWidget) -> MainView:
        from app.widgets.main_view import MainView
        return MainView()

    def _create_data_view(self, parent: QWidget) -> DataView:
        from app.widgets.data_view import DataView
        return DataView()

    def _create_joined_data_view(self, parent: QWidget) -> JoinedDataView:
        from app.widgets.join.joined_data_view import JoinedDataView
        return JoinedDataView()

    def _create_pivot_view(self, parent: QWidget) -> PivotResultsView:
        from app.widgets.pivot_results_view import PivotResultsView
        return PivotResultsView()

    # ==================== GETTERS ====================

    def get_stacked_widget(self) -> QStackedWidget:
        return self._stacked_widget

    def get_view(self, view_id: int) -> QWidget | None:
        return self._views.get(view_id)

    def get_main_view(self) -> MainView | None:
        return self._main_view

    def get_data_view(self) -> DataView | None:
        return self._data_view

    def get_joined_data_view(self) -> JoinedDataView | None:
        return self._joined_data_view

    def get_pivot_view(self) -> PivotResultsView | None:
        return self._pivot_view

    def get_view_switcher(self) -> ViewSwitcher:
        return self._view_switcher

    # ==================== NAVEGACIÓN ====================

    def switch_to(self, index: int) -> bool:
        mapped = self._id_to_index.get(index)
        if mapped is not None:
            return self._view_switcher.switch_to(mapped)
        return False

    def get_current_view(self) -> int:
        return self._view_switcher.get_current_view()

    def get_current_view_name(self) -> str:
        return self._view_switcher.get_view_name()

    # ==================== ACTUALIZACIÓN DE VISTAS ====================

    def update_data_view(self, df: pd.DataFrame) -> None:
        if self._data_view:
            self._data_view.set_data(df)

    def update_main_view(self, filepath: str | None) -> None:
        if filepath and self._main_view:
            self._main_view.add_file_to_list(filepath)
            self._main_view.set_file_completed(filepath)

    def show_info_modal(self, df: pd.DataFrame, filename: str) -> None:
        if self._info_modal is None and self._parent:
            from app.widgets.info_modal import InfoModal
            self._info_modal = InfoModal(self._parent)
        if self._info_modal:
            self._info_modal.update_info(df, filename)
            self._info_modal.exec()

    def set_join_result(self, result: object, left_name: str, right_name: str) -> None:
        if self._joined_data_view:
            self._joined_data_view.set_join_result(result, left_name, right_name)

    # ==================== SLOTS DE SEÑALES ====================

    def on_datos_originales_cargados(self, df: pd.DataFrame) -> None:
        if df is not None and self._main_view is not None:
            self._main_view.set_original_columns(df.columns.tolist())

    def on_datos_actualizados(self, df: pd.DataFrame) -> None:
        if df is not None:
            self.update_data_view(df)

    def set_column_visibility_enabled(self, enabled: bool) -> None:
        if self._data_view is not None:
            self._data_view.set_column_visibility_enabled(enabled)

    # ==================== CLEANUP ====================

    def cleanup(self) -> None:
        if self._info_modal is not None:
            self._info_modal.close()
            self._info_modal.deleteLater()
            self._info_modal = None

        self._main_view = None
        self._data_view = None
        self._joined_data_view = None
        self._pivot_view = None
        self._views.clear()
        self._view_factories.clear()
        self._parent = None
