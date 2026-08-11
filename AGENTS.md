# Reglas del proyecto

## Código Python

- No uses comprehensions sin transformación: `[x for x in it]`, `{x for x in s}`, `[i for i in range(n)]`. Usa `list(it)`, `set(s)`, `dict(...)`, `list(range(n))`.
- Usa `list(it)`/`set(it)`/`dict(it)` cuando el constructor cubra la transformación.
- Una comprehension SÍ es válida si transforma: `[f'Valor_{i}' for i in range(n)]`.
- Referencia: DeepSource PYL-R1721.
