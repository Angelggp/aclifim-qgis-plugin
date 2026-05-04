from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsDataSourceUri
)
from qgis.gui import QgsMapToolEmitPoint
import os
import json


def load_db_config():
    """Carga la configuración de la base de datos"""
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db_config.json')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            return None
    return None


def get_or_create_layer():
    layer_name = "Afiliados"
    
    # Cargar configuración de BD
    config = load_db_config()
    
    # Buscar si ya existe la capa en el proyecto
    for layer in QgsProject.instance().mapLayers().values():
        if layer.name() == layer_name:
            # Verificar que sea una capa válida y de la BD correcta
            if config and layer.providerType() == "postgres":
                # Obtener la fuente de datos de la capa
                source = layer.dataProvider().dataSourceUri()
                # Verificar que sea de nuestra BD
                if config['dbname'] in source:
                    print(f"[PLUGIN] Capa encontrada: {layer_name} (PostGIS)")
                    return layer
                else:
                    print(f"[PLUGIN] Capa '{layer_name}' encontrada pero conectada a otra BD, eliminando...")
                    QgsProject.instance().removeMapLayer(layer.id())
                    break
            elif not config and layer.providerType() == "memory":
                print(f"[PLUGIN] Capa encontrada: {layer_name} (Memoria)")
                return layer
            else:
                # Capa con mismo nombre pero tipo incorrecto
                print(f"[PLUGIN] Capa '{layer_name}' de tipo incorrecto, eliminando...")
                QgsProject.instance().removeMapLayer(layer.id())
                break
    
    # Intentar cargar desde PostGIS
    if config:
        print("[PLUGIN] Configuración de BD encontrada, intentando conectar a PostGIS...")
        try:
            # Crear URI de conexión
            uri = QgsDataSourceUri()
            uri.setConnection(
                config['host'],
                config['port'],
                config['dbname'],
                config['user'],
                config['password']
            )
            uri.setDataSource("public", "afiliados", "geom", "", "id")
            
            # Crear capa desde PostGIS
            layer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
            
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                print(f"[PLUGIN] Capa '{layer_name}' cargada desde PostGIS ({config['dbname']})")
                print(f"[PLUGIN] Fuente de datos: {layer.dataProvider().dataSourceUri()}")
                return layer
            else:
                print("[PLUGIN] Error al cargar capa desde PostGIS, usando capa de memoria")
        except Exception as e:
            print(f"[PLUGIN] Excepción al conectar a PostGIS: {e}, usando capa de memoria")
    else:
        print("[PLUGIN] No hay configuración de BD, usando capa de memoria")
    
    # Fallback: crear capa de memoria
    layer = QgsVectorLayer("Point?crs=EPSG:4326", f"{layer_name} (Temporal)", "memory")
    provider = layer.dataProvider()
    
    # Añadir campos para atributos
    from qgis.core import QgsField
    from PyQt5.QtCore import QVariant
    provider.addAttributes([
        QgsField("nombre", QVariant.String),
        QgsField("direccion", QVariant.String),
        QgsField("municipio", QVariant.String),
    ])
    layer.updateFields()
    QgsProject.instance().addMapLayer(layer)
    print(f"[PLUGIN] Capa '{layer_name} (Temporal)' creada en memoria")
    return layer


def add_test_point(iface):
    layer = get_or_create_layer()
    point = QgsPointXY(-80.456, 22.149)
    feature = QgsFeature()
    feature.setGeometry(QgsGeometry.fromPointXY(point))
    feature.setAttributes([
        "Juan Pérez",
        "Calle 1",
        "Cienfuegos"
    ])
    layer.dataProvider().addFeatures([feature])
    layer.updateExtents()

# --- NUEVO: Herramienta para click en el mapa ---
class MapClickTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, callback):
        super().__init__(canvas)
        self.callback = callback
        print("[PLUGIN] MapClickTool inicializado")

    def canvasReleaseEvent(self, event):
        print("[PLUGIN] Click detectado en el mapa")
        point = self.toMapCoordinates(event.pos())
        print(f"[PLUGIN] Coordenadas: {point.x()}, {point.y()}")
        self.callback(point)

def add_point_with_data(point, data):
    """
    Agrega un punto a la capa con los datos proporcionados
    
    Args:
        point: QgsPointXY con las coordenadas (en CRS del canvas)
        data: dict con los datos del afiliado (nombre, direccion, municipio)
    """
    print(f"\n[PLUGIN] === Iniciando add_point_with_data ===")
    print(f"[PLUGIN] Coordenadas recibidas (canvas): {point.x()}, {point.y()}")
    print(f"[PLUGIN] Datos recibidos: {data}")
    
    layer = get_or_create_layer()
    print(f"[PLUGIN] Capa obtenida: {layer.name()}")
    print(f"[PLUGIN] CRS de la capa: {layer.crs().authid()}")
    
    # IMPORTANTE: Transformar coordenadas del canvas al CRS de la capa
    from qgis.utils import iface
    canvas_crs = iface.mapCanvas().mapSettings().destinationCrs()
    layer_crs = layer.crs()
    print(f"[PLUGIN] CRS del canvas: {canvas_crs.authid()}")
    
    # Transformar punto si los CRS son diferentes
    if canvas_crs != layer_crs:
        transform = QgsCoordinateTransform(canvas_crs, layer_crs, QgsProject.instance())
        transformed_point = transform.transform(point)
        print(f"[PLUGIN] Coordenadas transformadas a {layer_crs.authid()}: {transformed_point.x()}, {transformed_point.y()}")
    else:
        transformed_point = point
        print(f"[PLUGIN] No se requiere transformación (mismo CRS)")
    
    print(f"[PLUGIN] Campos de la capa: {[field.name() for field in layer.fields()]}")
    print(f"[PLUGIN] Features actuales en capa: {layer.featureCount()}")
    
    # Crear feature con los campos de la capa
    feature = QgsFeature(layer.fields())
    print(f"[PLUGIN] Feature creado, tiene {len(feature.fields())} campos")
    
    # Asignar geometría con las coordenadas transformadas
    geom = QgsGeometry.fromPointXY(transformed_point)
    feature.setGeometry(geom)
    print(f"[PLUGIN] Geometría asignada: válida={not geom.isNull()}")
    
    # Asignar atributos según el tipo de capa
    if layer.providerType() == "postgres":
        # Para PostGIS: asignar solo los campos NO autogenerados
        # Encontrar los índices de los campos
        fields = layer.fields()
        field_map = {field.name(): idx for idx, field in enumerate(fields)}
        
        # Crear lista de atributos con todos los campos
        attrs = [None] * len(fields)
        
        # Asignar solo los campos que tenemos datos (sin id ni fecha_creacion)
        if 'nombre' in field_map:
            attrs[field_map['nombre']] = data.get('nombre', '')
        if 'direccion' in field_map:
            attrs[field_map['direccion']] = data.get('direccion', '')
        if 'municipio' in field_map:
            attrs[field_map['municipio']] = data.get('municipio', '')
        
        print(f"[PLUGIN] Mapa de campos: {field_map}")
        print(f"[PLUGIN] Atributos asignados (PostGIS): {attrs}")
    else:
        # Para capas de memoria
        attrs = [
            data.get('nombre', ''),
            data.get('direccion', ''),
            data.get('municipio', '')
        ]
        print(f"[PLUGIN] Atributos asignados (memoria): {attrs}")
    
    feature.setAttributes(attrs)
    
    # Agregar el feature según el tipo de capa
    print(f"[PLUGIN] Intentando agregar feature...")
    
    if layer.providerType() == "postgres":
        # Para PostGIS: usar startEditing/addFeature/commitChanges
        print("[PLUGIN] Usando método de edición para PostGIS")
        layer.startEditing()
        success = layer.addFeature(feature)
        
        if success:
            if layer.commitChanges():
                print("[PLUGIN] Cambios confirmados (commit)")
                # Actualizar extensiones de la capa
                layer.updateExtents()
                
                # Refrescar la capa
                layer.triggerRepaint()
                
                # Forzar refresco del canvas
                from qgis.utils import iface
                iface.mapCanvas().refresh()
                
                print(f"[PLUGIN] Total features en capa AHORA: {layer.featureCount()}")
                print(f"[PLUGIN] === Punto agregado exitosamente ===")
                return True
            else:
                errors = layer.commitErrors()
                print(f"[PLUGIN] *** ERROR en commit: {errors}")
                layer.rollBack()
                return False
        else:
            print("[PLUGIN] *** ERROR: addFeature retornó False ***")
            layer.rollBack()
            return False
    else:
        # Para capas de memoria: usar dataProvider directamente
        print("[PLUGIN] Usando dataProvider para capa de memoria")
        success, features = layer.dataProvider().addFeatures([feature])
        print(f"[PLUGIN] Resultado de addFeatures: success={success}")
        
        if success:
            print(f"[PLUGIN] Features agregados: {len(features)}")
            
            # Actualizar extensiones de la capa
            layer.updateExtents()
            print(f"[PLUGIN] Extensiones actualizadas")
            
            # Refrescar la capa
            layer.triggerRepaint()
            print(f"[PLUGIN] triggerRepaint() llamado")
            
            # Forzar refresco del canvas
            from qgis.utils import iface
            iface.mapCanvas().refresh()
            print(f"[PLUGIN] Canvas refrescado")
            
            print(f"[PLUGIN] Total features en capa AHORA: {layer.featureCount()}")
            print(f"[PLUGIN] === Punto agregado exitosamente ===")
            return True
        else:
            print("[PLUGIN] *** ERROR: addFeatures retornó False ***")
            print(f"[PLUGIN] Capacidades del provider: {layer.dataProvider().capabilitiesString()}")
            return False


def get_or_create_centros_layer():
    """
    Obtiene o crea la capa de centros de interés conectada a PostGIS
    """
    layer_name = "Centros de Interés"
    
    # Cargar configuración de BD
    config = load_db_config()
    
    # Buscar si ya existe la capa en el proyecto
    for layer in QgsProject.instance().mapLayers().values():
        if layer.name() == layer_name:
            # Verificar que sea una capa válida y de la BD correcta
            if config and layer.providerType() == "postgres":
                # Obtener la fuente de datos de la capa
                source = layer.dataProvider().dataSourceUri()
                # Verificar que sea de nuestra BD
                if config['dbname'] in source:
                    print(f"[PLUGIN] Capa encontrada: {layer_name} (PostGIS)")
                    return layer
                else:
                    print(f"[PLUGIN] Capa '{layer_name}' encontrada pero conectada a otra BD, eliminando...")
                    QgsProject.instance().removeMapLayer(layer.id())
                    break
            elif not config and layer.providerType() == "memory":
                print(f"[PLUGIN] Capa encontrada: {layer_name} (Memoria)")
                return layer
            else:
                # Capa con mismo nombre pero tipo incorrecto
                print(f"[PLUGIN] Capa '{layer_name}' de tipo incorrecto, eliminando...")
                QgsProject.instance().removeMapLayer(layer.id())
                break
    
    # Intentar cargar desde PostGIS
    if config:
        print("[PLUGIN] Configuración de BD encontrada, intentando conectar centros a PostGIS...")
        try:
            # Crear URI de conexión
            uri = QgsDataSourceUri()
            uri.setConnection(
                config['host'],
                config['port'],
                config['dbname'],
                config['user'],
                config['password']
            )
            uri.setDataSource("public", "centros_interes", "geom", "", "id")
            
            # Crear capa desde PostGIS
            layer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
            
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                print(f"[PLUGIN] Capa '{layer_name}' cargada desde PostGIS ({config['dbname']})")
                
                # Aplicar estilo diferente para distinguir de afiliados
                from qgis.core import QgsMarkerSymbol, QgsSingleSymbolRenderer
                from qgis.PyQt.QtGui import QColor
                
                symbol = QgsMarkerSymbol.createSimple({
                    'name': 'square',
                    'color': '255,140,0',  # Naranja
                    'size': '4'
                })
                renderer = QgsSingleSymbolRenderer(symbol)
                layer.setRenderer(renderer)
                layer.triggerRepaint()
                
                return layer
            else:
                print("[PLUGIN] Error al cargar capa de centros desde PostGIS")
        except Exception as e:
            print(f"[PLUGIN] Excepción al conectar centros a PostGIS: {e}")
    else:
        print("[PLUGIN] No hay configuración de BD para centros")
    
    return None