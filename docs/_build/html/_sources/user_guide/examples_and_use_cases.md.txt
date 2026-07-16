# Ejemplos y Casos de Uso

## 📋 Índice

1. [Introducción](#introducción)
2. [Ejemplos Básicos](#ejemplos-básicos)
3. [Casos de Uso Empresariales](#casos-de-uso-empresariales)
4. [Ejemplos con Datos Reales](#ejemplos-con-datos-reales)
5. [Plantillas de Ejemplo](#plantillas-de-ejemplo)
6. [Casos Especiales](#casos-especiales)
7. [Automatización y Scripts](#automatización-y-scripts)

## Introducción

Esta sección proporciona **ejemplos prácticos paso a paso** y **casos de uso reales** para ayudarte a implementar la exportación separada en diferentes escenarios. Cada ejemplo incluye:

- **Datos de muestra** para practicar
- **Configuración específica** recomendada
- **Plantillas Excel** de ejemplo
- **Resultados esperados** y métricas
- **Consejos prácticos** y mejores prácticas

## Ejemplos Básicos

### Ejemplo 1: Ventas por Región (Básico)

**📊 Datos de Muestra:**

```csv
Region,Vendedor,Producto,Precio,Cantidad,Total
Norte,Juan Pérez,Laptop Pro,1200.00,2,2400.00
Norte,Juan Pérez,Mouse Wireless,25.00,5,125.00
Sur,María García,Tablet Plus,450.00,3,1350.00
Sur,María García,Laptop Pro,1200.00,1,1200.00
Este,Carlos Ruiz,Smartphone,650.00,4,2600.00
Oeste,Ana Torres,Monitor 27",300.00,2,600.00
Norte,Juan Pérez,Smartphone,650.00,1,650.00
Sur,María García,Monitor 27",300.00,3,900.00
```

**🎯 Objetivo:** Crear un reporte por región con formato corporativo

**⚙️ Configuración:**

1. **Columna de Separación**: `Region`
2. **Plantilla**: `plantilla_ventas.xlsx` (ver sección de plantillas)
3. **Nombre de Archivo**: `Reporte_Ventas_{valor}_{fecha}.xlsx`
4. **Carpeta Destino**: `Reportes_2025/`
5. **Mapeo**: Automático (posición 1:1)

**📈 Resultado Esperado:**

- `Reporte_Ventas_Norte_2025-11-05.xlsx` (4 filas)
- `Reporte_Ventas_Sur_2025-11-05.xlsx` (3 filas)  
- `Reporte_Ventas_Este_2025-11-05.xlsx` (1 fila)
- `Reporte_Ventas_Oeste_2025-11-05.xlsx` (1 fila)

**💡 Consejos:**
- Cada archivo mantiene formato de plantilla corporativa
- Suma de totales por región correcta
- Celdas de totales calculadas automáticamente

### Ejemplo 2: Reporte Mensual por Departamento

**📊 Datos de Muestra:**

```csv
Mes,Departamento,Empleado,Categoria,Salario,Dias_Trabajados,Horas_Extras
2025-01,RRHH,Ana López,Gerente,3500,22,5
2025-01,Ventas,Carlos Pérez,Vendedor,2800,22,8
2025-01,IT,María Ruiz,Desarrollador,3200,22,3
2025-01,RRHH,Pedro García,Analista,2500,22,0
2025-02,RRHH,Ana López,Gerente,3500,20,7
2025-02,Ventas,Carlos Pérez,Vendedor,2800,20,12
2025-02,IT,María Ruiz,Desarrollador,3200,20,6
2025-02,Ventas,Lucía Martín,Vendedor,2600,20,4
```

**🎯 Objetivo:** Crear reporte mensual por departamento

**⚙️ Configuración:**

1. **Columna de Separación**: `Mes`
2. **Plantilla**: `plantilla_nomina.xlsx`
3. **Nombre de Archivo**: `{valor}_{Departamento}_Reporte.xlsx`
4. **Manejo de Duplicados**: Auto-numeración
5. **Celda Inicial**: A2 (para incluir encabezado en plantilla)

**📈 Resultado Esperado:**

- `2025-01_RRHH_Reporte.xlsx` (2 empleados RRHH enero)
- `2025-01_Ventas_Reporte.xlsx` (1 empleado ventas enero)
- `2025-01_IT_Reporte.xlsx` (1 empleado IT enero)
- `2025-02_RRHH_Reporte.xlsx` (1 empleado RRHH febrero)
- `2025-02_Ventas_Reporte.xlsx` (2 empleados ventas febrero)
- `2025-02_IT_Reporte.xlsx` (1 empleado IT febrero)

### Ejemplo 3: Inventario por Categoría

**📊 Datos de Muestra:**

```csv
Producto,Categoria,Stock,Precio_Costo,Precio_Venta,Proveedor,Fecha_Actualizacion
Laptop Dell XPS,Electrónicos,15,800.00,1200.00,TechCorp,2025-11-01
Mouse Logitech,Electrónicos,50,15.00,35.00,TechCorp,2025-11-01
Escritorio Jefe,Muebles,3,200.00,350.00,OfficeMax,2025-11-01
Silla Ergonómica,Muebles,8,120.00,180.00,OfficeMax,2025-11-01
iPhone 15,Electrónicos,12,700.00,950.00,AppleStore,2025-11-01
 archivador,Muebles,5,80.00,120.00,OfficeMax,2025-11-01
```

**🎯 Objetivo:** Separate inventario por categoría con alertas de stock

**⚙️ Configuración:**

1. **Columna de Separación**: `Categoria`
2. **Plantilla**: `plantilla_inventario.xlsx`
3. **Nombre de Archivo**: `Inventario_{valor}_{fecha}.xlsx`
4. **Mapeo Personalizado**: 
   - Producto → A
   - Stock → B (con formato condicional para alertas)
   - Precio_Costo → C
   - Precio_Venta → D

**📈 Resultado Esperado:**

- `Inventario_Electrónicos_2025-11-05.xlsx` (3 productos)
- `Inventario_Muebles_2025-11-05.xlsx` (3 productos)

## Casos de Uso Empresariales

### Caso 1: Empresa de Retail Multi-Tienda

**🏢 Contexto:** Cadena de tiendas con 25 ubicaciones que necesita reportes mensuales

**📊 Datos Types:**
- **Ventas diarias** por tienda
- **Inventario** por categoría y tienda  
- **Personal** por turno y tienda
- **Clientes** por zona geográfica

**⚙️ Configuración Empresarial:**

```yaml
Columna_Separación: "Tienda"
Plantilla: "corporativo_retail.xlsx"
Nombre_Archivo: "{valor}_{mes}_{año}_Reporte.xlsx"
Mapeo: Personalizado con fórmulas de totales
Performance: Chunking moderado (10K chunks)
Recovery: Habilitado con logs detallados
```

**📈 Beneficios:**
- 25 reportes automáticos por mes
- Formato corporativo consistente
- Alertas automáticas de bajo stock
- Integración con sistema ERP existente

### Caso 2: Hospital - Reportes por Departamento

**🏥 Contexto:** Hospital con 12 departamentos médicos

**📊 Datos Types:**
- **Pacientes** por departamento y médico
- **Citas médicas** por especialidad
- **Inventario médico** por categoría
- **Personal médico** por turno

**⚙️ Configuración Especializada:**

```yaml
Columna_Separación: "Departamento"
Plantilla: "medico_hipaa.xlsx"  # Cumple regulaciones
Nombre_Archivo: "Dept_{valor}_{fecha}.xlsx"
Seguridad: 
  - Encriptación archivos temporales
  - Logging de acceso
  - Sin datos sensibles en logs
Compliance: HIPAA compliant
```

**📋 Consideraciones Especiales:**
- Cumplimiento HIPAA
- Encriptación de archivos temporales
- Control de acceso por usuario
- Auditoría completa de accesos

### Caso 3: Universidad - Análisis por Carrera

**🎓 Contexto:** Universidad con 15 carreras universitarias

**📊 Datos Types:**
- **Estudiantes** por carrera y semestre
- **Calificaciones** por materia y carrera
- **Profesores** por departamento
- **Recursos académicos** por área

**⚙️ Configuración Educativa:**

```yaml
Columna_Separación: "Carrera"
Plantilla: "universitario_estandar.xlsx"
Nombre_Archivo: "{valor}_Analisis_{semestre}.xlsx"
Mapeo: Configuración por tipo de carrera
Analytics: Incluir métricas de rendimiento
Exportacion: CSV adicional para análisis estadístico
```

### Caso 4: Empresa de Manufactura - Control de Calidad

**🏭 Contexto:** Planta manufacturera con múltiples líneas de producción

**📊 Datos Types:**
- **Control de calidad** por línea y turno
- **Producción** por producto y fecha
- **Defectos** por tipo y línea
- **Mantenimiento** por máquina

**⚙️ Configuración Industrial:**

```yaml
Columna_Separación: "Linea_Produccion"
Plantilla: "manufactura_calidad.xlsx"
Nombre_Archivo: "Linea_{valor}_{fecha}_{turno}.xlsx"
Real_Time: Integración con sistemas SCADA
Alertas: Notificaciones automáticas de defectos
Backup: Replicación automática a servidor central
```

## Ejemplos con Datos Reales

### Dataset Empresarial Real: Datos de Ventas

**📊 Características del Dataset:**
- **Tamaño**: 50,000 registros de ventas
- **Período**: 2 años (2023-2024)
- **Regiones**: 8 regiones comerciales
- **Columnas**: 25 columnas incluyendo métricas calculadas

**⚙️ Configuración Optimizada:**

```python
# Configuración para dataset grande
config = {
    'separator_column': 'region_comercial',
    'chunk_size': 5000,
    'memory_limit_mb': 2048,
    'enable_progress_tracking': True,
    'parallel_processing': False,  # Para estabilidad
    'template': 'ventas_corporativo.xlsx'
}

# Nombre de archivo con múltiples variables
file_template = "Ventas_{region}_{año}_{mes|upper}.xlsx"
```

**📈 Resultados:**
- **8 archivos** Excel generados
- **Tiempo de procesamiento**: 8 minutos
- **Tamaño promedio por archivo**: 2.5MB
- **Memoria pico utilizada**: 1.2GB

### Dataset Científico: Resultados de Laboratorio

**🔬 Características del Dataset:**
- **Tamaño**: 15,000 mediciones experimentales
- **Experimentos**: 25 experimentos diferentes
- **Sensores**: 8 tipos de sensores
- **Período**: 6 meses de recolección

**⚙️ Configuración Científica:**

```python
config = {
    'separator_column': 'experimento_id',
    'chunk_size': 3000,
    'preserve_scientific_notation': True,
    'decimal_precision': 6,
    'include_metadata': True,
    'template': 'laboratorio_cientifico.xlsx'
}
```

**📋 Consideraciones Especiales:**
- Preservación de notación científica
- Precisión de 6 decimales
- Metadata experimental incluida
- Gráficos automáticos por experimento

## Plantillas de Ejemplo

### Plantilla 1: Reporte de Ventas Empresarial

**📋 Estructura de la Plantilla:**

```excel
A1: "REPORTE DE VENTAS"
A2: "Región:"
B2: "{region}"
A3: "Período:"
B3: "{fecha}"
A4: "Generado:"
B4: "{timestamp}"
A6: "Vendedor"
B6: "Producto"
C6: "Cantidad"
D6: "Precio Unit."
E6: "Total"
A7: [Datos comienzan aquí]
```

**🎨 Formato Aplicado:**
- **Encabezados** (fila 6): Negrita, fondo azul claro
- **Celdas de totales** (columna E): Fórmulas automáticas
- **Bordes**: Línea gruesa alrededor de tabla de datos
- **Formato moneda**: $#,##0.00 para columnas de precio

### Plantilla 2: Reporte Financiero

**📋 Estructura de la Plantilla:**

```excel
A1: "ANÁLISIS FINANCIERO"
A2: "Departamento: {valor}"
A3: "Período: {fecha_inicio} - {fecha_fin}"
A5: "Concepto"
B5: "Enero"
C5: "Febrero"
D5: "Marzo"
E5: "Total Trimestre"
A6: "Ingresos"
B6: [Fórmulas de suma]
C6: [Fórmulas de suma]
D6: [Fórmulas de suma]
E6: =SUMA(B6:D6)
A7: "Gastos"
B7: [Fórmulas de suma]
C7: [Fórmulas de suma]
D7: [Fórmulas de suma]
E7: =SUMA(B7:D7)
A8: "Utilidad"
B8: =B6-B7
C8: =C6-C7
D8: =D6-D7
E8: =E6-E7
```

**📊 Gráficos Incluidos:**
- **Gráfico de barras**: Comparativo mes a mes
- **Gráfico de torta**: Distribución gastos por categoría
- **Indicadores KPI**: Semáforos para alertas

### Plantilla 3: Control de Inventario

**📋 Estructura de la Plantilla:**

```excel
A1: "CONTROL DE INVENTARIO"
A2: "Categoría: {valor}"
A3: "Fecha Actualización: {fecha}"
A5: "Código"
B5: "Producto"
C5: "Stock Actual"
D5: "Stock Mínimo"
E5: "Estado"
F5: "Última Compra"
A6: [Datos]
B6: [Datos]
C6: [Datos]
D6: [Datos]
E6: =SI(C6<=D6,"CRÍTICO","OK")
F6: [Datos]
```

**⚠️ Alertas Automáticas:**
- **Formato condicional**: Celdas rojas cuando stock <= mínimo
- **Validación de datos**: Listas desplegables para estados
- **Fórmulas**: Cálculos automáticos de reorden

## Casos Especiales

### Caso Especial 1: Datos con Caracteres Especiales

**📊 Problema:** Nombres de productos con caracteres especiales

```csv
Producto,Categoria,Precio
"Café Espresso Premium™","Bebidas",3.50
"Grano Orgánico & Sostenible","Bebidas",5.20
"Kit \"Café del Chef\"","Accesorios",45.00
"Molinillo óntico ¿Nuevo?","Accesorios",75.00
```

**⚙️ Configuración:**

```python
config = {
    'character_handling': {
        'encoding': 'utf-8',
        'normalize_unicode': True,
        'excel_invalid_chars': 'replace',
        'replacement_char': '_'
    },
    'filename_sanitization': {
        'remove_quotes': True,
        'replace_ampersand': True,
        'max_length': 50
    }
}
```

**✅ Resultado:** Caracteres especiales preservados correctamente en Excel, nombres de archivo sanitizados automáticamente.

### Caso Especial 2: Columna de Separación con Muchos Valores Únicos

**📊 Problema:** 500+ valores únicos en columna de separación

```csv
Ciudad,Poblacion,Region
"Madrid-España",3200000,"Europa"
"París-Francia",2100000,"Europa"
"Tokio-Japón",13000000,"Asia"
...
```

**⚙️ Configuración Optimizada:**

```python
config = {
    'chunking_strategy': 'many_small_groups',
    'chunk_size': 1000,
    'group_processing': 'parallel',
    'memory_optimization': 'aggressive',
    'progress_tracking': 'detailed',
    'filename_template': '{ciudad|slug}_{timestamp}.xlsx'
}
```

**⚠️ Consideraciones:**
- Procesamiento en paralelo para velocidad
- Chunks pequeños para gestión de memoria
- Tracking detallado de progreso
- Plantilla de nombres con timestamp para evitar duplicados

### Caso Especial 3: Plantilla Excel con Múltiples Hojas

**📊 Escenario:** Plantilla con hoja de datos + hoja de gráficos + hoja de resumen

**⚙️ Configuración:**

```python
config = {
    'excel_template': {
        'target_sheet': 'Datos',
        'preserve_all_sheets': True,
        'sheet_protection': {
            'data_sheet': False,
            'charts_sheet': True,
            'summary_sheet': True
        }
    },
    'cell_mapping': {
        'data_start': 'A6',
        'include_headers': True,
        'preserve_formulas': True
    }
}
```

**✅ Resultado:** Datos se insertan en hoja especificada, otras hojas preservadas intactas.

## Automatización y Scripts

### Script de Automatización Básica

**📜 Script Python para automatización:**

```python
#!/usr/bin/env python3
"""
Script de automatización para exportación separada
Ejemplo de uso empresarial
"""

import pandas as pd
from core.data_handler import exportar_datos_separados
from pathlib import Path
import datetime

def automatizar_reportes_mensuales(archivo_datos, carpeta_destino):
    """
    Automatiza la generación de reportes mensuales
    
    Args:
        archivo_datos: Ruta al archivo CSV/Excel con datos
        carpeta_destino: Carpeta donde guardar reportes
    """
    
    # 1. Cargar datos
    df = pd.read_csv(archivo_datos)
    
    # 2. Filtrar solo datos del mes actual
    df['fecha'] = pd.to_datetime(df['fecha'])
    mes_actual = datetime.datetime.now().replace(day=1)
    df_mes = df[df['fecha'].dt.month == mes_actual.month]
    
    if df_mes.empty:
        print("No hay datos para el mes actual")
        return
    
    # 3. Configuración para exportación
    config = {
        'separator_column': 'departamento',
        'template_path': 'templates/plantilla_corporativa.xlsx',
        'output_folder': carpeta_destino,
        'file_template': 'Reporte_{valor}_{mes_actual:%Y_%m}.xlsx',
        'column_mapping': {
            'empleado': 'A',
            'ventas': 'B',
            'objetivo': 'C',
            'cumplimiento': 'D'
        },
        'enable_chunking': True,
        'chunk_size': 5000
    }
    
    # 4. Ejecutar exportación
    resultado = exportar_datos_separados(df_mes, config)
    
    # 5. Generar resumen
    if resultado['success']:
        print(f"✅ Exportación completada:")
        print(f"   📊 {resultado['groups_processed']} departamentos procesados")
        print(f"   📁 {len(resultado['files_created'])} archivos generados")
        print(f"   ⏱️  Tiempo: {resultado['processing_time']:.2f} segundos")
        
        # Enviar resumen por email (opcional)
        enviar_resumen_email(resultado)
    else:
        print(f"❌ Error en exportación: {resultado['errors']}")

def enviar_resumen_email(resultado):
    """
    Envía resumen de exportación por email
    (Requiere configuración SMTP)
    """
    # Implementación opcional
    pass

# Uso del script
if __name__ == "__main__":
    automatizar_reportes_mensuales(
        archivo_datos="datos/ventas_noviembre.csv",
        carpeta_destino="reportes/2025-11/"
    )
```

### Script de Monitoreo y Alertas

**📜 Script de monitoreo continuo:**

```python
#!/usr/bin/env python3
"""
Monitor de procesos de exportación separada
Envía alertas si hay problemas
"""

import time
import psutil
import smtplib
from email.mime.text import MimeText
from datetime import datetime, timedelta

class ExportMonitor:
    def __init__(self, alert_email=None, smtp_config=None):
        self.alert_email = alert_email
        self.smtp_config = smtp_config
        self.last_check = datetime.now()
        
    def check_system_resources(self):
        """Verifica recursos del sistema"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        alerts = []
        
        if cpu_percent > 80:
            alerts.append(f"CPU alta: {cpu_percent:.1f}%")
            
        if memory.percent > 85:
            alerts.append(f"Memoria alta: {memory.percent:.1f}%")
            
        if disk.percent > 90:
            alerts.append(f"Disco lleno: {disk.percent:.1f}%")
            
        return alerts
    
    def check_export_processes(self):
        """Verifica procesos de exportación activos"""
        # Buscar procesos de Python con keywords relacionados
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'python' in cmdline and 'exportar_datos_separados' in cmdline:
                    python_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return python_processes
    
    def send_alert(self, message):
        """Envía alerta por email"""
        if not self.alert_email or not self.smtp_config:
            print(f"ALERTA: {message}")
            return
            
        msg = MimeText(f"Alerta de Exportación Separada\n\n{message}\n\nTimestamp: {datetime.now()}")
        msg['Subject'] = "Alerta - Exportación Separada"
        msg['From'] = self.smtp_config['from']
        msg['To'] = self.alert_email
        
        try:
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            server.starttls()
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()
            print(f"Alerta enviada: {message}")
        except Exception as e:
            print(f"Error enviando alerta: {e}")
    
    def run_continuous_monitoring(self, interval_minutes=5):
        """Ejecuta monitoreo continuo"""
        while True:
            try:
                # Verificar recursos
                alerts = self.check_system_resources()
                
                # Verificar procesos
                export_processes = self.check_export_processes()
                
                if export_processes:
                    print(f"Monitoreando {len(export_processes)} procesos de exportación")
                
                if alerts:
                    for alert in alerts:
                        self.send_alert(alert)
                
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("Monitoreo detenido")
                break
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                time.sleep(60)

# Uso del monitor
if __name__ == "__main__":
    monitor = ExportMonitor(
        alert_email="admin@empresa.com",
        smtp_config={
            'server': 'smtp.gmail.com',
            'port': 587,
            'username': 'notificaciones@empresa.com',
            'password': 'app_password'
        }
    )
    
    monitor.run_continuous_monitoring(interval_minutes=5)
```

### Configuración de Tareas Programadas

**📜 Cron Job para Linux/macOS:**

```bash
#!/bin/bash
# Script para crontab - ejecutar diariamente a las 6 AM

# Variables
SCRIPT_PATH="/path/to/flash_sheet/scripts/automatizar_reportes.py"
LOG_PATH="/var/log/exportacion_separada.log"
DATA_PATH="/path/to/data/daily_sales.csv"
OUTPUT_PATH="/path/to/output/daily_reports/"

# Crear directorio de salida si no existe
mkdir -p "$OUTPUT_PATH"

# Ejecutar script de Python
cd "$(dirname "$SCRIPT_PATH")"
python3 "$SCRIPT_PATH" \
    --data-file "$DATA_PATH" \
    --output-folder "$OUTPUT_PATH" \
    --template "/path/to/templates/daily_template.xlsx" \
    >> "$LOG_PATH" 2>&1

# Rotar logs (mantener últimos 30 días)
find "$LOG_PATH" -mtime +30 -delete
```

**⏰ Crontab Entry:**

```bash
# Ejecutar diariamente a las 6:00 AM
0 6 * * * /path/to/flash_sheet/scripts/run_daily_export.sh

# Ejecutar cada 15 minutos para monitoreo
*/15 * * * * python3 /path/to/monitor_export.py
```

**🪟 Windows Task Scheduler:**

```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Exportación Separada Diaria</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2025-01-01T06:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>python</Command>
      <Arguments>"C:\path\to\flash_sheet\scripts\automatizar_reportes.py"</Arguments>
      <WorkingDirectory>C:\path\to\flash_sheet</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
```

---

## Resumen de Mejores Prácticas

### ✅ Recomendaciones Generales

1. **Configuración Inicial**:
   - Comienza con configuración por defecto
   - Usa ejemplos básicos para aprender
   - Prueba con datasets pequeños primero

2. **Optimización de Rendimiento**:
   - Activa chunking para datasets > 10K filas
   - Monitorea uso de memoria durante ejecución
   - Usa plantillas simples para mejor rendimiento

3. **Seguridad y Backup**:
   - Siempre haz backup de plantillas originales
   - Verifica permisos de carpeta destino
   - Usa recuperación automática en entornos críticos

4. **Automatización**:
   - Implementa scripts para tareas repetitivas
   - Configura monitoreo para procesos largos
   - Establece alertas para problemas

### 🚫 Errores Comunes a Evitar

1. **Plantillas demasiado complejas** ralentizan el proceso
2. **No verificar permisos** causa fallos en ejecución
3. **Charset incorrectos** pueden corromper caracteres especiales
4. **Nombres de archivo muy largos** fallan en algunos sistemas operativos
5. **No monitorear memoria** en datasets grandes puede causar crashes

### 📊 Métricas de Éxito Esperadas

| Métrica | Objetivo | Tiempo/Recurso |
|---------|----------|----------------|
| **Tiempo de Configuración** | < 5 minutos | Casos simples |
| **Procesamiento** | < 3x exportación normal | Según tamaño dataset |
| **Uso de Memoria** | < 2GB para 1M filas | Datasets grandes |
| **Tasa de Éxito** | > 95% sin intervención | Operación normal |
| **Preservación Formato** | 100% | Plantillas Excel |

**¡Gracias por revisar estos ejemplos y casos de uso!**

Para soporte adicional o casos específicos no cubiertos aquí, consulta la documentación técnica o contacta al equipo de desarrollo.