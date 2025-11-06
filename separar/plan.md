# Plan de Corrección: Preservación de Formato en Plantillas Excel

## Problema Identificado
Cuando se insertan valores en plantillas Excel, el formato original se está modificando en lugar de mantenerse intacto.

## Soluciones Propuestas

### 1. **Corrección del Carga de Plantilla**
- Cambiar `data_only=False` a `data_only=True` en la carga inicial
- Mantener formato preservado con `keep_vba=True`, `keep_links=True`, `data_only=False` para preserva formatos
- Implementar carga de solo formatos sin interpretar datos

### 2. **Preservación Explícita de Formatos**
- Cache de formatos antes de insertar datos
- Restauración de formatos después de escribir datos
- Verificación de formato antes y después del proceso

### 3. **Mejoras en el Proceso de Escritura**
- Usar `cell.value = value` sin tocar `cell.font`, `cell.fill`, `cell.border`
- Evitar sobrescribir estilos existentes
- Implementar verificación de integridad de formato

### 4. **Testing de Preservación de Formato**
- Crear tests específicos para verificar que el formato se preserve
- Tests con plantillas complejas con múltiples estilos
- Verificación de elementos de formato específicos (font, fill, border, number_format)

## Implementación
- Modificar `_create_excel_file_with_template` en `core/data_handler.py`
- Crear función auxiliar para preservar formatos
- Añadir logging para diagnosticar problemas de formato
- Crear tests específicos de preservación de formato

## Estado
- ✅ Problema identificado
- 🔄 Solución en desarrollo
- ⏳ Pendiente testing