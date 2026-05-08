# Guía de Solución de Problemas (Troubleshooting)

Plugin de Gestión de Afiliados para QGIS

---

## 📑 Índice de Problemas

- [Problemas con Microsoft Access](#problemas-con-microsoft-access)
  - [Error: No se encontró el driver ODBC](#1-error-no-se-encontró-el-driver-odbc)
  - [Error de codificación (byte 0x81)](#2-error-de-codificación-byte-0x81)
  - [Base de datos con contraseña](#3-base-de-datos-con-contraseña)
  - [Conflicto 32-bit vs 64-bit](#4-conflicto-32-bit-vs-64-bit)
- [Problemas con PostgreSQL](#problemas-con-postgresql)
- [Problemas de Instalación](#problemas-de-instalación)
- [Problemas de Rendimiento](#problemas-de-rendimiento)
- [Otros Problemas](#otros-problemas)

---

## Problemas con Microsoft Access

### 1. Error: No se encontró el driver ODBC

#### 🔴 Síntomas
```
Error al conectar a Access: [Microsoft][ODBC Driver Manager] Data source name not found and no default driver specified
```
o
```
❌ NO SE ENCONTRÓ EL DRIVER ODBC DE MICROSOFT ACCESS
```

#### 🔍 Causa
El sistema no tiene instalado el controlador ODBC de Microsoft Access necesario para que `pyodbc` se conecte a bases de datos `.mdb` o `.accdb`.

#### ✅ Solución

**Paso 1: Verificar si el driver está instalado**

1. Presiona `Win + R`
2. Escribe `odbcad32` y presiona Enter
3. Ve a la pestaña **"Controladores"**
4. Busca **"Microsoft Access Driver (*.mdb, *.accdb)"**

Si NO aparece en la lista, continúa con el Paso 2.

**Paso 2: Descargar e instalar el driver**

1. Ve a: https://www.microsoft.com/en-us/download/details.aspx?id=54920
2. Descarga **Microsoft Access Database Engine 2016 Redistributable**
3. Elige la versión:
   - **64-bit** (`AccessDatabaseEngine_X64.exe`) - Si tu Python/QGIS es de 64 bits (recomendado)
   - **32-bit** (`AccessDatabaseEngine.exe`) - Si tu Python/QGIS es de 32 bits

**Paso 3: Instalar**

- **Instalación Normal**: Doble clic en el archivo descargado
- **Si da error de compatibilidad**: Abre CMD como Administrador y ejecuta:
  ```cmd
  cd C:\Users\TuUsuario\Downloads
  AccessDatabaseEngine_X64.exe /quiet
  ```

**Paso 4: Verificar instalación**

1. Vuelve a abrir `odbcad32` (Win + R → odbcad32)
2. En "Controladores" debería aparecer ahora: **"Microsoft Access Driver (*.mdb, *.accdb)"**

#### 📝 Notas Importantes

- ✅ La instalación es **GRATUITA** y no requiere licencia de Microsoft Access
- ⚠️ Si tienes Microsoft Office instalado, instala la versión (32 o 64 bits) que coincida con tu Office
- ⚠️ En entornos empresariales, puede requerir permisos de administrador

---

### 2. Error de codificación (byte 0x81)

#### 🔴 Síntomas
```
Error inesperado al leer: 'charmap' codec can't decode byte 0x81 in position X: character maps to <undefined>
```
o
```
UnicodeDecodeError: 'cp1252' codec can't decode byte 0x81
```

#### 🔍 Causa
La base de datos Access contiene caracteres especiales (tildes, ñ, símbolos) que no pueden ser decodificados con la codificación `cp1252` (Windows-1252). El byte `0x81` y otros no están definidos en ese mapa de caracteres.

#### ✅ Solución

La **versión actualizada del plugin** ya incluye la corrección automática. Si aún tienes problemas:

**Solución Manual** (si usas versión antigua del código):

Edita el archivo `access_importer.py` y modifica el método `connect_to_access`:

```python
# REEMPLAZAR ESTO:
self.connection.setdecoding(pyodbc.SQL_CHAR, encoding='cp1252')
self.connection.setdecoding(pyodbc.SQL_WCHAR, encoding='cp1252')
self.connection.setencoding(encoding='cp1252')

# POR ESTO:
self.connection.setdecoding(pyodbc.SQL_CHAR, encoding='latin-1')
self.connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-16-le')
self.connection.setencoding(encoding='utf-8')
```

**¿Por qué funciona?**

| Codificación | Problema |
|--------------|----------|
| `cp1252` | No define bytes: 0x81, 0x8D, 0x8F, 0x90, 0x9D → crashea |
| `latin-1` | Define todos los 256 bytes (0x00-0xFF) → **nunca falla** |

#### 📝 Actualizar Plugin

Si usas el plugin oficial:
1. Descarga la última versión
2. Reemplaza la carpeta del plugin en QGIS
3. Reinicia QGIS

---

### 3. Base de datos con contraseña

#### 🔴 Síntomas
```
No se pudo conectar: Cannot open database ''. It may not be a database that your application recognizes, or the file may be corrupt.
```
o el plugin se conecta pero no muestra datos.

#### 🔍 Causa
La base de datos Access está protegida con contraseña de usuario o contraseña de base de datos.

#### ✅ Solución

**Opción 1: Usar la funcionalidad del plugin**

1. Al importar, el plugin debería detectar automáticamente que requiere contraseña
2. Ingresa la contraseña cuando se solicite

**Opción 2: Código manual**

Si usas el método directamente:
```python
from modules.access_importer import AccessImporter

importer = AccessImporter("ruta/a/base.accdb")
success, message = importer.connect_to_access(password="mi_contraseña")
```

**Tipos de contraseña en Access:**

| Tipo | Método de Conexión | Cuándo usar |
|------|-------------------|-------------|
| Contraseña de usuario | `PWD=contraseña` | Más común, establece contraseña al abrir |
| Usuario + Contraseña | `UID=Admin;PWD=contraseña` | Cuando hay usuario configurado |
| Database Password | `Database Password=contraseña` | Bases con cifrado completo |

El plugin prueba automáticamente los 3 métodos en orden.

---

### 4. Conflicto 32-bit vs 64-bit

#### 🔴 Síntomas
```
The specified DSN contains an architecture mismatch between the Driver and Application
```
o el driver no aparece en `odbcad32` pero sí está instalado.

#### 🔍 Causa
Tienes Python/QGIS de una arquitectura (32 o 64 bits) y el driver de Access de otra. Windows tiene dos versiones de `odbcad32.exe` (una para cada arquitectura).

#### ✅ Solución

**Paso 1: Verificar arquitectura de Python**

Abre la consola de Python en QGIS y ejecuta:
```python
import sys
print(sys.maxsize > 2**32)
# True = 64-bit, False = 32-bit
```

**Paso 2: Verificar drivers instalados**

- **Para ver drivers de 32-bit**: 
  - `C:\Windows\SysWOW64\odbcad32.exe` (en 64-bit Windows)
  - `C:\Windows\System32\odbcad32.exe` (en 32-bit Windows)
- **Para ver drivers de 64-bit**: 
  - `C:\Windows\System32\odbcad32.exe` (en 64-bit Windows)

**Paso 3: Instalar la versión correcta**

Descarga e instala el driver que coincida con tu Python:
- Python 64-bit → `AccessDatabaseEngine_X64.exe`
- Python 32-bit → `AccessDatabaseEngine.exe`

**Paso 4 (Opcional): Instalar ambas versiones**

Si necesitas ambas (por ejemplo, Office 32-bit y Python 64-bit):

```cmd
# Instalar primera versión (ejemplo: 32-bit)
AccessDatabaseEngine.exe /quiet

# Instalar segunda versión (ejemplo: 64-bit)
AccessDatabaseEngine_X64.exe /quiet
```

El parámetro `/quiet` fuerza la instalación ignorando conflictos.

---

## Problemas con PostgreSQL

### 1. Error: No se puede conectar a la base de datos

#### 🔴 Síntomas
```
Error en sincronización: could not connect to server: Connection refused
```

#### ✅ Soluciones

1. **Verificar que PostgreSQL esté corriendo**:
   ```cmd
   # Windows
   sc query postgresql-x64-14
   
   # Linux
   sudo systemctl status postgresql
   ```

2. **Verificar configuración de red** (`postgresql.conf`):
   ```
   listen_addresses = '*'  # o la IP específica
   port = 5432
   ```

3. **Verificar firewall** (`pg_hba.conf`):
   ```
   # Permitir conexiones locales
   host    all             all             127.0.0.1/32            md5
   host    all             all             ::1/128                 md5
   
   # Permitir conexiones de red local
   host    all             all             192.168.1.0/24          md5
   ```

4. **Reiniciar PostgreSQL** después de cambios:
   ```cmd
   # Windows
   net stop postgresql-x64-14
   net start postgresql-x64-14
   
   # Linux
   sudo systemctl restart postgresql
   ```

### 2. Error: PostGIS no está instalado

#### 🔴 Síntomas
```
ERROR: function postgis_version() does not exist
```

#### ✅ Solución
```sql
-- Conectarse a la base de datos como superusuario
psql -U postgres -d nombre_bd

-- Instalar extensión PostGIS
CREATE EXTENSION postgis;

-- Verificar instalación
SELECT PostGIS_version();
```

### 3. Error: Permisos insuficientes

#### 🔴 Síntomas
```
ERROR: permission denied for table afiliados
```

#### ✅ Solución
```sql
-- Como superusuario, otorgar permisos
GRANT CONNECT ON DATABASE nombre_bd TO usuario_plugin;
GRANT USAGE ON SCHEMA public TO usuario_plugin;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO usuario_plugin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO usuario_plugin;

-- Para tablas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO usuario_plugin;
```

---

## Problemas de Instalación

### 1. El plugin no aparece en QGIS

#### ✅ Solución

1. **Verificar ubicación del plugin**:
   - Windows: `C:\Users\TuUsuario\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`

2. **Verificar estructura de carpetas**:
   ```
   plugins/
   └── gestion_afiliados/
       ├── __init__.py
       ├── main_plugin.py
       ├── metadata.txt
       └── ...
   ```

3. **Activar el plugin**:
   - QGIS → Complementos → Administrar e instalar complementos
   - Pestaña "Instalados"
   - Buscar "Gestión de Afiliados"
   - Marcar la casilla

### 2. Error al activar el plugin

#### 🔴 Síntomas
```
Couldn't load plugin 'gestion_afiliados' due to an error when calling its classFactory() method
```

#### ✅ Soluciones

1. **Verificar logs de QGIS**:
   - Ver → Paneles → Mensajes de log
   - Buscar errores específicos

2. **Instalar dependencias Python**:
   ```bash
   # Desde OSGeo4W Shell (Windows) o terminal (Linux/Mac)
   python3 -m pip install psycopg2-binary pyodbc PyQt5
   ```

3. **Verificar metadata.txt**:
   - Debe existir y tener formato correcto
   - Verificar campos: `name`, `qgisMinimumVersion`, `version`

---

## Problemas de Rendimiento

### 1. La importación es muy lenta

#### 🔴 Síntomas
La importación de 10,000+ registros toma más de 10 minutos.

#### ✅ Soluciones

1. **Aumentar batch size** (si aplicable en futuras versiones)
2. **Optimizar PostgreSQL**:
   ```sql
   -- Aumentar memoria de trabajo
   SET work_mem = '256MB';
   
   -- Desactivar índices temporalmente
   ALTER TABLE afiliados DISABLE TRIGGER ALL;
   -- Importar datos...
   ALTER TABLE afiliados ENABLE TRIGGER ALL;
   ```

3. **Usar una red local** en lugar de conexión remota
4. **Cerrar otras aplicaciones** que usen mucho disco/red

### 2. QGIS se congela durante la importación

#### ✅ Solución

En futuras versiones esto se manejará con procesamiento en segundo plano. Actualmente:
- Sea paciente, el proceso está corriendo
- No cierre QGIS durante la importación
- Verifique la consola de Python para ver progreso

---

## Otros Problemas

### 1. La geocodificación no funciona

#### ✅ Soluciones

1. **Verificar conexión a Internet**
2. **Verificar límites de API** (Nominatim tiene límite de 1 req/seg)
3. **Usar API key de Google Maps** si disponible

### 2. No se muestran los mapas base

#### ✅ Soluciones

1. **Habilitar conexiones de red en QGIS**:
   - Configuración → Opciones → Red
   - Desmarcar "Usar proxy" si no lo necesitas

2. **Verificar firewall** que no bloquee QGIS

---

## 🔧 Herramientas de Diagnóstico

### Script de Verificación
Ejecuta el script incluido para diagnóstico automático:
```cmd
python verificar_dependencias.py
```

Genera un reporte completo: `verificacion_dependencias.txt`

### Habilitar Logs Detallados

En Python Console de QGIS:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📞 Obtener Ayuda

Si los problemas persisten:

1. **Ejecuta el script de verificación** y guarda el reporte
2. **Consulta los logs**:
   - QGIS: Ver → Paneles → Mensajes de log
   - Plugin: `[carpeta_plugin]/logs/` (si existe)
3. **Recopila información**:
   - Versión de QGIS
   - Sistema operativo y versión
   - Mensaje de error completo
   - Archivo de reporte de verificación
4. **Contacta a soporte técnico** con toda la información recopilada

---

## 📚 Referencias Adicionales

- [REQUISITOS_SISTEMA.md](REQUISITOS_SISTEMA.md) - Requisitos completos del sistema
- [README.md](../README.md) - Documentación general del plugin
- [Microsoft Access Database Engine](https://www.microsoft.com/en-us/download/details.aspx?id=54920) - Descarga oficial del driver

---

**Última actualización**: Mayo 2026  
**Versión**: 1.0
