"""
View Registry

Registro de vistas disponibles en la aplicación.
Define constantes de índices y metadata de cada vista.
"""


class ViewRegistry:
    """Registro de vistas disponibles"""
    
    # Constantes de índices de vistas
    VIEW_MAIN = 0       # Vista Principal (pantalla de bienvenida)
    VIEW_DATA = 1       # Vista de Datos (tabla paginada)
    VIEW_INFO = 2       # Vista de Información (modal)
    VIEW_GRAPHICS = 3   # Vista de Gráficos
    VIEW_JOIN = 4       # Vista de Datos Cruzados (Join)
    
    # Nombres de vistas para display
    VIEW_NAMES = {
        VIEW_MAIN: "Principal",
        VIEW_DATA: "Datos",
        VIEW_INFO: "Información",
        VIEW_GRAPHICS: "Gráficos",
        VIEW_JOIN: "Datos Cruzados",
    }
    
    # Descripciones de cada vista
    VIEW_DESCRIPTIONS = {
        VIEW_MAIN: "Pantalla de bienvenida y carga de archivos",
        VIEW_DATA: "Visualización tabular con paginación",
        VIEW_INFO: "Información estadística del dataset",
        VIEW_GRAPHICS: "Visualización gráfica de datos",
        VIEW_JOIN: "Resultado de cruce de datasets",
    }
    
    @classmethod
    def get_view_name(cls, index: int) -> str:
        """Obtener nombre de vista por índice"""
        return cls.VIEW_NAMES.get(index, f"Vista {index}")
    
    @classmethod
    def get_view_description(cls, index: int) -> str:
        """Obtener descripción de vista por índice"""
        return cls.VIEW_DESCRIPTIONS.get(index, "")
    
    @classmethod
    def get_all_view_indices(cls) -> list:
        """Obtener lista de todos los índices de vistas"""
        return list(cls.VIEW_NAMES.keys())
    
    @classmethod
    def is_valid_view(cls, index: int) -> bool:
        """Verificar si un índice de vista es válido"""
        return index in cls.VIEW_NAMES
