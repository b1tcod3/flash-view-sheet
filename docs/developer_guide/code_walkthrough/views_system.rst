Views System Architecture
========================

The views system in Flash Sheet implements a modular architecture for displaying and interacting with different types of data and visualizations.

Architecture Overview
---------------------

View Hierarchy
~~~~~~~~~~~~~~

The views system is built around a base View class with specialized implementations:

- **BaseView**: Abstract base class defining common interface
- **MainView**: Initial view with data loading options
- **DataView**: Primary data table display with manipulation tools
- **GraphicsView**: Chart and visualization interface
- **JoinedDataView**: Specialized view for join operation results
- **PivotView**: Pivot table creation and editing interface

View Management
~~~~~~~~~~~~~~~

Views are managed through the MainWindow's QStackedWidget:

.. code-block:: python

    class ViewManager:
        def __init__(self, stacked_widget):
            self.stacked_widget = stacked_widget
            self.views = {}
            self.current_view = None

        def register_view(self, name, view_instance):
            self.views[name] = view_instance
            self.stacked_widget.addWidget(view_instance)

        def switch_to_view(self, name):
            if name in self.views:
                self.stacked_widget.setCurrentWidget(self.views[name])
                self.current_view = name
                self.views[name].on_activated()

Base View Interface
-------------------

Common Interface
~~~~~~~~~~~~~~~~

All views implement a standard interface for consistency:

.. code-block:: python

    class BaseView(QWidget):
        # Signals
        data_changed = Signal()
        view_closed = Signal()
        export_requested = Signal(str)  # format

        def __init__(self, parent=None):
            super().__init__(parent)
            self.data = None
            self.setup_ui()

        def setup_ui(self):
            """Initialize the view's user interface"""
            raise NotImplementedError

        def set_data(self, data):
            """Load data into the view"""
            self.data = data
            self.update_display()

        def get_data(self):
            """Retrieve current data from the view"""
            return self.data

        def clear_data(self):
            """Reset view to empty state"""
            self.data = None
            self.update_display()

        def get_export_data(self):
            """Prepare data for export"""
            return self.data

        def update_display(self):
            """Refresh the visual display"""
            raise NotImplementedError

        def on_activated(self):
            """Called when view becomes active"""
            pass

DataView Implementation
-----------------------

Table Display Core
~~~~~~~~~~~~~~~~~~

DataView provides the primary data table interface:

.. code-block:: python

    class DataView(BaseView):
        def setup_ui(self):
            layout = QVBoxLayout()

            # Toolbar
            self.toolbar = self.create_toolbar()
            layout.addWidget(self.toolbar)

            # Table widget
            self.table = QTableWidget()
            self.table.setAlternatingRowColors(True)
            self.table.setSortingEnabled(True)
            layout.addWidget(self.table)

            # Status bar
            self.status_label = QLabel()
            layout.addWidget(self.status_label)

            self.setLayout(layout)

Data Table Features
~~~~~~~~~~~~~~~~~~~

Advanced table functionality for data exploration:

.. code-block:: python

    def setup_table(self):
        # Enable sorting
        self.table.setSortingEnabled(True)

        # Set selection behavior
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Configure headers
        horizontal_header = self.table.horizontalHeader()
        horizontal_header.setStretchLastSection(True)
        horizontal_header.setSectionsMovable(True)

        # Connect signals
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)

Pagination System
~~~~~~~~~~~~~~~~~

Efficient handling of large datasets:

.. code-block:: python

    class PaginationWidget(QWidget):
        def __init__(self, table_view, page_size=100):
            super().__init__()
            self.table_view = table_view
            self.page_size = page_size
            self.current_page = 0
            self.total_pages = 0

            self.setup_ui()

        def setup_ui(self):
            layout = QHBoxLayout()

            self.first_btn = QPushButton("<<")
            self.prev_btn = QPushButton("<")
            self.page_label = QLabel("Page 1 of 1")
            self.next_btn = QPushButton(">")
            self.last_btn = QPushButton(">>")

            layout.addWidget(self.first_btn)
            layout.addWidget(self.prev_btn)
            layout.addWidget(self.page_label)
            layout.addWidget(self.next_btn)
            layout.addWidget(self.last_btn)

            self.setLayout(layout)
            self.connect_signals()

Filtering and Search
~~~~~~~~~~~~~~~~~~~~

Real-time data filtering capabilities:

.. code-block:: python

    class FilterWidget(QWidget):
        def __init__(self, data_view):
            super().__init__()
            self.data_view = data_view
            self.filters = {}

            self.setup_ui()

        def setup_ui(self):
            layout = QVBoxLayout()

            # Global search
            self.search_box = QLineEdit()
            self.search_box.setPlaceholderText("Search all columns...")
            layout.addWidget(self.search_box)

            # Column-specific filters
            self.filter_layout = QVBoxLayout()
            layout.addLayout(self.filter_layout)

            self.setLayout(layout)
            self.connect_signals()

        def add_column_filter(self, column_name, data_type):
            if data_type == 'string':
                filter_widget = QLineEdit()
                filter_widget.setPlaceholderText(f"Filter {column_name}")
            elif data_type in ['int64', 'float64']:
                filter_widget = QHBoxLayout()
                min_spin = QSpinBox()
                max_spin = QSpinBox()
                filter_widget.addWidget(min_spin)
                filter_widget.addWidget(QLabel("-"))
                filter_widget.addWidget(max_spin)
            # Add date filters, etc.

            self.filters[column_name] = filter_widget
            self.filter_layout.addWidget(filter_widget)

GraphicsView Implementation
---------------------------

Chart Creation Interface
~~~~~~~~~~~~~~~~~~~~~~~~

Visualization view for creating and managing charts:

.. code-block:: python

    class GraphicsView(BaseView):
        def setup_ui(self):
            layout = QVBoxLayout()

            # Chart type selector
            self.chart_type_combo = QComboBox()
            self.chart_type_combo.addItems([
                'Bar Chart', 'Line Chart', 'Pie Chart',
                'Scatter Plot', 'Histogram', 'Box Plot'
            ])
            layout.addWidget(self.chart_type_combo)

            # Chart configuration
            self.config_widget = ChartConfigWidget()
            layout.addWidget(self.config_widget)

            # Chart display area
            self.chart_view = QChartView()
            layout.addWidget(self.chart_view)

            # Export options
            self.export_widget = ChartExportWidget()
            layout.addWidget(self.export_widget)

            self.setLayout(layout)

Chart Configuration
~~~~~~~~~~~~~~~~~~~

Dynamic chart configuration based on selected type:

.. code-block:: python

    class ChartConfigWidget(QWidget):
        def __init__(self):
            super().__init__()
            self.current_config = None

        def set_chart_type(self, chart_type):
            # Clear previous configuration
            self.clear_config()

            if chart_type == 'bar':
                self.current_config = BarChartConfig()
            elif chart_type == 'line':
                self.current_config = LineChartConfig()
            # etc.

            self.layout().addWidget(self.current_config)

        def get_chart_config(self):
            return self.current_config.get_config() if self.current_config else {}

Chart Rendering Engine
~~~~~~~~~~~~~~~~~~~~~~

Qt Charts integration for high-performance rendering:

.. code-block:: python

    def render_chart(self, config):
        chart = QChart()

        # Create series based on config
        if config['type'] == 'bar':
            series = QBarSeries()
            for category, value in config['data'].items():
                bar_set = QBarSet(category)
                bar_set.append(value)
                series.append(bar_set)
        elif config['type'] == 'line':
            series = QLineSeries()
            for point in config['data']:
                series.append(point[0], point[1])

        chart.addSeries(series)

        # Configure axes
        axis_x = QBarCategoryAxis()
        axis_x.append(config['categories'])
        chart.setAxisX(axis_x, series)

        axis_y = QValueAxis()
        chart.setAxisY(axis_y, series)

        self.chart_view.setChart(chart)

JoinedDataView Implementation
-----------------------------

Specialized Join Results View
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dedicated interface for displaying join operation results:

.. code-block:: python

    class JoinedDataView(BaseView):
        def setup_ui(self):
            layout = QVBoxLayout()

            # Join metadata display
            self.metadata_widget = JoinMetadataWidget()
            layout.addWidget(self.metadata_widget)

            # Results table
            self.results_table = QTableWidget()
            layout.addWidget(self.results_table)

            # Join statistics
            self.stats_widget = JoinStatsWidget()
            layout.addWidget(self.stats_widget)

            self.setLayout(layout)

Join Metadata Display
~~~~~~~~~~~~~~~~~~~~~

Information about the join operation performed:

.. code-block:: python

    class JoinMetadataWidget(QWidget):
        def __init__(self):
            super().__init__()
            self.setup_ui()

        def setup_ui(self):
            layout = QFormLayout()

            self.join_type_label = QLabel()
            self.left_table_label = QLabel()
            self.right_table_label = QLabel()
            self.join_keys_label = QLabel()
            self.result_rows_label = QLabel()

            layout.addRow("Join Type:", self.join_type_label)
            layout.addRow("Left Table:", self.left_table_label)
            layout.addRow("Right Table:", self.right_table_label)
            layout.addRow("Join Keys:", self.join_keys_label)
            layout.addRow("Result Rows:", self.result_rows_label)

            self.setLayout(layout)

        def update_metadata(self, join_info):
            self.join_type_label.setText(join_info['type'])
            self.left_table_label.setText(join_info['left_table'])
            self.right_table_label.setText(join_info['right_table'])
            self.join_keys_label.setText(', '.join(join_info['keys']))
            self.result_rows_label.setText(str(join_info['result_count']))

View Communication
------------------

Inter-View Data Flow
~~~~~~~~~~~~~~~~~~~~

Views communicate through the MainWindow coordinator:

.. code-block:: python

    # In MainWindow
    def on_data_loaded(self, data):
        current_view = self.stacked_widget.currentWidget()
        if hasattr(current_view, 'set_data'):
            current_view.set_data(data)

    def on_view_changed(self, index):
        new_view = self.stacked_widget.widget(index)
        if hasattr(new_view, 'on_activated'):
            new_view.on_activated()

Signal-Based Updates
~~~~~~~~~~~~~~~~~~~~

Views emit signals to notify of changes:

.. code-block:: python

    # In DataView
    def on_item_changed(self, item):
        # Update internal data
        row, col = item.row(), item.column()
        self.data.iloc[row, col] = item.text()

        # Notify other components
        self.data_changed.emit()

View State Management
~~~~~~~~~~~~~~~~~~~~~

Preserving view state during switches:

.. code-block:: python

    class ViewState:
        def __init__(self):
            self.scroll_position = 0
            self.selected_rows = []
            self.filter_settings = {}
            self.sort_column = 0
            self.sort_order = Qt.AscendingOrder

        def save_state(self, view):
            # Save current view state
            pass

        def restore_state(self, view):
            # Restore saved state
            pass

Performance Optimization
------------------------

Lazy Loading
~~~~~~~~~~~~

Load view components on demand:

.. code-block:: python

    def load_view_components(self):
        if not self.components_loaded:
            # Load heavy components
            self.load_table_data()
            self.load_chart_components()
            self.components_loaded = True

Memory Management
~~~~~~~~~~~~~~~~~

Efficient memory usage for large datasets:

.. code-block:: python

    def optimize_for_large_data(self, data_size):
        if data_size > 100000:  # 100K rows
            # Disable real-time sorting
            self.table.setSortingEnabled(False)

            # Enable pagination
            self.enable_pagination()

            # Use virtual scrolling
            self.enable_virtual_scrolling()

Virtual Scrolling
~~~~~~~~~~~~~~~~~

Display large datasets without loading all data:

.. code-block:: python

    class VirtualTableModel(QAbstractTableModel):
        def __init__(self, data_source, page_size=1000):
            super().__init__()
            self.data_source = data_source
            self.page_size = page_size
            self.current_page = 0
            self.cache = {}

        def rowCount(self, parent=QModelIndex()):
            return self.data_source.total_rows

        def columnCount(self, parent=QModelIndex()):
            return self.data_source.total_columns

        def data(self, index, role=Qt.DisplayRole):
            if role == Qt.DisplayRole:
                page = index.row() // self.page_size
                if page not in self.cache:
                    self.cache[page] = self.data_source.load_page(page)

                row_in_page = index.row() % self.page_size
                return self.cache[page].iloc[row_in_page, index.column()]

            return None

Testing and Quality Assurance
-----------------------------

View Testing Framework
~~~~~~~~~~~~~~~~~~~~~~

Comprehensive testing for view components:

.. code-block:: python

    def test_data_view(self):
        # Create test data
        test_df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['x', 'y', 'z']
        })

        # Create view
        view = DataView()

        # Test data loading
        view.set_data(test_df)
        self.assertEqual(view.table.rowCount(), 3)
        self.assertEqual(view.table.columnCount(), 2)

        # Test data retrieval
        retrieved_data = view.get_data()
        pd.testing.assert_frame_equal(retrieved_data, test_df)

Accessibility and Usability
---------------------------

Keyboard Navigation
~~~~~~~~~~~~~~~~~~~

Full keyboard accessibility:

- **Tab Navigation**: Move between controls
- **Arrow Keys**: Navigate table cells
- **Enter/Space**: Activate buttons and controls
- **Shortcut Keys**: Common operations (Ctrl+C, Ctrl+V, etc.)

Screen Reader Support
~~~~~~~~~~~~~~~~~~~~~

Accessibility features for assistive technologies:

.. code-block:: python

    def setup_accessibility(self):
        # Set accessible names and descriptions
        self.table.setAccessibleName("Data table")
        self.table.setAccessibleDescription("Main data display table")

        # Configure table headers
        for col in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(col)
            header_item.setAccessibleDescription(f"Column {col + 1}")

Theme and Styling
~~~~~~~~~~~~~~~~~~

Customizable appearance:

.. code-block:: python

    def apply_theme(self, theme_name):
        if theme_name == 'dark':
            self.setStyleSheet("""
                QTableWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
            """)
        elif theme_name == 'light':
            self.setStyleSheet("""
                QTableWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
            """)

Future Enhancements
-------------------

Planned Improvements
~~~~~~~~~~~~~~~~~~~~

- **Advanced Filtering**: Multi-column, regex, and custom filters
- **Data Editing**: In-place cell editing with validation
- **Collaborative Views**: Multi-user simultaneous editing
- **Custom View Plugins**: Third-party view extensions
- **3D Visualization**: Three-dimensional data visualization
- **Real-time Updates**: Live data streaming and updates