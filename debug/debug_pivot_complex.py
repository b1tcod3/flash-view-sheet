#!/usr/bin/env python3
"""
Debug específico para el test complejo de Combined Pivot
"""

import pandas as pd
import numpy as np
import logging
import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar módulos pivot
from core.pivot import CombinedPivotTable

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data() -> pd.DataFrame:
    """Crear datos de prueba para testing de combined pivot"""
    np.random.seed(42)
    
    # Crear dataset de ejemplo
    data = {
        'region': ['Norte', 'Sur', 'Este', 'Oeste', 'Norte', 'Sur', 'Este', 'Oeste'] * 12,
        'categoria': ['A', 'B', 'C'] * 32,
        'producto': ['Producto1', 'Producto2', 'Producto3', 'Producto4'] * 24,
        'vendedor': [f'Vendedor{i%8+1}' for i in range(96)],
        'ventas': np.random.normal(1000, 200, 96).round(2),
        'unidades': np.random.randint(10, 100, 96),
        'fecha': pd.date_range('2023-01-01', periods=96, freq='3D'),
        'descuento': np.random.uniform(0, 0.3, 96).round(2)
    }
    
    return pd.DataFrame(data)

def debug_complex_pivot():
    """Debug del pivote complejo paso a paso"""
    logger.info("=== DEBUG: PIVOTE COMPLEJO ===")
    
    # Crear datos
    df = create_test_data()
    logger.info(f"Dataset original: {df.shape}")
    logger.info(f"Columnas: {list(df.columns)}")
    logger.info(f"Primeras 5 filas:\n{df.head()}")
    
    # Crear tabla pivote
    pivot_table = CombinedPivotTable()
    
    # Parámetros complejos
    parameters = {
        'index': ['region', 'categoria'],
        'columns': ['producto', 'vendedor'],  # ¡Aquí está el problema! Múltiples columnas
        'values': ['ventas', 'unidades', 'descuento'],
        'aggfuncs': ['sum', 'mean', 'std'],
        'fill_value': 0,
        'dropna': False,
        'margins': True,
        'margins_name': 'Total'
    }
    
    logger.info(f"Parámetros: {parameters}")
    
    # Ejecutar paso a paso manualmente
    try:
        # Normalizar parámetros
        index = pivot_table.normalize_parameter(parameters['index'])
        columns = pivot_table.normalize_parameter(parameters['columns'])
        values = pivot_table.normalize_parameter(parameters['values'])
        aggfuncs = pivot_table.normalize_parameter(parameters['aggfuncs'])
        
        logger.info(f"Index normalizado: {index}")
        logger.info(f"Columns normalizado: {columns}")
        logger.info(f"Values normalizado: {values}")
        logger.info(f"Aggfuncs normalizado: {aggfuncs}")
        
        # Validar columnas
        all_columns = set(index + columns + values)
        logger.info(f"Todas las columnas requeridas: {all_columns}")
        pivot_table.validate_columns_exist(df, list(all_columns))
        
        # Ahora intentar el pivote multi-valor
        logger.info("Iniciando pivote multi-valor...")
        result = pivot_table._execute_multi_value_pivot(
            df, index, columns, values, aggfuncs,
            parameters['fill_value'], parameters['dropna'], 
            parameters['margins'], parameters['margins_name']
        )
        
        logger.info(f"Resultado final: {result.shape}")
        logger.info(f"Columnas resultado: {list(result.columns)}")
        
        if not result.empty:
            logger.info(f"Primeras filas del resultado:\n{result.head()}")
        else:
            logger.warning("El resultado está vacío!")
            
    except Exception as e:
        logger.error(f"Error en debug: {str(e)}")
        import traceback
        traceback.print_exc()

def test_simpler_cases():
    """Probar casos más simples para identificar el problema"""
    logger.info("=== TEST CASOS SIMPLES ===")
    
    df = create_test_data()
    pivot_table = CombinedPivotTable()
    
    # Test 1: Solo múltiples valores, sin múltiples columnas
    logger.info("Test 1: Múltiples valores, sin múltiples columnas")
    try:
        result1 = pivot_table.execute(df, {
            'index': ['region'],
            'columns': ['producto'],
            'values': ['ventas', 'unidades'],
            'aggfuncs': ['sum', 'mean']
        })
        logger.info(f"Test 1 exitoso: {result1.shape}")
    except Exception as e:
        logger.error(f"Test 1 falló: {str(e)}")
    
    # Test 2: Solo múltiples columnas, sin múltiples valores
    logger.info("Test 2: Solo múltiples columnas")
    try:
        result2 = pivot_table.execute(df, {
            'index': ['region'],
            'columns': ['producto', 'categoria'],
            'values': ['ventas'],
            'aggfuncs': ['sum']
        })
        logger.info(f"Test 2 exitoso: {result2.shape}")
    except Exception as e:
        logger.error(f"Test 2 falló: {str(e)}")
    
    # Test 3: El caso problemático original
    logger.info("Test 3: Caso problemático completo")
    try:
        result3 = pivot_table.execute(df, {
            'index': ['region', 'categoria'],
            'columns': ['producto', 'vendedor'],
            'values': ['ventas', 'unidades', 'descuento'],
            'aggfuncs': ['sum', 'mean', 'std']
        })
        logger.info(f"Test 3 exitoso: {result3.shape}")
    except Exception as e:
        logger.error(f"Test 3 falló: {str(e)}")

if __name__ == '__main__':
    test_simpler_cases()
    debug_complex_pivot()