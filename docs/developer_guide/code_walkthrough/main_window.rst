Main Window Architecture
========================

The MainWindow class serves as the central coordinator for the Flash Sheet application, managing the overall UI layout, view switching, and application state.

Class Overview
--------------

MainWindow inherits from PySide6's QMainWindow and implements the main application window with menu system, toolbar, and stacked widget for view management.

Key Responsibilities
~~~~~~~~~~~~~~~~~~~~

- **UI Initialization**: Set up menus, toolbars, and central widget
- **View Management**: Handle switching between different application views
- **Data Coordination**: Manage data flow between components
- **Menu Actions**: Implement file operations, data manipulation, and export functions
- **Status Updates**: Display application status and progress information

Initialization Process
----------------------

Window Setup
~~~~~~~~~~~~

.. code-block:: python

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flash Sheet - Data Analysis Tool")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()
        self.setup_connections()

UI Component Setup
~~~~~~~~~~~~~~~~~~

The setup_ui() method creates the main interface components:

- **Menu Bar**: File, Edit, View, Data, Help menus
- **Tool Bar**: Quick access buttons for common operations
- **Status Bar**: Progress indicators and status messages
- **Central Widget**: QStackedWidget containing different views

View System Architecture
------------------------

Stacked Widget Management
~~~~~~~~~~~~~~~~~~~~~~~~~

The application uses a QStackedWidget to manage multiple views:

.. code-block:: python

    self.stacked_widget = QStackedWidget()
    self.setCentralWidget(self.stacked_widget)

    # Add views
    self.main_view = MainView()
    self.data_view = DataView()
    self.graphics_view = GraphicsView()
    self.joined_data_view = JoinedDataView()

    self.stacked_widget.addWidget(self.main_view)
    self.stacked_widget.addWidget(self.data_view)
    # ... add other views

View Switching Logic
~~~~~~~~~~~~~~~~~~~~

View switching is handled through menu actions and toolbar buttons:

.. code-block:: python

    def switch_to_data_view(self):
        self.stacked_widget.setCurrentWidget(self.data_view)
        self.update_menu_state()

Menu System Implementation
--------------------------

File Menu
~~~~~~~~~

Handles data loading and application lifecycle:

- **Load File**: Open file dialog and load data
- **Load Folder**: Batch loading functionality
- **Save/Export**: Data export operations
- **Exit**: Application shutdown

Data Menu
~~~~~~~~~

Advanced data operations:

- **Join Data**: Cross-dataset operations
- **Pivot Table**: Data summarization
- **Filter Data**: Data filtering interface
- **Transform Data**: Data manipulation tools

View Menu
~~~~~~~~~

Interface management:

- **Data View**: Table display
- **Graphics View**: Chart visualization
- **Joined Data View**: Join results
- **Full Screen**: Toggle fullscreen mode

Data Flow Coordination
----------------------

Data Loading Pipeline
~~~~~~~~~~~~~~~~~~~~~

1. **File Selection**: User selects file(s)
2. **Format Detection**: Automatic format recognition
3. **Data Parsing**: Format-specific parsing
4. **Data Validation**: Integrity and type checking
5. **View Update**: Display data in appropriate view
6. **Status Update**: Inform user of completion

.. code-block:: python

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Data File", "", self.get_file_filters()
        )
        if file_path:
            try:
                data = self.data_handler.load_file(file_path)
                self.update_views_with_data(data)
                self.statusBar().showMessage(f"Loaded: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")

Export Coordination
~~~~~~~~~~~~~~~~~~~

Export operations coordinate between views and export handlers:

.. code-block:: python

    def export_data(self, format_type):
        current_view = self.stacked_widget.currentWidget()
        if hasattr(current_view, 'get_export_data'):
            data = current_view.get_export_data()
            export_handler = self.get_export_handler(format_type)
            export_handler.export(data)

Signal and Slot Connections
---------------------------

Event Handling
~~~~~~~~~~~~~~

The MainWindow connects various signals to maintain application state:

- **View Change Signals**: Update menus when views change
- **Data Change Signals**: Refresh displays when data updates
- **Progress Signals**: Show progress for long operations
- **Error Signals**: Display error messages to user

Connection Setup
~~~~~~~~~~~~~~~~

.. code-block:: python

    def setup_connections(self):
        # Menu connections
        self.action_load_file.triggered.connect(self.load_file)
        self.action_export_csv.triggered.connect(lambda: self.export_data('csv'))

        # View change connections
        self.stacked_widget.currentChanged.connect(self.on_view_changed)

        # Data handler connections
        self.data_handler.data_loaded.connect(self.on_data_loaded)
        self.data_handler.progress_updated.connect(self.update_progress)

Status and Progress Management
------------------------------

Status Bar Updates
~~~~~~~~~~~~~~~~~~

The status bar provides real-time feedback:

- **Operation Status**: Current operation description
- **Progress Bar**: Visual progress indication
- **Data Statistics**: Row/column counts
- **Memory Usage**: Current memory consumption

Progress Dialogs
~~~~~~~~~~~~~~~~

For long-running operations:

.. code-block:: python

    def show_progress_dialog(self, operation_name):
        self.progress_dialog = QProgressDialog(
            f"Processing {operation_name}...", "Cancel", 0, 100, self
        )
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

Error Handling
--------------

Exception Management
~~~~~~~~~~~~~~~~~~~~

Centralized error handling for user-friendly messages:

.. code-block:: python

    def handle_error(self, error, context=""):
        error_msg = f"Error {context}: {str(error)}"
        self.logger.error(error_msg)
        QMessageBox.critical(self, "Error", error_msg)

Recovery Mechanisms
~~~~~~~~~~~~~~~~~~~

- **Auto-save**: Periodic state saving
- **Graceful Degradation**: Continue operation with reduced functionality
- **User Guidance**: Clear error messages with suggested actions

Integration Points
------------------

Data Handler Integration
~~~~~~~~~~~~~~~~~~~~~~~~

The MainWindow coordinates with the DataHandler for data operations:

.. code-block:: python

    self.data_handler = DataHandler()
    self.data_handler.data_loaded.connect(self.on_data_loaded)

View Integration
~~~~~~~~~~~~~~~~

Each view implements standard interfaces for data exchange:

- **set_data(data)**: Load data into view
- **get_data()**: Retrieve current data
- **clear_data()**: Reset view state
- **get_export_data()**: Prepare data for export

Plugin Architecture
~~~~~~~~~~~~~~~~~~~

Future extensibility through plugin interfaces:

- **View Plugins**: Custom visualization views
- **Export Plugins**: Additional export formats
- **Data Source Plugins**: New data loading capabilities

Performance Considerations
--------------------------

Memory Management
~~~~~~~~~~~~~~~~~

- **Lazy Loading**: Load data on demand
- **View Caching**: Cache view states
- **Garbage Collection**: Explicit cleanup when switching views

UI Responsiveness
~~~~~~~~~~~~~~~~~

- **Threading**: Background processing for heavy operations
- **Progress Updates**: Regular UI updates during processing
- **Cancellation Support**: Allow user to cancel operations

Testing and Debugging
---------------------

Unit Testing
~~~~~~~~~~~~

MainWindow components should be testable:

- **Mock Views**: Test view switching logic
- **Mock Data Handler**: Test data flow
- **Event Simulation**: Test signal/slot connections

Debug Features
~~~~~~~~~~~~~~

- **Logging**: Comprehensive operation logging
- **Performance Profiling**: Identify bottlenecks
- **UI Debugging**: Inspect widget hierarchies

Future Enhancements
-------------------

Planned Improvements
~~~~~~~~~~~~~~~~~~~~

- **Multiple Document Interface**: Support multiple datasets simultaneously
- **Workspace Saving**: Save/restore complete application state
- **Undo/Redo System**: Operation history and reversal
- **Collaboration Features**: Multi-user editing capabilities

Extensibility
~~~~~~~~~~~~~

- **Plugin API**: Third-party extension support
- **Theme System**: Customizable UI themes
- **Localization**: Multi-language support
- **Accessibility**: Screen reader and keyboard navigation improvements