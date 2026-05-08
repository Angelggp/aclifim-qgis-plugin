# 🎯 Guía Rápida de Mejoras - Para Usuarios

**Plugin de Gestión de Afiliados - Actualización Mayo 2026**

---

## 🆕 ¿Qué cambió?

### 1. **Nueva Interfaz con Pestañas** 🎨

**Antes:** Todos los datos en un scroll largo

**Ahora:** 6 pestañas organizadas:

```
┌─────────────────────────────────────────┐
│      👤 Juan Pérez García               │
├─────────────────────────────────────────┤
│ [🆔 Identificación] [📍 Ubicación]      │
│ [🏥 Médicos] [👨‍👩‍👧 Familiares]             │
│ [💼 Laborales] [🏛️ Organización]        │
├─────────────────────────────────────────┤
│                                         │
│  Información organizada                 │
│  en una sola columna                    │
│  fácil de leer                          │
│                                         │
└─────────────────────────────────────────┘
```

**Ventajas:**
- ✅ Encuentra la información más rápido
- ✅ No hay que hacer scroll largo
- ✅ Organizado por categorías

---

### 2. **Campos Vacíos Claros** 📝

**Antes:**
```
Teléfono:           
Ocupación:          
```

**Ahora:**
```
Teléfono:           No especificado
Ocupación:          No especificado
```

**Ventaja:** Sabes que el campo existe pero no tiene información

---

### 3. **Descripciones Legibles** 🏥

**Antes:**
```
Limitación: 01
Ambulación: 08
```

**Ahora:**
```
Limitación:         Amputado en 1 Pierna (01)
Ambulación:         Bastón/Muleta + Prótesis (08)
```

**Ventaja:** No necesitas memorizar códigos

---

### 4. **Datos Más Seguros** 🔒

**Antes:**
- A veces usaba capas temporales
- Datos podían perderse

**Ahora:**
- **Siempre usa PostgreSQL**
- Datos 100% seguros y persistentes
- Si no hay PostgreSQL configurado, te avisa claramente

---

### 5. **Interfaz Más Limpia** ✨

**Cambios:**
- ✅ Campo "Org_Rev" eliminado (innecesario)
- ✅ Una sola columna (más fácil de leer)
- ✅ Puedes seleccionar y copiar texto
- ✅ Colores y estilos modernos

---

## 📖 Cómo Usar la Nueva Interfaz

### Ver Detalles de un Afiliado

1. **Haz clic en un afiliado** del mapa o de la tabla

2. **Se abre ventana con pestañas:**
   - 🆔 **Identificación:** Código, CI, Nombre, Edad
   - 📍 **Ubicación:** Dirección, Teléfono, Coordenadas
   - 🏥 **Médicos:** Limitación, Ambulación, Causa
   - 👨‍👩‍👧 **Familiares:** Estado Civil, Hijos, Conviventes
   - 💼 **Laborales:** Ocupación, Ingreso, Educación
   - 🏛️ **Organización:** Área, Cuota, Fechas

3. **Navega entre pestañas** haciendo clic

4. **Usa scroll** si hay muchos datos en una pestaña

5. **Copia información** seleccionando con el mouse

---

## 🔍 Pestañas en Detalle

### 🆔 Pestaña "Identificación"

**Contiene:**
- Código del afiliado
- CI (Carnet de Identidad)
- Folio
- Nombres y Apellidos completos
- Sexo y Edad
- Fecha de nacimiento
- Lugar de nacimiento
- Nacionalidad y Ciudadanía

**Cuándo usar:** Para identificar al afiliado

---

### 📍 Pestaña "Ubicación"

**Contiene:**
- Dirección completa
- Reparto
- Locación
- Teléfono
- Tipo de teléfono
- Coordenadas GPS (Longitud/Latitud)

**Cuándo usar:** Para contactar o visitar al afiliado

---

### 🏥 Pestaña "Médicos"

**Contiene:**
- **Limitación:** Tipo de discapacidad (con descripción legible)
- **Ambulación:** Cómo se desplaza (con descripción legible)
- Causa de la discapacidad
- Discapacidad asociada

**Cuándo usar:** Para conocer condición médica del afiliado

**Ejemplo:**
```
Limitación:         Amputado en 1 Pierna (01)
Ambulación:         Prótesis (03)
Causa:              Accidente laboral
```

---

### 👨‍👩‍👧 Pestaña "Familiares"

**Contiene:**
- Hijo de (nombre del padre/madre)
- Estado civil
- Número de hijos
- Conviventes
- Personas dependientes

**Cuándo usar:** Para conocer situación familiar

---

### 💼 Pestaña "Laborales"

**Contiene:**
- Ocupación
- Centro de trabajo o estudio
- Ingreso mensual (en $)
- Grado escolar
- Especialidad

**Cuándo usar:** Para conocer situación laboral/educativa

---

### 🏛️ Pestaña "Organización"

**Contiene:**
- Área de ACLIFIM
- Jefe de núcleo
- Cuota mensual (en $)
- **Fechas:**
  - Fecha de ingreso
  - Fecha de alta
  - Fecha de baja
  - Motivo de baja
- **Estado del sistema:**
  - Estado actual (Nuevo, Normal, etc.)
  - Fecha de creación en el sistema
  - Última modificación

**Cuándo usar:** Para información administrativa

---

## 💡 Consejos de Uso

### Copiar Información

1. Haz clic sobre cualquier valor
2. Selecciona el texto que quieres copiar
3. Presiona `Ctrl + C`
4. Pega en otro lugar con `Ctrl + V`

**Ejemplo:** Copiar dirección para Google Maps

---

### Navegar Rápido

- **Mouse:** Haz clic en las pestañas
- **Teclado:** 
  - `Ctrl + Tab` → Siguiente pestaña
  - `Ctrl + Shift + Tab` → Pestaña anterior
- **Scroll:** Rueda del mouse o flecha arriba/abajo

---

### Buscar Información Específica

1. Ve directamente a la pestaña correcta:
   - ¿Teléfono? → 📍 **Ubicación**
   - ¿Discapacidad? → 🏥 **Médicos**
   - ¿Familia? → 👨‍👩‍👧 **Familiares**
   - ¿Trabajo? → 💼 **Laborales**
   - ¿Fechas? → 🏛️ **Organización**

2. Haz scroll si es necesario

3. Lee la información

---

## ❓ Preguntas Frecuentes

### ¿Dónde está el campo "Org_Rev"?

**Respuesta:** Se eliminó porque no era necesario. Si realmente lo necesitas, puedes consultarlo directamente en la base de datos PostgreSQL.

---

### ¿Por qué algunos campos dicen "No especificado"?

**Respuesta:** Significa que ese campo no tiene información guardada para ese afiliado. Puedes editarlo si tienes los datos.

---

### ¿Las capas temporales siguen funcionando?

**Respuesta:** **No.** El plugin ahora requiere PostgreSQL obligatoriamente. Esto garantiza que **todos tus datos se guarden** de forma segura y no se pierdan al cerrar QGIS.

---

### ¿Qué significa "Amputado en 1 Pierna (01)"?

**Respuesta:** Es la **descripción legible** del código 01. Antes solo veías "01" y no sabías qué significaba. Ahora ves la descripción completa.

**Otros ejemplos:**
- `02` = "Amputado en 2 Piernas"
- `08` = "Parálisis en 1 Pierna"
- `15` = "Otras limitaciones"

---

### ¿Puedo volver al diseño anterior?

**Respuesta:** No, pero el nuevo diseño es **mucho mejor**:
- ✅ Más organizado
- ✅ Más fácil de usar
- ✅ Más rápido para encontrar información
- ✅ Más moderno

---

### ¿Cómo se ve si no hay PostgreSQL configurado?

**Respuesta:** Verás un mensaje de error en la consola Python de QGIS:

```
[PLUGIN] ERROR: No hay configuración de base de datos PostgreSQL.
[PLUGIN] Por favor, configure la conexión a PostgreSQL desde el menú del plugin.
```

**Solución:** Ve al menú del plugin → "Configurar Base de Datos" → Ingresa los datos de PostgreSQL.

---

## 🚀 Ventajas del Nuevo Diseño

| Característica | Antes | Ahora |
|----------------|-------|-------|
| Organización | Un scroll largo | 6 pestañas temáticas |
| Lectura | Múltiples columnas | Una columna clara |
| Campos vacíos | Blancos | "No especificado" |
| Códigos médicos | "01", "08" | "Amputado en 1 Pierna (01)" |
| Copiar texto | No | ✅ Sí |
| Capas temporales | Sí (peligroso) | No (más seguro) |
| Estilo | Básico | Moderno con colores |

---

## 📞 ¿Necesitas Ayuda?

### Si algo no funciona:

1. **Verifica PostgreSQL:**
   - ¿Está instalado?
   - ¿Está configurado en el plugin?
   - ¿La tabla `afiliados` existe?

2. **Reinicia QGIS:**
   - Cierra QGIS completamente
   - Ábrelo de nuevo

3. **Revisa la consola Python:**
   - Ve a: Complementos → Consola de Python
   - Busca mensajes con `[PLUGIN]`
   - Lee los errores si hay

4. **Consulta documentación:**
   - `docs/TROUBLESHOOTING.md` - Problemas comunes
   - `docs/GUIA_INSTALACION.md` - Instalación
   - `docs/RESUMEN_EJECUTIVO_MAYO_2026.md` - Todas las mejoras

---

## ✅ Checklist de Verificación

Después de actualizar el plugin, verifica:

- [ ] Al abrir detalles de afiliado, veo 6 pestañas
- [ ] Cada pestaña tiene información organizada
- [ ] Campos vacíos muestran "No especificado"
- [ ] Códigos médicos muestran descripciones legibles
- [ ] Puedo seleccionar y copiar texto
- [ ] No veo campo "Org_Rev"
- [ ] No se crean capas temporales
- [ ] Solo veo capa "Afiliados" conectada a PostgreSQL

Si todos tienen ✅, **el plugin está funcionando correctamente!** 🎉

---

## 🎓 Resumen Rápido

**3 cosas más importantes:**

1. **🎨 Nueva interfaz con pestañas** → Más fácil de usar
2. **📝 Descripciones legibles** → Entiendes los códigos médicos
3. **🔒 Siempre PostgreSQL** → Datos seguros y persistentes

**¡Disfruta del plugin mejorado!** 🚀

---

**Fecha:** 8 de mayo de 2026  
**Versión:** 2.1  
**Creado para:** Usuarios finales del plugin
