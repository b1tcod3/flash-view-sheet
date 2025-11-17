#!/usr/bin/env python3
"""
Script para crear archivos Excel de ejemplo para la funcionalidad de carga de carpeta
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def create_sample_data():
    """Crear datos de ejemplo para diferentes trimestres"""

    # Productos disponibles
    productos = [
        "Laptop Dell", "Mouse Logitech", "Teclado Mecánico", "Monitor 24\"", "Impresora HP",
        "Disco Duro 1TB", "Memoria RAM 8GB", "Tarjeta Gráfica", "Webcam HD", "Auriculares"
    ]

    # Vendedores
    vendedores = ["Ana García", "Carlos López", "María Rodríguez", "Juan Martínez", "Laura Sánchez"]

    # Regiones
    regiones = ["Norte", "Sur", "Este", "Oeste", "Centro"]

    # Función para generar datos de un trimestre
    def generate_quarter_data(year, quarter, num_records=50):
        np.random.seed(42 + quarter)  # Semilla consistente por trimestre

        start_date = datetime(year, (quarter-1)*3 + 1, 1)
        end_date = datetime(year, quarter*3, 28) if quarter < 4 else datetime(year, 12, 31)

        dates = [start_date + timedelta(days=np.random.randint(0, 90)) for _ in range(num_records)]

        data = {
            'Fecha': dates,
            'Producto': np.random.choice(productos, num_records),
            'Cantidad': np.random.randint(1, 10, num_records),
            'Precio': np.round(np.random.uniform(50, 500, num_records), 2),
            'Vendedor': np.random.choice(vendedores, num_records),
            'Región': np.random.choice(regiones, num_records)
        }

        df = pd.DataFrame(data)
        df['Total'] = df['Cantidad'] * df['Precio']

        return df

    # Crear directorio si no existe
    os.makedirs('sample_data', exist_ok=True)

    # Generar datos para cada trimestre de 2025
    quarters = [
        ('ventas_q1.xlsx', 2025, 1),
        ('ventas_q2.xlsx', 2025, 2),
        ('ventas_q3.xlsx', 2025, 3),
        ('ventas_q4.xlsx', 2025, 4)
    ]

    for filename, year, quarter in quarters:
        print(f"Creando {filename}...")
        df = generate_quarter_data(year, quarter)

        # Guardar como Excel
        filepath = os.path.join('sample_data', filename)
        df.to_excel(filepath, index=False)

        print(f"  ✓ {len(df)} registros guardados en {filepath}")

    # Crear un archivo adicional con estructura ligeramente diferente
    print("Creando ventas_extra.xlsx con estructura diferente...")
    df_extra = generate_quarter_data(2025, 1, 30)
    # Añadir una columna extra
    df_extra['Descuento'] = np.round(np.random.uniform(0, 0.1, len(df_extra)), 2)
    df_extra['Total_Con_Descuento'] = df_extra['Total'] * (1 - df_extra['Descuento'])

    df_extra.to_excel('sample_data/ventas_extra.xlsx', index=False)
    print(f"  ✓ {len(df_extra)} registros con estructura extendida")

    print("\n✅ Todos los archivos de ejemplo creados exitosamente!")
    print("📁 Revisa la carpeta 'sample_data' para ver los archivos generados.")

if __name__ == "__main__":
    create_sample_data()