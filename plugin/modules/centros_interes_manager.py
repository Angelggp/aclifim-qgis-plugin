"""
Módulo para gestionar Centros de Interés en PostgreSQL
"""
import psycopg2
import os
import json


def load_db_config():
    """Carga la configuración de la base de datos"""
    config_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'db_config.json'
    )
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            return None
    return None


def get_all_centros_interes():
    """
    Obtiene todos los centros de interés desde PostgreSQL
    Retorna: list de dict con id, nombre, tipo, descripcion, direccion, lon, lat
    """
    config = load_db_config()
    if not config:
        print("[CENTROS] No hay configuración de BD")
        return []
    
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            dbname=config['dbname']
        )
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, nombre, tipo, descripcion, direccion,
                   ST_X(geom) as lon, ST_Y(geom) as lat,
                   fecha_creacion
            FROM centros_interes 
            ORDER BY nombre
            """
        )
        
        rows = cursor.fetchall()
        centros = []
        
        for row in rows:
            centros.append({
                'id': row[0],
                'nombre': row[1] or '',
                'tipo': row[2] or '',
                'descripcion': row[3] or '',
                'direccion': row[4] or '',
                'lon': row[5],
                'lat': row[6],
                'fecha_creacion': row[7]
            })
        
        cursor.close()
        conn.close()
        
        print(f"[CENTROS] {len(centros)} centros de interés encontrados")
        return centros
        
    except Exception as e:
        print(f"[CENTROS] Error al obtener centros: {e}")
        return []


def get_centro_by_id(centro_id):
    """
    Obtiene un centro de interés por ID
    Retorna: dict con todos los campos o None
    """
    config = load_db_config()
    if not config:
        return None
    
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            dbname=config['dbname']
        )
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, nombre, tipo, descripcion, direccion,
                   ST_X(geom) as lon, ST_Y(geom) as lat,
                   fecha_creacion, fecha_modificacion
            FROM centros_interes 
            WHERE id = %s
            """,
            (centro_id,)
        )
        
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            conn.close()
            return None
        
        centro = {
            'id': row[0],
            'nombre': row[1],
            'tipo': row[2],
            'descripcion': row[3],
            'direccion': row[4],
            'lon': row[5],
            'lat': row[6],
            'fecha_creacion': row[7],
            'fecha_modificacion': row[8]
        }
        
        cursor.close()
        conn.close()
        
        return centro
        
    except Exception as e:
        print(f"[CENTROS] Error al obtener centro: {e}")
        return None


def create_centro_interes(nombre, tipo, descripcion, direccion, point):
    """
    Crea un nuevo centro de interés
    
    Args:
        nombre: Nombre del centro
        tipo: Tipo (hospital, escuela, etc.)
        descripcion: Descripción opcional
        direccion: Dirección opcional
        point: QgsPointXY con las coordenadas
    
    Retorna: (bool, int/str) - (éxito, ID del centro o mensaje de error)
    """
    config = load_db_config()
    if not config:
        return False, "No hay configuración de BD"
    
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            dbname=config['dbname']
        )
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO centros_interes (nombre, tipo, descripcion, direccion, geom)
            VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            RETURNING id
            """,
            (nombre, tipo, descripcion, direccion, point.x(), point.y())
        )
        
        centro_id = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"[CENTROS] Centro de interés creado: ID {centro_id}")
        return True, centro_id
        
    except Exception as e:
        error_msg = f"Error al crear centro: {str(e)}"
        print(f"[CENTROS] {error_msg}")
        return False, error_msg


def update_centro_interes(centro_id, nombre, tipo, descripcion, direccion, point=None):
    """
    Actualiza un centro de interés existente
    
    Args:
        centro_id: ID del centro
        nombre: Nombre del centro
        tipo: Tipo
        descripcion: Descripción
        direccion: Dirección
        point: QgsPointXY con nuevas coordenadas (opcional)
    
    Retorna: (bool, str) - (éxito, mensaje)
    """
    config = load_db_config()
    if not config:
        return False, "No hay configuración de BD"
    
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            dbname=config['dbname']
        )
        cursor = conn.cursor()
        
        if point:
            # Actualizar con nueva ubicación
            cursor.execute(
                """
                UPDATE centros_interes 
                SET nombre = %s, tipo = %s, descripcion = %s, direccion = %s,
                    geom = ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (nombre, tipo, descripcion, direccion, point.x(), point.y(), centro_id)
            )
        else:
            # Actualizar sin cambiar ubicación
            cursor.execute(
                """
                UPDATE centros_interes 
                SET nombre = %s, tipo = %s, descripcion = %s, direccion = %s,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (nombre, tipo, descripcion, direccion, centro_id)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"[CENTROS] Centro de interés actualizado: ID {centro_id}")
        return True, "Centro actualizado exitosamente"
        
    except Exception as e:
        error_msg = f"Error al actualizar centro: {str(e)}"
        print(f"[CENTROS] {error_msg}")
        return False, error_msg


def delete_centro_interes(centro_id):
    """
    Elimina un centro de interés
    
    Args:
        centro_id: ID del centro a eliminar
    
    Retorna: (bool, str) - (éxito, mensaje)
    """
    config = load_db_config()
    if not config:
        return False, "No hay configuración de BD"
    
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            dbname=config['dbname']
        )
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM centros_interes WHERE id = %s", (centro_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"[CENTROS] Centro de interés eliminado: ID {centro_id}")
        return True, "Centro eliminado exitosamente"
        
    except Exception as e:
        error_msg = f"Error al eliminar centro: {str(e)}"
        print(f"[CENTROS] {error_msg}")
        return False, error_msg


def search_centros_interes(nombre=None, tipo=None):
    """
    Busca centros de interés con filtros
    Retorna: list de dict
    """
    config = load_db_config()
    if not config:
        return []
    
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            dbname=config['dbname']
        )
        cursor = conn.cursor()
        
        query = """
            SELECT id, nombre, tipo, descripcion, direccion,
                   ST_X(geom) as lon, ST_Y(geom) as lat
            FROM centros_interes 
            WHERE 1=1
        """
        params = []
        
        if nombre:
            query += " AND LOWER(nombre) LIKE LOWER(%s)"
            params.append(f'%{nombre}%')
        
        if tipo:
            query += " AND LOWER(tipo) LIKE LOWER(%s)"
            params.append(f'%{tipo}%')
        
        query += " ORDER BY nombre"
        
        cursor.execute(query, tuple(params))
        
        rows = cursor.fetchall()
        centros = []
        
        for row in rows:
            centros.append({
                'id': row[0],
                'nombre': row[1] or '',
                'tipo': row[2] or '',
                'descripcion': row[3] or '',
                'direccion': row[4] or '',
                'lon': row[5],
                'lat': row[6]
            })
        
        cursor.close()
        conn.close()
        
        print(f"[CENTROS] {len(centros)} centros encontrados en búsqueda")
        return centros
        
    except Exception as e:
        print(f"[CENTROS] Error en búsqueda: {e}")
        return []
