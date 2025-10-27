"""
Módulo para manejo de datos - carga, análisis y exportación
"""

import pandas as pd
import os
from typing import Optional, Tuple, Dict, Any


def cargar_datos(filepath: str) -> pd.DataFrame:
    """
    Cargar datos desde un archivo Excel o CSV
    
    Args:
        filepath: Ruta del archivo a cargar
        
    Returns:
        DataFrame de Pandas con los datos cargados
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo no es soportado
        Exception: Para otros errores de carga
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"El archivo no existe: {filepath}")
    
    # Determinar el tipo de archivo por extensión
    extension = os.path.splitext(filepath)[1].lower()
    
    try:
        if extension in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath)
        elif extension == '.csv':
            df = pd.read_csv(filepath)
        else:
            raise ValueError(f"Formato de archivo no soportado: {extension}")
    except Exception as e:
        raise Exception(f"Error al cargar el archivo {filepath}: {str(e)}")
    
    return df


def obtener_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Obtener metadata del DataFrame
    
    Args:
        df: DataFrame de Pandas
        
    Returns:
        Diccionario con información sobre los datos
    """
    metadata = {
        'filas': df.shape[0],
        'columnas': df.shape[1],
        'nombres_columnas': df.columns.tolist(),
        'tipos_datos': df.dtypes.astype(str).tolist(),
        'columnas_numericas': df.select_dtypes(include=['number']).columns.tolist(),
        'columnas_texto': df.select_dtypes(include=['object']).columns.tolist(),
        'valores_nulos': df.isnull().sum().to_dict()
    }
    
    return metadata


def obtener_estadisticas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Obtener estadísticas descriptivas del DataFrame
    
    Args:
        df: DataFrame de Pandas
        
    Returns:
        DataFrame con estadísticas descriptivas
    """
    try:
        # Obtener estadísticas para todas las columnas
        estadisticas = df.describe(include='all')
        return estadisticas
    except Exception as e:
        # Si hay error, devolver DataFrame vacío
        return pd.DataFrame()


def aplicar_filtro(df: pd.DataFrame, columna: str, termino: str) -> pd.DataFrame:
    """
    Aplicar filtro a los datos
    
    Args:
        df: DataFrame original
        columna: Nombre de la columna a filtrar
        termino: Término de búsqueda
        
    Returns:
        DataFrame filtrado
    """
    if columna not in df.columns:
        raise ValueError(f"Columna no encontrada: {columna}")
    
    # Filtrar por contenido de texto (case-insensitive)
    df_filtrado = df[df[columna].astype(str).str.contains(termino, case=False, na=False)]
    
    return df_filtrado


def exportar_a_pdf(df: pd.DataFrame, filepath: str) -> bool:
    """
    Exportar DataFrame a archivo PDF
    
    Args:
        df: DataFrame a exportar
        filepath: Ruta de destino
        
    Returns:
        True si la exportación fue exitosa
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        from reportlab.lib import colors
        
        # Crear documento
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        
        # Convertir DataFrame a lista de listas
        data = [df.columns.tolist()] + df.values.tolist()
        
        # Crear tabla
        tabla = Table(data)
        estilo = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        tabla.setStyle(estilo)
        
        # Construir documento
        doc.build([tabla])
        return True
        
    except Exception as e:
        print(f"Error al exportar a PDF: {str(e)}")
        return False


def exportar_a_sql(df: pd.DataFrame, filepath: str, nombre_tabla: str) -> bool:
    """
    Exportar DataFrame a base de datos SQL
    
    Args:
        df: DataFrame a exportar
        filepath: Ruta de la base de datos
        nombre_tabla: Nombre de la tabla en la base de datos
        
    Returns:
        True si la exportación fue exitosa
    """
    try:
        from sqlalchemy import create_engine
        
        # Crear engine para SQLite
        engine = create_engine(f'sqlite:///{filepath}')
        
        # Exportar a SQL
        df.to_sql(nombre_tabla, engine, if_exists='replace', index=False)
        return True
        
    except Exception as e:
        print(f"Error al exportar a SQL: {str(e)}")
        return False