# app/services/pivot_service.py — Documentacion Completa

Servicio centralizado para operaciones de tablas pivote en Flash View Sheet. Define la clase `PivotService` que crea pivotes simples, combinados, agregaciones de fallback y tablas de contingencia, con un patron de fallback en cascada que garantiza siempre un resultado o un None controlado.

---

## Indice

1. [Vision General](#1-vision-general)
2. [Importaciones](#2-importaciones)
3. [Clase PivotService](#3-clase-pivotservice)
   - [3.1 Constructor](#31-constructor)
   - [3.2 Cleanup](#32-cleanup)
   - [3.3 Pivot Simples](#33-pivot-simples)
   - [3.4 Pivot Combinada](#34-pivot-combinada)
   - [3.5 Agregaciones](#35-agregaciones)
   - [3.6 Interfaz Simplificada](#36-interfaz-simplificada)
   - [3.7 Utilidades](#37-utilidades)
   - [3.8 Validacion](#38-validacion)
4. [Diagrama de Dependencias](#4-diagrama-de-dependencias)
5. [Flujo de Ejecucion](#5-flujo-de-ejecucion)
6. [Resumen](#6-resumen)

---

## 1. Vision General

`pivot_service.py` (471 lineas) es el **servicio de tablas pivote** de la aplicacion. Contiene una unica clase:

- **`PivotService`** — Clase que gestiona todas las operaciones de pivot, agregacion y crosstab

Responsabilidades clave:
- Crear tablas pivote simples via `pd.pivot_table`
- Crear tablas pivote combinadas (multiples valores x multiples funciones de agregacion)
- Crear agregaciones cuando el pivote no es posible (fallback)
- Crear tablas de contingencia (crosstab) via `pd.crosstab`
- Detectar columnas numéricas de forma robusta via `is_numeric_dtype`
- Validar configuraciones de pivote antes de ejecutarlas
- Mantener cache del ultimo resultado (`last_result`, `last_config`)

**Diseno:**
- Sin dependencias de Qt/PySide6 — completamente libre de UI
- Patron de fallback en cascada: pivote → agregacion → `None`
- Logging profesional via `logging.getLogger(__name__)`
- Deteccion de tipos numericos via `pandas.api.types.is_numeric_dtype` (soporta Int64, float32, int32, nullable integers)
- Los metodos de interfaz simplificada (`execute_simple`, `execute_combined`) envuelven los fallbacks en try/except para nunca propagar excepciones no controladas

---

## 2. Importaciones

### Modulos estandar
| Simbolo | Modulo | Uso |
|---------|--------|-----|
| `logging` | `logging` | Sistema de logging del modulo |
| `Any` | `typing` | Tipo generico para config y stats |

### Pandas
| Simbolo | Modulo | Uso |
|---------|--------|-----|
| `pd` | `pandas` | `pd.pivot_table`, `pd.crosstab`, `pd.concat`, `DataFrame.groupby` |
| `is_numeric_dtype` | `pandas.api.types` | Deteccion robusta de columnas numericas |

### Logger
```python
logger = logging.getLogger(__name__)
```
Los mensajes de WARNING se emiten cuando un pivote falla y se inicia fallback. Los mensajes de DEBUG se emiten cuando una combinacion concreta de columna+funcion falla en `create_combined_pivot`.

---

## 3. Clase PivotService

Clase sin herencia (no es QObject). Estado cacheado del ultimo resultado.

### 3.1 Constructor

```python
def __init__(self) -> None:
```

Atributos de estado:

| Atributo | Tipo | Inicial | Descripcion |
|----------|------|---------|-------------|
| `last_result` | `pd.DataFrame \| None` | `None` | DataFrame resultado del ultimo pivot/agregacion exitoso |
| `last_config` | `dict[str, Any] \| None` | `None` | Configuracion usada en la ultima operacion exitosa |

### 3.2 Cleanup

```python
def cleanup(self) -> None:
```

Libera la cache de resultados:

| Atributo | Valor post-cleanup |
|----------|-------------------|
| `last_result` | `None` |
| `last_config` | `None` |

Usar en cierre de aplicacion o al resetear el servicio.

---

### 3.3 Pivot Simples

#### create_simple_pivot

```python
def create_simple_pivot(
    self,
    df: pd.DataFrame,
    index: str | list[str],
    columns: str | list[str] | None = None,
    values: str | list[str] | None = None,
    aggfunc: str = 'sum'
) -> pd.DataFrame | None:
```

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | requerido | DataFrame fuente |
| `index` | `str \| list[str]` | requerido | Columna(s) para el indice |
| `columns` | `str \| list[str] \| None` | `None` | Columna(s) para las columnas del pivote |
| `values` | `str \| list[str] \| None` | `None` | Columna(s) a agregar |
| `aggfunc` | `str` | `'sum'` | Funcion de agregacion |

Retorna `pd.DataFrame | None` (None si df es None o vacio).

**Flujo:**
1. Valida que `df` no sea None ni este vacio
2. Llama a `pd.pivot_table(df, index, columns, values, aggfunc, margins=False, dropna=True)`
3. Guarda resultado en `last_result` y configuracion en `last_config`
4. Retorna el DataFrame pivoteado
5. En caso de excepcion, relanza con mensaje descriptivo

---

### 3.4 Pivot Combinada

#### create_combined_pivot

```python
def create_combined_pivot(
    self,
    df: pd.DataFrame,
    index: str | list[str],
    columns: str | list[str],
    values: list[str],
    aggfuncs: list[str] | None = None
) -> pd.DataFrame | None:
```

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | requerido | DataFrame fuente |
| `index` | `str \| list[str]` | requerido | Columna(s) para el indice |
| `columns` | `str \| list[str]` | requerido | Columna(s) para las columnas del pivote |
| `values` | `list[str]` | requerido | Lista de columnas a agregar |
| `aggfuncs` | `list[str] \| None` | `None` | Lista de funciones de agregacion. Default: `['sum', 'mean', 'count']` |

Retorna `pd.DataFrame | None`.

**Flujo:**
1. Valida que `df` no sea None ni este vacio
2. Si `aggfuncs` es None, usa `['sum', 'mean', 'count']`
3. Para cada `(val_col, agg)` en `values × aggfuncs`:
   - Intenta `pd.pivot_table` con esa combinacion
   - Si es valida y no vacia, anade sufijo `_{agg}` a las columnas y concatena
   - Si falla con `ValueError` o `KeyError`, registra en `logger.debug` y continua con la siguiente combinacion
4. Si hay resultados, concatena todos los DataFrames con `pd.concat(axis=1)`
5. Guarda en `last_result` / `last_config` y retorna
6. Si ninguno funciono, retorna `None`

**Nota:** El `except` interno solo captura `ValueError` y `KeyError` (errores esperables al pivotar). Errores inesperados (TypeError, RuntimeError) propagan al `except` externo.

---

### 3.5 Agregaciones

#### create_simple_aggregation

```python
def create_simple_aggregation(
    self,
    df: pd.DataFrame,
    index: str | list[str],
    values: str | list[str],
    aggfunc: str = 'mean'
) -> pd.DataFrame | None:
```

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | requerido | DataFrame fuente |
| `index` | `str \| list[str]` | requerido | Columna(s) para groupBy |
| `values` | `str \| list[str]` | requerido | Columna(s) a agregar |
| `aggfunc` | `str` | `'mean'` | Funcion de agregacion |

Retorna `pd.DataFrame | None`.

**Flujo:**
1. Normaliza `index` y `values` a `list[str]`
2. Ejecuta `df.groupby(index).agg({col: aggfunc for col in values}).reset_index()`
3. Renombra columnas: las columnas de indice mantienen su nombre, las demas reciben sufijo `_{aggfunc}` (siempre, incluyendo `sum`)
4. Guarda en `last_result` / `last_config`

#### create_fallback_aggregation

```python
def create_fallback_aggregation(
    self,
    df: pd.DataFrame,
    index: str | list[str],
    values: str | list[str],
    aggfunc: str = 'mean'
) -> pd.DataFrame | None:
```

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | requerido | DataFrame fuente |
| `index` | `str \| list[str]` | requerido | Columna(s) para groupBy (puede ser vacio para agregacion global) |
| `values` | `str \| list[str]` | requerido | Columna(s) a agregar |
| `aggfunc` | `str` | `'mean'` | Funcion de agregacion |

Retorna `pd.DataFrame | None`.

**Flujo:**
1. Normaliza `index`:
   - `str` → `[index]`
   - `list` → `index[:2]` (limitado a 2 columnas para evitar cardinalidad excesiva)
   - otro → `[]`
2. Normaliza `values` a `list[str]`
3. Si `values` esta vacio, detecta columnas numericas via `is_numeric_dtype(df[col])`
4. Si aun no hay valores, usa todas las columnas como fallback
5. Filtra columnas que existen en `df`
6. Si `aggfunc` es lista, toma el primer elemento
7. Si hay groupBy, ejecuta `df.groupby(groupby_columns)[values_columns].agg(agg_function).reset_index()`
8. Si no hay groupBy, ejecuta agregacion global: `df[values_columns].agg(agg_function).to_frame().T.reset_index(drop=True)`
9. Guarda en `last_result` / `last_config`

**Limite de 2 columnas groupBy:** Se limita a 2 columnas para evitar que `n filas × m columnas` genere cardinalidad excesiva en el resultado.

---

### 3.6 Interfaz Simplificada

Metodos de alto nivel que encapsulan el patron pivote → fallback → None.

#### execute_simple

```python
def execute_simple(
    self,
    df: pd.DataFrame,
    config: dict[str, Any]
) -> pd.DataFrame | None:
```

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `df` | `pd.DataFrame` | DataFrame fuente |
| `config` | `dict[str, Any]` | Configuracion. Keys: `index`/`rows`, `values`, `aggfunc`, `is_pivot`, `columns` |

**Flujo de fallback:**
```
execute_simple
  ├─ [si is_pivot] → create_simple_pivot()
  │   └─ si falla → logger.warning
  │
  ├─ → create_simple_aggregation()
  │   └─ si falla → logger.warning
  │
  └─ → self.last_result = None; return None
```

#### execute_combined

```python
def execute_combined(
    self,
    df: pd.DataFrame,
    config: dict[str, Any]
) -> pd.DataFrame | None:
```

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `df` | `pd.DataFrame` | DataFrame fuente |
| `config` | `dict[str, Any]` | Configuracion. Keys: `index`/`rows`, `columns`, `values`, `aggfuncs`/`aggfunc` |

**Flujo de fallback:**
```
execute_combined
  ├─ → create_combined_pivot()
  │   └─ si falla → logger.warning
  │
  ├─ → create_fallback_aggregation()
  │   └─ si falla → logger.warning
  │
  └─ → self.last_result = None; return None
```

**Seguridad:** Ambos metodos envuelven los fallbacks en try/except. Si todo falla, `last_result` se pone en `None` y se retorna `None`. Nunca propagan excepciones al caller.

---

### 3.7 Utilidades

#### get_crosstab

```python
def get_crosstab(
    self,
    df: pd.DataFrame,
    index: str,
    columns: str,
    normalize: bool = False
) -> pd.DataFrame | None:
```

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | requerido | DataFrame fuente |
| `index` | `str` | requerido | Columna para filas |
| `columns` | `str` | requerido | Columna para columnas |
| `normalize` | `bool` | `False` | Si True, retorna porcentajes (× 100, redondeados a 2 decimales) |

Usa `pd.crosstab()`. Guarda en `last_result` / `last_config`.

#### get_pivot_stats

```python
def get_pivot_stats(self) -> dict[str, Any] | None:
```

Retorna estadisticas del ultimo resultado:

| Key | Tipo | Descripcion |
|-----|------|-------------|
| `rows` | `int` | Numero de filas |
| `columns` | `int` | Numero de columnas |
| `shape` | `tuple[int, int]` | Forma del DataFrame |
| `config` | `dict \| None` | Configuracion usada |

Retorna `None` si `last_result` es None.

#### get_aggregation_functions

```python
def get_aggregation_functions(self) -> list[tuple[str, str]]:
```

Retorna lista de tuplas `(nombre_display, nombre_funcion)`:

| Display | Funcion |
|---------|---------|
| Suma | `sum` |
| Promedio | `mean` |
| Mediana | `median` |
| Minimo | `min` |
| Maximo | `max` |
| Desviacion estandar | `std` |
| Recuento | `count` |
| Primer valor | `first` |
| Ultimo valor | `last` |

---

### 3.8 Validacion

#### validate_pivot_config

```python
def validate_pivot_config(
    self,
    df: pd.DataFrame,
    config: dict[str, Any]
) -> dict[str, Any]:
```

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `df` | `pd.DataFrame` | DataFrame fuente |
| `config` | `dict[str, Any]` | Configuracion a validar |

Retorna dict con:
- `is_valid: bool`
- `message: str`

**Validaciones en orden:**
1. `df` es None o vacio → `{'is_valid': False, 'message': 'No hay datos'}`
2. Columnas de indice faltantes → `{'is_valid': False, 'message': 'Faltan columnas de indice: ...'}`
3. Columnas de valores faltantes → `{'is_valid': False, 'message': 'Faltan columnas de valores: ...'}`
4. Columnas de valores no numericas → `{'is_valid': False, 'message': 'Las columnas de valores no son numericas'}`

Usa `is_numeric_dtype()` para la verificacion de tipos (cubre Int64, float32, int32, nullable integers).

---

## 4. Diagrama de Dependencias

```
AppCoordinator
  ├── _procesar_pivot_simple(config)
  │     └── pivot_service.execute_simple(df, config)
  │           ├── create_simple_pivot()      → pd.pivot_table()
  │           └── create_simple_aggregation() → df.groupby().agg()
  │
  ├── _procesar_pivot_combinada(config)
  │     └── pivot_service.execute_combined(df, config)
  │           ├── create_combined_pivot()     → pd.pivot_table() × N
  │           │     └── pd.concat(axis=1)
  │           └── create_fallback_aggregation()
  │                 └── df.groupby().agg()  o  df.agg() [global]
  │
  └── exportar_resultado_pivote()
        └── pivot_service.get_pivot_stats()

PivotService
  ├── pd.pivot_table()       (simple y combinada)
  ├── pd.crosstab()          (get_crosstab)
  ├── df.groupby().agg()     (agregaciones)
  ├── pd.concat()            (combinada)
  └── pandas.api.types.is_numeric_dtype()  (fallback y validacion)
```

---

## 5. Flujo de Ejecucion

### Patron de fallback en cascada

```
execute_simple(config)
  │
  ├── [is_pivot=True] ──→ create_simple_pivot()
  │                         ├── Éxito → return DataFrame
  │                         └── Excepción → logger.warning
  │
  └── ──→ create_simple_aggregation()
            ├── Éxito → return DataFrame
            └── Excepción → logger.warning

            ↓ si todo falla

          self.last_result = None
          return None


execute_combined(config)
  │
  └── ──→ create_combined_pivot()
            ├── Éxito → return DataFrame
            └── Excepción → logger.warning

  └── ──→ create_fallback_aggregation()
            ├── Éxito → return DataFrame
            └── Excepción → logger.warning

            ↓ si todo falla

          self.last_result = None
          return None
```

### create_combined_pivot — loop interno

```
for val_col in values:
    for agg in aggfuncs:
        try:
            pivot_table(df, index, columns, val_col, agg)
            ├── Resultado válido → add_suffix(_{agg}) → append
            └── ValueError/KeyError → logger.debug → continue
        except (ValueError, KeyError) as e:
            logger.debug("No se pudo pivotar columna %s con función %s: %s", val_col, agg, e)
            continue

concat(result_dfs, axis=1) → combined
```

---

## 6. Resumen

| Aspecto | Detalle |
|---------|---------|
| **Lineas** | 471 |
| **Clases** | 1 (`PivotService`) |
| **Responsabilidad** | Pivotes, agregaciones, crosstab, validacion |
| **Patron** | Service (sin UI, sin herencia Qt) |
| **Dependencias Qt** | Ninguna |
| **Metodos publicos** | 10 (`cleanup`, `create_simple_pivot`, `create_combined_pivot`, `create_simple_aggregation`, `create_fallback_aggregation`, `get_crosstab`, `get_pivot_stats`, `get_aggregation_functions`, `validate_pivot_config`, `execute_simple`, `execute_combined`) |
| **Metodos de interfaz** | 2 (`execute_simple`, `execute_combined`) — encapsulan fallback |
| **Fallback en cascada** | pivote → agregacion → `None` |
| **Deteccion de tipos** | `is_numeric_dtype()` — soporta Int64, float32, int32, nullable integers |
| **Logging** | `logger.warning` en fallbacks, `logger.debug` en combine fallido |
| **Cache** | `last_result` + `last_config` (invalidados en `cleanup()` o fallo total) |
| **Funciones de agregacion** | 9 (sum, mean, median, min, max, std, count, first, last) |
| **Limite groupBy** | 2 columnas maximo en `create_fallback_aggregation` |
| **Seguridad** | Fallbacks envueltos en try/except — nunca propagan excepciones |
