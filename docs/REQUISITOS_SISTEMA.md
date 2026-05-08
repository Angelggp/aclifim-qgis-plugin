# Requisitos del Sistema - Plugin de Gestión de Afiliados

## 📋 Información General

Este documento describe los requisitos técnicos necesarios para instalar y utilizar el **Plugin de Gestión de Afiliados** en QGIS.

---

## 💻 Requisitos de Sistema

### Sistema Operativo
- **Windows**: 7, 8, 10, 11 (32-bit o 64-bit)
- **Linux**: Ubuntu 18.04+, Debian 10+, otras distribuciones compatibles con QGIS
- **macOS**: 10.13+ (High Sierra o superior)

### Software Base Requerido
| Software | Versión Mínima | Recomendada | Notas |
|----------|----------------|-------------|-------|
| **QGIS** | 3.16 | 3.28+ | Debe incluir soporte Python 3 |
| **Python** | 3.7 | 3.9+ | Incluido con QGIS |
| **PostgreSQL** | 10 | 14+ | Con extensión PostGIS |
| **PostGIS** | 2.5 | 3.3+ | Extensión geoespacial |

---

## 🔧 Componentes Adicionales Requeridos

### Para Importación desde Microsoft Access

Si va a importar datos desde bases de datos **Microsoft Access** (.mdb o .accdb), necesita:

#### Windows
- **Microsoft Access Database Engine 2016 Redistributable**
  - Descarga oficial: https://www.microsoft.com/en-us/download/details.aspx?id=54920
  - **GRATUITO** (no requiere licencia de Microsoft Access)
  - Versiones disponibles: 32-bit y 64-bit
  
  ⚠️ **IMPORTANTE**: 
  - Si tiene **Microsoft Office instalado**, debe instalar la versión (32 o 64 bits) que coincida con su Office
  - Si tiene **Python/QGIS de 64 bits**, instale la versión de 64 bits del driver
  - Si la instalación da error de compatibilidad, ejecute desde CMD: `AccessDatabaseEngine.exe /quiet`

#### Linux
- **mdbtools** (solo para archivos .mdb antiguos)
  ```bash
  # Ubuntu/Debian
  sudo apt-get install mdbtools
  
  # CentOS/RHEL
  sudo yum install mdbtools
  ```
  
  ⚠️ **NOTA**: El soporte para Access en Linux es limitado. Se recomienda exportar a CSV en Windows.

#### macOS
- **mdbtools** (vía Homebrew)
  ```bash
  brew install mdbtools
  ```
  
  ⚠️ **NOTA**: El soporte para Access en macOS es limitado. Se recomienda exportar a CSV en Windows.

---

## 📦 Librerías Python Requeridas

Estas librerías se instalan automáticamente con el plugin, pero se listan aquí por referencia:

```
PyQt5>=5.12.0
psycopg2-binary>=2.8.6
pyodbc>=4.0.30          # Solo Windows para Access
```

---

## 🗄️ Requisitos de Base de Datos PostgreSQL

### Configuración Mínima
- **Usuario**: Con permisos CREATE, INSERT, UPDATE, DELETE, SELECT
- **Base de datos**: Debe tener extensión PostGIS habilitada
- **Conexión**: Puerto 5432 (o personalizado) accesible desde la máquina cliente

### Verificar PostGIS
Ejecute en PostgreSQL para verificar que PostGIS está instalado:

```sql
SELECT PostGIS_version();
```

Si no está instalado:
```sql
CREATE EXTENSION postgis;
```

---

## 💾 Requisitos de Espacio en Disco

| Componente | Espacio Requerido |
|------------|-------------------|
| Plugin QGIS | ~5 MB |
| Microsoft Access Database Engine | ~50 MB |
| Base de datos PostgreSQL | Variable según datos |
| Archivos Access (.mdb/.accdb) | Variable según datos |

**Espacio recomendado libre**: 500 MB mínimo

---

## 🌐 Requisitos de Red

### Conexión a PostgreSQL
- **Puerto**: 5432 (predeterminado) o el configurado en su servidor
- **Firewall**: El puerto debe estar abierto para conexiones desde su máquina
- **Latencia**: < 100ms para rendimiento óptimo
- **Ancho de banda**: Mínimo 1 Mbps para importaciones grandes

### Conexión a Internet (Opcional)
- Requerida para:
  - Geocodificación con servicios externos (Nominatim, Google Maps API)
  - Descarga de tiles de mapas base
- No es requerida para funcionalidad básica del plugin

---

## 🔐 Permisos y Acceso

### Permisos de Usuario (Windows)
- **Lectura/escritura** en la carpeta de instalación de QGIS
- **Lectura** en las carpetas donde están los archivos Access
- No se requieren permisos de administrador para uso normal

### Permisos de Base de Datos
El usuario de PostgreSQL necesita:
```sql
GRANT CONNECT ON DATABASE nombre_bd TO usuario;
GRANT USAGE ON SCHEMA public TO usuario;
GRANT CREATE ON SCHEMA public TO usuario;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO usuario;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO usuario;
```

---

## ⚠️ Problemas Conocidos y Limitaciones

### Microsoft Access
1. **Bases de datos con contraseña**: Requieren contraseña en cada importación
2. **Archivos corruptos**: No se pueden importar si Access no puede abrirlos
3. **Versiones muy antiguas** (.mdb de Access 97): Pueden tener problemas de compatibilidad
4. **Bases de datos grandes** (>2GB): Pueden tardar varios minutos en importar

### Compatibilidad de Arquitectura (32-bit vs 64-bit)
- **Windows**: Si tiene Office 32-bit y QGIS 64-bit, puede haber conflictos con el driver ODBC
- **Solución**: Instale ambas versiones del driver Access usando `/quiet` en la instalación

### Rendimiento
- **Importaciones grandes** (>10,000 registros): Pueden tomar varios minutos
- **Geocodificación masiva**: Limitada por las APIs externas (límites de requests/día)

---

## ✅ Verificación de Requisitos

Antes de instalar el plugin, verifique:

- [ ] QGIS 3.16 o superior instalado
- [ ] PostgreSQL con PostGIS funcionando
- [ ] Conexión exitosa a la base de datos PostgreSQL
- [ ] Microsoft Access Database Engine instalado (si va a importar desde Access)
- [ ] Permisos de lectura/escritura en carpetas necesarias
- [ ] Firewall configurado para permitir conexión a PostgreSQL

**Herramienta de verificación**: Ejecute el script `verificar_dependencias.py` incluido en el plugin para validar automáticamente todos los requisitos.

---

## 📞 Soporte

Si tiene problemas instalando o cumpliendo los requisitos:

1. Consulte el archivo **TROUBLESHOOTING.md** para soluciones comunes
2. Verifique los logs en: `[carpeta_plugin]/logs/`
3. Contacte al equipo de soporte con:
   - Versión de QGIS
   - Sistema operativo y versión
   - Mensaje de error completo
   - Logs del plugin

---

## 📝 Notas Adicionales

### Para Administradores de TI
- El plugin puede desplegarse en múltiples máquinas copiando la carpeta del plugin
- Los archivos de configuración están en `[perfil_usuario]/.qgis3/`
- Se recomienda configurar el servidor PostgreSQL en una red local para mejor rendimiento

### Para Desarrolladores
- El código fuente está disponible en el repositorio
- Los requisitos completos de desarrollo están en `requirements.txt`
- Documentación técnica en `docs/DESARROLLO.md`

---

**Última actualización**: Mayo 2026  
**Versión del documento**: 1.0
