"""
Utilidades para migración de capas de bases de datos antiguas
"""
from qgis.core import QgsProject, QgsDataSourceUri, QgsVectorLayer
from qgis.PyQt.QtWidgets import QMessageBox
import json
import os


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


def find_afiliados_layer_with_different_db():
    """
    Busca si existe una capa 'Afiliados' conectada a una BD diferente a la configurada
    Retorna: (layer, old_dbname) o (None, None)
    """
    config = load_db_config()
    if not config:
        return None, None
    
    target_dbname = config['dbname']
    
    # Buscar capa "Afiliados"
    for layer in QgsProject.instance().mapLayers().values():
        if "Afiliados" in layer.name() or "afiliados" in layer.name().lower():
            # Verificar si es una capa PostGIS
            if layer.providerType() == "postgres":
                source = layer.dataProvider().dataSourceUri()
                # Extraer el nombre de la BD del URI
                try:
                    uri = QgsDataSourceUri(source)
                    current_dbname = uri.database()
                    
                    # Si es diferente a la configurada
                    if current_dbname != target_dbname:
                        print(f"[MIGRACIÓN] Capa '{layer.name()}' encontrada conectada a '{current_dbname}'")
                        return layer, current_dbname
                except:
                    pass
    
    return None, None


def migrate_afiliados_layer(iface, old_layer):
    """
    Reemplaza la capa antigua de Afiliados por una nueva conectada a la BD configurada
    
    Args:
        iface: Interface de QGIS
        old_layer: Capa antigua a reemplazar
    
    Retorna: (bool, str) - (éxito, mensaje)
    """
    config = load_db_config()
    if not config:
        return False, "No hay configuración de BD"
    
    try:
        # Crear URI de conexión a la nueva BD
        uri = QgsDataSourceUri()
        uri.setConnection(
            config['host'],
            config['port'],
            config['dbname'],
            config['user'],
            config['password']
        )
        uri.setDataSource("public", "afiliados", "geom", "", "id")
        
        # Crear nueva capa
        new_layer = QgsVectorLayer(uri.uri(), "Afiliados", "postgres")
        
        if not new_layer.isValid():
            return False, "No se pudo conectar a la nueva BD. Verifica la configuración."
        
        # Obtener el índice de la capa antigua en el TOC (Table of Contents)
        root = QgsProject.instance().layerTreeRoot()
        old_node = root.findLayer(old_layer.id())
        insert_index = 0
        
        if old_node:
            parent = old_node.parent()
            insert_index = parent.children().index(old_node)
        
        # Eliminar la capa antigua
        old_layer_id = old_layer.id()
        QgsProject.instance().removeMapLayer(old_layer_id)
        print(f"[MIGRACIÓN] Capa antigua eliminada")
        
        # Agregar la nueva capa en la misma posición
        QgsProject.instance().addMapLayer(new_layer, False)
        root.insertLayer(insert_index, new_layer)
        print(f"[MIGRACIÓN] Nueva capa agregada conectada a '{config['dbname']}'")
        
        # Mensaje de éxito
        msg = f"Capa 'Afiliados' actualizada exitosamente a la BD '{config['dbname']}'"
        iface.messageBar().pushMessage(
            "ACLIFIM",
            msg,
            level=3,  # Success
            duration=5
        )
        
        return True, msg
        
    except Exception as e:
        error_msg = f"Error durante la migración: {str(e)}"
        print(f"[MIGRACIÓN] {error_msg}")
        return False, error_msg


def check_and_migrate_if_needed(iface):
    """
    Verifica si hay una capa de Afiliados con BD diferente y pregunta si migrar
    
    Args:
        iface: Interface de QGIS
    
    Retorna: bool - True si se migró o no fue necesario, False si se canceló
    """
    old_layer, old_dbname = find_afiliados_layer_with_different_db()
    
    if old_layer:
        config = load_db_config()
        new_dbname = config['dbname'] if config else 'aclifim_db'
        
        # Preguntar al usuario
        reply = QMessageBox.question(
            None,
            "Actualizar conexión de capa",
            f"Se detectó que la capa 'Afiliados' está conectada a la base de datos '{old_dbname}'.\n\n"
            f"¿Deseas actualizarla para que use la nueva base de datos '{new_dbname}'?\n\n"
            f"Nota: Los datos permanecerán en sus respectivas bases de datos, "
            f"solo se actualiza la conexión en este proyecto.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            success, msg = migrate_afiliados_layer(iface, old_layer)
            
            if success:
                QMessageBox.information(
                    None,
                    "Migración exitosa",
                    f"{msg}\n\nGuarda el proyecto (Ctrl+S) para conservar los cambios."
                )
                return True
            else:
                QMessageBox.warning(
                    None,
                    "Error en migración",
                    msg
                )
                return False
        else:
            print("[MIGRACIÓN] Usuario canceló la migración")
            return False
    
    return True  # No hay nada que migrar
