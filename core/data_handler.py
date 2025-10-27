"""
Módulo para manejo de datos - carga, análisis y exportación
"""

import pandas as pd
import os
from typing import Optional, Tuple, Dict, Any
import sys

# Añadir directorio raíz para importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import optimization_config


def cargar_datos(filepath: str, chunk_size: int = None) -> pd.DataFrame:
    """
    Cargar datos desde un archivo Excel o CSV con optimización para archivos grandes

    Args:
        filepath: Ruta del archivo a cargar
        chunk_size: Tamaño de chunk para lectura (solo para CSV grandes)

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
            # Para Excel, verificar tamaño del archivo usando configuración
            file_size = os.path.getsize(filepath)
            if file_size > optimization_config.CHUNK_LOADING_THRESHOLD:
                print(f"Archivo Excel grande detectado ({file_size / 1024 / 1024:.1f}MB), cargando con optimización...")
                df = pd.read_excel(filepath, engine='openpyxl')
            else:
                df = pd.read_excel(filepath)
        elif extension == '.csv':
            # Para CSV, usar chunks si se especifica o si el archivo es muy grande
            file_size = os.path.getsize(filepath)
            if chunk_size or file_size > optimization_config.CHUNK_LOADING_THRESHOLD:
                if chunk_size is None:
                    chunk_size = optimization_config.get_csv_chunk_size(file_size)
                df = _cargar_csv_en_chunks(filepath, chunk_size)
            else:
                df = pd.read_csv(filepath)
        elif extension == '.json':
            # Para JSON, usar pandas read_json
            df = pd.read_json(filepath)
        elif extension in ['.xml']:
            # Para XML, usar pandas read_xml si está disponible, o lxml
            try:
                df = pd.read_xml(filepath)
            except AttributeError:
                # Si pandas no tiene read_xml, usar lxml
                from lxml import etree
                tree = etree.parse(filepath)
                root = tree.getroot()
                data = []
                for child in root:
                    row = {}
                    for subchild in child:
                        row[subchild.tag] = subchild.text
                    data.append(row)
                df = pd.DataFrame(data)
        else:
            raise ValueError(f"Formato de archivo no soportado: {extension}")
    except Exception as e:
        raise Exception(f"Error al cargar el archivo {filepath}: {str(e)}")

    return df


def cargar_datos_con_opciones(filepath: str, skip_rows: int = 0, column_names: dict = None, chunk_size: int = None) -> pd.DataFrame:
    """
    Cargar datos desde un archivo con opciones adicionales como saltar filas y renombrar columnas

    Args:
        filepath: Ruta del archivo a cargar
        skip_rows: Número de filas a saltar al inicio (la siguiente fila se usa como header)
        column_names: Diccionario con nombres de columnas a renombrar {original: nuevo}
        chunk_size: Tamaño de chunk para lectura (solo para CSV grandes)

    Returns:
        DataFrame de Pandas con los datos cargados y opciones aplicadas
    """
    # Determinar el tipo de archivo por extensión
    extension = os.path.splitext(filepath)[1].lower()

    try:
        if extension in ['.xlsx', '.xls']:
            # Para Excel, usar header=skip_rows para usar la fila después de saltar como header
            if skip_rows > 0:
                df = pd.read_excel(filepath, header=skip_rows)
                # Resetear index para que empiece desde 0
                df = df.reset_index(drop=True)
            else:
                df = pd.read_excel(filepath)
        elif extension == '.csv':
            # Para CSV, usar header=skip_rows para usar la fila después de saltar como header
            if skip_rows > 0:
                df = pd.read_csv(filepath, header=skip_rows)
                # Resetear index para que empiece desde 0
                df = df.reset_index(drop=True)
            else:
                df = pd.read_csv(filepath)
        elif extension == '.json':
            # Para JSON, no se puede usar header, así que cargar normal y luego saltar
            df = pd.read_json(filepath)
            if skip_rows > 0:
                df = df.iloc[skip_rows:].reset_index(drop=True)
        elif extension in ['.xml']:
            # Para XML, cargar normal y luego saltar
            try:
                df = pd.read_xml(filepath)
            except AttributeError:
                # Si pandas no tiene read_xml, usar lxml
                from lxml import etree
                tree = etree.parse(filepath)
                root = tree.getroot()
                data = []
                for child in root:
                    row = {}
                    for subchild in child:
                        row[subchild.tag] = subchild.text
                    data.append(row)
                df = pd.DataFrame(data)

            if skip_rows > 0:
                df = df.iloc[skip_rows:].reset_index(drop=True)
        else:
            raise ValueError(f"Formato de archivo no soportado: {extension}")
    except Exception as e:
        raise Exception(f"Error al cargar el archivo {filepath}: {str(e)}")

    # Aplicar renombrado de columnas si se especifica
    if column_names:
        df = df.rename(columns=column_names)

    return df


def _cargar_csv_en_chunks(filepath: str, chunk_size: int = None) -> pd.DataFrame:
    """
    Cargar archivo CSV en chunks para optimizar memoria

    Args:
        filepath: Ruta del archivo CSV
        chunk_size: Tamaño de cada chunk (si None, se calcula automáticamente)

    Returns:
        DataFrame completo
    """
    if chunk_size is None:
        # Calcular chunk_size basado en el tamaño del archivo
        file_size = os.path.getsize(filepath)
        if file_size > 500 * 1024 * 1024:  # 500MB
            chunk_size = 10000
        elif file_size > 100 * 1024 * 1024:  # 100MB
            chunk_size = 25000
        else:
            chunk_size = 50000

    print(f"Cargando CSV en chunks de {chunk_size} filas...")

    # Leer primera parte para obtener estructura
    first_chunk = pd.read_csv(filepath, nrows=1)
    columns = first_chunk.columns

    # Inicializar DataFrame vacío con la estructura correcta
    df_list = []

    # Leer archivo en chunks
    for chunk in pd.read_csv(filepath, chunksize=chunk_size):
        df_list.append(chunk)

    # Concatenar todos los chunks
    result_df = pd.concat(df_list, ignore_index=True)

    print(f"CSV cargado exitosamente: {len(result_df)} filas, {len(result_df.columns)} columnas")
    return result_df


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


def obtener_estadisticas(df: pd.DataFrame, columnas: list = None, percentiles: list = None) -> pd.DataFrame:
    """
    Obtener estadísticas descriptivas del DataFrame con optimización para datasets grandes

    Args:
        df: DataFrame de Pandas
        columnas: Lista de columnas específicas (si None, usar todas las numéricas)
        percentiles: Lista de percentiles a calcular (si None, usar [25, 50, 75])

    Returns:
        DataFrame con estadísticas descriptivas
    """
    try:
        if len(df) == 0:
            return pd.DataFrame()

        # Si no se especifican columnas, usar solo las numéricas para optimizar
        if columnas is None:
            columnas = df.select_dtypes(include=['number']).columns.tolist()
            if not columnas:
                # Si no hay columnas numéricas, usar todas
                columnas = df.columns.tolist()

        # Configurar percentiles por defecto (convertir a decimales)
        if percentiles is None:
            percentiles = [0.25, 0.5, 0.75]  # Usar decimales en lugar de porcentajes
        else:
            # Convertir percentiles de porcentaje a decimal si es necesario
            percentiles = [p/100 if p > 1 else p for p in percentiles]

        # Para datasets muy grandes, usar sample para estadísticas aproximadas
        if optimization_config.should_sample_stats(len(df)):
            print(f"Dataset grande detectado ({len(df)} filas), calculando estadísticas con sample...")
            sample_size = min(optimization_config.STATS_SAMPLE_SIZE, len(df))
            df_sample = df.sample(n=sample_size, random_state=42)
        else:
            df_sample = df

        # Calcular estadísticas solo para las columnas especificadas
        estadisticas = df_sample[columnas].describe(percentiles=percentiles, include='all')

        return estadisticas
    except Exception as e:
        print(f"Error al calcular estadísticas: {str(e)}")
        # Si hay error, devolver DataFrame vacío
        return pd.DataFrame()


def obtener_estadisticas_basicas(df: pd.DataFrame) -> dict:
    """
    Obtener estadísticas básicas optimizadas para datasets grandes

    Args:
        df: DataFrame de Pandas

    Returns:
        Diccionario con estadísticas básicas
    """
    try:
        basic_stats = {
            'total_filas': len(df),
            'total_columnas': len(df.columns),
            'columnas_numericas': len(df.select_dtypes(include=['number']).columns),
            'columnas_texto': len(df.select_dtypes(include=['object']).columns),
            'columnas_fecha': len(df.select_dtypes(include=['datetime']).columns),
            'memoria_uso_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'filas_duplicadas': df.duplicated().sum(),
            'valores_nulos_total': df.isnull().sum().sum()
        }

        return basic_stats
    except Exception as e:
        print(f"Error al calcular estadísticas básicas: {str(e)}")
        return {}


def aplicar_filtro(df: pd.DataFrame, columna: str, termino: str, use_index: bool = True) -> pd.DataFrame:
    """
    Aplicar filtro a los datos con optimización para datasets grandes

    Args:
        df: DataFrame original
        columna: Nombre de la columna a filtrar
        termino: Término de búsqueda
        use_index: Usar búsqueda indexada para mejor rendimiento

    Returns:
        DataFrame filtrado
    """
    if columna not in df.columns:
        raise ValueError(f"Columna no encontrada: {columna}")

    if len(df) == 0:
        return df

    # Para datasets muy grandes, usar optimizaciones
    if optimization_config.should_optimize_filtering(len(df)) and use_index:
        return _aplicar_filtro_indexado(df, columna, termino)
    else:
        return _aplicar_filtro_simple(df, columna, termino)


def _aplicar_filtro_simple(df: pd.DataFrame, columna: str, termino: str) -> pd.DataFrame:
    """
    Aplicar filtro simple (método original)

    Args:
        df: DataFrame original
        columna: Nombre de la columna a filtrar
        termino: Término de búsqueda

    Returns:
        DataFrame filtrado
    """
    # Filtrar por contenido de texto (case-insensitive)
    df_filtrado = df[df[columna].astype(str).str.contains(termino, case=False, na=False)]
    return df_filtrado


def _aplicar_filtro_indexado(df: pd.DataFrame, columna: str, termino: str) -> pd.DataFrame:
    """
    Aplicar filtro optimizado usando indexación para datasets grandes

    Args:
        df: DataFrame original
        columna: Nombre de la columna a filtrar
        termino: Término de búsqueda

    Returns:
        DataFrame filtrado
    """
    try:
        # Convertir columna a string para búsqueda de texto
        columna_str = df[columna].astype(str)

        # Crear una serie booleana para el filtro
        if termino.startswith('^') and termino.endswith('$'):
            # Búsqueda exacta (regex)
            pattern = termino[1:-1]
            mask = columna_str.str.match(pattern, case=False, na=False)
        elif termino.startswith('*') or termino.endswith('*'):
            # Búsqueda con wildcards
            pattern = termino.replace('*', '.*')
            mask = columna_str.str.contains(pattern, case=False, na=False, regex=True)
        else:
            # Búsqueda normal
            mask = columna_str.str.contains(termino, case=False, na=False)

        # Aplicar filtro
        df_filtrado = df[mask]

        print(f"Filtro aplicado: {len(df_filtrado)} de {len(df)} filas encontradas")
        return df_filtrado

    except Exception as e:
        print(f"Error en filtrado indexado, usando método simple: {str(e)}")
        return _aplicar_filtro_simple(df, columna, termino)


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


def exportar_a_imagen(table_view, filepath: str) -> bool:
    """
    Exportar vista de tabla a imagen

    Args:
        table_view: QTableView a capturar
        filepath: Ruta de destino para la imagen

    Returns:
        True si la exportación fue exitosa
    """
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QPixmap

        # Capturar la vista de la tabla como pixmap
        pixmap = table_view.grab()

        # Guardar como imagen (PNG por defecto)
        success = pixmap.save(filepath)

        if success:
            return True
        else:
            print(f"Error al guardar la imagen en {filepath}")
            return False

    except Exception as e:
        print(f"Error al exportar a imagen: {str(e)}")
        return False


def limpiar_datos(df: pd.DataFrame, opciones: dict = None) -> pd.DataFrame:
    """
    Limpiar datos del DataFrame aplicando varias operaciones de limpieza

    Args:
        df: DataFrame original
        opciones: Diccionario con opciones de limpieza
            - eliminar_duplicados: bool (default True)
            - eliminar_nulos: bool (default False)
            - rellenar_nulos: dict con columna: valor para rellenar
            - eliminar_columnas: list de columnas a eliminar
            - convertir_tipos: dict con columna: tipo

    Returns:
        DataFrame limpio
    """
    df_clean = df.copy()

    if opciones is None:
        opciones = {}

    # Eliminar duplicados
    if opciones.get('eliminar_duplicados', True):
        df_clean = df_clean.drop_duplicates()

    # Eliminar filas con nulos si se especifica
    if opciones.get('eliminar_nulos', False):
        df_clean = df_clean.dropna()

    # Rellenar nulos con valores especificados
    rellenar_nulos = opciones.get('rellenar_nulos', {})
    for columna, valor in rellenar_nulos.items():
        if columna in df_clean.columns:
            df_clean[columna] = df_clean[columna].fillna(valor)

    # Eliminar columnas especificadas
    eliminar_columnas = opciones.get('eliminar_columnas', [])
    for columna in eliminar_columnas:
        if columna in df_clean.columns:
            df_clean = df_clean.drop(columns=[columna])

    # Convertir tipos de datos
    convertir_tipos = opciones.get('convertir_tipos', {})
    for columna, tipo in convertir_tipos.items():
        if columna in df_clean.columns:
            try:
                if tipo == 'numeric':
                    df_clean[columna] = pd.to_numeric(df_clean[columna], errors='coerce')
                elif tipo == 'datetime':
                    df_clean[columna] = pd.to_datetime(df_clean[columna], errors='coerce')
                elif tipo == 'string':
                    df_clean[columna] = df_clean[columna].astype(str)
            except Exception as e:
                print(f"Error al convertir tipo de {columna}: {str(e)}")

    return df_clean


def agregar_datos(df: pd.DataFrame, operaciones: list) -> pd.DataFrame:
    """
    Realizar operaciones de agregación en el DataFrame

    Args:
        df: DataFrame original
        operaciones: Lista de diccionarios con operaciones
            Cada operación: {
                'grupo': ['col1', 'col2'],  # Columnas para agrupar
                'funciones': {'col3': 'sum', 'col4': ['mean', 'count']},
                'nombre': 'resultado'  # Nombre para el resultado
            }

    Returns:
        DataFrame con resultados de agregación
    """
    resultados = []

    for op in operaciones:
        grupo = op.get('grupo', [])
        funciones = op.get('funciones', {})
        nombre = op.get('nombre', 'agregado')

        try:
            if grupo:
                # Agregación por grupos
                df_agregado = df.groupby(grupo).agg(funciones).reset_index()
            else:
                # Agregación global
                df_agregado = df.agg(funciones).to_frame().T.reset_index(drop=True)

            # Aplanar columnas si hay múltiples funciones
            df_agregado.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col
                                   for col in df_agregado.columns]

            df_agregado['operacion'] = nombre
            resultados.append(df_agregado)

        except Exception as e:
            print(f"Error en agregación '{nombre}': {str(e)}")

    if resultados:
        return pd.concat(resultados, ignore_index=True)
    else:
        return pd.DataFrame()


def pivotar_datos(df: pd.DataFrame, index: str, columns: str, values: str,
                  aggfunc: str = 'mean') -> pd.DataFrame:
    """
    Crear tabla pivote del DataFrame

    Args:
        df: DataFrame original
        index: Columna para usar como índice
        columns: Columna para usar como columnas
        values: Columna para usar como valores
        aggfunc: Función de agregación (mean, sum, count, etc.)

    Returns:
        DataFrame pivoteado
    """
    try:
        if aggfunc == 'mean':
            func = np.mean
        elif aggfunc == 'sum':
            func = np.sum
        elif aggfunc == 'count':
            func = 'count'
        else:
            func = aggfunc

        df_pivot = df.pivot_table(index=index, columns=columns, values=values, aggfunc=func)
        return df_pivot.reset_index()
    except Exception as e:
        print(f"Error al crear tabla pivote: {str(e)}")
        return pd.DataFrame()