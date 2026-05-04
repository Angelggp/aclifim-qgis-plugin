"""
Módulo para importar datos desde Access a PostgreSQL
"""
import pyodbc
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


class AccessImporter:
    """Gestiona la importación de datos desde Access a PostgreSQL"""
    
    def __init__(self, access_file_path):
        self.access_file_path = access_file_path
        self.connection = None
    
    def connect_to_access(self):
        """
        Conecta a la base de datos Access
        Retorna: (bool, str) - (éxito, mensaje)
        """
        try:
            # Detectar si es .mdb o .accdb
            if self.access_file_path.endswith('.accdb'):
                driver = '{Microsoft Access Driver (*.mdb, *.accdb)}'
            else:
                driver = '{Microsoft Access Driver (*.mdb)}'
            
            conn_str = f'DRIVER={driver};DBQ={self.access_file_path}'
            self.connection = pyodbc.connect(conn_str)
            
            # Configurar decodificación para manejar caracteres especiales en español
            # Access usa Windows-1252 (CP1252) en lugar de UTF-8
            self.connection.setdecoding(pyodbc.SQL_CHAR, encoding='cp1252')
            self.connection.setdecoding(pyodbc.SQL_WCHAR, encoding='cp1252')
            self.connection.setencoding(encoding='cp1252')
            
            print(f"[IMPORTADOR] Conectado a Access: {self.access_file_path}")
            return True, "Conexión exitosa a Access"
        except pyodbc.Error as e:
            error_msg = f"Error al conectar a Access: {str(e)}"
            print(f"[IMPORTADOR] {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            print(f"[IMPORTADOR] {error_msg}")
            return False, error_msg
    
    def get_tables(self):
        """
        Obtiene la lista de tablas en la base de datos Access
        Retorna: (bool, list/str) - (éxito, lista de nombres de tablas o mensaje de error)
        """
        if not self.connection:
            return False, "No hay conexión a Access"
        
        try:
            cursor = self.connection.cursor()
            tables = []
            all_tables = []
            
            for table_info in cursor.tables(tableType='TABLE'):
                table_name = table_info.table_name
                all_tables.append(table_name)  # Guardar todas para debug
                
                # Filtrar tablas del sistema y temporales más agresivamente
                if (not table_name.startswith('MSys') and 
                    not table_name.startswith('~') and
                    not table_name.startswith('f_') and  # Algunas tablas del sistema empiezan con f_
                    not table_name.startswith('USys')):
                    tables.append(table_name)
            
            cursor.close()
            print(f"[IMPORTADOR] Total de tablas en archivo: {len(all_tables)}")
            print(f"[IMPORTADOR] Todas las tablas: {', '.join(all_tables[:20])}...")  # Mostrar primeras 20
            print(f"[IMPORTADOR] {len(tables)} tablas filtradas: {', '.join(tables)}")
            
            # Verificar si ACLIFIM está en la lista
            if 'ACLIFIM' in tables:
                print("[IMPORTADOR] ✅ Tabla ACLIFIM encontrada")
            else:
                print("[IMPORTADOR] ⚠️ Tabla ACLIFIM NO encontrada en tablas filtradas")
                # Buscar variaciones
                aclifim_variants = [t for t in all_tables if 'ACLIFIM' in t.upper()]
                if aclifim_variants:
                    print(f"[IMPORTADOR] Variaciones encontradas: {aclifim_variants}")
            
            return True, tables
            
        except Exception as e:
            error_msg = f"Error al listar tablas: {str(e)}"
            print(f"[IMPORTADOR] {error_msg}")
            return False, error_msg
    
    def get_table_columns(self, table_name):
        """
        Obtiene las columnas de una tabla específica
        Retorna: (bool, list/str) - (éxito, lista de nombres de columnas o mensaje de error)
        """
        if not self.connection:
            return False, "No hay conexión a Access"
        
        try:
            cursor = self.connection.cursor()
            columns = []
            
            for column in cursor.columns(table=table_name):
                columns.append(column.column_name)
            
            cursor.close()
            print(f"[IMPORTADOR] Tabla '{table_name}' tiene {len(columns)} columnas")
            print(f"[IMPORTADOR] Columnas: {', '.join(columns)}")
            return True, columns
            
        except Exception as e:
            error_msg = f"Error al obtener columnas: {str(e)}"
            print(f"[IMPORTADOR] {error_msg}")
            return False, error_msg
    
    def get_afiliados_from_access(self, table_name='ACLIFIM'):
        """
        Lee afiliados desde Access detectando automáticamente las columnas disponibles
        Retorna: (bool, list/str) - (éxito, lista de registros o mensaje de error)
        """
        if not self.connection:
            return False, "No hay conexión a Access"
        
        try:
            cursor = self.connection.cursor()
            
            # Primero, obtener las columnas disponibles
            success, columns_result = self.get_table_columns(table_name)
            if not success:
                return False, columns_result
            
            available_columns = [col.upper() for col in columns_result]
            
            # Mapeo de campos esperados a nombres posibles en Access
            field_mapping = {
                'codigo': ['CODIGO', 'COD', 'CODE'],
                'folio': ['FOLIO', 'Folio'],
                'nombres': ['NOMBRES', 'NOMBRE', 'NAME'],
                'apellidos': ['APELLIDOS', 'APELLIDO', 'LASTNAME'],
                'fecha_nacimiento': ['FECH_NACI', 'FECHA_NACIMIENTO', 'FECHANAC'],
                'carnet_id': ['CARNET_ID', 'CI', 'CARNET'],
                'sexo': ['SEXO', 'SEX', 'GENERO'],
                'edad': ['EDAD', 'AGE'],
                'lugar_nacimiento': ['LUGARNACIM', 'LUGAR_NACIMIENTO'],
                'nacionalidad': ['NACIONALIDAD', 'NATIONALITY'],
                'ciudadania': ['CIUDADANIA', 'Ciudadania'],
                'hijo_de': ['HIJO DE', 'Hijo de', 'HIJODE'],
                'locacion': ['LOCACION', 'Locacion', 'UBICACION'],
                'direccion': ['DIRECCION', 'DIRECCIÓN', 'ADDRESS'],
                'reparto': ['REPARTO', 'BARRIO'],
                'telefono': ['TELEFONO', 'TELÉFONO', 'TEL', 'PHONE'],
                'area': ['AREA', 'ÁREA'],
                'cuota': ['CUOTA', 'QUOTA'],
                'estado_civil': ['EST_CIVIL', 'ESTADO_CIVIL', 'ESTADOCIVIL'],
                'jefe_nucleo': ['JDENUCLEO', 'JEFE_NUCLEO'],
                'no_hijos': ['NODEHIJOS', 'NO_HIJOS', 'NUM_HIJOS'],
                'conviventes': ['CONVIVENTES', 'Conviventes'],
                'no_personas_dep': ['NODEPERDEP', 'NO_PERSONAS_DEP'],
                'org_rev': ['ORG_REV', 'Org_Rev'],
                'limitacion': ['LIMITACIÓN', 'LIMITACION', 'Limitación'],
                'limitacion_cod': ['LIMITACION', 'LIMITACION_COD'],
                'nivel_ambulacion': ['NEVAMBULACION', 'NIVEL_AMBULACION'],
                'ambulacion_cod': ['AMBULACION', 'AMBULACION_COD'],
                'causa': ['CAUSA', 'CAUSE'],
                'discap_asociada': ['DISCAPASOCIADA', 'DISCAP_ASOCIADA'],
                'ocupacion': ['OCUPACIÓN', 'OCUPACION', 'OCCUPATION'],
                'centro_trabajo': ['CENTRABOESTU', 'CENTRO_TRABAJO'],
                'ingreso_mensual': ['INGRESOMENSUAL', 'INGRESO_MENSUAL'],
                'grado_escolar': ['GRADO_ESC', 'GRADO_ESCOLAR'],
                'especialidad': ['ESPECIALIDAD', 'SPECIALTY'],
                'fecha_ingreso': ['FECH_INGR', 'FECHA_INGRESO'],
                'fecha_alta': ['FECHA ALTA', 'FECHA_ALTA', 'FECHAALTA'],
                'fecha_baja': ['FECH_BAJA', 'FECHA_BAJA'],
                'motivo_baja': ['MOT_BAJA', 'MOTIVO_BAJA'],
                'tipo_telefono': ['TIPTEL', 'TIPO_TELEFONO']
            }
            
            # Construir lista de campos a leer
            fields_to_read = []
            field_indices = {}
            
            for field_key, possible_names in field_mapping.items():
                for name in possible_names:
                    if name.upper() in available_columns:
                        # Usar corchetes si el nombre tiene espacios
                        if ' ' in name:
                            fields_to_read.append(f'[{name}]')
                        else:
                            fields_to_read.append(name)
                        field_indices[field_key] = len(fields_to_read) - 1
                        break
            
            if not fields_to_read:
                return False, f"No se encontraron campos reconocidos en la tabla '{table_name}'"
            
            # Construir query
            query = f"SELECT {', '.join(fields_to_read)} FROM [{table_name}]"
            print(f"[IMPORTADOR] Query: {query}")
            
            cursor.execute(query)
            rows = cursor.fetchall()
            afiliados = []
            
            for row in rows:
                # Crear diccionario con valores por defecto
                afiliado = {
                    'codigo': '',
                    'folio': '',
                    'nombres': '',
                    'apellidos': '',
                    'fecha_nacimiento': None,
                    'carnet_id': '',
                    'sexo': '',
                    'edad': None,
                    'lugar_nacimiento': '',
                    'nacionalidad': '',
                    'ciudadania': '',
                    'hijo_de': '',
                    'locacion': '',
                    'direccion': '',
                    'reparto': '',
                    'telefono': '',
                    'area': '',
                    'cuota': None,
                    'estado_civil': '',
                    'jefe_nucleo': '',
                    'no_hijos': None,
                    'conviventes': '',
                    'no_personas_dep': None,
                    'org_rev': '',
                    'limitacion': '',
                    'limitacion_cod': '',
                    'nivel_ambulacion': '',
                    'ambulacion_cod': '',
                    'causa': '',
                    'discap_asociada': '',
                    'ocupacion': '',
                    'centro_trabajo': '',
                    'ingreso_mensual': None,
                    'grado_escolar': '',
                    'especialidad': '',
                    'fecha_ingreso': None,
                    'fecha_alta': None,
                    'fecha_baja': None,
                    'motivo_baja': '',
                    'tipo_telefono': ''
                }
                
                # Llenar solo los campos que existen
                for field_key, idx in field_indices.items():
                    try:
                        value = row[idx]
                        if value is not None:
                            # Conversión según tipo de campo
                            if field_key in ['edad', 'no_hijos', 'no_personas_dep']:
                                afiliado[field_key] = int(value) if value else None
                            elif field_key in ['cuota', 'ingreso_mensual']:
                                afiliado[field_key] = float(value) if value else None
                            elif field_key in ['fecha_nacimiento', 'fecha_ingreso', 'fecha_alta', 'fecha_baja']:
                                afiliado[field_key] = value  # Dejar como está (fecha)
                            else:
                                # Convertir a string manejando posibles errores de codificación
                                try:
                                    if isinstance(value, bytes):
                                        # Si es bytes, decodificar como cp1252
                                        afiliado[field_key] = value.decode('cp1252', errors='replace').strip()
                                    else:
                                        afiliado[field_key] = str(value).strip()
                                except Exception as conv_error:
                                    # Fallback: usar representación segura
                                    print(f"[IMPORTADOR] Warning: Error convirtiendo '{field_key}': {conv_error}")
                                    afiliado[field_key] = repr(value).strip()
                    except Exception as e:
                        print(f"[IMPORTADOR] Error procesando campo '{field_key}': {e}")
                        continue
                
                afiliados.append(afiliado)
            
            cursor.close()
            print(f"[IMPORTADOR] {len(afiliados)} registros leídos desde Access")
            return True, afiliados
            
        except pyodbc.Error as e:
            error_msg = f"Error al leer datos: {str(e)}"
            print(f"[IMPORTADOR] {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Error inesperado al leer: {str(e)}"
            print(f"[IMPORTADOR] {error_msg}")
            return False, error_msg
    
    def synchronize_with_postgresql(self, afiliados, progress_callback=None):
        """
        Sincroniza los afiliados con PostgreSQL de forma inteligente:
        - Inserta nuevos (estado='nuevo')
        - Detecta cambios de dirección (estado='cambio_direccion', guarda geom_anterior)
        - Actualiza datos literales de existentes
        - Elimina bajas (los que están en PG pero no en Access)
        
        Args:
            afiliados: lista de diccionarios con datos de afiliados
            progress_callback: función opcional(current, total, message) para reportar progreso
        
        Retorna: (bool, dict/str) - (éxito, estadísticas o mensaje de error)
        """
        config = load_db_config()
        if not config:
            return False, "No hay configuración de BD PostgreSQL"
        
        try:
            # Conectar a PostgreSQL
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                dbname=config['dbname']
            )
            cursor = conn.cursor()
            
            # Estadísticas
            nuevos = 0
            actualizados = 0
            cambios_direccion = 0
            eliminados = 0
            errores = 0
            
            # 1. Obtener todos los afiliados actuales en PostgreSQL
            cursor.execute("SELECT codigo, direccion, geom FROM afiliados WHERE codigo IS NOT NULL AND codigo != ''")
            afiliados_pg = {row[0]: {'direccion': row[1], 'geom': row[2]} for row in cursor.fetchall()}
            
            # 2. Procesar cada afiliado de Access
            codigos_access = set()
            total_afiliados = len(afiliados)
            
            for idx, afiliado in enumerate(afiliados, 1):
                codigo = afiliado.get('codigo', '').strip()
                if not codigo:
                    print(f"[SYNC] Afiliado sin código, omitiendo: {afiliado.get('nombres', 'N/A')}")
                    if progress_callback:
                        progress_callback(idx, total_afiliados, f"Omitiendo registro sin código ({idx}/{total_afiliados})")
                    continue
                
                codigos_access.add(codigo)
                
                # Reportar progreso
                if progress_callback:
                    nombre_completo = f"{afiliado.get('nombres', '')} {afiliado.get('apellidos', '')}".strip()
                    progress_callback(idx, total_afiliados, f"Procesando: {nombre_completo} ({idx}/{total_afiliados})")
                direccion_access = afiliado.get('direccion', '').strip()
                
                try:
                    # ¿Existe en PostgreSQL?
                    if codigo in afiliados_pg:
                        # AFILIADO EXISTENTE
                        direccion_pg = afiliados_pg[codigo]['direccion'] or ''
                        geom_pg = afiliados_pg[codigo]['geom']
                        
                        # ¿Cambió la dirección?
                        if direccion_access != direccion_pg:
                            # CAMBIO DE DIRECCIÓN
                            cursor.execute(
                                """
                                UPDATE afiliados 
                                SET nombres = %s, apellidos = %s, carnet_id = %s,
                                    sexo = %s, fecha_nacimiento = %s, edad = %s,
                                    lugar_nacimiento = %s, nacionalidad = %s, ciudadania = %s,
                                    hijo_de = %s, locacion = %s, direccion = %s, reparto = %s,
                                    telefono = %s, area = %s, cuota = %s, estado_civil = %s,
                                    jefe_nucleo = %s, no_hijos = %s, conviventes = %s,
                                    no_personas_dep = %s, org_rev = %s, limitacion = %s,
                                    limitacion_cod = %s, nivel_ambulacion = %s, ambulacion_cod = %s,
                                    causa = %s, discap_asociada = %s, ocupacion = %s,
                                    centro_trabajo = %s, ingreso_mensual = %s, grado_escolar = %s,
                                    especialidad = %s, fecha_ingreso = %s, fecha_alta = %s,
                                    fecha_baja = %s, motivo_baja = %s, tipo_telefono = %s,
                                    geom_anterior = geom, geom = NULL,
                                    estado = 'cambio_direccion', fecha_modificacion = CURRENT_TIMESTAMP
                                WHERE codigo = %s
                                """,
                                (afiliado['nombres'], afiliado['apellidos'], afiliado['carnet_id'],
                                 afiliado['sexo'], afiliado['fecha_nacimiento'], afiliado['edad'],
                                 afiliado['lugar_nacimiento'], afiliado['nacionalidad'], afiliado['ciudadania'],
                                 afiliado['hijo_de'], afiliado['locacion'], afiliado['direccion'], afiliado['reparto'],
                                 afiliado['telefono'], afiliado['area'], afiliado['cuota'], afiliado['estado_civil'],
                                 afiliado['jefe_nucleo'], afiliado['no_hijos'], afiliado['conviventes'],
                                 afiliado['no_personas_dep'], afiliado['org_rev'], afiliado['limitacion'],
                                 afiliado['limitacion_cod'], afiliado['nivel_ambulacion'], afiliado['ambulacion_cod'],
                                 afiliado['causa'], afiliado['discap_asociada'], afiliado['ocupacion'],
                                 afiliado['centro_trabajo'], afiliado['ingreso_mensual'], afiliado['grado_escolar'],
                                 afiliado['especialidad'], afiliado['fecha_ingreso'], afiliado['fecha_alta'],
                                 afiliado['fecha_baja'], afiliado['motivo_baja'], afiliado['tipo_telefono'],
                                 codigo)
                            )
                            cambios_direccion += 1
                            print(f"[SYNC] Cambio dirección: {codigo} - {afiliado['nombres']} {afiliado['apellidos']}")
                        else:
                            # ACTUALIZACIÓN NORMAL (solo datos literales)
                            cursor.execute(
                                """
                                UPDATE afiliados 
                                SET nombres = %s, apellidos = %s, carnet_id = %s,
                                    sexo = %s, fecha_nacimiento = %s, edad = %s,
                                    lugar_nacimiento = %s, nacionalidad = %s, ciudadania = %s,
                                    hijo_de = %s, locacion = %s, reparto = %s,
                                    telefono = %s, area = %s, cuota = %s, estado_civil = %s,
                                    jefe_nucleo = %s, no_hijos = %s, conviventes = %s,
                                    no_personas_dep = %s, org_rev = %s, limitacion = %s,
                                    limitacion_cod = %s, nivel_ambulacion = %s, ambulacion_cod = %s,
                                    causa = %s, discap_asociada = %s, ocupacion = %s,
                                    centro_trabajo = %s, ingreso_mensual = %s, grado_escolar = %s,
                                    especialidad = %s, fecha_ingreso = %s, fecha_alta = %s,
                                    fecha_baja = %s, motivo_baja = %s, tipo_telefono = %s,
                                    fecha_modificacion = CURRENT_TIMESTAMP
                                WHERE codigo = %s
                                """,
                                (afiliado['nombres'], afiliado['apellidos'], afiliado['carnet_id'],
                                 afiliado['sexo'], afiliado['fecha_nacimiento'], afiliado['edad'],
                                 afiliado['lugar_nacimiento'], afiliado['nacionalidad'], afiliado['ciudadania'],
                                 afiliado['hijo_de'], afiliado['locacion'], afiliado['reparto'],
                                 afiliado['telefono'], afiliado['area'], afiliado['cuota'], afiliado['estado_civil'],
                                 afiliado['jefe_nucleo'], afiliado['no_hijos'], afiliado['conviventes'],
                                 afiliado['no_personas_dep'], afiliado['org_rev'], afiliado['limitacion'],
                                 afiliado['limitacion_cod'], afiliado['nivel_ambulacion'], afiliado['ambulacion_cod'],
                                 afiliado['causa'], afiliado['discap_asociada'], afiliado['ocupacion'],
                                 afiliado['centro_trabajo'], afiliado['ingreso_mensual'], afiliado['grado_escolar'],
                                 afiliado['especialidad'], afiliado['fecha_ingreso'], afiliado['fecha_alta'],
                                 afiliado['fecha_baja'], afiliado['motivo_baja'], afiliado['tipo_telefono'],
                                 codigo)
                            )
                            actualizados += 1
                    else:
                        # AFILIADO NUEVO
                        cursor.execute(
                            """
                            INSERT INTO afiliados (
                                codigo, folio, nombres, apellidos, carnet_id,
                                sexo, fecha_nacimiento, edad, lugar_nacimiento, nacionalidad, ciudadania,
                                hijo_de, locacion, direccion, reparto, telefono, area, cuota,
                                estado_civil, jefe_nucleo, no_hijos, conviventes, no_personas_dep,
                                org_rev, limitacion, limitacion_cod, nivel_ambulacion, ambulacion_cod,
                                causa, discap_asociada, ocupacion, centro_trabajo, ingreso_mensual,
                                grado_escolar, especialidad, fecha_ingreso, fecha_alta, fecha_baja,
                                motivo_baja, tipo_telefono, estado, geom
                            ) VALUES (
                                %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s,
                                %s, %s, 'nuevo', NULL
                            )
                            """,
                            (afiliado['codigo'], afiliado['folio'], afiliado['nombres'], afiliado['apellidos'], afiliado['carnet_id'],
                             afiliado['sexo'], afiliado['fecha_nacimiento'], afiliado['edad'], afiliado['lugar_nacimiento'], 
                             afiliado['nacionalidad'], afiliado['ciudadania'],
                             afiliado['hijo_de'], afiliado['locacion'], afiliado['direccion'], afiliado['reparto'], 
                             afiliado['telefono'], afiliado['area'], afiliado['cuota'],
                             afiliado['estado_civil'], afiliado['jefe_nucleo'], afiliado['no_hijos'], afiliado['conviventes'], 
                             afiliado['no_personas_dep'],
                             afiliado['org_rev'], afiliado['limitacion'], afiliado['limitacion_cod'], afiliado['nivel_ambulacion'], 
                             afiliado['ambulacion_cod'],
                             afiliado['causa'], afiliado['discap_asociada'], afiliado['ocupacion'], afiliado['centro_trabajo'], 
                             afiliado['ingreso_mensual'],
                             afiliado['grado_escolar'], afiliado['especialidad'], afiliado['fecha_ingreso'], afiliado['fecha_alta'], 
                             afiliado['fecha_baja'],
                             afiliado['motivo_baja'], afiliado['tipo_telefono'])
                        )
                        nuevos += 1
                        print(f"[SYNC] Nuevo: {codigo} - {afiliado['nombres']} {afiliado['apellidos']}")
                        
                except Exception as e:
                    print(f"[SYNC] Error con afiliado {codigo}: {e}")
                    errores += 1
                    continue
            
            # 3. Eliminar bajas (los que están en PG pero NO en Access)
            if progress_callback:
                progress_callback(total_afiliados, total_afiliados, "Procesando eliminaciones...")
            
            codigos_pg = set(afiliados_pg.keys())
            codigos_eliminar = codigos_pg - codigos_access
            
            for codigo in codigos_eliminar:
                try:
                    cursor.execute("DELETE FROM afiliados WHERE codigo = %s", (codigo,))
                    eliminados += 1
                    print(f"[SYNC] Eliminado (baja): {codigo}")
                except Exception as e:
                    print(f"[SYNC] Error al eliminar {codigo}: {e}")
            
            # Commit final
            if progress_callback:
                progress_callback(total_afiliados, total_afiliados, "Guardando cambios en la base de datos...")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            stats = {
                'nuevos': nuevos,
                'actualizados': actualizados,
                'cambios_direccion': cambios_direccion,
                'eliminados': eliminados,
                'errores': errores,
                'total_procesados': len(afiliados)
            }
            
            print(f"[SYNC] Finalizado: {nuevos} nuevos, {actualizados} actualizados, "
                  f"{cambios_direccion} cambios dirección, {eliminados} eliminados, {errores} errores")
            
            return True, stats
            
        except Exception as e:
            error_msg = f"Error en sincronización: {str(e)}"
            print(f"[SYNC] {error_msg}")
            return False, error_msg
    
    def import_to_postgresql(self, afiliados):
        """
        Método legacy para compatibilidad (ahora usa synchronize_with_postgresql)
        """
        return self.synchronize_with_postgresql(afiliados)
    
    def close(self):
        """Cierra la conexión a Access"""
        if self.connection:
            self.connection.close()
            print("[IMPORTADOR] Conexión a Access cerrada")
    
    def import_full_process(self, table_name='ACLIFIM'):
        """
        Proceso completo de sincronización con Access
        Retorna: (bool, dict/str) - (éxito, estadísticas o mensaje)
        """
        # 1. Conectar a Access
        success, msg = self.connect_to_access()
        if not success:
            return False, msg
        
        # 2. Leer afiliados
        success, data = self.get_afiliados_from_access(table_name)
        if not success:
            self.close()
            return False, data
        
        afiliados = data
        if len(afiliados) == 0:
            self.close()
            return False, "No se encontraron registros en la tabla"
        
        # 3. Sincronizar con PostgreSQL
        success, result = self.synchronize_with_postgresql(afiliados)
        
        # 4. Cerrar conexión
        self.close()
        
        return success, result


def get_all_afiliados():
    """
    Obtiene TODOS los afiliados desde PostgreSQL con campos actualizados
    Retorna: list de dict con id, codigo, carnet_id, nombres, apellidos, direccion, estado, ubicado
    """
    config = load_db_config()
    if not config:
        print("[IMPORTADOR] No hay configuración de BD")
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
        
        # Obtener todos los afiliados con nuevos campos
        cursor.execute(
            """
            SELECT id, codigo, carnet_id, nombres, apellidos, direccion, estado,
                   CASE WHEN geom IS NOT NULL THEN 'Sí' ELSE 'No' END as ubicado
            FROM afiliados 
            ORDER BY nombres, apellidos
            """
        )
        
        rows = cursor.fetchall()
        afiliados = []
        
        for row in rows:
            afiliados.append({
                'id': row[0],
                'codigo': row[1] or '',
                'carnet_id': row[2] or '',
                'nombres': row[3] or '',
                'apellidos': row[4] or '',
                'direccion': row[5] or '',
                'estado': row[6] or 'normal',
                'ubicado': row[7]
            })
        
        cursor.close()
        conn.close()
        
        print(f"[IMPORTADOR] {len(afiliados)} afiliados encontrados")
        return afiliados
        
    except Exception as e:
        print(f"[IMPORTADOR] Error al obtener afiliados: {e}")
        return []


def get_afiliados_sin_coordenadas():
    """
    Obtiene la lista de afiliados sin coordenadas desde PostgreSQL
    Retorna: list de dict con id, codigo, carnet_id, nombres, apellidos, direccion, estado
    """
    config = load_db_config()
    if not config:
        print("[IMPORTADOR] No hay configuración de BD")
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
        
        # Buscar afiliados sin coordenadas
        cursor.execute(
            """
            SELECT id, codigo, carnet_id, nombres, apellidos, direccion, estado
            FROM afiliados 
            WHERE geom IS NULL
            ORDER BY 
                CASE 
                    WHEN estado = 'cambio_direccion' THEN 1
                    WHEN estado = 'nuevo' THEN 2
                    ELSE 3
                END,
                nombres, apellidos
            """
        )
        
        rows = cursor.fetchall()
        afiliados = []
        
        for row in rows:
            afiliados.append({
                'id': row[0],
                'codigo': row[1] or '',
                'carnet_id': row[2] or '',
                'nombres': row[3] or '',
                'apellidos': row[4] or '',
                'direccion': row[5] or '',
                'estado': row[6] or 'normal'
            })
        
        cursor.close()
        conn.close()
        
        print(f"[IMPORTADOR] {len(afiliados)} afiliados sin coordenadas encontrados")
        return afiliados
        
    except Exception as e:
        print(f"[IMPORTADOR] Error al obtener afiliados sin coordenadas: {e}")
        return []


def update_afiliado_coordinates(afiliado_id, point):
    """
    Actualiza las coordenadas de un afiliado y cambia su estado a 'normal'
    Si tenía geom_anterior (cambio de dirección), lo elimina del mapa
    
    Args:
        afiliado_id: ID del afiliado en la BD
        point: QgsPointXY con las coordenadas
    
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
        
        # Actualizar geometría, estado y limpiar geom_anterior
        cursor.execute(
            """
            UPDATE afiliados 
            SET geom = ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                estado = 'normal',
                geom_anterior = NULL,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (point.x(), point.y(), afiliado_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"[IMPORTADOR] Coordenadas actualizadas para afiliado ID {afiliado_id}")
        return True, "Coordenadas actualizadas exitosamente"
        
    except Exception as e:
        error_msg = f"Error al actualizar coordenadas: {str(e)}"
        print(f"[IMPORTADOR] {error_msg}")
        return False, error_msg


def get_afiliado_by_id(afiliado_id):
    """
    Obtiene los detalles completos de un afiliado por ID
    Retorna: dict con todos los campos del afiliado o None
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
            SELECT 
                id, codigo, folio, nombres, apellidos, carnet_id,
                sexo, fecha_nacimiento, edad, lugar_nacimiento, nacionalidad, ciudadania,
                hijo_de, locacion, direccion, reparto, telefono, area, cuota,
                estado_civil, jefe_nucleo, no_hijos, conviventes, no_personas_dep,
                org_rev, limitacion, limitacion_cod, nivel_ambulacion, ambulacion_cod,
                causa, discap_asociada, ocupacion, centro_trabajo, ingreso_mensual,
                grado_escolar, especialidad, fecha_ingreso, fecha_alta, fecha_baja,
                motivo_baja, tipo_telefono, estado, fecha_creacion, fecha_modificacion,
                ST_X(geom) as lon, ST_Y(geom) as lat
            FROM afiliados 
            WHERE id = %s
            """,
            (afiliado_id,)
        )
        
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            conn.close()
            return None
        
        afiliado = {
            'id': row[0],
            'codigo': row[1],
            'folio': row[2],
            'nombres': row[3],
            'apellidos': row[4],
            'carnet_id': row[5],
            'sexo': row[6],
            'fecha_nacimiento': row[7],
            'edad': row[8],
            'lugar_nacimiento': row[9],
            'nacionalidad': row[10],
            'ciudadania': row[11],
            'hijo_de': row[12],
            'locacion': row[13],
            'direccion': row[14],
            'reparto': row[15],
            'telefono': row[16],
            'area': row[17],
            'cuota': row[18],
            'estado_civil': row[19],
            'jefe_nucleo': row[20],
            'no_hijos': row[21],
            'conviventes': row[22],
            'no_personas_dep': row[23],
            'org_rev': row[24],
            'limitacion': row[25],
            'limitacion_cod': row[26],
            'nivel_ambulacion': row[27],
            'ambulacion_cod': row[28],
            'causa': row[29],
            'discap_asociada': row[30],
            'ocupacion': row[31],
            'centro_trabajo': row[32],
            'ingreso_mensual': row[33],
            'grado_escolar': row[34],
            'especialidad': row[35],
            'fecha_ingreso': row[36],
            'fecha_alta': row[37],
            'fecha_baja': row[38],
            'motivo_baja': row[39],
            'tipo_telefono': row[40],
            'estado': row[41],
            'fecha_creacion': row[42],
            'fecha_modificacion': row[43],
            'lon': row[44],
            'lat': row[45]
        }
        
        cursor.close()
        conn.close()
        
        return afiliado
        
    except Exception as e:
        print(f"[IMPORTADOR] Error al obtener afiliado: {e}")
        return None


def search_afiliados(nombre=None, codigo=None, carnet_id=None, apellido=None, fecha_desde=None, fecha_hasta=None):
    """
    Busca afiliados con filtros múltiples
    Retorna: list de dict con id, codigo, carnet_id, nombres, apellidos, direccion
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
        
        # Construir query dinámica
        query = """
            SELECT id, codigo, carnet_id, nombres, apellidos, direccion, estado
            FROM afiliados 
            WHERE 1=1
        """
        params = []
        
        if nombre:
            query += " AND LOWER(nombres) LIKE LOWER(%s)"
            params.append(f'%{nombre}%')
        
        if apellido:
            query += " AND LOWER(apellidos) LIKE LOWER(%s)"
            params.append(f'%{apellido}%')
        
        if codigo:
            query += " AND codigo LIKE %s"
            params.append(f'%{codigo}%')
        
        if carnet_id:
            query += " AND carnet_id LIKE %s"
            params.append(f'%{carnet_id}%')
        
        if fecha_desde:
            query += " AND fecha_ingreso >= %s"
            params.append(fecha_desde)
        
        if fecha_hasta:
            query += " AND fecha_ingreso <= %s"
            params.append(fecha_hasta)
        
        query += " ORDER BY nombres, apellidos"
        
        cursor.execute(query, tuple(params))
        
        rows = cursor.fetchall()
        afiliados = []
        
        for row in rows:
            afiliados.append({
                'id': row[0],
                'codigo': row[1] or '',
                'carnet_id': row[2] or '',
                'nombres': row[3] or '',
                'apellidos': row[4] or '',
                'direccion': row[5] or '',
                'estado': row[6] or 'normal'
            })
        
        cursor.close()
        conn.close()
        
        print(f"[IMPORTADOR] {len(afiliados)} afiliados encontrados en búsqueda")
        return afiliados
        
    except Exception as e:
        print(f"[IMPORTADOR] Error en búsqueda: {e}")
        return []

