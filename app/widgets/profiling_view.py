"""
ProfilingView - Widget para mostrar el perfil de datos del dataset.

Muestra un resumen general del dataset y una tarjeta por cada columna
con tipo, nulos, cardinalidad, estadísticas numéricas y valores más
frecuentes. Diseño plano y minimalista, alto ratio tinta-datos.
"""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel,
                               QScrollArea, QVBoxLayout, QWidget)

_BG_COLOR = "#f8fafc"
_BORDER_COLOR = "#e2e8f0"
_BAR_COLOR = "#94a3b8"
_TRACK_COLOR = "#e2e8f0"
_BODY_COLOR = "#334155"
_MUTED_COLOR = "#64748b"
_TITLE_COLOR = "#1e293b"
_ERROR_COLOR = "#b45309"


class _PercentBar(QWidget):
    """Barra horizontal plana con etiqueta de porcentaje."""

    def __init__(self, percent: float, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(16)
        self._percent = max(0.0, min(percent, 100.0))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._bar = QFrame()
        self._bar.setFixedHeight(6)
        self._bar.setStyleSheet(
            f"QFrame {{ background-color: {_TRACK_COLOR}; border: none; "
            f"border-radius: 3px; }}"
        )
        layout.addWidget(self._bar, 1)

        self._label = QLabel(f"{percent:.1f}%")
        self._label.setFixedWidth(52)
        self._label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._label.setStyleSheet(f"color: {_BODY_COLOR}; font-size: 11px;")
        layout.addWidget(self._label)

        self._fill = QFrame(self._bar)
        self._fill.setFixedHeight(6)
        self._fill.setStyleSheet(
            f"QFrame {{ background-color: {_BAR_COLOR}; border: none; "
            f"border-radius: 3px; }}"
        )
        self._fill.setGeometry(0, 0, 0, 6)

    def _update_fill(self) -> None:
        fill_width = max(0, int(self._bar.width() * self._percent / 100))
        self._fill.setGeometry(0, 0, fill_width, 6)

    def resizeEvent(self, event: Any) -> None:
        super().resizeEvent(event)
        self._update_fill()


class ProfilingView(QWidget):
    """Vista de perfil de datos del dataset cargado."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._profile: dict[str, Any] | None = None
        self._loading = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet(f"background-color: {_BG_COLOR};")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(12)

        header = QLabel("Perfil de Datos")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet(f"color: {_TITLE_COLOR};")
        main_layout.addWidget(header)

        self._summary_label = QLabel("")
        self._summary_label.setStyleSheet(f"color: {_MUTED_COLOR}; font-size: 12px;")
        main_layout.addWidget(self._summary_label)

        self._status_label = QLabel("Carga un archivo para ver su perfil de datos.")
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setStyleSheet(f"color: {_MUTED_COLOR}; font-size: 13px;")
        main_layout.addWidget(self._status_label)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: transparent; }}"
            f"QScrollArea > QWidget > QWidget {{ background: {_BG_COLOR}; }}"
        )
        self._cards_widget = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_widget)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(8)
        self._cards_layout.addStretch()
        self._scroll.setWidget(self._cards_widget)
        main_layout.addWidget(self._scroll, 1)

        self._scroll.setVisible(False)

    # ==================== ESTADOS ====================

    def show_loading(self) -> None:
        """Mostrar estado de cálculo en curso."""
        self._loading = True
        self._clear_cards()
        self._summary_label.setText("")
        self._status_label.setText("Calculando perfil...")
        self._status_label.setVisible(True)
        self._scroll.setVisible(False)

    def set_progress(self, percent: int) -> None:
        """Actualizar el porcentaje mostrado mientras se calcula."""
        if self._loading:
            self._status_label.setText(f"Calculando perfil... {percent}%")

    def clear_profile(self) -> None:
        """Limpiar el perfil mostrado."""
        self._loading = False
        self._profile = None
        self._clear_cards()
        self._summary_label.setText("")
        self._status_label.setText("Carga un archivo para ver su perfil de datos.")
        self._status_label.setVisible(True)
        self._scroll.setVisible(False)

    # ==================== POBLADO ====================

    def set_profile(self, profile: dict[str, Any]) -> None:
        """Construir las tarjetas de columnas a partir del perfil."""
        self._loading = False
        self._profile = profile
        self._clear_cards()

        if profile is None:
            self.clear_profile()
            return

        total_rows = profile.get('total_rows', 0)
        if total_rows == 0:
            self.clear_profile()
            return

        columns = profile.get('columns', {})
        memory = profile.get('memory_usage_mb', 0.0)
        duplicated = profile.get('duplicated_rows', 0)
        quality = profile.get('data_quality_summary') or {}
        quality_score = quality.get('overall_quality_score')

        summary = (
            f"{total_rows:,} filas · {len(columns)} columnas · "
            f"{memory:.2f} MB · {duplicated:,} filas duplicadas"
        )
        if quality_score is not None:
            summary += f" · Calidad {quality_score:.1f}%"
        self._summary_label.setText(summary)
        self._status_label.setVisible(False)
        self._scroll.setVisible(True)

        for name, col_profile in columns.items():
            self._cards_layout.insertWidget(
                self._cards_layout.count() - 1, self._create_column_card(name, col_profile)
            )

    def _clear_cards(self) -> None:
        while self._cards_layout.count() > 1:
            item = self._cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _create_column_card(self, name: str, profile: dict[str, Any]) -> QFrame:
        if profile.get('error'):
            return self._create_error_card(name, profile.get('error_msg', 'Error desconocido'))

        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background-color: white; border: 1px solid {_BORDER_COLOR}; "
            f"border-radius: 8px; }}"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        header = QHBoxLayout()
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 11, QFont.Bold))
        name_label.setStyleSheet(f"color: {_TITLE_COLOR}; border: none;")
        header.addWidget(name_label)
        header.addStretch()
        dtype_label = QLabel(profile.get('dtype', ''))
        dtype_label.setStyleSheet(
            f"color: {_MUTED_COLOR}; font-size: 11px; background: {_BG_COLOR}; "
            f"border: 1px solid {_BORDER_COLOR}; border-radius: 4px; padding: 2px 8px;"
        )
        header.addWidget(dtype_label)
        layout.addLayout(header)

        rows = QGridLayout()
        rows.setHorizontalSpacing(16)
        rows.setVerticalSpacing(4)

        null_count = profile.get('null_count', 0)
        null_percent = profile.get('null_percent', 0.0)
        rows.addWidget(self._metric_label("Nulos"), 0, 0)
        rows.addWidget(_PercentBar(null_percent), 0, 1)
        rows.addWidget(self._metric_label(f"{null_count:,} valores"), 1, 1)

        unique_count = profile.get('unique_count', 0)
        unique_percent = profile.get('unique_percent', 0.0)
        rows.addWidget(self._metric_label("Únicos"), 2, 0)
        rows.addWidget(_PercentBar(unique_percent), 2, 1)
        rows.addWidget(self._metric_label(f"{unique_count:,} valores"), 3, 1)

        rows.setColumnStretch(0, 0)
        rows.setColumnStretch(1, 1)
        layout.addLayout(rows)

        numeric_stats = profile.get('numeric_stats')
        if numeric_stats:
            layout.addWidget(self._numeric_stats_grid(numeric_stats))

        date_range = profile.get('date_range')
        if date_range:
            layout.addWidget(self._metric_label(
                f"Rango: {date_range.get('min', '')} → {date_range.get('max', '')} "
                f"({date_range.get('days_span', 0):,} días)"
            ))

        top_values = profile.get('top_values')
        if top_values:
            layout.addWidget(self._values_list_widget("Valores más frecuentes", top_values))

        distribution = profile.get('value_distribution')
        if distribution:
            layout.addWidget(self._values_list_widget("Distribución", distribution))

        return card

    def _create_error_card(self, name: str, error_msg: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background-color: white; border: 1px solid {_BORDER_COLOR}; "
            f"border-radius: 8px; }}"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        header = QHBoxLayout()
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 11, QFont.Bold))
        name_label.setStyleSheet(f"color: {_TITLE_COLOR}; border: none;")
        header.addWidget(name_label)
        header.addStretch()
        badge = QLabel("error")
        badge.setStyleSheet(
            f"color: {_ERROR_COLOR}; font-size: 11px; background: #fef3c7; "
            f"border: 1px solid #fde68a; border-radius: 4px; padding: 2px 8px;"
        )
        header.addWidget(badge)
        layout.addLayout(header)

        error_label = QLabel(error_msg)
        error_label.setWordWrap(True)
        error_label.setStyleSheet(f"color: {_ERROR_COLOR}; font-size: 12px; border: none;")
        layout.addWidget(error_label)

        return card

    def _metric_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(f"color: {_MUTED_COLOR}; font-size: 12px; border: none;")
        return label

    def _numeric_stats_grid(self, stats: dict[str, Any]) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background-color: {_BG_COLOR}; border: 1px solid {_BORDER_COLOR}; "
            f"border-radius: 6px; }}"
        )
        grid = QGridLayout(frame)
        grid.setContentsMargins(10, 6, 10, 6)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(2)

        labels = [
            ("Conteo", 'count', "{:,}"),
            ("Mínimo", 'min', "{:,.4g}"),
            ("Máximo", 'max', "{:,.4g}"),
            ("Media", 'mean', "{:,.4g}"),
            ("Mediana", 'median', "{:,.4g}"),
            ("Desv. std", 'std', "{:,.4g}"),
            ("P25", 'q25', "{:,.4g}"),
            ("P75", 'q75', "{:,.4g}"),
        ]
        for col_index, (title, key, fmt) in enumerate(labels):
            value = stats.get(key)
            title_label = QLabel(title)
            title_label.setStyleSheet(
                f"color: {_MUTED_COLOR}; font-size: 11px; border: none;"
            )
            value_label = QLabel(self._format_value(value, fmt))
            value_label.setStyleSheet(
                f"color: {_BODY_COLOR}; font-size: 11px; font-weight: 600; border: none;"
            )
            grid.addWidget(title_label, 0, col_index)
            grid.addWidget(value_label, 1, col_index)

        return frame

    def _values_list_widget(self, title_text: str, values: list[list[Any]]) -> QFrame:
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.setSpacing(2)

        title = QLabel(title_text)
        title.setStyleSheet(f"color: {_MUTED_COLOR}; font-size: 11px; border: none;")
        layout.addWidget(title)

        for value, count in values:
            row = QHBoxLayout()
            value_label = QLabel(str(value) if value is not None else "(nulo)")
            value_label.setStyleSheet(
                f"color: {_BODY_COLOR}; font-size: 12px; border: none;"
            )
            count_label = QLabel(f"{count:,}")
            count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            count_label.setStyleSheet(
                f"color: {_MUTED_COLOR}; font-size: 11px; border: none;"
            )
            row.addWidget(value_label, 1)
            row.addWidget(count_label)
            layout.addLayout(row)

        return frame

    @staticmethod
    def _format_value(value: Any, fmt: str) -> str:
        if value is None:
            return "—"
        try:
            return fmt.format(value)
        except (TypeError, ValueError):
            return str(value)

    def get_profile(self) -> dict[str, Any] | None:
        """Devolver el perfil actualmente mostrado."""
        return self._profile
