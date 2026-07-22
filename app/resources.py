"""
Gestión centralizada de recursos estáticos de la aplicación.
"""

from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ASSETS_DIR = _PROJECT_ROOT / "assets"


def get_asset_path(asset_name: str) -> Path:
    """
    Devuelve la ruta absoluta a un recurso dentro de la carpeta assets/.

    Args:
        asset_name: Nombre del archivo (ej. 'logo.png').

    Returns:
        Path completo al recurso.
    """
    return _ASSETS_DIR / asset_name
