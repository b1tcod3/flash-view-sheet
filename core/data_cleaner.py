"""
Funciones puras de limpieza de datos.

Todas las funciones operan sobre un DataFrame y devuelven otro DataFrame
(o un dict con estadísticas). Sin efectos secundarios ni dependencias de UI.
"""

import pandas as pd


def limpiar_nulos(df: pd.DataFrame, estrategia: str = 'eliminar') -> pd.DataFrame:
    """
    Eliminar o rellenar valores nulos.

    Estrategias:
    - 'eliminar': dropna()
    - 'cero': fillna(0)
    - 'promedio': fillna con la media (solo columnas numéricas)
    """
    if estrategia == 'eliminar':
        return df.dropna()
    if estrategia == 'cero':
        return df.fillna(0)
    if estrategia == 'promedio':
        result = df.copy()
        numeric_cols = result.select_dtypes(include='number').columns
        result[numeric_cols] = result[numeric_cols].fillna(result[numeric_cols].mean())
        return result
    raise ValueError(f"Estrategia no válida: '{estrategia}'. Usa 'eliminar', 'cero' o 'promedio'.")


def eliminar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """Eliminar filas duplicadas."""
    return df.drop_duplicates()


def limpiar_espacios_texto(df: pd.DataFrame) -> pd.DataFrame:
    """Aplicar str.strip() a todas las columnas de tipo object."""
    result = df.copy()
    for col in result.select_dtypes(include='object').columns:
        result[col] = result[col].str.strip()
    return result


def limpieza_rapida(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica nulos→eliminar → duplicados → espacios.
    Macro de uso frecuente.
    """
    result = limpiar_nulos(df, estrategia='eliminar')
    result = eliminar_duplicados(result)
    result = limpiar_espacios_texto(result)
    return result


def resumen_limpieza(df_original: pd.DataFrame, df_limpio: pd.DataFrame) -> dict[str, int | list[str]]:
    """
    Genera estadísticas comparativas entre el DataFrame original y el limpio.

    Devuelve:
    - rows_original: filas originales
    - rows_final: filas finales
    - rows_removed: filas eliminadas
    - columns_affected: columnas que cambiaron (por tener nulos o espacios)
    """
    cols_with_nulos = [
        col for col in df_original.columns
        if df_original[col].isna().any()
    ]
    cols_with_espacios = [
        col for col in df_original.select_dtypes(include='object').columns
        if df_original[col].str.strip().ne(df_original[col]).any()
    ]
    affected: list[str] = list(set(cols_with_nulos + cols_with_espacios))

    return {
        'rows_original': len(df_original),
        'rows_final': len(df_limpio),
        'rows_removed': len(df_original) - len(df_limpio),
        'columns_affected': affected,
    }
