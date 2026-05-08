"""
Catálogos de códigos y descripciones para el sistema de afiliados

Contiene los diccionarios de mapeo de códigos numéricos a descripciones
para limitaciones, ambulación, y otros campos codificados.
"""

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
    
    return f"{descripcion} ({codigo_normalizado})"


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
    
    return f"{descripcion} ({codigo_normalizado})"


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
