# Importación desde Access con Contraseña

## 🔐 Cómo Funciona

El plugin ahora **detecta automáticamente** si tu base de datos Access tiene contraseña y te la pide cuando sea necesario.

---

## 📋 Paso a Paso

### 1. Seleccionar archivo Access

1. En el plugin, haz clic en **"Seleccionar Archivo Access"**
2. Navega y selecciona tu archivo `.mdb` o `.accdb`

### 2. Ingreso de contraseña (si es necesario)

**Si la base de datos NO tiene contraseña:**
- ✅ Se conectará automáticamente
- ✅ Continuará con la importación

**Si la base de datos TIENE contraseña:**
- 🔒 Aparecerá un diálogo pidiendo la contraseña
- 🔑 Ingresa la contraseña
- ✅ El plugin intentará conectarse con la contraseña

![Diálogo de contraseña](imagen_dialogo_password.png)

### 3. Importación automática

Una vez conectado:
- 🔍 Detecta automáticamente la tabla `ACLIFIM`
- 📊 Lee todos los registros
- 💾 Sincroniza con PostgreSQL
- ✅ Muestra estadísticas finales

---

## ⚠️ Tipos de Contraseña en Access

El plugin prueba automáticamente **3 tipos** de contraseña:

| Tipo | Cuándo se Usa | Cómo se Configura en Access |
|------|---------------|----------------------------|
| **Contraseña de Usuario** | Más común | Herramientas → Seguridad → Establecer contraseña |
| **Usuario + Contraseña** | Con usuarios configurados | Sistema de usuarios de Access |
| **Database Password** | Cifrado completo | Cifrar con contraseña (Access 2007+) |

**No necesitas saber cuál tipo tiene tu base de datos** - el plugin los prueba todos automáticamente.

---

## 🚀 Ventajas del Nuevo Sistema

| Antes | Ahora |
|-------|-------|
| ❌ Tenías que exportar sin contraseña | ✅ Importa directamente |
| ❌ Riesgo de seguridad | ✅ Mantiene la protección |
| ❌ Pasos extra | ✅ Proceso directo |
| ❌ No soportaba contraseñas | ✅ Soporte completo |

---

## 🔧 Ejemplo de Uso

### Escenario 1: Base de datos sin contraseña
```
1. Clic en "Seleccionar Archivo Access"
2. Seleccionar archivo
   → ✅ Conexión automática
   → ✅ Importación completa
```

### Escenario 2: Base de datos con contraseña
```
1. Clic en "Seleccionar Archivo Access"
2. Seleccionar archivo
3. Aparece diálogo: "Contraseña Requerida"
4. Ingresar contraseña: "mi_password123"
5. Clic en OK
   → ✅ Conexión exitosa
   → ✅ Importación completa
```

### Escenario 3: Contraseña incorrecta
```
1. Clic en "Seleccionar Archivo Access"
2. Seleccionar archivo
3. Ingresar contraseña: "password_incorrecta"
4. Clic en OK
   → ❌ Error: "No se pudo conectar con la contraseña proporcionada"
   → 🔄 Vuelve a intentar desde el paso 1
```

---

## ❓ Preguntas Frecuentes

### ¿Necesito quitar la contraseña de mi base de datos?

**NO**. El plugin ahora soporta bases de datos con contraseña. Mantén tu base de datos protegida.

### ¿La contraseña se guarda en algún lugar?

**NO**. La contraseña solo se usa durante la importación y **NO se guarda** en ningún archivo o configuración. Tendrás que ingresarla cada vez que importes.

### ¿Puedo importar múltiples veces con la misma contraseña?

Sí, pero tendrás que ingresar la contraseña cada vez. Esto es por seguridad.

### ¿Funciona con bases de datos muy antiguas (.mdb)?

Sí, funciona con:
- ✅ `.mdb` (Access 97, 2000, 2003)
- ✅ `.accdb` (Access 2007, 2010, 2013, 2016+)

### ¿Qué hago si olvido la contraseña?

Opciones:
1. **Recuperar contraseña**: Usa herramientas como "Access Password Recovery"
2. **Crear copia sin contraseña**: En Access, abre la BD con contraseña y guárdala como nueva BD sin contraseña
3. **Exportar a CSV**: En Access, exporta la tabla ACLIFIM a CSV y luego importa el CSV en PostgreSQL directamente

### ¿El plugin muestra la contraseña mientras la escribo?

NO. El campo de contraseña usa **modo oculto** (muestra ••••• en lugar de los caracteres reales) por seguridad.

---

## 🛠️ Solución de Problemas

### Problema: "No se pudo conectar con la contraseña proporcionada"

**Causas posibles:**
1. Contraseña incorrecta
2. Base de datos corrupta
3. Archivo no es una base de datos Access válida

**Soluciones:**
1. Verifica que la contraseña sea correcta (mayúsculas/minúsculas importan)
2. Intenta abrir la BD en Microsoft Access primero para verificar que funciona
3. Si Access también pide reparar la BD, hazlo antes de importar

### Problema: El diálogo de contraseña no aparece

**Causa:** La BD no tiene contraseña configurada o el plugin no detecta que la necesita.

**Solución:** Si estás seguro que tiene contraseña pero no la pide, puede ser que:
- La contraseña sea vacía (se permite en Access)
- El tipo de protección no sea estándar

Intenta abrir en Access para verificar.

---

## 📝 Notas Técnicas

### Cómo Detecta que Necesita Contraseña

El plugin:
1. Intenta conectar **sin contraseña** primero
2. Si falla, analiza el mensaje de error
3. Si el error menciona "password", "contraseña", o "cannot open", asume que necesita contraseña
4. Muestra el diálogo para pedirla

### Métodos de Conexión Probados

En orden:
1. `PWD=contraseña` (contraseña de usuario - más común)
2. `UID=Admin;PWD=contraseña` (con usuario Admin)
3. `Database Password=contraseña` (cifrado completo)

Si ninguno funciona, muestra error.

---

## 🔐 Seguridad

### ¿Es Seguro Ingresar mi Contraseña?

**SÍ**. El plugin:
- ✅ NO guarda la contraseña en ningún archivo
- ✅ NO envía la contraseña a ningún servidor
- ✅ Solo la usa temporalmente para la conexión ODBC local
- ✅ La contraseña se elimina de la memoria cuando termina la importación

### ¿Se Envía la Contraseña por Internet?

**NO**. Todo el proceso es **100% local**:
- La conexión es directa entre tu computadora y el archivo Access
- No hay comunicación con servidores externos
- PostgreSQL puede estar en tu máquina o en red local

---

## 📞 Soporte

Si tienes problemas con bases de datos protegidas:
1. Verifica que puedas abrir la BD en Microsoft Access
2. Anota el mensaje de error exacto del plugin
3. Consulta [TROUBLESHOOTING.md](TROUBLESHOOTING.md#3-base-de-datos-con-contraseña)

---

**Última actualización**: Mayo 2026  
**Versión del plugin**: 2.0+
