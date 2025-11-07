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

# Widgets de Tabla Pivote
from .pivot_table_widget import PivotTableWidget
from .pivot_config_dialog import PivotConfigDialog
from .pivot_filter_panel import PivotFilterPanel
from .pivot_aggregation_panel import PivotAggregationPanel

__all__ = [
    'InfoPanel',
    'VisualizationPanel',
    'MainView',
    'InfoModal',
    'GraphicsView',
    'LoadOptionsDialog',
    'ExportSeparatedDialog',
    # Widgets de Tabla Pivote
    'PivotTableWidget',
    'PivotConfigDialog',
    'PivotFilterPanel',
    'PivotAggregationPanel'
]