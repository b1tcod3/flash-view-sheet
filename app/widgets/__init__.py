"""
Widgets para la aplicación Flash View Sheet
"""

# Widgets existentes
from .info_panel import InfoPanel
from .main_view import MainView
from .info_modal import InfoModal
from .load_options_dialog import LoadOptionsDialog
from .csv_separator_dialog import CSVSeparatorDialog
from .excel_sheet_dialog import ExcelSheetDialog
from .export_separated_dialog import ExportSeparatedDialog
from .about_dialog import AboutDialog

# Widgets de Carpeta
from .folder_load_dialog import FolderLoadDialog

# Widgets de Join
from .join.join_dialog import JoinDialog
from .join.joined_data_view import JoinedDataView

# Widget de resultados de pivote
from .pivot_results_view import PivotResultsView

# DataView (widget de paginación)
from .data_view import DataView

__all__ = [
    'InfoPanel',
    'MainView',
    'InfoModal',
    'LoadOptionsDialog',
    'CSVSeparatorDialog',
    'ExcelSheetDialog',
    'ExportSeparatedDialog',
    'AboutDialog',
    'FolderLoadDialog',
    # Widgets de Join
    'JoinDialog',
    'JoinedDataView',
    # Widget de resultados de pivote
    'PivotResultsView',
    # DataView
    'DataView',
]
