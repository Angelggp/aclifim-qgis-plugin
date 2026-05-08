"""
Utilidades del plugin de Gestión de Afiliados
"""

from .catalogos import (
    get_limitacion_descripcion,
    get_ambulacion_descripcion,
    get_limitacion_codigo_y_descripcion,
    get_ambulacion_codigo_y_descripcion,
    get_todas_limitaciones,
    get_todas_ambulaciones,
    LIMITACIONES,
    AMBULACION
)

__all__ = [
    'get_limitacion_descripcion',
    'get_ambulacion_descripcion',
    'get_limitacion_codigo_y_descripcion',
    'get_ambulacion_codigo_y_descripcion',
    'get_todas_limitaciones',
    'get_todas_ambulaciones',
    'LIMITACIONES',
    'AMBULACION'
]
