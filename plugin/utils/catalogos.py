"""
Catálogos de códigos y descripciones para el sistema de afiliados

Contiene los diccionarios de mapeo de códigos numéricos a descripciones
para limitaciones, ambulación, y otros campos codificados.
"""

# Catálogo de Causas de la discapacidad
CAUSAS = {
    '01': 'Accidente del Tránsito',
    '02': 'Accidente Ferroviario',
    '03': 'Accidente Laboral',
    '04': 'Accidente en el Hogar',
    '05': 'Otro Accidente',
    '06': 'Acción de Guerra',
    '07': 'Enfermedad Congénita',
    '08': 'Enfermedad Encefalopática',
    '09': 'Enfermedad Poliomielitis',
    '10': 'Otra Enfermedad',
    '11': 'Parálisis Cerebral',
    '12': 'Violencia contra las personas',
    # Variantes sin cero inicial
    '1': 'Accidente del Tránsito',
    '2': 'Accidente Ferroviario',
    '3': 'Accidente Laboral',
    '4': 'Accidente en el Hogar',
    '5': 'Otro Accidente',
    '6': 'Acción de Guerra',
    '7': 'Enfermedad Congénita',
    '8': 'Enfermedad Encefalopática',
    '9': 'Enfermedad Poliomielitis',
}

# Catálogo de Grado Escolar
GRADO_ESCOLAR = {
    '00': 'Iletrado',
    '01': '1°',
    '02': '2°',
    '03': '3°',
    '04': '4°',
    '05': '5°',
    '06': '6°',
    '07': '7°',
    '08': '8°',
    '09': '9°',
    '10': '10°',
    '11': '11°',
    '12': '12°',
    '13': 'Tec Medio',
    '14': 'Universitario',
    '15': 'Prescolar',
    # Variantes sin cero inicial
    '0': 'Iletrado',
    '1': '1°',
    '2': '2°',
    '3': '3°',
    '4': '4°',
    '5': '5°',
    '6': '6°',
    '7': '7°',
    '8': '8°',
    '9': '9°',
}

# Catálogo de Motivos de Baja
MOTIVOS_BAJA = {
    '1': 'Fallecido',
    '2': 'Traslado',
    '3': 'Desconocido',
    '4': 'Solicitud Propia',
    '5': 'Recuperado Total',
    '6': 'Salida del País',
    '7': 'Sancionado',
    '8': 'Repetido',
}

# Catálogo de Áreas
AREAS = {
    'C05N05': 'La Barrera',
    'C06N06': 'Buena Vista',
    'C07N07': 'Caonao',
    'C08N08': 'Junco Sur',
    'C09N09': 'Pueblo Griffo',
    'C10N10': 'Pastorita',
    'C11N11': 'La Gloria',
    'C12N12': 'Pepito Tey',
    'C13N13': 'Paraiso',
    'C14N14': 'Castillo - Cen',
    'C15N15': 'Guao',
    'C16N16': 'Punta Gorda',
    'C17N17': 'Juanita 1',
    'C18N18': 'Juanita 2',
    'C19N19': 'Rancho Luna',
    'ERROR': 'ERROR',
}

# Catálogo de Sexo
SEXO = {
    'F': 'Femenino',
    'M': 'Masculino',
    'A': 'Niña',
    'O': 'Niño',
}

# Catálogo de Ocupaciones
OCUPACIONES = {
    '01': 'Trabajador',
    '02': 'Trabajador y Estudiante',
    '03': 'Estudiante',
    '04': 'Trabajador por Cuenta Propia',
    '05': 'Ama de Casa',
    '06': 'Asistenciado Social',
    '07': 'Jubilado ó Retirado',
    '08': 'Desempleado',
    '09': 'Imposibilitados sin Pensión',
    '10': 'Otros',
    '11': 'Trabajador Agrícola',
    '12': 'Trabajador de Taller Protegido',
    '13': 'Trabajador a Domicilio',
    '14': 'Curso de PROENDIS',
    # Variantes sin cero inicial
    '1': 'Trabajador',
    '2': 'Trabajador y Estudiante',
    '3': 'Estudiante',
    '4': 'Trabajador por Cuenta Propia',
    '5': 'Ama de Casa',
    '6': 'Asistenciado Social',
    '7': 'Jubilado ó Retirado',
    '8': 'Desempleado',
    '9': 'Imposibilitados sin Pensión',
}

# Catálogo de Limitaciones
LIMITACIONES = {
    '01': 'Amputado en 1 Pierna',
    '02': 'Amputado en 2 Piernas',
    '03': 'Amputado en 1 Brazo',
    '04': 'Amputado en 2 Brazos',
    '05': 'Amputado en 1 Pierna y 1 Brazo',
    '06': 'Amputado en 3 Extremidades',
    '07': 'Amputado en 4 Extremidades',
    '08': 'Parálisis en 1 Pierna',
    '09': 'Parálisis en 2 Piernas',
    '10': 'Parálisis en 1 Brazo',
    '11': 'Parálisis en 2 Brazos',
    '12': 'Parálisis en 1 Pierna y 1 Brazo',
    '13': 'Parálisis en 3 Extremidades',
    '14': 'Parálisis en 4 Extremidades',
    '15': 'Otras limitaciones',
    # Variantes sin cero inicial
    '1': 'Amputado en 1 Pierna',
    '2': 'Amputado en 2 Piernas',
    '3': 'Amputado en 1 Brazo',
    '4': 'Amputado en 2 Brazos',
    '5': 'Amputado en 1 Pierna y 1 Brazo',
    '6': 'Amputado en 3 Extremidades',
    '7': 'Amputado en 4 Extremidades',
    '8': 'Parálisis en 1 Pierna',
    '9': 'Parálisis en 2 Piernas',
}

# Catálogo de Niveles de Ambulación
AMBULACION = {
    '00': 'Encamado Permanente',
    '01': 'Silla de Ruedas',
    '02': 'Bastón o Muleta',
    '03': 'Prótesis',
    '04': 'Aparato Ortopédico',
    '05': 'Silla de ruedas + Bastón/Muleta',
    '06': 'Silla de ruedas + Prótesis',
    '07': 'Silla de ruedas + Aparato Ortopédico',
    '08': 'Bastón/Muleta + Prótesis',
    '09': 'Bastón/Muleta + Aparato Ortopédico',
    '10': 'Prótesis + Aparato Ortopédico',
    '11': 'Silla de ruedas + Bastón/Muleta + Prótesis',
    '12': 'Silla de ruedas + Bastón/Muleta + Aparato Ortopédico',
    '13': 'Silla de ruedas + Prótesis + Aparato Ortopédico',
    '14': 'Bastón/Muleta + Prótesis + Aparato Ortopédico',
    '15': 'Silla de ruedas + Bastón/Muleta + Prótesis + Aparato Ortopédico',
    '16': 'Camina sin ayuda',
    # Variantes sin cero inicial (para códigos 0X)
    '0': 'Encamado Permanente',
    '1': 'Silla de Ruedas',
    '2': 'Bastón o Muleta',
    '3': 'Prótesis',
    '4': 'Aparato Ortopédico',
    '5': 'Silla de ruedas + Bastón/Muleta',
    '6': 'Silla de ruedas + Prótesis',
    '7': 'Silla de ruedas + Aparato Ortopédico',
    '8': 'Bastón/Muleta + Prótesis',
    '9': 'Bastón/Muleta + Aparato Ortopédico',
}


def get_limitacion_descripcion(codigo):
    """
    Obtiene la descripción de una limitación según su código.
    
    Args:
        codigo: código de limitación (str, int, o None)
    
    Returns:
        str: descripción legible o el código si no se encuentra
    """
    if codigo is None or str(codigo).strip() == '':
        return 'No especificado'
    
    codigo_str = str(codigo).strip()
    
    # Normalizar código (agregar cero inicial si es necesario para códigos de 1 dígito)
    if len(codigo_str) == 1 and codigo_str.isdigit():
        codigo_normalizado = '0' + codigo_str
    else:
        codigo_normalizado = codigo_str
    
    # Buscar en el diccionario
    descripcion = LIMITACIONES.get(codigo_normalizado)
    
    # Si no se encuentra con cero inicial, intentar sin él
    if descripcion is None:
        descripcion = LIMITACIONES.get(codigo_str)
    
    # Si aún no se encuentra, retornar el código con un mensaje
    if descripcion is None:
        return f"Código {codigo_str} (no definido)"
    
    return descripcion


def get_ambulacion_descripcion(codigo):
    """
    Obtiene la descripción de un nivel de ambulación según su código.
    
    Args:
        codigo: código de ambulación (str, int, o None)
    
    Returns:
        str: descripción legible o el código si no se encuentra
    """
    if codigo is None or str(codigo).strip() == '':
        return 'No especificado'
    
    codigo_str = str(codigo).strip()
    
    # Normalizar código (agregar cero inicial si es necesario para códigos de 1 dígito)
    if len(codigo_str) == 1 and codigo_str.isdigit():
        codigo_normalizado = '0' + codigo_str
    else:
        codigo_normalizado = codigo_str
    
    # Buscar en el diccionario
    descripcion = AMBULACION.get(codigo_normalizado)
    
    # Si no se encuentra con cero inicial, intentar sin él
    if descripcion is None:
        descripcion = AMBULACION.get(codigo_str)
    
    # Si aún no se encuentra, retornar el código con un mensaje
    if descripcion is None:
        return f"Código {codigo_str} (no definido)"
    
    return descripcion


def get_limitacion_codigo_y_descripcion(codigo):
    """
    Obtiene código normalizado y descripción por separado.
    
    Args:
        codigo: código de limitación
    
    Returns:
        tuple: (codigo_normalizado, descripcion)
    """
    if codigo is None or str(codigo).strip() == '':
        return ('', 'No especificado')
    
    codigo_str = str(codigo).strip()
    
    # Normalizar código
    if len(codigo_str) == 1 and codigo_str.isdigit():
        codigo_normalizado = '0' + codigo_str
    else:
        codigo_normalizado = codigo_str
    
    descripcion = LIMITACIONES.get(codigo_normalizado) or LIMITACIONES.get(codigo_str)
    
    if descripcion is None:
        return (codigo_normalizado, f"Código no definido")
    
    return (codigo_normalizado, descripcion)


def get_ambulacion_codigo_y_descripcion(codigo):
    """
    Obtiene código normalizado y descripción por separado.
    
    Args:
        codigo: código de ambulación
    
    Returns:
        tuple: (codigo_normalizado, descripcion)
    """
    if codigo is None or str(codigo).strip() == '':
        return ('', 'No especificado')
    
    codigo_str = str(codigo).strip()
    
    # Normalizar código
    if len(codigo_str) == 1 and codigo_str.isdigit():
        codigo_normalizado = '0' + codigo_str
    else:
        codigo_normalizado = codigo_str
    
    descripcion = AMBULACION.get(codigo_normalizado) or AMBULACION.get(codigo_str)
    
    if descripcion is None:
        return (codigo_normalizado, f"Código no definido")
    
    return (codigo_normalizado, descripcion)


def get_todas_limitaciones():
    """
    Retorna lista de tuplas (codigo, descripcion) de todas las limitaciones.
    Útil para llenar combos/listas.
    
    Returns:
        list: [(codigo, descripcion), ...]
    """
    # Filtrar para evitar duplicados (solo códigos con cero inicial)
    return [(k, v) for k, v in sorted(LIMITACIONES.items()) if len(k) == 2]


def get_todas_ambulaciones():
    """
    Retorna lista de tuplas (codigo, descripcion) de todos los niveles de ambulación.
    Útil para llenar combos/listas.
    
    Returns:
        list: [(codigo, descripcion), ...]
    """
    # Filtrar para evitar duplicados (solo códigos con cero inicial)
    return [(k, v) for k, v in sorted(AMBULACION.items()) if len(k) == 2]


def _get_descripcion(catalogo, codigo, con_codigo=False):
    """Helper interno: busca descripción en un catálogo, con o sin normalización."""
    if codigo is None or str(codigo).strip() == '':
        return 'No especificado'
    codigo_str = str(codigo).strip()
    # Intentar con cero inicial si es un solo dígito
    if len(codigo_str) == 1 and codigo_str.isdigit():
        codigo_norm = '0' + codigo_str
    else:
        codigo_norm = codigo_str
    descripcion = catalogo.get(codigo_norm) or catalogo.get(codigo_str)
    if descripcion is None:
        return f"Código {codigo_str} (no definido)"
    if con_codigo:
        return f"{descripcion} ({codigo_norm})"
    return descripcion


def get_causa_descripcion(codigo):
    """Retorna la descripción de una causa de discapacidad según su código."""
    return _get_descripcion(CAUSAS, codigo)


def get_grado_escolar_descripcion(codigo):
    """Retorna la descripción del grado escolar según su código."""
    return _get_descripcion(GRADO_ESCOLAR, codigo)


def get_motivo_baja_descripcion(codigo):
    """Retorna la descripción del motivo de baja según su código."""
    return _get_descripcion(MOTIVOS_BAJA, codigo, con_codigo=False)


def get_area_descripcion(codigo):
    """Retorna el nombre del área según su código."""
    if codigo is None or str(codigo).strip() == '':
        return 'No especificado'
    codigo_str = str(codigo).strip().upper()
    return AREAS.get(codigo_str, f"Área {codigo_str} (no definida)")


def get_sexo_descripcion(codigo):
    """Retorna la descripción del sexo según su código."""
    if codigo is None or str(codigo).strip() == '':
        return 'No especificado'
    codigo_str = str(codigo).strip().upper()
    return SEXO.get(codigo_str, f"Código {codigo_str} (no definido)")


def get_ocupacion_descripcion(codigo):
    """Retorna la descripción de la ocupación según su código."""
    return _get_descripcion(OCUPACIONES, codigo)


# Catálogo de Locación
LOCACION = {
    '1': 'Urbana',
    '2': 'Rural',
}


def get_locacion_descripcion(codigo):
    """Retorna 'Urbana' o 'Rural' según el código de locación."""
    if codigo is None or str(codigo).strip() == '':
        return 'No especificado'
    return LOCACION.get(str(codigo).strip(), str(codigo).strip())


def get_jefe_nucleo_descripcion(valor):
    """Retorna 'Sí' o 'No' para el campo jefe de núcleo."""
    if valor is None or str(valor).strip() == '':
        return 'No'
    v = str(valor).strip().upper()
    if v in ('S', 'SI', 'SÍ', '1', 'TRUE', 'YES', 'Y'):
        return 'Sí'
    return 'No'
