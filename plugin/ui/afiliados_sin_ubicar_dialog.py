"""
Diálogo para gestionar afiliados sin coordenadas
"""
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView
)
from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsRubberBand
from qgis.core import QgsWkbTypes, QgsCoordinateTransform, QgsProject, QgsCoordinateReferenceSystem
from qgis.PyQt.QtGui import QColor

from ..modules.access_importer import get_afiliados_sin_coordenadas, update_afiliado_coordinates
from ..modules.map_tools import MapClickTool


class AfiliadosSinUbicarDialog(QDialog):
    """Diálogo que muestra afiliados sin coordenadas y permite ubicarlos"""
    
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.afiliados = []
        self.selected_afiliado_id = None
        self.map_tool = None
        self.rubber_band = None
        
        self.setWindowTitle("Afiliados Sin Ubicar")
        self.resize(700, 500)
        
        self.setup_ui()
        self.load_afiliados()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout()
        
        # Etiqueta de información
        self.info_label = QLabel("Selecciona un afiliado y haz click en 'Ubicar en Mapa'")
        layout.addWidget(self.info_label)
        
        # Tabla de afiliados
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Dirección", "Municipio"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Ajustar columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.btn_ubicar = QPushButton("Ubicar en Mapa")
        self.btn_ubicar.clicked.connect(self.ubicar_afiliado)
        self.btn_ubicar.setEnabled(False)
        buttons_layout.addWidget(self.btn_ubicar)
        
        self.btn_refresh = QPushButton("Actualizar Lista")
        self.btn_refresh.clicked.connect(self.load_afiliados)
        buttons_layout.addWidget(self.btn_refresh)
        
        self.btn_close = QPushButton("Cerrar")
        self.btn_close.clicked.connect(self.close)
        buttons_layout.addWidget(self.btn_close)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Conectar señal de selección
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_afiliados(self):
        """Carga la lista de afiliados sin coordenadas"""
        self.afiliados = get_afiliados_sin_coordenadas()
        self.table.setRowCount(0)
        
        if len(self.afiliados) == 0:
            self.info_label.setText("Todos los afiliados tienen coordenadas asignadas")
            self.btn_ubicar.setEnabled(False)
            return
        
        self.info_label.setText(f"{len(self.afiliados)} afiliados sin ubicar. Selecciona uno para ubicarlo en el mapa.")
        
        # Llenar tabla
        for afiliado in self.afiliados:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(afiliado['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(afiliado['nombre']))
            self.table.setItem(row, 2, QTableWidgetItem(afiliado['direccion']))
            self.table.setItem(row, 3, QTableWidgetItem(afiliado['municipio']))
    
    def on_selection_changed(self):
        """Maneja el cambio de selección en la tabla"""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            self.selected_afiliado_id = int(self.table.item(row, 0).text())
            self.btn_ubicar.setEnabled(True)
        else:
            self.selected_afiliado_id = None
            self.btn_ubicar.setEnabled(False)
    
    def ubicar_afiliado(self):
        """Activa la herramienta para ubicar el afiliado seleccionado en el mapa"""
        if not self.selected_afiliado_id:
            QMessageBox.warning(self, "Advertencia", "Selecciona un afiliado primero")
            return
        
        # Obtener datos del afiliado seleccionado
        row = self.table.currentRow()
        nombre = self.table.item(row, 1).text()
        
        # Activar herramienta de click en mapa
        canvas = self.iface.mapCanvas()
        self.previous_map_tool = canvas.mapTool()
        self.map_tool = MapClickTool(canvas, self.on_point_selected)
        canvas.setMapTool(self.map_tool)
        
        # Mensaje
        self.iface.messageBar().pushMessage(
            "ACLIFIM",
            f"Haz click en el mapa para ubicar a '{nombre}'",
            level=0,
            duration=5
        )
        
        print(f"[SIN UBICAR] Modo de ubicación activado para afiliado ID {self.selected_afiliado_id}")
        
        # Minimizar el diálogo (no cerrar)
        self.showMinimized()
    
    def on_point_selected(self, point):
        """Callback cuando se hace click en el mapa"""
        print(f"[SIN UBICAR] Punto seleccionado: {point.x()}, {point.y()}")
        
        # Crear marcador temporal
        canvas = self.iface.mapCanvas()
        self.rubber_band = QgsRubberBand(canvas, QgsWkbTypes.PointGeometry)
        self.rubber_band.setColor(QColor(255, 0, 0, 180))
        self.rubber_band.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.rubber_band.setIconSize(5)
        self.rubber_band.setWidth(1)
        self.rubber_band.addPoint(point)
        
        # Confirmar ubicación
        row = self.table.currentRow()
        nombre = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Confirmar ubicación",
            f"¿Ubicar a '{nombre}' en estas coordenadas?\n\n"
            f"Lon: {point.x():.6f}\n"
            f"Lat: {point.y():.6f}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        # Limpiar marcador temporal
        if self.rubber_band:
            canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None
        
        if reply == QMessageBox.Yes:
            # Transformar coordenadas si es necesario
            canvas_crs = canvas.mapSettings().destinationCrs()
            target_crs = QgsCoordinateReferenceSystem("EPSG:4326")
            
            if canvas_crs != target_crs:
                transform = QgsCoordinateTransform(canvas_crs, target_crs, QgsProject.instance())
                transformed_point = transform.transform(point)
            else:
                transformed_point = point
            
            # Actualizar coordenadas en la BD
            success, msg = update_afiliado_coordinates(self.selected_afiliado_id, transformed_point)
            
            if success:
                QMessageBox.information(self, "Éxito", f"Afiliado '{nombre}' ubicado correctamente")
                # Recargar lista
                self.load_afiliados()
                # Refrescar capa en QGIS
                self.refresh_layer()
            else:
                QMessageBox.critical(self, "Error", msg)
        
        # Restaurar herramienta anterior
        if hasattr(self, 'previous_map_tool') and self.previous_map_tool:
            canvas.setMapTool(self.previous_map_tool)
        else:
            canvas.unsetMapTool(self.map_tool)
        
        # Restaurar ventana
        self.showNormal()
        self.activateWindow()
    
    def refresh_layer(self):
        """Refresca la capa de Afiliados en QGIS para mostrar el nuevo punto"""
        from qgis.core import QgsProject
        
        for layer in QgsProject.instance().mapLayers().values():
            if "Afiliados" in layer.name() or "afiliados" in layer.name().lower():
                layer.triggerRepaint()
                print("[SIN UBICAR] Capa de afiliados refrescada")
        
        self.iface.mapCanvas().refresh()
