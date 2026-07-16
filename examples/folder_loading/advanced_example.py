#!/usr/bin/env python3
"""
Ejemplo avanzado de carga de carpeta con Flash Sheet

Este ejemplo muestra funcionalidades avanzadas como:
- Filtros de archivos
- Renombrado de columnas
- Manejo de archivos con estructuras diferentes
- Configuración personalizada
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Añadir el directorio raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from core.loaders.folder_loader import FolderLoader
from core.consolidation.excel_consolidator import ExcelConsolidator
from core.models.folder_load_config import FolderLoadConfig, ColumnAlignmentStrategy

def advanced_folder_loading() -> None:
    """Ejemplo avanzado de carga de carpeta con configuración personalizada"""

    print("🚀 Flash Sheet - Ejemplo Avanzado de Carga de Carpeta")
    print("=" * 65)

    # Ruta a la carpeta con archivos de ejemplo
    folder_path = str(Path(__file__).parent / 'sample_data')

    print(f"📁 Cargando carpeta: {folder_path}")
    print()

    try:
        # 1. Crear configuración personalizada
        print("1️⃣ Creando configuración personalizada...")
        config = FolderLoadConfig(
            folder_path=folder_path,
            included_files=[],  # Incluir todos
            excluded_files=[],  # Excluir ninguno
            included_columns=['Producto', 'Cantidad', 'Precio', 'Total', 'Vendedor', 'Región'],  # Ejemplo: incluir solo estas columnas
            excluded_columns=[],  # Excluir ninguna
            alignment_strategy=ColumnAlignmentStrategy.BY_POSITION,
            column_rename_mapping={
                'Producto': 'Nombre_Producto',
                'Cantidad': 'Unidades_Vendidas',
                'Precio': 'Precio_Unitario',
                'Total': 'Monto_Total',
                'Vendedor': 'Nombre_Vendedor',
                'Región': 'Zona_Geografica'
            },
            add_source_column=True,
            source_column_name='Archivo_Origen'
        )
        print("   ✓ Configuración creada con mapeo de columnas")
        print()

        # 2. Crear loader con configuración
        print("2️⃣ Creando FolderLoader...")
        loader = FolderLoader(config.folder_path)
        print(f"   ✓ Encontrados {len(loader.excel_files)} archivos Excel")
        print()

        # 3. Filtrar archivos según configuración
        print("3️⃣ Aplicando filtros de archivos...")
        filtered_files = []
        for file_path in loader.get_excel_files():
            filename = Path(file_path).name
            if config.should_include_file(filename):
                filtered_files.append(file_path)
                print(f"   ✓ Incluyendo: {filename}")
            else:
                print(f"   ✗ Excluyendo: {filename}")

        print(f"   📊 Archivos a procesar: {len(filtered_files)}")
        print()

        # 4. Obtener metadata solo de archivos filtrados
        print("4️⃣ Analizando estructura de archivos...")
        file_metadata = []
        for file_path in filtered_files:
            meta = loader.get_file_metadata(file_path)
            file_metadata.append(meta)
            print(f"   📄 {meta['filename']}: {meta['num_columns']} cols, ~{meta['num_rows']} filas")

        # Verificar si hay diferencias en estructura
        column_counts = [meta['num_columns'] for meta in file_metadata]
        if len(set(column_counts)) > 1:
            print("   ⚠️  Archivos con diferente número de columnas detectados")
            for meta in file_metadata:
                print(f"     • {meta['filename']}: {meta['num_columns']} columnas")
        else:
            print("   ✅ Todos los archivos tienen la misma estructura")
        print()

        # 5. Crear consolidator con configuración
        print("5️⃣ Creando ExcelConsolidator con configuración...")
        consolidator = ExcelConsolidator()

        # Aplicar mapeo de columnas
        consolidator.set_column_mappings(config.column_rename_mapping)
        print("   ✓ Mapeo de columnas aplicado")

        # Aplicar selección de columnas
        consolidator.set_column_selection(config.included_columns, config.excluded_columns)
        print("   ✓ Selección de columnas aplicada")
        print()

        # 6. Cargar archivos con manejo de errores
        print("6️⃣ Cargando archivos con validación...")
        loaded_dataframes = []

        for i, file_path in enumerate(filtered_files, 1):
            filename = Path(file_path).name
            print(f"   Cargando {i}/{len(filtered_files)}: {filename}")

            try:
                # Cargar archivo Excel
                df = pd.read_excel(file_path)

                # Validar que tenga datos
                if df.empty:
                    print(f"     ⚠️  Archivo vacío, omitiendo")
                    continue

                # Añadir al consolidator
                consolidator.add_dataframe(df, filename)
                loaded_dataframes.append((filename, len(df)))

                print(f"     ✓ {len(df)} filas cargadas correctamente")

            except Exception as e:
                print(f"     ❌ Error cargando {filename}: {e}")
                continue

        print(f"   📊 Total de archivos cargados: {len(loaded_dataframes)}")
        print()

        # 7. Consolidar con método de alineación especificado
        print("7️⃣ Consolidando datos...")
        print(f"   Método de alineación: {config.alignment_strategy.value}")

        consolidated_df = consolidator.consolidate()
        print("   ✓ Consolidación completada")
        print()

        # 8. Verificar resultado de renombrado
        print("8️⃣ Verificando renombrado de columnas...")
        renamed_columns = [col for col in consolidated_df.columns if col in config.column_rename_mapping.values()]
        original_columns = [col for col in consolidated_df.columns if col not in config.column_rename_mapping.values()]

        print(f"   📊 Columnas renombradas: {len(renamed_columns)}")
        for orig, new in config.column_rename_mapping.items():
            if new in consolidated_df.columns:
                print(f"     ✓ {orig} → {new}")
            else:
                print(f"     ⚠️  {orig} → {new} (no encontrado)")

        print(f"   📊 Columnas originales: {len(original_columns)}")
        for col in original_columns:
            print(f"     • {col}")
        print()

        # 9. Análisis del resultado consolidado
        print("9️⃣ Análisis del dataset consolidado:")
        print(f"   📊 Dimensiones: {consolidated_df.shape[0]} filas × {consolidated_df.shape[1]} columnas")
        print(f"   📊 Columnas finales: {list(consolidated_df.columns)}")
        print()

        # 10. Estadísticas avanzadas
        print("🔟 Estadísticas avanzadas:")

        # Información por archivo origen
        if config.source_column_name in consolidated_df.columns:
            source_col = config.source_column_name
            files_summary = consolidated_df.groupby(source_col).size()
            print(f"   📁 Filas por archivo origen:")
            for filename, count in files_summary.items():
                print(f"     • {filename}: {count} filas")

        # Análisis de valores nulos
        null_counts = consolidated_df.isnull().sum()
        total_nulls = null_counts.sum()
        if total_nulls > 0:
            print(f"   ⚠️  Valores nulos encontrados: {total_nulls}")
            print("   Columnas con nulos:")
            for col, count in null_counts[null_counts > 0].items():
                print(f"     • {col}: {count} nulos")
        else:
            print("   ✅ No se encontraron valores nulos")

        # Estadísticas numéricas si existen
        numeric_columns = consolidated_df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            print(f"   📊 Estadísticas de columnas numéricas:")
            for col in numeric_columns:
                if col != config.source_column_name:  # Excluir columna de origen
                    mean_val = consolidated_df[col].mean()
                    print(f"     • {col}: promedio = {mean_val:.2f}")

        print()

        # 11. Mostrar muestra del resultado
        print("1️⃣1️⃣ Muestra del resultado consolidado:")
        print(consolidated_df.head(5).to_string(index=False))
        print()

        print("✅ ¡Ejemplo avanzado completado exitosamente!")
        print("💡 Tips avanzados:")
        print("   • Usa FolderLoadConfig para personalizar el comportamiento")
        print("   • El mapeo de columnas maneja diferencias entre archivos")
        print("   • La columna de origen ayuda a rastrear la procedencia de datos")

    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    advanced_folder_loading()