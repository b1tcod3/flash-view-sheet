"""
Vista de Gráficos y Estadísticas para Flash View Sheet
Muestra visualizaciones basadas en datos filtrados
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                               QPushButton, QLabel, QGroupBox, QScrollArea,
                               QFrame, QMessageBox, QProgressBar, QTableView)
from PySide6.QtCore import Qt, QThread, Signal
import numpy as np
from app.models.pandas_model import VirtualizedPandasModel

class VisualizationWorker(QThread):
    """Hilo para generar visualizaciones en segundo plano"""

    finished = Signal(object)  # Signal para enviar la figura de matplotlib
    error = Signal(str)

    def __init__(self, df, plot_type, columns):
        super().__init__()
        self.df = df
        self.plot_type = plot_type
        self.columns = columns

    def run(self):
        """Generar la visualización"""
        try:
            fig = self._create_plot()
            self.finished.emit(fig)
        except Exception as e:
            self.error.emit(str(e))

    def _create_plot(self):
        """Crear el gráfico basado en el tipo"""
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        if self.plot_type == 'histogram':
            self._create_histogram(ax)
        elif self.plot_type == 'scatter':
            self._create_scatter(ax)
        elif self.plot_type == 'boxplot':
            self._create_boxplot(ax)
        elif self.plot_type == 'correlation':
            self._create_correlation(ax)
        elif self.plot_type == 'line':
            self._create_line(ax)
        else:
            ax.text(0.5, 0.5, 'Tipo de gráfico no soportado',
                    ha='center', va='center', transform=ax.transAxes)

        fig.tight_layout()
        return fig

    def _create_histogram(self, ax):
        """Crear histograma"""
        col = self.columns[0]
        data = self.df[col].dropna()

        if pd.api.types.is_numeric_dtype(data):
            ax.hist(data, bins=30, alpha=0.7, edgecolor='black')
            ax.set_title(f'Histograma de {col}')
            ax.set_xlabel(col)
            ax.set_ylabel('Frecuencia')
        else:
            data.value_counts().plot(kind='bar', ax=ax)
            ax.set_title(f'Histograma de {col}')
            ax.set_xlabel(col)
            ax.set_ylabel('Frecuencia')

    def _create_scatter(self, ax):
        """Crear scatter plot"""
        if len(self.columns) >= 2:
            x_col, y_col = self.columns[0], self.columns[1]
            x_data = self.df[x_col].dropna()
            y_data = self.df[y_col].dropna()

            # Filtrar datos comunes
            common_index = x_data.index.intersection(y_data.index)
            x_data = x_data.loc[common_index]
            y_data = y_data.loc[common_index]

            ax.scatter(x_data, y_data, alpha=0.6)
            ax.set_title(f'Scatter Plot: {x_col} vs {y_col}')
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
        else:
            ax.text(0.5, 0.5, 'Selecciona dos columnas para scatter plot',
                    ha='center', va='center', transform=ax.transAxes)

    def _create_boxplot(self, ax):
        """Crear box plot"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            data = self.df[numeric_cols].dropna()
            ax.boxplot(data.values, labels=numeric_cols)
            ax.set_title('Box Plot de Columnas Numéricas')
            ax.set_ylabel('Valor')
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.text(0.5, 0.5, 'No hay columnas numéricas para box plot',
                    ha='center', va='center', transform=ax.transAxes)

    def _create_correlation(self, ax):
        """Crear mapa de correlación"""
        numeric_df = self.df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            corr = numeric_df.corr()
            sns.heatmap(corr, annot=True, cmap='coolwarm', center=0,
                        square=True, ax=ax)
            ax.set_title('Mapa de Correlación')
        else:
            ax.text(0.5, 0.5, 'Necesitas al menos 2 columnas numéricas',
                    ha='center', va='center', transform=ax.transAxes)

    def _create_line(self, ax):
        """Crear gráfico de línea"""
        if len(self.columns) >= 2:
            x_col, y_col = self.columns[0], self.columns[1]
            x_data = self.df[x_col].dropna()
            y_data = self.df[y_col].dropna()

            # Filtrar datos comunes y ordenar por x
            common_index = x_data.index.intersection(y_data.index)
            data = pd.DataFrame({x_col: x_data.loc[common_index],
                                y_col: y_data.loc[common_index]}).sort_values(x_col)

            ax.plot(data[x_col], data[y_col])
            ax.set_title(f'Gráfico de Línea: {x_col} vs {y_col}')
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
        else:
            ax.text(0.5, 0.5, 'Selecciona dos columnas para gráfico de línea',
                    ha='center', va='center', transform=ax.transAxes)


class GraphicsView(QWidget):
    """
    Vista para mostrar visualizaciones y tabla de datos
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.df = None
        self.current_canvas = None
        self.worker = None
        self.table_model = None
        self.setup_ui()

    def setup_ui(self):
        """Configurar la interfaz de la vista de gráficos"""
        main_layout = QVBoxLayout(self)

        # Controles de visualización
        controls_group = QGroupBox("Controles de Visualización")
        controls_layout = QVBoxLayout(controls_group)

        # Selector de tipo de gráfico
        plot_type_layout = QHBoxLayout()
        plot_type_layout.addWidget(QLabel("Tipo de Gráfico:"))
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems([
            'Histograma', 'Scatter Plot', 'Box Plot',
            'Mapa de Correlación', 'Gráfico de Línea'
        ])
        plot_type_layout.addWidget(self.plot_type_combo)
        controls_layout.addLayout(plot_type_layout)

        # Selectores de columnas
        columns_layout = QHBoxLayout()
        columns_layout.addWidget(QLabel("Columna X:"))
        self.x_column_combo = QComboBox()
        columns_layout.addWidget(self.x_column_combo)

        columns_layout.addWidget(QLabel("Columna Y:"))
        self.y_column_combo = QComboBox()
        columns_layout.addWidget(self.y_column_combo)
        controls_layout.addLayout(columns_layout)

        # Botón para generar gráfico
        self.generate_btn = QPushButton("Generar Gráfico")
        self.generate_btn.clicked.connect(self.generate_plot)
        controls_layout.addWidget(self.generate_btn)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)

        main_layout.addWidget(controls_group)

        # Área para el gráfico y tabla
        content_layout = QHBoxLayout()

        # Área para el gráfico
        plot_group = QGroupBox("Visualización")
        plot_layout = QVBoxLayout(plot_group)

        self.plot_area = QScrollArea()
        self.plot_area.setWidgetResizable(True)
        self.plot_widget = QWidget()
        self.plot_widget_layout = QVBoxLayout(self.plot_widget)
        self.plot_area.setWidget(self.plot_widget)
        plot_layout.addWidget(self.plot_area)

        content_layout.addWidget(plot_group, 1)

        # Área para la tabla
        table_group = QGroupBox("Datos Filtrados")
        table_layout = QVBoxLayout(table_group)

        self.table_view = QTableView()
        table_layout.addWidget(self.table_view)

        content_layout.addWidget(table_group, 1)

        main_layout.addLayout(content_layout)

        # Conectar cambios en el tipo de gráfico
        self.plot_type_combo.currentTextChanged.connect(self.update_column_selectors)

    def update_data(self, df: pd.DataFrame):
        """
        Actualizar los datos para visualización

        Args:
            df: DataFrame de Pandas
        """
        self.df = df

        # Actualizar selectores de columnas
        self.x_column_combo.clear()
        self.y_column_combo.clear()

        if df is not None and not df.empty:
            self.x_column_combo.addItems(df.columns.tolist())
            self.y_column_combo.addItems(df.columns.tolist())

            # Actualizar tabla
            self.table_model = VirtualizedPandasModel(df)
            self.table_view.setModel(self.table_model)

        self.update_column_selectors()

    def update_column_selectors(self):
        """Actualizar la visibilidad de selectores de columnas basado en el tipo de gráfico"""
        plot_type = self.plot_type_combo.currentText()

        if plot_type in ['Histograma', 'Box Plot']:
            self.x_column_combo.setVisible(True)
            self.y_column_combo.setVisible(False)
        elif plot_type in ['Scatter Plot', 'Gráfico de Línea']:
            self.x_column_combo.setVisible(True)
            self.y_column_combo.setVisible(True)
        elif plot_type == 'Mapa de Correlación':
            self.x_column_combo.setVisible(False)
            self.y_column_combo.setVisible(False)
        else:
            self.x_column_combo.setVisible(True)
            self.y_column_combo.setVisible(False)

    def generate_plot(self):
        """Generar el gráfico seleccionado"""
        if self.df is None or self.df.empty:
            QMessageBox.warning(self, "Advertencia", "No hay datos para visualizar.")
            return

        plot_type_spanish = self.plot_type_combo.currentText()
        columns = []

        # Map Spanish names to English keys
        plot_type_map = {
            'Histograma': 'histogram',
            'Scatter Plot': 'scatter',
            'Box Plot': 'boxplot',
            'Mapa de Correlación': 'correlation',
            'Gráfico de Línea': 'line'
        }
        plot_type = plot_type_map.get(plot_type_spanish, plot_type_spanish.lower().replace(' ', ''))

        if plot_type_spanish in ['Histograma', 'Box Plot']:
            if not self.x_column_combo.currentText():
                QMessageBox.warning(self, "Advertencia", "Selecciona una columna.")
                return
            columns.append(self.x_column_combo.currentText())
        elif plot_type_spanish in ['Scatter Plot', 'Gráfico de Línea']:
            if not self.x_column_combo.currentText() or not self.y_column_combo.currentText():
                QMessageBox.warning(self, "Advertencia", "Selecciona ambas columnas.")
                return
            columns.extend([self.x_column_combo.currentText(), self.y_column_combo.currentText()])

        # Mostrar barra de progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.generate_btn.setEnabled(False)

        # Crear y ejecutar hilo de trabajo
        self.worker = VisualizationWorker(self.df, plot_type, columns)
        self.worker.finished.connect(self.on_plot_finished)
        self.worker.error.connect(self.on_plot_error)
        self.worker.start()

    def on_plot_finished(self, fig):
        """Manejar la finalización de la generación del gráfico"""
        # Ocultar barra de progreso
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)

        # Limpiar área de gráfico anterior
        for i in reversed(range(self.plot_widget_layout.count())):
            widget = self.plot_widget_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Crear canvas en el hilo principal
        canvas = FigureCanvas(fig)

        # Añadir nuevo gráfico
        self.current_canvas = canvas
        self.plot_widget_layout.addWidget(canvas)

        # Ajustar tamaño
        canvas.setMinimumSize(400, 300)

    def on_plot_error(self, error_msg):
        """Manejar errores en la generación del gráfico"""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Error al generar gráfico: {error_msg}")