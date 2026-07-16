Ejemplos Prácticos - Cruce de Datos (Joins)
===========================================

Esta guía proporciona ejemplos prácticos del uso de la funcionalidad de cruce de datos en Flash Sheet, con casos de uso reales y código de ejemplo.

Casos de Uso Empresariales
---------------------------

Enriquecimiento de Datos de Ventas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Escenario**: Una empresa de e-commerce tiene datos de ventas pero necesita información adicional de clientes para análisis.

**Datos de Ventas**:

.. code-block:: text

    | order_id | customer_id | product_id | quantity | order_date |
    |----------|-------------|------------|----------|------------|
    | 1001     | CUST001     | PROD001    | 2        | 2025-01-15 |
    | 1002     | CUST002     | PROD002    | 1        | 2025-01-16 |
    | 1003     | CUST001     | PROD003    | 3        | 2025-01-17 |

**Datos de Clientes**:

.. code-block:: text

    | customer_id | name       | region | customer_type |
    |-------------|------------|--------|---------------|
    | CUST001     | Juan Pérez | Norte  | Premium      |
    | CUST002     | Ana García | Sur    | Standard     |
    | CUST003     | Carlos Ruiz| Este   | Premium      |

**Join Recomendado**: Left Join

.. code-block:: python

    from core.join.data_join_manager import DataJoinManager
    from core.join.models import JoinConfig, JoinType

    # Cargar datasets
    sales_df = pd.read_csv('sales_data.csv')
    customers_df = pd.read_csv('customers_data.csv')

    # Configurar join
    config = JoinConfig(
        join_type=JoinType.LEFT,
        left_keys=['customer_id'],
        right_keys=['customer_id'],
        suffixes=('_sales', '_customer')
    )

    # Ejecutar join
    join_manager = DataJoinManager(sales_df, customers_df)
    result = join_manager.execute_join(config)

    # Resultado incluye toda la información de ventas + datos de clientes
    print(result.data.head())

**Resultado**:

.. code-block:: text

    | order_id | customer_id | product_id | quantity | order_date | name       | region | customer_type |
    |----------|-------------|------------|----------|------------|------------|--------|---------------|
    | 1001     | CUST001     | PROD001    | 2        | 2025-01-15 | Juan Pérez | Norte  | Premium      |
    | 1002     | CUST002     | PROD002    | 1        | 2025-01-16 | Ana García | Sur    | Standard     |
    | 1003     | CUST001     | PROD003    | 3        | 2025-01-17 | Juan Pérez | Norte  | Premium      |

Análisis de Inventario y Proveedores
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Escenario**: Un minorista necesita combinar información de productos con datos de proveedores.

**Datos de Productos**:

.. code-block:: text

    | product_id | product_name | category | stock_quantity |
    |------------|--------------|----------|----------------|
    | PROD001    | Laptop A1    | Electronics | 50         |
    | PROD002    | Mouse B2     | Accessories| 200        |
    | PROD003    | Keyboard C3  | Accessories| 75         |

**Datos de Proveedores**:

.. code-block:: text

    | supplier_id | product_id | supplier_name | cost_price | lead_time |
    |-------------|------------|---------------|------------|-----------|
    | SUP001      | PROD001    | TechCorp      | 800.00     | 7         |
    | SUP002      | PROD002    | AccSupplier   | 15.50      | 3         |
    | SUP003      | PROD003    | AccSupplier   | 25.00      | 3         |

**Join Recomendado**: Inner Join

.. code-block:: python

    config = JoinConfig(
        join_type=JoinType.INNER,
        left_keys=['product_id'],
        right_keys=['product_id'],
        validate_integrity=True
    )

    join_manager = DataJoinManager(products_df, suppliers_df)
    result = join_manager.execute_join(config)

**Resultado**: Solo productos que tienen proveedores asignados.

Consolidación de Datos Financieros
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Escenario**: Un banco necesita combinar transacciones con información de cuentas.

**Datos de Transacciones**:

.. code-block:: text

    | transaction_id | account_id | amount | transaction_date |
    |----------------|------------|--------|------------------|
    | TXN001         | ACC001     | 500.00 | 2025-01-15      |
    | TXN002         | ACC002     | 250.00 | 2025-01-16      |
    | TXN003         | ACC001     | -100.00| 2025-01-17      |

**Datos de Cuentas**:

.. code-block:: text

    | account_id | customer_name | account_type | balance |
    |------------|---------------|--------------|---------|
    | ACC001     | Juan Pérez    | Checking     | 2500.00 |
    | ACC002     | Ana García    | Savings      | 5000.00 |
    | ACC003     | Carlos Ruiz   | Checking     | 1200.00 |

**Join Recomendado**: Left Join con indicador

.. code-block:: python

    config = JoinConfig(
        join_type=JoinType.LEFT,
        left_keys=['account_id'],
        right_keys=['account_id'],
        indicator=True,  # Añadir columna _merge
        sort_results=True
    )

    result = join_manager.execute_join(config)

**Resultado**: Todas las transacciones con información de cuenta, columna _merge indica origen.

Análisis de Recursos Humanos
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Escenario**: Departamento de RRHH combina datos de empleados con evaluaciones de desempeño.

**Datos de Empleados**:

.. code-block:: text

    | employee_id | name       | department | hire_date  |
    |-------------|------------|------------|------------|
    | EMP001      | Juan Pérez | IT         | 2023-01-15 |
    | EMP002      | Ana García | HR         | 2023-03-20 |
    | EMP003      | Carlos Ruiz| Finance    | 2023-06-10 |

**Datos de Evaluaciones**:

.. code-block:: text

    | employee_id | review_date | rating | reviewer    |
    |-------------|-------------|--------|-------------|
    | EMP001      | 2024-12-01 | 4.5    | Manager A   |
    | EMP002      | 2024-12-01 | 4.2    | Manager B   |
    | EMP004      | 2024-12-01 | 3.8    | Manager C   |

**Join Recomendado**: Left Join (todos los empleados, incluso sin evaluación)

.. code-block:: python

    config = JoinConfig(
        join_type=JoinType.LEFT,
        left_keys=['employee_id'],
        right_keys=['employee_id'],
        suffixes=('_emp', '_review')
    )

**Resultado**: Todos los empleados con sus evaluaciones (si existen).

Cross Join para Análisis de Escenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Escenario**: Análisis de sensibilidad con múltiples escenarios.

**Datos de Productos**:

.. code-block:: text

    | product_id | product_name | base_price |
    |------------|--------------|------------|
    | PROD001    | Laptop       | 1000.00    |
    | PROD002    | Monitor      | 300.00     |

**Escenarios de Descuento**:

.. code-block:: text

    | scenario_id | discount_pct | description    |
    |-------------|--------------|----------------|
    | SCEN001     | 0.05         | Light Discount |
    | SCEN002     | 0.10         | Medium Discount|
    | SCEN003     | 0.15         | Heavy Discount |

**Join Recomendado**: Cross Join

.. code-block:: python

    config = JoinConfig(
        join_type=JoinType.CROSS
        # No keys needed for cross join
    )

    result = join_manager.execute_join(config)

**Resultado**: Todas las combinaciones producto-escenario para análisis de sensibilidad.

Ejemplos Avanzados
------------------

Join con Múltiples Columnas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Join usando múltiples columnas como clave
    config = JoinConfig(
        join_type=JoinType.INNER,
        left_keys=['customer_id', 'product_category'],
        right_keys=['client_id', 'category'],
        validate_integrity=True
    )

Join con Preview
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Obtener preview antes de ejecutar join completo
    preview = join_manager.get_join_preview(config, max_rows=50)

    if len(preview) > 10000:  # Si el resultado será muy grande
        print("Resultado muy grande, considere filtrar datos primero")
    else:
        result = join_manager.execute_join(config)

Manejo de Errores
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from core.join.exceptions import (
        JoinValidationError,
        JoinExecutionError,
        MemoryLimitExceededError
    )

    try:
        result = join_manager.execute_join(config)
        if result.success:
            print(f"Join exitoso: {result.metadata.result_rows} filas")
        else:
            print(f"Join falló: {result.error_message}")
    except JoinValidationError as e:
        print(f"Error de validación: {e}")
        # Corregir configuración
    except MemoryLimitExceededError as e:
        print("Memoria insuficiente, considere datasets más pequeños")
    except JoinExecutionError as e:
        print(f"Error de ejecución: {e}")

Uso del Historial
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from core.join.join_history import JoinHistory

    # Inicializar historial
    history = JoinHistory()

    # Después de ejecutar join
    history.add_entry("sales.csv", "customers.csv", config, result)

    # Recuperar joins anteriores
    recent_joins = history.get_entries(limit=5)

    # Re-ejecutar join anterior
    old_config = recent_joins[0].config
    # ... cargar datasets y ejecutar

Casos de Uso por Industria
---------------------------

Retail y E-commerce
~~~~~~~~~~~~~~~~~~~

- **Customer 360**: Unir datos de compras, navegación web y soporte al cliente
- **Análisis de Inventario**: Combinar niveles de stock con datos de proveedores
- **Segmentación de Clientes**: Unir datos demográficos con comportamiento de compra

Finanzas y Banca
~~~~~~~~~~~~~~~~

- **Risk Assessment**: Combinar datos de transacciones con scores de riesgo
- **Portfolio Analysis**: Unir posiciones de inversión con datos de mercado
- **Compliance Reporting**: Combinar datos de clientes con requisitos regulatorios

Salud y Farmacéutica
~~~~~~~~~~~~~~~~~~~~

- **Patient Records**: Unir historiales médicos con datos de tratamientos
- **Clinical Trials**: Combinar datos de pacientes con resultados de estudios
- **Drug Interaction Analysis**: Unir prescripciones con bases de datos de interacciones

Manufactura e Industria
~~~~~~~~~~~~~~~~~~~~~~~

- **Supply Chain**: Combinar datos de proveedores con requerimientos de producción
- **Quality Control**: Unir datos de producción con resultados de inspección
- **Maintenance Planning**: Combinar datos de equipos con historiales de mantenimiento

Mejores Prácticas
-----------------

1. **Validación de Datos**
   - Siempre usar `validate_integrity=True` para joins importantes
   - Verificar tipos de datos antes de join
   - Usar preview para estimar tamaño del resultado

2. **Gestión de Memoria**
   - Para datasets grandes, el sistema automáticamente usa chunking
   - Monitorear uso de memoria en operaciones complejas
   - Considerar filtrado previo para reducir tamaño de datos

3. **Nombres de Columnas**
   - Usar sufijos descriptivos para columnas duplicadas
   - Evitar nombres de columnas demasiado largos
   - Mantener consistencia en nomenclatura

4. **Historial y Reproducibilidad**
   - Guardar configuraciones importantes en historial
   - Documentar propósito de cada join
   - Usar nombres descriptivos para datasets

5. **Performance**
   - Para cross joins, limitar tamaño de datasets
   - Usar inner joins cuando sea posible (más eficientes)
   - Considerar índices en columnas de join si es aplicable

Solución de Problemas Comunes
-----------------------------

**Join Produce Muy Pocas Filas**
- Verificar que las columnas de join tienen valores matching
- Revisar tipos de datos (string vs integer)
- Considerar usar left join en lugar de inner

**Join Produce Demasiadas Filas**
- Verificar cardinalidad de la relación
- Revisar si se necesita distinct en alguna tabla
- Considerar agregar más columnas a la clave de join

**Out of Memory Error**
- Reducir tamaño de datasets con filtros
- Usar chunking (automático para datasets grandes)
- Considerar joins en etapas

**Columnas Duplicadas Confusas**
- Usar sufijos claros y descriptivos
- Renombrar columnas antes del join si es necesario
- Revisar esquema de resultado antes de proceder

Recursos Adicionales
--------------------

- **Documentación Técnica**: `docs/developer_guide/architecture.rst`
- **API Reference**: `docs/api/classes.rst`
- **Guía de Usuario**: `docs/user_guide/README.md`
- **Testing**: `tests/test_join.py` para ejemplos de uso en código