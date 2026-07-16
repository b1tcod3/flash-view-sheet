# Manual de Configuración Avanzada

## 📋 Índice

1. [Introducción](#introducción)
2. [Configuración de Rendimiento](#configuración-de-rendimiento)
3. [Opciones de Memoria y Chunking](#opciones-de-memoria-y-chunking)
4. [Plantillas de Nombres Avanzadas](#plantillas-de-nombres-avanzadas)
5. [Mapeo de Columnas Detallado](#mapeo-de-columnas-detallado)
6. [Manejo de Casos Especiales](#manejo-de-casos-especiales)
7. [Configuración de Logging](#configuración-de-logging)
8. [Optimizaciones por Tipo de Datos](#optimizaciones-por-tipo-de-datos)
9. [Configuración para Entornos Corporativos](#configuración-para-entornos-corporativos)

## Introducción

Este manual está dirigido a **usuarios avanzados** que necesitan personalizar la funcionalidad de exportación separada para casos específicos, optimizar rendimiento en entornos corporativos, o resolver situaciones complejas de datos.

### Perfil de Usuario Avanzado

- Administradores de datos
- Desarrolladores que integran la funcionalidad
- Usuarios en entornos con datasets grandes
- Administradores de sistemas que optimizan para múltiples usuarios

## Configuración de Rendimiento

### Optimización de Velocidad

**Configuración Recomendada por Tamaño de Dataset:**

| Tamaño Dataset | Estrategia | Tamaño Chunk | RAM Requerida |
|---------------|------------|--------------|---------------|
| **Pequeño** (< 10K filas) | Directo | N/A | < 200MB |
| **Mediano** (10K-100K) | Moderado | 10,000 | 500MB |
| **Grande** (100K-1M) | Agresivo | 5,000 | 1GB |
| **Muy Grande** (> 1M) | Conservador | 1,000 | 2GB+ |

**Parámetros de Optimización:**

```python
config.optimization_config = {
    'enable_chunking': True,
    'chunk_size': 5000,
    'memory_limit_mb': 2048,
    'parallel_processing': False,
    'progressive_output': True,
    'temp_cleanup': True
}
```

### Configuración de Multihilo

**Para Datasets Extremadamente Grandes:**

```python
config.parallel_config = {
    'enabled': True,
    'max_workers': 4,  # No exceder número de CPUs
    'chunk_size': 2500,  # Chunks más pequeños para paralelización
    'memory_per_thread': 512  # MB por hilo
}
```

**⚠️ Precauciones:**
- Solo habilitar en sistemas con 8GB+ RAM
- Monitorear uso de memoria durante ejecución
- Desactivar si hay problemas de estabilidad

### Optimización de I/O

**Para Entornos con Almacenamiento Lento:**

```python
config.io_config = {
    'use_temp_files': True,
    'temp_directory': '/tmp/flash_sheet_exports',
    'compress_temp': True,
    'buffer_size_kb': 512,
    'async_writing': False  # Mantener sincrónico para mejor control
}
```

## Opciones de Memoria y Chunking

### Gestión Automática de Memoria

**Configuración de Thresholds:**

```python
config.memory_config = {
    'auto_threshold': True,  # Detecta automáticamente límites del sistema
    'system_memory_percent': 70,  # Usar máximo 70% de RAM disponible
    'gc_frequency': 100,  # Garbage collection cada 100 operaciones
    'memory_leak_detection': True,
    'max_chunk_memory_mb': 512  # Límite por chunk individual
}
```

### Chunking Inteligente

**Configuración Adaptativa:**

```python
config.chunking_strategy = {
    'adaptive_sizing': True,  # Ajusta tamaño según datos
    'data_size_analysis': True,  # Analiza distribución de datos
    'balance_memory_speed': True,  # Equilibra velocidad vs memoria
    'predictive_sizing': True  # Predice tamaño óptimo basado en patrón de datos
}
```

**Configuración Manual por Escenario:**

```python
# Escenario 1: Muchos grupos pequeños
scenarios.many_small_groups = {
    'chunk_size': 1000,
    'group_threshold': 1000,
    'memory_per_group': 'auto'
}

# Escenario 2: Pocos grupos grandes
scenarios.few_large_groups = {
    'chunk_size': 5000,
    'group_threshold': 10,
    'memory_per_group': 100  # MB
}

# Escenario 3: Distribución uniforme
scenarios.uniform_distribution = {
    'chunk_size': 10000,
    'group_threshold': 'auto',
    'memory_per_group': 'adaptive'
}
```

### Monitoreo de Memoria

**Configuración de Alertas:**

```python
config.memory_monitoring = {
    'enable_alerts': True,
    'warning_threshold_mb': 1500,  # Alerta al 75% del límite
    'critical_threshold_mb': 1800,  # Crítico al 90% del límite
    'alert_callback': 'custom_memory_handler',
    'auto_reduce_chunking': True,
    'emergency_stop_mb': 2048  # Parar automáticamente si excede
}
```

## Plantillas de Nombres Avanzadas

### Sistema de Placeholders Extendido

**Placeholders Básicos:**
- `{valor}` - Valor de columna de separación
- `{fecha}` - Fecha actual (YYYY-MM-DD)
- `{hora}` - Hora actual (HHMMSS)
- `{contador}` - Número secuencial
- `{columna_nombre}` - Nombre de columna

**Placeholders Avanzados:**

```python
advanced_placeholders = {
    '{timestamp}': 'Timestamp Unix en segundos',
    '{uuid}': 'UUID único corto (8 caracteres)',
    '{hash_md5}': 'Hash MD5 de contenido (primeros 8 chars)',
    '{filas}': 'Número de filas en el grupo',
    '{columnas}': 'Número de columnas en el grupo',
    '{tamaño_kb}': 'Tamaño estimado del archivo en KB',
    '{usuario}': 'Nombre de usuario actual',
    '{maquina}': 'Nombre de máquina',
    '{version_datos}': 'Versión o hash de los datos',
    '{sesion_id}': 'ID único de sesión de exportación'
}
```

### Funciones de Procesamiento de Nombres

**Filtros y Transformaciones:**

```python
# Formato: {valor|FILTRO|PARAMETRO}
filters = {
    'upper': '{valor|upper}',  # MAYÚSCULAS
    'lower': '{valor|lower}',  # minúsculas
    'title': '{valor|title}',  # Título Caso
    'slug': '{valor|slug}',    # slug-case
    'date': '{fecha|date|YYYY_MM}',  # Fecha personalizada
    'sanitize': '{valor|sanitize}',  # Sin caracteres especiales
    'length': '{valor|length|10}',   # Máximo 10 caracteres
    'prefix': '{valor|prefix|PRE_}', # Agregar prefijo
    'suffix': '{valor|suffix|_SUF}', # Agregar sufijo
}
```

**Ejemplos de Uso:**

```python
# Ejemplo 1: Nombres corporativos
plantilla_corporativa = "{valor|upper}_{fecha|date|YYYY}_{contador|03d}.xlsx"
# Resultado: NORTE_2025_001.xlsx

# Ejemplo 2: Nombres seguros para sistemas
plantilla_sistema = "{valor|sanitize}_{timestamp}.xlsx"  
# Resultado: norte_sur_1733487234.xlsx

# Ejemplo 3: Nombres descriptivos
plantilla_descriptiva = "Reporte_{valor|title}_{fecha|date|MM_YYYY}_({filas}_filas).xlsx"
# Resultado: Reporte_Norte_11_2025_(1250_filas).xlsx
```

### Configuración de Conflictos

**Resolución Automática de Duplicados:**

```python
config.filename_conflicts = {
    'strategy': 'timestamp_suffix',  # auto_number, timestamp_suffix, hash_suffix
    'max_attempts': 999,
    'fallback_strategy': 'uuid_suffix',
    'preserve_extension': True,
    'case_sensitive': False,  # Manejar diferencias case-insensitive
    'special_chars': 'remove'  # remove, replace_with_underscore, keep
}
```

## Mapeo de Columnas Detallado

### Tipos de Mapeo Avanzados

**1. Mapeo por Patrones:**

```python
config.mapping_patterns = {
    'auto_pattern_matching': True,
    'pattern_config': {
        'date_columns': ['fecha', 'date', 'tiempo', 'time'],
        'amount_columns': ['total', 'cantidad', 'amount', 'sum'],
        'name_columns': ['nombre', 'name', 'producto', 'item'],
        'id_columns': ['id', 'codigo', 'code', 'identifier']
    }
}
```

**2. Mapeo con Transformaciones:**

```python
config.column_transformations = {
    'enabled': True,
    'transformations': {
        'date_format': {
            'enabled': True,
            'input_format': 'YYYY-MM-DD',
            'output_format': 'DD/MM/YYYY',
            'columns': ['fecha_ingreso', 'fecha_nacimiento']
        },
        'number_format': {
            'enabled': True,
            'decimal_places': 2,
            'thousands_separator': ',',
            'columns': ['precio', 'total', 'cantidad']
        },
        'text_cleaning': {
            'enabled': True,
            'trim_whitespace': True,
            'remove_special_chars': False,
            'columns': ['comentarios', 'descripcion']
        }
    }
}
```

**3. Mapeo Condicional:**

```python
config.conditional_mapping = {
    'enabled': True,
    'rules': [
        {
            'condition': 'column.type == "numeric"',
            'mapping': 'auto_by_position',
            'skip_formatting': True
        },
        {
            'condition': 'column.name.contains("fecha")',
            'mapping': 'A',  # Siempre a columna A
            'date_format': 'YYYY-MM-DD'
        },
        {
            'condition': 'column.values.max() > 1000000',
            'mapping': 'last_available_column',
            'number_format': '#,##0'
        }
    ]
}
```

### Validación de Mapeo

**Configuración de Validación:**

```python
config.mapping_validation = {
    'strict_mode': False,
    'validation_rules': {
        'required_columns': [],  # Columnas que DEBEN estar mapeadas
        'forbidden_columns': ['password', 'secret'],  # Columnas que NO se pueden mapear
        'max_columns_per_excel': 16384,  # Límite Excel
        'column_order_strict': False  # Permitir reordenamiento automático
    },
    'auto_correction': {
        'enabled': True,
        'suggest_alternatives': True,
        'auto_resolve_conflicts': True
    }
}
```

## Manejo de Casos Especiales

### Configuración para Valores Nulos

**Estrategias Avanzadas:**

```python
config.null_handling = {
    'default_strategy': 'group_together',
    'strategies': {
        'group_together': {
            'null_group_name': 'Valores_Nulos',
            'create_file': True
        },
        'separate_file': {
            'null_file_name': 'Sin_Valores_{fecha}.xlsx',
            'include_in_summary': True
        },
        'exclude': {
            'log_excluded_count': True,
            'summary_file': True
        },
        'custom_value': {
            'custom_null_value': 'NO_VALOR',
            'preserved_types': ['numeric', 'date']  # Solo aplicar a estos tipos
        }
    },
    'detection_sensitivity': 'medium'  # low, medium, high
}
```

### Configuración para Caracteres Especiales

**Sanitización Avanzada:**

```python
config.character_handling = {
    'excel_invalid_chars': 'remove',  # remove, replace, escape
    'replacement_char': '_',
    'max_filename_length': 255,
    'preserve_accents': True,
    'normalize_unicode': True,
    'platform_specific': {
        'windows': {
            'reserved_names': True,  # CON, PRN, AUX, etc.
            'case_preservation': True
        },
        'unix': {
            'path_separator_handling': 'escape'
        }
    }
}
```

### Configuración de Recovery

**Manejo de Errores y Recovery:**

```python
config.recovery_config = {
    'enable_automatic_recovery': True,
    'recovery_strategies': {
        'template_corruption': {
            'try_backup': True,
            'create_default': True,
            'notification_level': 'warning'
        },
        'disk_space': {
            'cleanup_temp_files': True,
            'reduce_chunk_size': True,
            'emergency_location': None  # Usar ubicación temporal
        },
        'memory_exhaustion': {
            'reduce_chunk_size': True,
            'pause_and_resume': True,
            'gc_frequency': 50
        },
        'partial_failure': {
            'continue_with_remaining': True,
            'retry_failed_groups': 3,
            'progress_persistence': True
        }
    }
}
```

## Configuración de Logging

### Niveles de Logging Detallados

**Configuración de Logs:**

```python
config.logging_config = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'file_logging': {
        'enabled': True,
        'path': 'logs/separacion_datos.log',
        'max_size_mb': 100,
        'backup_count': 5,
        'format': '%(asctime)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
    },
    'console_logging': {
        'enabled': True,
        'level': 'INFO',
        'color_output': True
    },
    'log_categories': {
        'performance': True,
        'errors': True,
        'user_actions': True,
        'memory_usage': True,
        'file_operations': True
    }
}
```

### Métricas y Monitoreo

**Configuración de Métricas:**

```python
config.metrics_config = {
    'enabled': True,
    'collection_points': {
        'memory_usage': 'per_chunk',
        'processing_time': 'per_group',
        'file_sizes': 'per_file',
        'error_rates': 'per_operation'
    },
    'export_metrics': {
        'format': 'json',  # json, csv, excel
        'path': 'metrics/separacion_metrics.json',
        'include_sample_data': False
    },
    'real_time_monitoring': {
        'enabled': True,
        'update_frequency_seconds': 5,
        'webhook_url': None,  # Para notificaciones
        'alert_thresholds': {
            'processing_time_minutes': 60,
            'memory_usage_percent': 85,
            'error_rate_percent': 5
        }
    }
}
```

## Optimizaciones por Tipo de Datos

### Optimización para Datos Numéricos

```python
config.numeric_optimization = {
    'enable_compression': True,
    'float_precision': 2,  # Reducir precisión para archivos más pequeños
    'zero_handling': {
        'convert_to_null': False,
        'format_as_integer': False
    },
    'large_number_handling': {
        'use_scientific_notation': True,
        'preserve_significant_digits': 6
    }
}
```

### Optimización para Texto

```python
config.text_optimization = {
    'encoding': 'utf-8',
    'trim_whitespace': True,
    'normalize_unicode': True,
    'compress_repeated_spaces': True,
    'max_length_per_cell': 32767,  # Límite Excel
    'truncation_strategy': 'ellipsis',  # truncate, ellipsis, error
    'multiline_handling': 'preserve'  # preserve, flatten, escape
}
```

### Optimización para Fechas

```python
config.date_optimization = {
    'preserve_timezone': True,
    'format_conversion': {
        'enabled': True,
        'standard_format': 'YYYY-MM-DD HH:MM:SS',
        'local_timezone': True
    },
    'serialization': {
        'as_excel_serial': False,  # O como string ISO
        'excel_date_format': 'DD/MM/YYYY'
    }
}
```

## Configuración para Entornos Corporativos

### Configuración Multi-Usuario

```python
config.corporate_config = {
    'multi_user_support': {
        'enabled': True,
        'max_concurrent_exports': 4,
        'user_quotas': {
            'max_files_per_user': 1000,
            'max_disk_space_mb': 5000,
            'max_concurrent_jobs': 2
        },
        'resource_allocation': {
            'cpu_cores_per_job': 2,
            'memory_per_job_mb': 1024,
            'io_priority': 'normal'  # low, normal, high
        }
    }
}
```

### Configuración de Seguridad

```python
config.security_config = {
    'data_encryption': {
        'temp_files': False,  # Solo para datos sensibles
        'output_files': False,
        'encryption_algorithm': 'AES-256'
    },
    'access_control': {
        'user_permissions': True,
        'column_restrictions': {
            'sensitive_columns': ['salario', 'ssn', 'cedula'],
            'mask_in_logs': True,
            'require_confirmation': True
        }
    },
    'audit_logging': {
        'enabled': True,
        'log_user_actions': True,
        'log_data_access': True,
        'retention_days': 365
    }
}
```

### Configuración de Integración

```python
config.integration_config = {
    'api_endpoints': {
        'enabled': False,
        'authentication': 'api_key',
        'rate_limiting': {
            'requests_per_hour': 100,
            'burst_limit': 10
        }
    },
    'database_integration': {
        'enabled': False,
        'connection_string': None,
        'metadata_storage': {
            'export_history': True,
            'user_preferences': True,
            'performance_metrics': True
        }
    },
    'notification_system': {
        'email_notifications': {
            'enabled': False,
            'smtp_server': None,
            'admin_email': None
        },
        'webhook_notifications': {
            'enabled': False,
            'endpoints': []
        }
    }
}
```

## Configuración Avanzada del Sistema

### Configuración de Performance Tuning

```python
config.performance_tuning = {
    'excel_optimization': {
        'disable_calculation_on_load': True,
        'preserve_formulas': True,
        'optimize_file_size': True,
        'compatibility_mode': 'excel_2016'
    },
    'memory_tuning': {
        'initial_chunk_size': 'auto',
        'growth_factor': 1.5,
        'max_growth_attempts': 10,
        'memory_mapping': True
    },
    'io_tuning': {
        'buffer_size_kb': 1024,
        'async_io': False,
        'compression_level': 6,
        'temp_file_cleanup': 'immediate'
    }
}
```

### Configuración de Desarrollo y Debug

```python
config.development_config = {
    'debug_mode': False,
    'profile_performance': False,
    'memory_profiling': False,
    'detailed_logging': False,
    'test_data_generation': {
        'enabled': False,
        'data_size_limit': 1000,
        'preserve_original_data': True
    },
    'api_simulation': {
        'enabled': False,
        'delay_responses': False,
        'error_simulation': False
    }
}
```

---

**Nota Importante**: Esta configuración avanzada requiere conocimientos técnicos. Para la mayoría de usuarios, la configuración por defecto es suficiente y recomendada. Solo modificar estos parámetros si hay necesidades específicas o problemas de rendimiento documentados.

**Consultar Soporte Técnico** para implementaciones complejas o integraciones corporativas.