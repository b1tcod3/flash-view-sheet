"""
Widgets para la aplicación Flash View Sheet
"""

# Widgets existentes
from .info_panel import InfoPanel
from .visualization_panel import VisualizationPanel
from .main_view import MainView
from .info_modal import InfoModal
from .graphics_view import GraphicsView
from .load_options_dialog import LoadOptionsDialog
from .export_separated_dialog import ExportSeparatedDialog
from .about_dialog import AboutDialog

# Widgets de Carpeta
from .folder_load_dialog import FolderLoadDialog

# Widgets de Tabla Pivote
from .pivot_table_widget import PivotTableWidget
from .pivot_config_dialog import PivotConfigDialog
from .pivot_filter_panel import PivotFilterPanel
from .pivot_aggregation_panel import PivotAggregationPanel

# Widgets de Join
from .join.join_dialog import JoinDialog
from .join.joined_data_view import JoinedDataView

# Widgets de Pivot Simple
from .simple_pivot_dialog import SimplePivotDialog

# DataView desde paginacion
from paginacion.data_view import DataView

__all__ = [
    'InfoPanel',
    'VisualizationPanel',
    'MainView',
    'InfoModal',
    'GraphicsView',
    'LoadOptionsDialog',
    'ExportSeparatedDialog',
    'AboutDialog',
    'FolderLoadDialog',
    # Widgets de Tabla Pivote
    'PivotTableWidget',
    'PivotConfigDialog',
    'PivotFilterPanel',
    'PivotAggregationPanel',
    # Widgets de Join
    'JoinDialog',
    'JoinedDataView',
    # Widget de Pivot Simple
    'SimplePivotDialog',
    # DataView
    'DataView',
]
