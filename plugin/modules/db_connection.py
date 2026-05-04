"""
Módulo para gestionar la conexión con PostgreSQL/PostGIS
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class DatabaseManager:
    """Gestiona la conexión y operaciones con la base de datos PostgreSQL/PostGIS"""
    
    def __init__(self, host='localhost', port='5432', user='postgres', password='', dbname='aclifim_db'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.connection = None
    
    def test_connection(self):
        """
        Prueba la conexión al servidor PostgreSQL (sin especificar BD)
        Retorna: (bool, str) - (éxito, mensaje)
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname='postgres'  # Conectar a BD por defecto
            )
            conn.close()
            return True, "Conexión exitosa al servidor PostgreSQL"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"
    
    def create_database_if_not_exists(self):
        """
        Crea la base de datos si no existe
        Retorna: (bool, str) - (éxito, mensaje)
        """
        try:
            # Conectar a la BD postgres (por defecto)
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Verificar si la BD existe
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.dbname,)
            )
            exists = cursor.fetchone()
            
            if not exists:
                # Crear la base de datos
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(self.dbname)
                    )
                )
                print(f"[DB] Base de datos '{self.dbname}' creada exitosamente")
                msg = f"Base de datos '{self.dbname}' creada"
            else:
                print(f"[DB] Base de datos '{self.dbname}' ya existe")
                msg = f"Base de datos '{self.dbname}' encontrada"
            
            cursor.close()
            conn.close()
            return True, msg
            
        except Exception as e:
            return False, f"Error al crear BD: {str(e)}"
    
    def enable_postgis(self):
        """
        Habilita la extensión PostGIS en la base de datos
        Retorna: (bool, str) - (éxito, mensaje)
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.dbname
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Intentar crear la extensión (si ya existe, no hace nada)
            cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
            
            # Verificar versión de PostGIS
            cursor.execute("SELECT PostGIS_Version()")
            result = cursor.fetchone()
            version = result[0] if result else "desconocida"
            print(f"[DB] PostGIS habilitado: versión {version}")
            
            cursor.close()
            conn.close()
            return True, f"PostGIS habilitado (v{version})"
            
        except Exception as e:
            return False, f"Error al habilitar PostGIS: {str(e)}"
    
    def create_afiliados_table(self):
        """
        Crea la tabla 'afiliados' completa con todos los campos de Access
        Retorna: (bool, str) - (éxito, mensaje)
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.dbname
            )
            cursor = conn.cursor()
            
            # Crear tabla completa con todos los campos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS afiliados (
                    -- Identificación
                    id SERIAL PRIMARY KEY,
                    codigo VARCHAR(20),
                    folio VARCHAR(50),
                    nombres VARCHAR(255),
                    apellidos VARCHAR(255),
                    carnet_id VARCHAR(20),
                    
                    -- Datos demográficos
                    sexo VARCHAR(20),
                    fecha_nacimiento DATE,
                    edad INTEGER,
                    lugar_nacimiento VARCHAR(100),
                    nacionalidad VARCHAR(50),
                    ciudadania VARCHAR(50),
                    
                    -- Datos familiares
                    hijo_de VARCHAR(255),
                    estado_civil VARCHAR(50),
                    no_hijos INTEGER,
                    conviventes VARCHAR(50),
                    no_personas_dep INTEGER,
                    
                    -- Ubicación
                    locacion VARCHAR(50),
                    direccion VARCHAR(255),
                    reparto VARCHAR(100),
                    telefono VARCHAR(50),
                    tipo_telefono VARCHAR(50),
                    
                    -- Organización
                    area VARCHAR(50),
                    cuota DECIMAL(10,2),
                    jefe_nucleo VARCHAR(10),
                    org_rev VARCHAR(50),
                    
                    -- Datos médicos/discapacidad
                    limitacion VARCHAR(50),
                    limitacion_cod VARCHAR(50),
                    nivel_ambulacion VARCHAR(50),
                    ambulacion_cod VARCHAR(50),
                    causa VARCHAR(100),
                    discap_asociada VARCHAR(100),
                    
                    -- Datos laborales/educativos
                    ocupacion VARCHAR(100),
                    centro_trabajo VARCHAR(255),
                    ingreso_mensual DECIMAL(10,2),
                    grado_escolar VARCHAR(50),
                    especialidad VARCHAR(100),
                    
                    -- Fechas administrativas
                    fecha_ingreso DATE,
                    fecha_alta DATE,
                    fecha_baja DATE,
                    motivo_baja VARCHAR(100),
                    
                    -- Campos de control del sistema
                    estado VARCHAR(20) DEFAULT 'normal',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion TIMESTAMP,
                    
                    -- Geometría (ubicación en mapa)
                    geom GEOMETRY(Point, 4326),
                    geom_anterior GEOMETRY(Point, 4326)
                )
            """)
            
            # Crear índices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS afiliados_geom_idx 
                ON afiliados USING GIST (geom)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS afiliados_codigo_idx 
                ON afiliados (codigo)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS afiliados_carnet_idx 
                ON afiliados (carnet_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS afiliados_estado_idx 
                ON afiliados (estado)
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("[DB] Tabla 'afiliados' creada/verificada exitosamente")
            return True, "Tabla 'afiliados' lista"
            
        except Exception as e:
            return False, f"Error al crear tabla: {str(e)}"
    
    def update_existing_afiliados_table(self):
        """
        Actualiza tabla afiliados existente agregando columnas nuevas
        (sin perder datos existentes)
        Retorna: (bool, str) - (éxito, mensaje)
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.dbname
            )
            cursor = conn.cursor()
            
            # Lista de columnas a agregar (si no existen)
            columns_to_add = [
                "codigo VARCHAR(20)",
                "folio VARCHAR(50)",
                "apellidos VARCHAR(255)",
                "carnet_id VARCHAR(20)",
                "sexo VARCHAR(20)",
                "fecha_nacimiento DATE",
                "edad INTEGER",
                "lugar_nacimiento VARCHAR(100)",
                "nacionalidad VARCHAR(50)",
                "ciudadania VARCHAR(50)",
                "hijo_de VARCHAR(255)",
                "estado_civil VARCHAR(50)",
                "no_hijos INTEGER",
                "conviventes VARCHAR(50)",
                "no_personas_dep INTEGER",
                "locacion VARCHAR(50)",
                "reparto VARCHAR(100)",
                "telefono VARCHAR(50)",
                "tipo_telefono VARCHAR(50)",
                "area VARCHAR(50)",
                "cuota DECIMAL(10,2)",
                "jefe_nucleo VARCHAR(10)",
                "org_rev VARCHAR(50)",
                "limitacion VARCHAR(50)",
                "limitacion_cod VARCHAR(50)",
                "nivel_ambulacion VARCHAR(50)",
                "ambulacion_cod VARCHAR(50)",
                "causa VARCHAR(100)",
                "discap_asociada VARCHAR(100)",
                "ocupacion VARCHAR(100)",
                "centro_trabajo VARCHAR(255)",
                "ingreso_mensual DECIMAL(10,2)",
                "grado_escolar VARCHAR(50)",
                "especialidad VARCHAR(100)",
                "fecha_ingreso DATE",
                "fecha_alta DATE",
                "fecha_baja DATE",
                "motivo_baja VARCHAR(100)",
                "estado VARCHAR(20) DEFAULT 'normal'",
                "fecha_modificacion TIMESTAMP",
                "geom_anterior GEOMETRY(Point, 4326)"
            ]
            
            # Intentar agregar cada columna
            for column in columns_to_add:
                col_name = column.split()[0]
                try:
                    cursor.execute(f"ALTER TABLE afiliados ADD COLUMN IF NOT EXISTS {column}")
                    print(f"[DB] Columna '{col_name}' agregada/verificada")
                except Exception as e:
                    print(f"[DB] Advertencia al agregar columna '{col_name}': {e}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("[DB] Tabla 'afiliados' actualizada exitosamente")
            return True, "Tabla 'afiliados' actualizada"
            
        except Exception as e:
            return False, f"Error al actualizar tabla: {str(e)}"
    
    def create_centros_interes_table(self):
        """
        Crea la tabla 'centros_interes' para lugares de interés
        Retorna: (bool, str) - (éxito, mensaje)
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.dbname
            )
            cursor = conn.cursor()
            
            # Crear tabla de centros de interés
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS centros_interes (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    tipo VARCHAR(100),
                    descripcion TEXT,
                    direccion VARCHAR(255),
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion TIMESTAMP,
                    geom GEOMETRY(Point, 4326)
                )
            """)
            
            # Crear índice espacial
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS centros_interes_geom_idx 
                ON centros_interes USING GIST (geom)
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("[DB] Tabla 'centros_interes' creada/verificada exitosamente")
            return True, "Tabla 'centros_interes' lista"
            
        except Exception as e:
            return False, f"Error al crear tabla centros_interes: {str(e)}"
    
    def initialize_database(self):
        """
        Inicializa completamente la base de datos:
        1. Prueba conexión
        2. Crea BD si no existe
        3. Habilita PostGIS
        4. Crea tabla afiliados
        5. Crea tabla centros_interes
        
        Retorna: (bool, list[str]) - (éxito, lista de mensajes)
        """
        messages = []
        
        # 1. Probar conexión
        success, msg = self.test_connection()
        messages.append(msg)
        if not success:
            return False, messages
        
        # 2. Crear BD
        success, msg = self.create_database_if_not_exists()
        messages.append(msg)
        if not success:
            return False, messages
        
        # 3. Habilitar PostGIS
        success, msg = self.enable_postgis()
        messages.append(msg)
        if not success:
            return False, messages
        
        # 4. Crear tabla afiliados
        success, msg = self.create_afiliados_table()
        messages.append(msg)
        if not success:
            return False, messages
        
        # 5. Crear tabla centros de interés
        success, msg = self.create_centros_interes_table()
        messages.append(msg)
        if not success:
            return False, messages
        
        return True, messages
    
    def get_connection_uri(self):
        """
        Retorna el URI de conexión para usar en QGIS
        """
        return f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password} sslmode=disable"
