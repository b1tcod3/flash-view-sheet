"""
View Registry

Registro de vistas disponibles en la aplicación.
Define constantes de índices y metadata de cada vista.
"""


class ViewRegistry:
    """Registro de vistas disponibles"""

    VIEW_MAIN = 0
    VIEW_DATA = 1
    VIEW_INFO = 2
    VIEW_JOIN = 3
    VIEW_PIVOT = 4

    VIEW_NAMES = {
        VIEW_MAIN: "Principal",
        VIEW_DATA: "Datos",
        VIEW_INFO: "Información",
        VIEW_JOIN: "Datos Cruzados",
        VIEW_PIVOT: "Pivote",
    }

    VIEW_DESCRIPTIONS = {
        VIEW_MAIN: "Pantalla de bienvenida y carga de archivos",
        VIEW_DATA: "Visualización tabular con paginación",
        VIEW_INFO: "Información estadística del dataset",
        VIEW_JOIN: "Resultado de cruce de datasets",
        VIEW_PIVOT: "Tablas pivote automáticas por combinación categórica × numérica",
    }

    @classmethod
    def get_view_name(cls, index: int) -> str:
        return cls.VIEW_NAMES.get(index, f"Vista {index}")

    @classmethod
    def get_view_description(cls, index: int) -> str:
        return cls.VIEW_DESCRIPTIONS.get(index, "")

    @classmethod
    def get_all_view_indices(cls) -> list:
        return list(cls.VIEW_NAMES.keys())

    @classmethod
    def is_valid_view(cls, index: int) -> bool:
        return index in cls.VIEW_NAMES
