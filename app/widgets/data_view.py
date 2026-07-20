"""
DataView - Widget principal para vista de datos con paginación y filtros integrados.
Diseño moderno con botones segmentados dinámicos y barra de búsqueda minimalista.
"""

import pandas as pd
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableView,
                               QLineEdit, QPushButton, QLabel, QFrame,
                               QMessageBox, QSpinBox, QSizePolicy, QButtonGroup,
                               QSpacerItem, QComboBox, QHeaderView)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.services.pagination_manager import PaginationManager
from app.models.pandas_model import VirtualizedPandasModel
from typing import Optional


_MAX_QUICK_FILTER_VALUES = 5


class DataView(QWidget):
    """
    Widget principal que integra filtros dinámicos, tabla y paginación en una sola vista.
    """

    filter_applied = Signal(str, str)
    filter_cleared = Signal()
    data_updated = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.pagination_manager: Optional[PaginationManager] = None
        self.pandas_model: Optional[VirtualizedPandasModel] = None
        self.original_df: Optional[pd.DataFrame] = None
        self._sorting_in_progress: bool = False
        self._quick_filter_groups: dict[str, QButtonGroup] = {}

        self.setup_ui()

    def setup_ui(self) -> None:
        self.setStyleSheet("background-color: white;")
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 16, 20, 16)

        self._quick_filters_container = QWidget()
        self._quick_filters_layout = QVBoxLayout(self._quick_filters_container)
        self._quick_filters_layout.setContentsMargins(0, 0, 0, 0)
        self._quick_filters_layout.setSpacing(4)
        main_layout.addWidget(self._quick_filters_container)
        self._quick_filters_container.setVisible(False)

        self._create_search_section(main_layout)
        self._create_table_section(main_layout)
        self._create_pagination_section(main_layout)

    def _create_search_section(self, parent_layout: QVBoxLayout) -> None:
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 8)

        self.search_column_combo = QComboBox()
        self.search_column_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #f9fafb;
                color: #374151;
                min-width: 130px;
            }
        """)
        search_layout.addWidget(self.search_column_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar...")
        self.search_input.setMinimumWidth(220)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 6px 12px;
                background-color: white;
                color: #374151;
            }
            QLineEdit:focus { border: 1px solid #4a90e2; }
        """)
        self.search_input.returnPressed.connect(self._apply_text_filter)
        search_layout.addWidget(self.search_input, 1)

        self.clear_search_btn = QPushButton("Limpiar")
        self.clear_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6; color: #4b5563; border: 1px solid #d1d5db;
                border-radius: 6px; padding: 6px 12px; font-weight: bold;
            }
            QPushButton:hover { background-color: #e5e7eb; }
        """)
        self.clear_search_btn.clicked.connect(self.clear_filter)
        search_layout.addWidget(self.clear_search_btn)

        parent_layout.addLayout(search_layout)

    def _create_table_section(self, parent_layout: QVBoxLayout) -> None:
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(False)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSortingEnabled(True)
        self.table_view.setShowGrid(False)
        self.table_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # type: ignore[attr-defined]
        header.setStretchLastSection(True)

        self.table_view.setStyleSheet("""
            QTableView {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                outline: none;
            }
            QTableView::item {
                padding: 8px 5px;
                border-bottom: 1px solid #f3f4f6;
                color: #374151;
            }
            QTableView::item:selected {
                background-color: #eff6ff;
                color: #1d4ed8;
            }
            QHeaderView::section {
                background-color: #f9fafb;
                color: #111827;
                font-weight: bold;
                padding: 8px 10px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                border-right: 1px solid #e5e7eb;
                text-align: left;
            }
        """)

        parent_layout.addWidget(self.table_view, 1)

    def _create_pagination_section(self, parent_layout: QVBoxLayout) -> None:
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet("""
            QFrame {
                border-top: 1px solid #e5e7eb;
                background-color: white;
                padding-top: 10px;
            }
            QLabel { color: #6b7280; font-size: 13px; }
            QPushButton {
                background-color: white; border: 1px solid #d1d5db;
                border-radius: 4px; padding: 4px 8px; color: #374151;
            }
            QPushButton:hover { background-color: #f3f4f6; }
            QPushButton:disabled {
                background-color: #f9fafb; color: #9ca3af;
                border: 1px solid #e5e7eb;
            }
            QSpinBox {
                border: 1px solid #d1d5db; border-radius: 4px; padding: 2px;
            }
        """)

        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(0, 0, 0, 0)

        self.page_info_label = QLabel("0 registros")
        pagination_layout.addWidget(self.page_info_label)

        pagination_layout.addStretch()

        pagination_layout.addWidget(QLabel("Filas por página:"))
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setRange(10, 1000)
        self.page_size_spin.setValue(10)
        self.page_size_spin.valueChanged.connect(self._change_page_size)
        pagination_layout.addWidget(self.page_size_spin)

        pagination_layout.addSpacing(12)

        self.first_page_btn = QPushButton("⏮")
        self.prev_page_btn = QPushButton("◀")
        self.next_page_btn = QPushButton("▶")
        self.last_page_btn = QPushButton("⏭")

        for btn in (self.first_page_btn, self.prev_page_btn,
                    self.next_page_btn, self.last_page_btn):
            btn.setFixedWidth(32)
            pagination_layout.addWidget(btn)

        self.first_page_btn.clicked.connect(self.first_page)
        self.prev_page_btn.clicked.connect(self.previous_page)
        self.next_page_btn.clicked.connect(self.next_page)
        self.last_page_btn.clicked.connect(self.last_page)

        parent_layout.addWidget(pagination_frame)

    # ------------------------------------------------------------------
    # Dynamic quick filters
    # ------------------------------------------------------------------

    def _populate_quick_filters(self, df: pd.DataFrame) -> None:
        while self._quick_filters_layout.count():
            child = self._quick_filters_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_sub_layout(child.layout())

        self._quick_filter_groups.clear()

        candidates: list[str] = []
        for col in df.columns:
            nunique = df[col].nunique(dropna=True)
            if 1 < nunique <= _MAX_QUICK_FILTER_VALUES:
                candidates.append(col)

        if not candidates:
            self._quick_filters_container.setVisible(False)
            return

        self._quick_filters_container.setVisible(True)

        for col in candidates:
            row = self._create_quick_filter_row(col, df)
            self._quick_filters_layout.addWidget(row)

    def _create_quick_filter_row(self, col: str, df: pd.DataFrame) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
            }
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(0)

        label = QLabel(col)
        label.setStyleSheet("""
            color: #4b5563; font-weight: bold; font-size: 12px;
            border: none; padding-right: 8px;
        """)
        layout.addWidget(label)

        btn_group = QButtonGroup(frame)
        btn_group.setExclusive(True)
        self._quick_filter_groups[col] = btn_group

        values = sorted(df[col].dropna().unique().tolist())

        all_btn = QPushButton("Todos")
        all_btn.setCheckable(True)
        all_btn.setChecked(True)
        all_btn.setStyleSheet(self._segment_btn_style(first=True))
        btn_group.addButton(all_btn, 0)
        all_btn.clicked.connect(lambda: self._apply_quick_filter_clear(col))
        layout.addWidget(all_btn)

        for i, val in enumerate(values):
            btn = QPushButton(str(val))
            btn.setCheckable(True)
            btn.setStyleSheet(self._segment_btn_style())
            btn_group.addButton(btn, i + 1)
            btn.clicked.connect(lambda checked, c=col, v=str(val): self._apply_quick_filter(c, v))
            layout.addWidget(btn)

        layout.addStretch()
        return frame

    @staticmethod
    def _segment_btn_style(first: bool = False) -> str:
        border_left = "border-left: none;" if not first else ""
        return f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid #d1d5db;
                {border_left}
                padding: 5px 14px;
                color: #4b5563;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:checked {{
                background-color: #eff6ff;
                color: #1d4ed8;
                border-color: #93b4f5;
            }}
            QPushButton:hover:!checked {{ background-color: #f3f4f6; }}
        """

    def _apply_quick_filter(self, column: str, value: str) -> None:
        if self.pagination_manager is None or self.original_df is None:
            return
        try:
            self.pagination_manager.apply_filter(column, value)
            self.filter_applied.emit(column, value)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al filtrar: {e}")

    def _apply_quick_filter_clear(self, column: str) -> None:
        if self.pagination_manager is None or self.original_df is None:
            return
        self.pagination_manager.clear_filter()
        for col, group in self._quick_filter_groups.items():
            if col != column:
                continue
            for btn in group.buttons():
                if btn.text() == "Todos":
                    btn.setChecked(True)
                    break
        self.filter_cleared.emit()

    @staticmethod
    def _clear_sub_layout(layout) -> None:  # type: ignore[no-untyped-def]
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                DataView._clear_sub_layout(child.layout())

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------

    def set_data(self, df: pd.DataFrame) -> None:
        self.original_df = df.copy()

        if self.pagination_manager is None:
            self.pagination_manager = PaginationManager(df, self.page_size_spin.value())
            self._connect_pagination_signals()
        else:
            self.pagination_manager.set_data(df)

        if not df.empty:
            self.search_column_combo.clear()
            self.search_column_combo.addItems(df.columns.tolist())

        self._populate_quick_filters(df)
        self.update_view()

    def _connect_pagination_signals(self) -> None:
        assert self.pagination_manager is not None
        self.pagination_manager.page_changed.connect(self._on_page_changed)
        self.pagination_manager.page_size_changed.connect(self._on_page_size_changed)
        self.pagination_manager.data_changed.connect(self._on_data_changed)
        self.pagination_manager.total_pages_changed.connect(self._on_total_pages_changed)

    def _connect_model_signals(self) -> None:
        if self.pandas_model is not None:
            self.pandas_model.layoutChanged.connect(self._on_model_sorted)

    def _on_model_sorted(self) -> None:
        if self.pandas_model is None or self.pagination_manager is None or self.original_df is None:
            return
        if self._sorting_in_progress:
            return

        self._sorting_in_progress = True
        try:
            sorted_data = self.pandas_model.get_sorted_data()
            if len(sorted_data) < len(self.original_df):
                full_sorted = self.original_df.sort_values(
                    sorted_data.columns[0], ascending=False
                )
            else:
                full_sorted = sorted_data

            self.pagination_manager.set_data(full_sorted, preserve_page=True)
            self.original_df = full_sorted.copy()
        finally:
            self._sorting_in_progress = False

    def update_view(self) -> None:
        if self.pagination_manager is None or self.original_df is None:
            return
        if self._sorting_in_progress:
            return

        current_page_data = self.pagination_manager.get_page_data()
        self.pandas_model = VirtualizedPandasModel(current_page_data)
        self.table_view.setModel(self.pandas_model)
        self._connect_model_signals()

        self._update_page_info()
        self._update_pagination_buttons()
        self.data_updated.emit(self.pagination_manager.filtered_df)

    # ------------------------------------------------------------------
    # Filters
    # ------------------------------------------------------------------

    def _apply_text_filter(self) -> None:
        if self.pagination_manager is None:
            return

        column = self.search_column_combo.currentText()
        term = self.search_input.text().strip()

        if not column or not term:
            return

        try:
            self.pagination_manager.apply_filter(column, term)
            self.filter_applied.emit(column, term)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error de búsqueda: {e}")

    def clear_filter(self) -> None:
        if self.pagination_manager:
            self.pagination_manager.clear_filter()
            self.search_input.clear()

            for group in self._quick_filter_groups.values():
                for btn in group.buttons():
                    if btn.text() == "Todos":
                        btn.setChecked(True)
                        break

            self.filter_cleared.emit()

    # ------------------------------------------------------------------
    # Pagination UI
    # ------------------------------------------------------------------

    def _update_page_info(self) -> None:
        if self.pagination_manager is None:
            self.page_info_label.setText("Sin datos")
            return

        info = self.pagination_manager.get_page_info()
        if info['total_rows'] == 0:
            self.page_info_label.setText("No hay registros")
        else:
            self.page_info_label.setText(
                f"Mostrando {info['start_row']}–{info['end_row']} de "
                f"{info['total_rows']} registros"
            )

    def _update_pagination_buttons(self) -> None:
        if self.pagination_manager is None:
            for btn in (self.first_page_btn, self.prev_page_btn,
                        self.next_page_btn, self.last_page_btn):
                btn.setEnabled(False)
            return

        can_prev = self.pagination_manager.can_go_previous()
        can_next = self.pagination_manager.can_go_next()
        curr = self.pagination_manager.get_current_page()
        total = self.pagination_manager.get_total_pages()

        self.first_page_btn.setEnabled(can_prev and curr > 1)
        self.prev_page_btn.setEnabled(can_prev)
        self.next_page_btn.setEnabled(can_next)
        self.last_page_btn.setEnabled(can_next and curr < total)

    # ------------------------------------------------------------------
    # Pagination actions
    # ------------------------------------------------------------------

    def first_page(self) -> None:
        if self.pagination_manager:
            self.pagination_manager.first_page()

    def previous_page(self) -> None:
        if self.pagination_manager:
            self.pagination_manager.previous_page()

    def next_page(self) -> None:
        if self.pagination_manager:
            self.pagination_manager.next_page()

    def last_page(self) -> None:
        if self.pagination_manager:
            self.pagination_manager.last_page()

    def _change_page_size(self, size: int) -> None:
        if self.pagination_manager:
            self.pagination_manager.set_page_size(size)

    # ------------------------------------------------------------------
    # PaginationManager slots
    # ------------------------------------------------------------------

    def _on_page_changed(self, _page: int) -> None:
        self.update_view()

    def _on_page_size_changed(self, size: int) -> None:
        self.page_size_spin.setValue(size)
        self.update_view()

    def _on_data_changed(self) -> None:
        self.update_view()

    def _on_total_pages_changed(self, _total: int) -> None:
        self._update_pagination_buttons()
        self._update_page_info()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_current_filter_info(self) -> dict:
        if self.pagination_manager:
            return self.pagination_manager.get_filter_info()
        return {}

    def export_current_page(self) -> pd.DataFrame:
        if self.pagination_manager:
            return self.pagination_manager.get_page_data()
        return pd.DataFrame()

    def set_column_visibility_enabled(self, _enabled: bool) -> None:
        pass
