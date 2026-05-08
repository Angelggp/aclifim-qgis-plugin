# 📄 Exportar Afiliados a PDF

## Descripción

Esta funcionalidad permite exportar la información completa de un afiliado a un archivo PDF bien formateado, ideal para impresión o archivo.

## Instalación de Dependencias

Antes de usar esta funcionalidad, es necesario instalar la librería `reportlab`:

```bash
pip install reportlab
```

O instalar todas las dependencias del plugin:

```bash
pip install -r requirements.txt
```

## Formas de Exportar

### 1. Desde el Diálogo de Detalles ⭐

Esta es la forma **recomendada** porque puedes revisar toda la información antes de exportar:

1. Selecciona un afiliado en cualquier tabla
2. Haz doble clic o presiona el botón **"📋 Ver Detalles"**
3. Revisa la información en las pestañas
4. Presiona el botón **"📄 Exportar PDF"** (botón verde a la izquierda de "Cerrar")
5. Elige dónde guardar el archivo
6. ¡Listo!

### 2. Desde el Menú Contextual (Click Derecho) 🚀

Esta forma es más rápida para exportar sin abrir el diálogo:

1. **Click derecho** sobre un afiliado en la tabla
2. Selecciona **"📄 Exportar a PDF"** del menú
3. Elige dónde guardar el archivo
4. ¡Listo!

También funciona con:
- Tabla de **Todos los Afiliados**
- Tabla de **Afiliados Sin Ubicar**

## Contenido del PDF

El PDF generado incluye toda la información del afiliado organizada en secciones:

### 📋 Secciones Incluidas

1. **🆔 Identificación y Datos Personales**
   - Código, CI, Folio, ID
   - Nombres, Apellidos, Sexo, Edad
   - Fecha y lugar de nacimiento
   - Nacionalidad, Ciudadanía

2. **📍 Ubicación y Contacto**
   - Dirección, Reparto, Locación
   - Teléfono y tipo
   - Coordenadas GPS (si está ubicado)

3. **🏥 Datos Médicos**
   - Limitación (con descripción completa)
   - Nivel de ambulación (con descripción completa)
   - Causa y discapacidades asociadas

4. **👨‍👩‍👧 Datos Familiares**
   - Hijo de, Estado civil
   - Número de hijos, Conviventes
   - Personas dependientes

5. **💼 Datos Laborales y Educativos**
   - Ocupación, Centro de trabajo/estudio
   - Ingreso mensual
   - Grado escolar, Especialidad

6. **🏛️ Organización y Fechas**
   - Área ACLIFIM, Jefe de núcleo
   - Cuota
   - Fechas de ingreso, alta, baja
   - Estado del sistema
   - Fecha de creación y modificación

## Formato del PDF

- **Tamaño:** A4
- **Diseño:** Tabla de 2 columnas
- **Fuente:** Helvetica 9-18pt
- **Colores:** Profesional (azul #3498db para títulos)
- **Nombre de archivo sugerido:** `Afiliado_[Codigo]_[Apellidos]_[Nombres].pdf`

## Ventajas

✅ **Portabilidad:** Los PDFs se pueden compartir fácilmente
✅ **Impresión:** Formato optimizado para impresora
✅ **Archivo:** Ideal para expedientes físicos
✅ **Profesional:** Diseño limpio y organizado
✅ **Completo:** Incluye toda la información disponible

## Notas

- Si la librería `reportlab` no está instalada, el plugin mostrará un mensaje con instrucciones
- Los PDFs se guardan por defecto en la carpeta "Documentos"
- El nombre de archivo sugerido incluye código y nombre del afiliado
- Los campos vacíos se muestran como "No especificado"
- Las fechas se formatean en formato DD/MM/YYYY
