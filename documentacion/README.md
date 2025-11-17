# Documentación de Flash Sheet

Esta carpeta contiene la documentación HTML generada del proyecto Flash Sheet.

## Cómo compilar y actualizar la documentación

### Paso 1: Instalar dependencias
Asegúrate de tener instaladas las dependencias necesarias:
```bash
pip install sphinx sphinx-rtd-theme
```

### Paso 2: Compilar la documentación
Desde la raíz del proyecto, ejecuta:
```bash
cd docs
sphinx-build -b html . _build/html
```

### Paso 3: Copiar a la carpeta de documentación
Desde la raíz del proyecto, ejecuta:
```bash
cp -r docs/_build/html/* documentacion/
```

### Paso 4: Verificar
Abre `documentacion/index.html` en tu navegador para ver la documentación.

## Estructura de la documentación

- **index.html**: Página principal con tabla de contenidos
- **user_guide/**: Guía de usuario
- **developer_guide/**: Guía de desarrollador
- **api/**: Referencia de API
- **releases/**: Notas de release

## Servir la documentación localmente

Para servir la documentación en un servidor local:
```bash
cd documentacion
python -m http.server 8000
```

Luego abre http://localhost:8000 en tu navegador.

## Desplegar en un servidor web

### Opción 1: Servidor local (desarrollo)
Si tienes Apache/Nginx sirviendo `/var/www/html/`, la documentación ya está disponible en:
```
http://tu-servidor/proyectos/flash-sheet/documentacion/index.html
```

### Opción 2: Subir a un servidor remoto
1. Compila y copia la documentación siguiendo los pasos 1-3
2. Comprime la carpeta `documentacion/`:
   ```bash
   tar -czf documentacion.tar.gz documentacion/
   ```
3. Sube el archivo comprimido a tu servidor
4. Descomprímelo en el directorio web público:
   ```bash
   tar -xzf documentacion.tar.gz
   ```
5. Asegúrate de que el servidor web tenga permisos de lectura en los archivos

### Opción 3: GitHub Pages o similar
Para servicios como GitHub Pages, Netlify, etc.:
1. Configura el directorio `documentacion/` como raíz del sitio
2. Sube los archivos HTML generados al repositorio
3. El servicio automáticamente servirá `index.html` como página principal

## Notas

- La documentación se genera usando Sphinx con el tema Read the Docs
- Los archivos fuente están en `docs/` en formato RST y Markdown
- Después de cambios en los archivos fuente, recompila siguiendo los pasos 2-3
- Los enlaces internos son relativos, por lo que funcionan en cualquier ubicación