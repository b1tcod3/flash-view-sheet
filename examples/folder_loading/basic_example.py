#!/usr/bin/env python3
"""
Ejemplo básico de carga de carpeta con Flash Sheet

Este ejemplo muestra cómo usar la funcionalidad de carga de carpeta
para consolidar múltiples archivos Excel de forma programática.
"""

import sys
from pathlib import Path
import pandas as pd

# Añadir el directorio raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from core.loaders.folder_loader import FolderLoader
from core.consolidation.excel_consolidator import ExcelConsolidator

def basic_folder_loading() -> None:
    """Ejemplo básico de carga de carpeta"""

    print("🚀 Flash Sheet - Ejemplo Básico de Carga de Carpeta")
    print("=" * 60)

    # Ruta a la carpeta con archivos de ejemplo
    folder_path = str(Path(__file__).parent / 'sample_data')

    print(f"📁 Cargando carpeta: {folder_path}")
    print()

    try:
        # 1. Crear el loader de carpeta
        print("1️⃣ Creando FolderLoader...")
        loader = FolderLoader(folder_path)
        print(f"   ✓ Encontrados {len(loader.excel_files)} archivos Excel")
        print()

        # 2. Mostrar archivos encontrados
        print("2️⃣ Archivos Excel encontrados:")
        for i, file_path in enumerate(loader.get_excel_files(), 1):
            filename = Path(file_path).name
            print(f"   {i}. {filename}")
        print()

        # 3. Obtener metadata de archivos
        print("3️⃣ Obteniendo metadata de archivos...")
        all_metadata = loader.get_all_metadata()

        print("   Metadata de archivos:")
        for meta in all_metadata:
            print(f"   📄 {meta['filename']}: {meta['num_columns']} columnas, ~{meta['num_rows']} filas")
        print()

        # 4. Crear consolidator
        print("4️⃣ Creando ExcelConsolidator...")
        consolidator = ExcelConsolidator()
        print("   ✓ Consolidator creado")
        print()

        # 5. Cargar y consolidar archivos
        print("5️⃣ Cargando y consolidando archivos...")
        total_files = len(loader.get_excel_files())

        for i, file_path in enumerate(loader.get_excel_files(), 1):
            print(f"   Cargando archivo {i}/{total_files}: {os.path.basename(file_path)}")

            # Cargar archivo Excel
            df = pd.read_excel(file_path)

            # Añadir al consolidator
            consolidator.add_dataframe(df, os.path.basename(file_path))

            print(f"     ✓ {len(df)} filas cargadas")
        print()

        # 6. Consolidar datos
        print("6️⃣ Consolidando datos...")
        consolidated_df = consolidator.consolidate()
        print("   ✓ Consolidación completada")
        print()

        # 7. Mostrar resultados
        print("7️⃣ Resultados de la consolidación:")
        print(f"   📊 Total de filas: {len(consolidated_df)}")
        print(f"   📊 Total de columnas: {len(consolidated_df.columns)}")
        print(f"   📊 Columnas: {list(consolidated_df.columns)}")
        print()

        # 8. Mostrar primeras filas
        print("8️⃣ Primeras 10 filas del dataset consolidado:")
        print(consolidated_df.head(10).to_string(index=False))
        print()

        # 9. Estadísticas básicas
        print("9️⃣ Estadísticas básicas:")
        if 'Total' in consolidated_df.columns:
            total_ventas = consolidated_df['Total'].sum()
            print(f"   💰 Total de ventas: ${total_ventas:.2f}")
        if 'Región' in consolidated_df.columns:
            ventas_por_region = consolidated_df.groupby('Región')['Total'].sum()
            print("   💰 Ventas por región:")
            for region, total in ventas_por_region.items():
                print(f"     • {region}: ${total:.2f}")
        print()

        print("✅ ¡Ejemplo completado exitosamente!")
        print("💡 Tip: Puedes usar este código como base para tus propios scripts de consolidación")

    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    basic_folder_loading()