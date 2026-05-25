# Sistema de Catálogos de Códigos

**Plugin de Gestión de Afiliados - Conversión de Códigos a Descripciones**

---

## 📝 ¿Qué es?

El sistema de catálogos convierte códigos numéricos almacenados en la base de datos a descripciones legibles para el usuario. En lugar de mostrar "01" o "08", el sistema muestra "Amputado en 1 Pierna" o "Bastón/Muleta + Prótesis".

---

## 🎯 Catálogos Implementados

### 1. Limitaciones (Discapacidades)

Códigos del 01 al 15 que describen el tipo de limitación física del afiliado:

| Código | Descripción |
|--------|-------------|
| 01 | Amputado en 1 Pierna |
| 02 | Amputado en 2 Piernas |
| 03 | Amputado en 1 Brazo |
| 04 | Amputado en 2 Brazos |
| 05 | Amputado en 1 Pierna y 1 Brazo |
| 06 | Amputado en 3 Extremidades |
| 07 | Amputado en 4 Extremidades |
| 08 | Parálisis en 1 Pierna |
| 09 | Parálisis en 2 Piernas |
| 10 | Parálisis en 1 Brazo |
| 11 | Parálisis en 2 Brazos |
| 12 | Parálisis en 1 Pierna y 1 Brazo |
| 13 | Parálisis en 3 Extremidades |
| 14 | Parálisis en 4 Extremidades |
| 15 | Otras limitaciones |

### 2. Nivel de Ambulación (Movilidad)

Códigos del 00 al 16 que describen cómo se desplaza el afiliado:

| Código | Descripción |
|--------|-------------|
| 00 | Encamado Permanente |
| 01 | Silla de Ruedas |
| 02 | Bastón o Muleta |
| 03 | Prótesis |
| 04 | Aparato Ortopédico |
| 05 | Silla de ruedas + Bastón/Muleta |
| 06 | Silla de ruedas + Prótesis |
| 07 | Silla de ruedas + Aparato Ortopédico |
| 08 | Bastón/Muleta + Prótesis |
| 09 | Bastón/Muleta + Aparato Ortopédico |
| 10 | Prótesis + Aparato Ortopédico |
| 11 | Silla de ruedas + Bastón/Muleta + Prótesis |
| 12 | Silla de ruedas + Bastón/Muleta + Aparato Ortopédico |
| 13 | Silla de ruedas + Prótesis + Aparato Ortopédico |
| 14 | Bastón/Muleta + Prótesis + Aparato Ortopédico |
| 15 | Silla de ruedas + Bastón/Muleta + Prótesis + Aparato Ortopédico |
| 16 | Camina sin ayuda |

### 3. Locación _(añadido v2.2)_

Indica si el afiliado reside en zona urbana o rural:

| Código | Descripción |
|--------|-------------|
| 1      | Urbana      |
| 2      | Rural       |

### 4. Jefe de Núcleo _(añadido v2.2)_

Indica si el afiliado es jefe del núcleo familiar. El campo almacena varios formatos posibles provenientes de Access:

| Valores en Access | Descripción mostrada |
|-------------------|----------------------|
| S, SI, Sí, 1, TRUE, YES, Y | Sí |
| N, NO, 0, FALSE, cualquier otro | No |

```
plugin/
└── utils/
    ├── __init__.py          ← Exporta funciones del módulo
    └── catalogos.py         ← Diccionarios y funciones de conversión
```

---

## 🔧 Cómo Funciona

### Archivo: `plugin/utils/catalogos.py`

**Diccionarios de mapeo:**
```python
LIMITACIONES = {
    '01': 'Amputado en 1 Pierna',
    '02': 'Amputado en 2 Piernas',
    # ...
}

AMBULACION = {
    '00': 'Encamado Permanente',
    '01': 'Silla de Ruedas',
    # ...
}

# Añadidos en v2.2
LOCACION = {
    '1': 'Urbana',
    '2': 'Rural',
}
```

**Funciones principales:**

1. **`get_limitacion_descripcion(codigo)`**
   - Entrada: código (ej: '01', '1', 1, None)
   - Salida: `"Amputado en 1 Pierna"` o `"No especificado"`
   
2. **`get_ambulacion_descripcion(codigo)`**
   - Entrada: código (ej: '08', '8', 8, None)
   - Salida: `"Bastón/Muleta + Prótesis"` o `"No especificado"`

3. **`get_locacion_descripcion(codigo)`** _(añadido v2.2)_
   - Entrada: '1', '2' o None
   - Salida: `"Urbana"`, `"Rural"` o `"No especificado"`

4. **`get_jefe_nucleo_descripcion(valor)`** _(añadido v2.2)_
   - Entrada: 'S', 'SI', 'Sí', '1', 'TRUE', 'YES', 'Y', 'N', '0', etc.
   - Salida: `"Sí"` o `"No"`

5. **`get_causa_descripcion(codigo)`**
   - Salida: descripción de la causa de la discapacidad o `"No especificado"`

6. **`get_ocupacion_descripcion(codigo)`**
   - Salida: descripción de la ocupación o `"No especificado"`

7. **`get_grado_escolar_descripcion(codigo)`**
   - Salida: descripción del grado escolar o `"No especificado"`

8. **`get_limitacion_codigo_y_descripcion(codigo)`**
   - Retorna tupla: `('01', 'Amputado en 1 Pierna')`
   
9. **`get_ambulacion_codigo_y_descripcion(codigo)`**
   - Retorna tupla: `('08', 'Bastón/Muleta + Prótesis')`

10. **`get_todas_limitaciones()`**
    - Retorna lista: `[('01', 'Amputado en 1 Pierna'), ...]`
    - Útil para llenar ComboBox o listas

11. **`get_todas_ambulaciones()`**
    - Retorna lista: `[('00', 'Encamado Permanente'), ...]`

---

## 💻 Uso en el Código

### En el Diálogo de Detalle de Afiliado

**Antes:**
```python
# Mostraba solo el código
self.add_field(layout, row, "Limitación:", self.afiliado.get('limitacion'))
self.add_field(layout, row, "Código:", self.afiliado.get('limitacion_cod'))
# Output: "Limitación: " | "Código: 01"
```

**Ahora:**
```python
from utils.catalogos import (
    get_limitacion_descripcion, get_locacion_descripcion,
    get_jefe_nucleo_descripcion
)

limitacion_cod = self.afiliado.get('limitacion_cod')
limitacion_desc = get_limitacion_descripcion(limitacion_cod)
# Output: "Limitación: Amputado en 1 Pierna"

locacion_desc = get_locacion_descripcion(self.afiliado.get('locacion'))
# Output: "Urbana" o "Rural"

jefe_desc = get_jefe_nucleo_descripcion(self.afiliado.get('jefe_nucleo'))
# Output: "Sí" o "No"
```

### En Formularios o ComboBox

```python
from utils.catalogos import get_todas_limitaciones, get_todas_ambulaciones

# Llenar un QComboBox con limitaciones
for codigo, descripcion in get_todas_limitaciones():
    self.limitacion_combo.addItem(f"{descripcion} ({codigo})", codigo)

# Obtener código seleccionado
codigo_seleccionado = self.limitacion_combo.currentData()
```

### En Tablas

```python
from utils.catalogos import get_ambulacion_descripcion

# Al llenar una tabla
for afiliado in afiliados:
    codigo = afiliado.get('ambulacion_cod')
    descripcion = get_ambulacion_descripcion(codigo)
    # Mostrar descripcion en la celda de la tabla
    item = QTableWidgetItem(descripcion)
    table.setItem(row, col, item)
```

---

## ✨ Características

### 1. Normalización Automática
Los códigos se normalizan automáticamente:
- `'1'` → `'01'`
- `1` → `'01'`
- `'01'` → `'01'`

### 2. Manejo de Valores Nulos
```python
get_limitacion_descripcion(None)      # → "No especificado"
get_limitacion_descripcion('')        # → "No especificado"
get_limitacion_descripcion('  ')     # → "No especificado"
```

### 3. Códigos No Definidos
```python
get_limitacion_descripcion('99')     # → "Código 99 (no definido)"
```

### 4. Formato Limpio (v2.2)
Las descripciones ya **no incluyen** el código entre paréntesis. Se muestra únicamente el texto descriptivo:
```
"Amputado en 1 Pierna"
"Silla de Ruedas"
"Urbana"
"Sí"
```

> **Nota:** Los campos de formulario y combos que necesiten mostrar el código deben concatenarlo manualmente: `f"{desc} ({cod})"`.

---

## 🆕 Agregar Nuevos Catálogos

### Paso 1: Definir el Diccionario

En `plugin/utils/catalogos.py`:

```python
# Nuevo catálogo de ejemplo: Estado Civil
ESTADO_CIVIL = {
    '01': 'Soltero/a',
    '02': 'Casado/a',
    '03': 'Divorciado/a',
    '04': 'Viudo/a',
    '05': 'Unión Libre',
}
```

### Paso 2: Crear Función de Conversión

```python
def get_estado_civil_descripcion(codigo):
    """
    Obtiene la descripción del estado civil según su código.
    
    Args:
        codigo: código de estado civil (str, int, o None)
    
    Returns:
        str: descripción legible
    """
    if codigo is None or str(codigo).strip() == '':
        return 'No especificado'
    
    codigo_str = str(codigo).strip()
    
    # Normalizar código
    if len(codigo_str) == 1 and codigo_str.isdigit():
        codigo_normalizado = '0' + codigo_str
    else:
        codigo_normalizado = codigo_str
    
    descripcion = ESTADO_CIVIL.get(codigo_normalizado) or ESTADO_CIVIL.get(codigo_str)
    
    if descripcion is None:
        return f"Código {codigo_str} (no definido)"
    
    return f"{descripcion} ({codigo_normalizado})"


def get_todos_estados_civiles():
    """Retorna lista de tuplas (codigo, descripcion)"""
    return [(k, v) for k, v in sorted(ESTADO_CIVIL.items()) if len(k) == 2]
```

### Paso 3: Exportar en `__init__.py`

```python
from .catalogos import (
    # ... existentes ...
    get_estado_civil_descripcion,
    get_todos_estados_civiles,
    ESTADO_CIVIL
)

__all__ = [
    # ... existentes ...
    'get_estado_civil_descripcion',
    'get_todos_estados_civiles',
    'ESTADO_CIVIL'
]
```

### Paso 4: Usar en la UI

```python
from utils.catalogos import get_estado_civil_descripcion

estado_civil_cod = self.afiliado.get('estado_civil')
estado_civil_desc = get_estado_civil_descripcion(estado_civil_cod)
self.add_field(layout, row, "Estado Civil:", estado_civil_desc)
```

---

## 🔄 Actualizar Catálogos Existentes

Para agregar o modificar descripciones en catálogos existentes:

1. **Editar el diccionario** en `catalogos.py`:
   ```python
   LIMITACIONES = {
       # ... existentes ...
       '16': 'Nueva limitación',  # Agregar
       '02': 'Amputado en ambas piernas',  # Modificar
   }
   ```

2. **Reiniciar QGIS** o recargar el plugin

3. **Verificar** en el diálogo de detalle de afiliados

---

## 🧪 Pruebas

### Probar una Conversión

```python
# En QGIS Python Console
from plugin.utils.catalogos import get_limitacion_descripcion, get_ambulacion_descripcion

# Probar diferentes formatos
print(get_limitacion_descripcion('01'))   # Código con cero
print(get_limitacion_descripcion('1'))    # Código sin cero
print(get_limitacion_descripcion(1))      # Código numérico
print(get_limitacion_descripcion(None))   # Valor nulo

# Probar ambulación
print(get_ambulacion_descripcion('08'))
print(get_ambulacion_descripcion('16'))
```

### Listar Todos los Códigos

```python
from plugin.utils.catalogos import get_todas_limitaciones, get_todas_ambulaciones

# Limitaciones
for codigo, descripcion in get_todas_limitaciones():
    print(f"{codigo}: {descripcion}")

# Ambulación
for codigo, descripcion in get_todas_ambulaciones():
    print(f"{codigo}: {descripcion}")
```

---

## 🎨 Visualización

### Antes de la Implementación:
```
Limitación: [vacío]
Código: 01

Nivel Ambulación: [vacío]
Código: 08
```

### Después de la Implementación:
```
Limitación: Amputado en 1 Pierna (01)

Nivel Ambulación: Bastón/Muleta + Prótesis (08)
```

---

## 📊 Ventajas del Sistema

1. ✅ **Legibilidad**: Los usuarios ven descripciones claras
2. ✅ **Mantenibilidad**: Fácil actualizar o agregar códigos
3. ✅ **Centralizado**: Todas las descripciones en un solo lugar
4. ✅ **Reutilizable**: Funciones disponibles en todo el plugin
5. ✅ **Robusto**: Maneja valores nulos y códigos inválidos
6. ✅ **Normalización**: Acepta múltiples formatos de entrada
7. ✅ **Extensible**: Fácil agregar nuevos catálogos

---

## 🔍 Dónde Se Usa

| Ubicación | Uso |
|-----------|-----|
| `ui/detalle_afiliado_dialog.py` | Muestra descripciones en el diálogo de detalles |
| (Futuro) Formularios de edición | ComboBox con opciones seleccionables |
| (Futuro) Tablas | Columnas con descripciones |
| (Futuro) Reportes | Exportación con descripciones legibles |

---

## 📝 Notas Importantes

1. **No modificar la base de datos**: Los códigos se mantienen en la BD, solo se convierten en la UI
2. **Actualizar al agregar códigos**: Si se agregan nuevos códigos en Access, agrégalos también al diccionario
3. **Consistencia**: Mantén el formato `"Descripción (XX)"` en todas las funciones
4. **Documentación**: Actualiza este documento al agregar nuevos catálogos

---

## 🐛 Solución de Problemas

### Error: `ModuleNotFoundError: No module named 'utils'`

**Solución:**
```python
# Agregar path del plugin en imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.catalogos import ...
```

### No se muestran las descripciones

**Verificar:**
1. ¿El código existe en el diccionario?
2. ¿El formato del código es correcto? (ej: '01' vs '1')
3. ¿El campo de la BD tiene valor?
4. ¿Se reinició QGIS después de los cambios?

### Códigos con formato incorrecto en la BD

**Si la BD tiene:**
- `'1'` en lugar de `'01'`: ✅ La función normaliza automáticamente
- `1` (int) en lugar de `'01'`: ✅ La función convierte a string
- `None` o `''`: ✅ Muestra "No especificado"

---

**Última actualización**: Mayo 2026  
**Versión**: 1.0
