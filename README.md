# Plugin de Gestión de Afiliados - QGIS

Plugin de QGIS para la gestión geoespacial de afiliados con importación desde Microsoft Access.

## ✨ Características Principales

- 📥 Importación automática desde bases de datos Microsoft Access (.mdb/.accdb)
- 🗺️ Gestión geoespacial de afiliados en PostgreSQL + PostGIS
- 📍 Geocodificación de direcciones
- 🔍 Búsqueda y filtrado avanzado
- 📊 Centros de interés y análisis espacial
- 🔄 Sincronización inteligente de datos

## 🆕 Mejoras de Compatibilidad v2.0

✅ **Detección automática de drivers ODBC** - Ya no crashea si falta el driver  
✅ **Soporte para bases con contraseña** - Funciona con Access protegido  
✅ **Corrección de errores de codificación** - Maneja correctamente tildes, ñ, y caracteres especiales  
✅ **Mensajes de error claros** - Incluye instrucciones de solución  
✅ **Script de verificación de dependencias** - Diagnóstico automático  
✅ **Documentación completa** - Guías de instalación, troubleshooting, y requisitos

Ver [MEJORAS_IMPLEMENTADAS.md](docs/MEJORAS_IMPLEMENTADAS.md) para detalles técnicos completos.

## 🚀 Inicio Rápido

### 1. Verificar Requisitos

**Requisitos mínimos:**
- QGIS 3.16+ (recomendado: 3.28+)
- PostgreSQL 10+ con PostGIS
- Microsoft Access Database Engine (para importar desde Access)
- Python 3.7+

**Ejecutar verificación automática:**
```bash
python verificar_dependencias.py
```

Ver [REQUISITOS_SISTEMA.md](docs/REQUISITOS_SISTEMA.md) para detalles completos.

### 2. Instalación

**Paso a paso completo:** Ver [GUIA_INSTALACION.md](docs/GUIA_INSTALACION.md)

**Instalación rápida:**
1. Instalar [Microsoft Access Database Engine 2016](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
2. Copiar carpeta del plugin a: `C:\Users\[Usuario]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
3. Activar en QGIS: Complementos → Administrar e instalar complementos
4. Configurar conexión a PostgreSQL en el plugin

### 3. Uso Básico

```python
# Importación automática desde Access (detección de tabla automática)
from modules.access_importer import AccessImporter

importer = AccessImporter("ruta/base_datos.accdb")
success, result = importer.auto_detect_and_import(
    password="contraseña_opcional"  # Solo si la BD está protegida
)

if success:
    print(f"✅ Importados: {result['nuevos']} nuevos, {result['actualizados']} actualizados")
```

## 📚 Documentación

| Documento | Descripción | Cuándo Usar |
|-----------|-------------|-------------|
| [GUIA_INSTALACION.md](docs/GUIA_INSTALACION.md) | Instalación paso a paso | Al instalar el plugin |
| [REQUISITOS_SISTEMA.md](docs/REQUISITOS_SISTEMA.md) | Requisitos técnicos detallados | Antes de instalar |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Solución de problemas comunes | Cuando hay errores |
| [IMPORTACION_CON_PASSWORD.md](docs/IMPORTACION_CON_PASSWORD.md) | 🆕 Guía de importación con contraseña | Para BD protegidas |
| [MEJORAS_IMPLEMENTADAS.md](docs/MEJORAS_IMPLEMENTADAS.md) | Detalles técnicos de mejoras | Para desarrolladores |

## 🔐 Nuevo: Importación desde Access con Contraseña

Ya **NO necesitas exportar tu base de datos sin contraseña**. El plugin ahora:

✅ Detecta automáticamente si la BD tiene contraseña  
✅ Te pide la contraseña cuando sea necesario  
✅ Prueba 3 métodos de conexión automáticamente  
✅ Mantiene tu BD protegida y segura  

**Uso:**
1. Selecciona tu archivo Access (.mdb/.accdb)
2. Si tiene contraseña, aparecerá un diálogo pidiéndola
3. Ingresa la contraseña
4. ¡Listo! Importación automática

Ver [IMPORTACION_CON_PASSWORD.md](docs/IMPORTACION_CON_PASSWORD.md) para más detalles.

## 🔧 Tecnologías

- **Frontend**: PyQt5
- **Backend**: Python 3.7+, PyQGIS
- **Base de Datos**: PostgreSQL 10+ con PostGIS
- **Conectividad**: pyodbc (Access), psycopg2 (PostgreSQL)
- **GIS**: QGIS 3.16+

## 📁 Estructura del Proyecto

```
Plugin/
├── plugin/
│   ├── __init__.py
│   ├── main_plugin.py
│   ├── metadata.txt
│   ├── modules/
│   │   ├── access_importer.py  ← Mejorado v2.0
│   │   ├── db_connection.py
│   │   ├── map_tools.py
│   │   └── ...
│   ├── ui/
│   │   ├── main_dialog.py
│   │   ├── afiliado_form.py
│   │   └── ...
│   └── resources/
├── docs/
│   ├── GUIA_INSTALACION.md      ← Nuevo
│   ├── REQUISITOS_SISTEMA.md    ← Nuevo
│   ├── TROUBLESHOOTING.md       ← Nuevo
│   └── MEJORAS_IMPLEMENTADAS.md ← Nuevo
├── database/
│   └── schema.sql
├── tests/
├── verificar_dependencias.py    ← Nuevo
├── requirements.txt
└── README.md
```

## 🐛 Solución de Problemas

### Error: Driver ODBC no encontrado

```
❌ NO SE ENCONTRÓ EL DRIVER ODBC DE MICROSOFT ACCESS
```

**Solución:**
1. Descargar: [Microsoft Access Database Engine 2016](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
2. Instalar (elegir 64-bit si tu QGIS es 64-bit)
3. Si da error: `AccessDatabaseEngine_X64.exe /quiet`

Ver [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md#1-error-no-se-encontró-el-driver-odbc) para más detalles.

### Error: Codificación de caracteres (byte 0x81)

Este error está **RESUELTO** en la versión 2.0. Si aún lo tienes, actualiza el plugin.

Ver [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md#2-error-de-codificación-byte-0x81) para detalles.

### Más Problemas

Consulta la [guía completa de troubleshooting](docs/TROUBLESHOOTING.md) con soluciones a 15+ problemas comunes.

## ✅ Verificación de Instalación

### Verificar dependencias del sistema
```bash
# Ejecutar script de verificación
python verificar_dependencias.py

# Resultado esperado:
✓ Python 3.7+
✓ PyQt5
✓ psycopg2
✓ pyodbc
✓ Driver ODBC Access
✓ Conexión PostgreSQL
...
✓ TODOS LOS REQUISITOS CRÍTICOS ESTÁN SATISFECHOS
```

### Probar conexión a base de datos Access
```bash
# Probar sin contraseña
python probar_conexion_access.py ruta/base_datos.mdb

# Probar con contraseña
python probar_conexion_access.py ruta/base_datos.accdb mi_contraseña

# Resultado esperado:
✅ CONEXIÓN EXITOSA
✅ Lista de tablas disponibles (incluyendo ACLIFIM)
```

## 🤝 Contribución

Para desarrolladores que quieran contribuir:

1. Lee [MEJORAS_IMPLEMENTADAS.md](docs/MEJORAS_IMPLEMENTADAS.md) para entender los cambios
2. Revisa el código en `plugin/modules/access_importer.py`
3. **No revertir** las mejoras de codificación (`latin-1` en lugar de `cp1252`)
4. Mantener compatibilidad con contraseñas de Access
5. Actualizar tests según sea necesario

## 📊 Changelog

### v2.0 (Mayo 2026) - Mejoras de Compatibilidad
- ✅ Detección automática de drivers ODBC
- ✅ Soporte para bases de datos Access con contraseña
- ✅ Corrección de errores de codificación (byte 0x81)
- ✅ Método `auto_detect_and_import()` para importación simplificada
- ✅ Mensajes de error mejorados con instrucciones
- ✅ Script de verificación de dependencias
- ✅ Documentación completa (4 documentos nuevos)

### v1.0 (Anterior)
- Funcionalidad básica de importación desde Access
- Gestión de afiliados en PostgreSQL
- Geocodificación básica

## 📞 Soporte

¿Tienes problemas? Sigue este orden:

1. ✅ Ejecuta `python verificar_dependencias.py`
2. ✅ Consulta [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. ✅ Revisa [GUIA_INSTALACION.md](docs/GUIA_INSTALACION.md)
4. ✅ Contacta a soporte con el reporte generado

## 📄 Licencia

[Especificar licencia]

## 👥 Autores

- [Tu equipo/nombre]

---

**Estado**: ✅ Producción (v2.0)  
**Última actualización**: Mayo 2026
