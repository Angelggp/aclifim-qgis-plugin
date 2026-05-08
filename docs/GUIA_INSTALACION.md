# Guía de Instalación y Configuración

**Plugin de Gestión de Afiliados para QGIS**

---

## 📋 Antes de Empezar

Esta guía le ayudará a instalar y configurar el plugin paso a paso. El proceso completo toma aproximadamente **30-45 minutos**.

### ¿Qué necesito tener instalado?
- ✅ Windows 7, 8, 10 u 11 (recomendado: Windows 10/11)
- ✅ QGIS 3.16 o superior (recomendado: QGIS 3.28+)
- ✅ PostgreSQL 10+ con PostGIS (recomendado: PostgreSQL 14+)
- ✅ Conexión a Internet (para descargar componentes)

### ¿Qué voy a instalar?
1. Microsoft Access Database Engine (para leer archivos .mdb/.accdb)
2. Plugin de Gestión de Afiliados para QGIS
3. Configuración de conexión a la base de datos

---

## 📦 PARTE 1: Instalar Componentes Requeridos

### Paso 1.1: Verificar QGIS

1. Abra **QGIS**
2. Vaya a **Ayuda → Acerca de**
3. Verifique que la versión sea **3.16 o superior**

Si no tiene QGIS instalado:
- Descargue desde: https://qgis.org/es/site/forusers/download.html
- Instale la versión **QGIS Standalone Installer** (recomendado: versión LTR)

### Paso 1.2: Verificar PostgreSQL

1. Abra el **administrador de servicios de Windows**:
   - Presione `Win + R`
   - Escriba `services.msc` y presione Enter
2. Busque un servicio llamado **"postgresql-x64-XX"** (donde XX es la versión)
3. Verifique que esté en estado **"En ejecución"**

Si no tiene PostgreSQL instalado:
- Descargue desde: https://www.postgresql.org/download/windows/
- Durante la instalación, **anote la contraseña del usuario "postgres"**
- Instale también **PostGIS** cuando se le solicite (o use Stack Builder después)

### Paso 1.3: Instalar Driver de Microsoft Access

⚠️ **IMPORTANTE**: Este paso es OBLIGATORIO para importar datos desde Access.

**A. Determinar la arquitectura de su Python/QGIS**

1. Abra QGIS
2. Vaya a **Complementos → Consola de Python**
3. Escriba y ejecute:
   ```python
   import sys
   print("64-bit" if sys.maxsize > 2**32 else "32-bit")
   ```
4. **Anote si es 32-bit o 64-bit**

**B. Descargar el driver**

1. Visite: https://www.microsoft.com/en-us/download/details.aspx?id=54920
2. Haga clic en **"Descargar"**
3. Seleccione el archivo según su arquitectura:
   - ✅ **64-bit**: `AccessDatabaseEngine_X64.exe` ← (Más común)
   - **32-bit**: `AccessDatabaseEngine.exe`
4. Descargue el archivo

**C. Instalar el driver**

**Método 1: Instalación Normal** (pruebe primero este)

1. Doble clic en el archivo descargado
2. Siga el asistente de instalación
3. Haga clic en "Acepto" → "Instalar"

**Método 2: Si da error de compatibilidad**

Si aparece un error como _"Ya tiene instalados componentes de Office de otra versión"_:

1. Presione `Win + X` → Seleccione **"Windows PowerShell (Administrador)"** o **"Símbolo del sistema (Administrador)"**
2. Navegue a la carpeta de Descargas:
   ```cmd
   cd C:\Users\SuNombre\Downloads
   ```
3. Ejecute con el parámetro `/quiet`:
   ```cmd
   AccessDatabaseEngine_X64.exe /quiet
   ```
4. Espere 1-2 minutos (no habrá ventanas, se instala en silencio)

**D. Verificar la instalación**

1. Presione `Win + R`
2. Escriba `odbcad32` y presione Enter
3. Vaya a la pestaña **"Controladores"**
4. **Busque**: "Microsoft Access Driver (*.mdb, *.accdb)"
5. ✅ Si aparece → **¡Instalación exitosa!**
6. ❌ Si NO aparece → Repita el Método 2 o consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🔌 PARTE 2: Instalar el Plugin

### Paso 2.1: Obtener el plugin

**Opción A: Desde archivo ZIP**

1. Localice el archivo `gestion_afiliados.zip` que le proporcionamos
2. **NO lo descomprima todavía**

**Opción B: Desde repositorio de QGIS** (si está publicado)

1. En QGIS, vaya a **Complementos → Administrar e instalar complementos**
2. Busque "Gestión de Afiliados"
3. Haga clic en **"Instalar complemento"**
4. **Salte al Paso 2.3**

### Paso 2.2: Instalar desde ZIP (si usa Opción A)

**Método 1: Instalación Manual**

1. Descomprima `gestion_afiliados.zip`
2. Copie la carpeta `gestion_afiliados` completa
3. Péguala en la carpeta de plugins de QGIS:
   ```
   C:\Users\SuNombre\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
   ```
   💡 **Tip**: Puede pegar esta ruta directamente en el Explorador de Archivos

**Método 2: Desde QGIS**

1. En QGIS, vaya a **Complementos → Administrar e instalar complementos**
2. Vaya a la pestaña **"Instalar desde ZIP"**
3. Haga clic en **"..."** y seleccione el archivo `gestion_afiliados.zip`
4. Haga clic en **"Instalar complemento"**
5. Espere el mensaje "Complemento instalado correctamente"

### Paso 2.3: Activar el plugin

1. Vaya a **Complementos → Administrar e instalar complementos**
2. En la pestaña **"Instalados"**
3. Busque **"Gestión de Afiliados"**
4. **Marque la casilla** junto al nombre
5. Si aparece algún error, consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md#problemas-de-instalación)

✅ **Verificación**: Debería aparecer un nuevo ícono ![🗺️] en la barra de herramientas de QGIS.

---

## ⚙️ PARTE 3: Configurar Base de Datos

### Paso 3.1: Preparar PostgreSQL

**A. Crear la base de datos** (si no existe)

1. Abra **pgAdmin** (instalado con PostgreSQL)
2. Conéctese al servidor (usuario: `postgres`, contraseña: la que eligió al instalar)
3. Clic derecho en **"Databases"** → **"Create" → "Database..."**
4. Nombre: `gestion_afiliados` (o el nombre que prefiera)
5. Haga clic en **"Save"**

**B. Habilitar PostGIS**

1. En pgAdmin, seleccione su base de datos recién creada
2. Haga clic en **"Query Tool"** (ícono de documento con rayo)
3. Escriba:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```
4. Presione **F5** o haga clic en el botón ▶️ (Ejecutar)
5. Verifique que diga "Query returned successfully"

**C. Crear un usuario para el plugin** (opcional pero recomendado)

```sql
-- Crear usuario
CREATE USER usuario_plugin WITH PASSWORD 'contraseña_segura';

-- Otorgar permisos
GRANT CONNECT ON DATABASE gestion_afiliados TO usuario_plugin;
GRANT USAGE ON SCHEMA public TO usuario_plugin;
GRANT CREATE ON SCHEMA public TO usuario_plugin;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO usuario_plugin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO usuario_plugin;

-- Para tablas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO usuario_plugin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
GRANT USAGE, SELECT ON SEQUENCES TO usuario_plugin;
```

### Paso 3.2: Configurar el plugin

**A. Abrir configuración**

1. En QGIS, haga clic en el ícono del plugin o vaya a **Complementos → Gestión de Afiliados**
2. En el diálogo principal, haga clic en **"Configuración de BD"** o **"⚙️"**

**B. Ingresar datos de conexión**

Llene los campos:

| Campo | Valor de Ejemplo | Descripción |
|-------|------------------|-------------|
| **Host** | `localhost` | Dirección del servidor PostgreSQL |
| **Puerto** | `5432` | Puerto de PostgreSQL (predeterminado) |
| **Base de Datos** | `gestion_afiliados` | Nombre de la BD creada en Paso 3.1 |
| **Usuario** | `usuario_plugin` | Usuario con permisos |
| **Contraseña** | `contraseña_segura` | Contraseña del usuario |

💡 **Notas**:
- Si PostgreSQL está en **otro servidor**, use la IP en lugar de `localhost` (ej: `192.168.1.100`)
- Si cambió el puerto al instalar PostgreSQL, use ese puerto

**C. Probar conexión**

1. Haga clic en el botón **"Probar Conexión"**
2. Debería aparecer: ✅ **"Conexión exitosa a PostgreSQL"**
3. Si aparece un error, verifique:
   - Usuario y contraseña correctos
   - PostgreSQL está corriendo (Paso 1.2)
   - Firewall no bloquea el puerto 5432
   - Consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md#problemas-con-postgresql)

**D. Guardar configuración**

1. Haga clic en **"Guardar"** o **"Aceptar"**
2. La configuración se guarda en: `[carpeta_plugin]/db_config.json`

---

## 🧪 PARTE 4: Verificar Instalación

### Paso 4.1: Ejecutar script de verificación

1. Abra el Explorador de Archivos
2. Navegue a la carpeta del plugin:
   ```
   C:\Users\SuNombre\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\gestion_afiliados\
   ```
3. Haga **Shift + Clic derecho** en un área vacía → **"Abrir ventana de PowerShell aquí"** o **"Abrir en Terminal"**
4. Ejecute:
   ```cmd
   python verificar_dependencias.py
   ```
5. Revise el reporte generado

### Paso 4.2: Interpretar resultados

El script mostrará:

- ✓ **Verde**: Componente instalado correctamente
- ⚠ **Amarillo**: Advertencia (funcionalidad opcional afectada)
- ✗ **Rojo**: Error crítico (debe resolverse)

**Si hay errores rojos**:
1. Anote los componentes que fallan
2. Consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Corrija los problemas
4. Vuelva a ejecutar el script de verificación

**Si solo hay advertencias amarillas**:
- El plugin funcionará, pero algunas funciones opcionales pueden no estar disponibles
- Puede continuar con la instalación

**Si todo es verde**:
- ✅ **¡Instalación completa y exitosa!**
- Puede empezar a usar el plugin

---

## 🚀 PARTE 5: Primer Uso

### Paso 5.1: Importar datos de prueba (opcional)

1. Prepare un archivo Access (.mdb o .accdb) con datos de prueba
2. En el plugin, haga clic en **"Importar desde Access"**
3. Seleccione el archivo
4. Si la base de datos tiene contraseña, ingrésela cuando se solicite
5. Espere a que complete la importación
6. Revise el resumen de resultados

### Paso 5.2: Explorar funcionalidades

El plugin incluye:

- 📥 **Importar desde Access**: Migrar datos de bases Access
- 🗺️ **Gestión de afiliados**: Ver, editar, ubicar afiliados
- 📍 **Geocodificación**: Ubicar afiliados en el mapa por dirección
- 📊 **Centros de interés**: Marcar lugares importantes
- 📈 **Reportes y estadísticas**: Generar informes

### Paso 5.3: Consultar documentación

Para aprender más sobre cada funcionalidad:
- [README.md](../README.md) - Guía completa de usuario
- [MANUAL_USUARIO.md](MANUAL_USUARIO.md) - Manual detallado (si existe)

---

## ❓ Preguntas Frecuentes (FAQ)

### ¿Necesito comprar Microsoft Access?

**NO**. Solo necesita el driver gratuito (Access Database Engine) para leer archivos Access. No requiere licencia de Access.

### ¿Puedo usar el plugin sin importar desde Access?

**SÍ**. Si sus datos ya están en PostgreSQL o los ingresa manualmente, no necesita el driver de Access.

### ¿El plugin funciona en Mac o Linux?

El plugin está diseñado principalmente para **Windows**. En Mac/Linux:
- El plugin QGIS funcionará
- La importación desde Access tiene limitaciones (requiere `mdbtools` y no es 100% compatible)
- **Recomendación**: Exporte datos de Access a CSV en Windows, luego impórtelos en Mac/Linux

### ¿Cuánto espacio en disco necesito?

- Plugin: ~5 MB
- Driver Access: ~50 MB
- Base de datos: Depende de sus datos (generalmente 50-500 MB)

### ¿Puedo instalar en múltiples computadoras?

**SÍ**. Repita estos pasos en cada máquina. Solo necesita una instancia de PostgreSQL (puede ser en una máquina servidor y las demás se conectan).

### ¿Necesito permisos de administrador?

- **Para instalar el driver de Access**: SÍ (Paso 1.3)
- **Para instalar el plugin**: NO
- **Para usar el plugin**: NO

---

## 🆘 Obtener Ayuda

Si tiene problemas durante la instalación:

1. **Consulte primero**:
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Soluciones a problemas comunes
   - [REQUISITOS_SISTEMA.md](REQUISITOS_SISTEMA.md) - Requisitos detallados

2. **Ejecute el script de verificación**:
   ```cmd
   python verificar_dependencias.py
   ```
   Guarde el reporte generado.

3. **Contacte a soporte** con:
   - Versión de QGIS (Ayuda → Acerca de)
   - Sistema operativo y versión
   - Mensaje de error completo (captura de pantalla)
   - Reporte de verificación (`verificacion_dependencias.txt`)

---

## ✅ Lista de Verificación Final

Antes de considerar la instalación completa, verifique:

- [ ] QGIS 3.16+ instalado y funcionando
- [ ] PostgreSQL con PostGIS funcionando
- [ ] Driver de Microsoft Access instalado
- [ ] Plugin aparece en menú de QGIS
- [ ] Configuración de BD guardada y probada
- [ ] Script de verificación ejecutado sin errores críticos
- [ ] Importación de prueba exitosa (opcional)

Si todos los ítems están marcados: **¡Felicitaciones! Instalación completada exitosamente.** 🎉

---

## 📞 Información de Contacto

**Soporte Técnico**: [email/teléfono de soporte]  
**Documentación**: [enlace a docs online]  
**Actualizaciones**: [enlace a repositorio/updates]

---

**Versión del documento**: 1.0  
**Última actualización**: Mayo 2026  
**Tiempo estimado de instalación**: 30-45 minutos
