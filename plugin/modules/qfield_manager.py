"""
Módulo de integración con QField.

Permite exportar afiliados a GeoPackage (.gpkg) para trabajar en campo
con QField, y luego importar los cambios de coordenadas de vuelta a PostgreSQL.

Flujo típico:
  1. Exportar afiliados sin ubicar a un .gpkg
  2. Copiar el .gpkg al dispositivo móvil con QField
  3. En el campo, abrir el .gpkg en QField y asignar coordenadas a cada afiliado
  4. Copiar el .gpkg modificado de vuelta al PC
  5. Importar el .gpkg modificado: el plugin actualiza las coordenadas en la BD
"""
import os


def exportar_afiliados_gpkg(filepath, solo_sin_ubicar=False):
    """
    Exporta afiliados a un GeoPackage para usar en QField.

    Args:
        filepath (str): Ruta del archivo .gpkg a crear.
        solo_sin_ubicar (bool): Si True, exporta solo afiliados sin coordenadas.

    Returns:
        tuple: (éxito: bool, mensaje: str, cantidad: int)
    """
    from qgis.core import (
        QgsVectorLayer, QgsVectorFileWriter, QgsField,
        QgsFeature, QgsGeometry, QgsPointXY,
        QgsCoordinateReferenceSystem, QgsProject
    )
    from qgis.PyQt.QtCore import QVariant
    from .access_importer import _connect_postgresql

    try:
        conn = _connect_postgresql()
        cursor = conn.cursor()

        if solo_sin_ubicar:
            cursor.execute("""
                SELECT id, nombres, apellidos, carnet_id, codigo, direccion,
                       estado, limitacion, nivel_ambulacion,
                       ST_X(geom) AS lon, ST_Y(geom) AS lat
                FROM afiliados
                WHERE geom IS NULL
                   OR estado IN ('nuevo', 'cambio_direccion')
                ORDER BY apellidos, nombres
            """)
        else:
            cursor.execute("""
                SELECT id, nombres, apellidos, carnet_id, codigo, direccion,
                       estado, limitacion, nivel_ambulacion,
                       ST_X(geom) AS lon, ST_Y(geom) AS lat
                FROM afiliados
                ORDER BY apellidos, nombres
            """)

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            return False, "No hay afiliados para exportar.", 0

        # Crear capa de memoria con geometría de puntos en WGS84
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "afiliados_qfield", "memory")
        provider = layer.dataProvider()

        provider.addAttributes([
            QgsField("id",         QVariant.Int),
            QgsField("nombres",    QVariant.String),
            QgsField("apellidos",  QVariant.String),
            QgsField("carnet_id",  QVariant.String),
            QgsField("codigo",     QVariant.String),
            QgsField("direccion",  QVariant.String),
            QgsField("estado",     QVariant.String),
            QgsField("limitacion", QVariant.String),
            QgsField("ambulacion", QVariant.String),
        ])
        layer.updateFields()

        features = []
        for row in rows:
            (afil_id, nombres, apellidos, carnet_id, codigo, direccion,
             estado, limitacion, ambulacion, lon, lat) = row

            feat = QgsFeature()
            feat.setAttributes([
                int(afil_id) if afil_id is not None else None,
                nombres    or '',
                apellidos  or '',
                carnet_id  or '',
                codigo     or '',
                direccion  or '',
                estado     or '',
                str(limitacion)  if limitacion  is not None else '',
                str(ambulacion)  if ambulacion  is not None else '',
            ])

            if lon is not None and lat is not None:
                feat.setGeometry(QgsGeometry.fromPointXY(
                    QgsPointXY(float(lon), float(lat))
                ))
            # Si no tiene coords la geometría queda nula — QField la mostrará
            # como punto pendiente de ubicar

            features.append(feat)

        provider.addFeatures(features)
        layer.updateExtents()

        # Escribir GeoPackage
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName   = "GPKG"
        options.fileEncoding = "UTF-8"

        result = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer,
            filepath,
            QgsProject.instance().transformContext(),
            options
        )
        # writeAsVectorFormatV3 returns (error_code, error_message, ...) — unpack safely
        error_code = result[0] if isinstance(result, tuple) else result
        error_msg  = result[1] if isinstance(result, tuple) and len(result) > 1 else ""

        if error_code != QgsVectorFileWriter.NoError:
            return False, f"Error al crear el GeoPackage: {error_msg}", 0

        return True, "GeoPackage creado correctamente.", len(features)

    except Exception as e:
        return False, f"Error inesperado: {str(e)}", 0


def leer_cambios_gpkg(filepath):
    """
    Lee un GeoPackage modificado en QField y detecta afiliados con coordenadas
    nuevas o actualizadas.

    Returns:
        tuple: (éxito: bool, mensaje: str, cambios: list[dict])
            cambios: [{'id', 'nombres', 'apellidos', 'lon', 'lat'}, ...]
    """
    from qgis.core import QgsVectorLayer

    if not os.path.exists(filepath):
        return False, "El archivo no existe.", []

    try:
        # Intentar cargar la capa 'afiliados_qfield' dentro del GPKG
        layer = QgsVectorLayer(
            f"{filepath}|layername=afiliados_qfield",
            "gpkg_temp",
            "ogr"
        )
        if not layer.isValid():
            # Fallback: cargar sin especificar nombre de capa
            layer = QgsVectorLayer(filepath, "gpkg_temp", "ogr")

        if not layer.isValid():
            return False, "No se pudo leer el archivo. Verifica que sea un GeoPackage válido.", []

        cambios = []
        for feature in layer.getFeatures():
            geom = feature.geometry()
            if geom is None or geom.isNull():
                continue

            point = geom.asPoint()
            # Ignorar coordenada nula (0,0)
            if abs(point.x()) < 0.0001 and abs(point.y()) < 0.0001:
                continue

            afil_id = feature['id']
            if afil_id is None:
                continue

            cambios.append({
                'id':       int(afil_id),
                'nombres':  (feature['nombres']   or '').strip(),
                'apellidos':(feature['apellidos']  or '').strip(),
                'lon':      float(point.x()),
                'lat':      float(point.y()),
            })

        return True, f"{len(cambios)} afiliados con coordenadas encontrados.", cambios

    except Exception as e:
        return False, f"Error al leer el archivo: {str(e)}", []


def aplicar_cambios_gpkg(cambios):
    """
    Aplica la lista de cambios de coordenadas a la base de datos PostgreSQL.

    Args:
        cambios (list[dict]): cada elemento tiene 'id', 'lon', 'lat'

    Returns:
        tuple: (actualizados: int, errores: int, mensajes_error: list[str])
    """
    from qgis.core import QgsPointXY
    from .access_importer import update_afiliado_coordinates

    actualizados = 0
    errores      = 0
    msgs         = []

    for cambio in cambios:
        try:
            point = QgsPointXY(cambio['lon'], cambio['lat'])
            ok, msg = update_afiliado_coordinates(cambio['id'], point)
            if ok:
                actualizados += 1
            else:
                errores += 1
                msgs.append(f"ID {cambio['id']}: {msg}")
        except Exception as e:
            errores += 1
            msgs.append(f"ID {cambio['id']}: {str(e)}")

    return actualizados, errores, msgs
