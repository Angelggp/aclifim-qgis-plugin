from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog,
    QProgressDialog,
    QTabWidget,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QGroupBox,
    QLineEdit,
    QGridLayout,
    QComboBox,
    QMenu,
    QAction,
    QSpinBox
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.gui import QgsRubberBand, QgsMapToolEmitPoint
from qgis.core import QgsWkbTypes, QgsPointXY, QgsProject

from ..modules.map_tools import (
    MapClickTool,
    get_or_create_layer,
    add_point_with_data,
    force_reload_afiliados_layer,
    highlight_afiliados_by_ids,
    clear_afiliados_highlight,
    draw_centro_buffer
)
from .afiliado_form import AfiliadoForm
from .resumen_afiliado_dialog import ResumenAfiliadoDialog
from .db_config_dialog import DatabaseConfigDialog
from .centro_interes_form import CentroInteresForm
from ..modules.access_importer import (
    AccessImporter, 
    get_all_afiliados, 
    get_afiliados_sin_coordenadas, 
    update_afiliado_coordinates,
    search_afiliados,
    get_afiliado_by_id
)
from ..modules.centros_interes_manager import (
    get_all_centros_interes,
    create_centro_interes,
    update_centro_interes,
    delete_centro_interes,
    search_centros_interes,
    get_centro_by_id,
    get_afiliados_en_radio_centro
)
from ..utils.pdf_exporter import PDFExporter


class MainDialog(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.map_tool = None
        self.rubber_band = None
        self.buffer_rubber_band = None
        self.search_highlight_ids = []
        self.buffer_highlight_ids = []

        self.setWindowTitle("ACLIFIM - Gestión de Afiliados")
        self.resize(800, 600)

        # Layout principal
        main_layout = QVBoxLayout()
        
        # Crear tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_manage_tab(), "Gestionar Afiliados")
        self.tabs.addTab(self.create_centros_tab(), "Centros de Interés")
        self.tabs.addTab(self.create_import_tab(), "Importar")
        self.tabs.addTab(self.create_config_tab(), "Configuración")
        
        main_layout.addWidget(self.tabs)
        
        # Botón cerrar
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.close)
        close_layout.addWidget(btn_close)
        main_layout.addLayout(close_layout)
        
        self.setLayout(main_layout)
        
        # Cargar capas al iniciar
        self.load_afiliados_layer()
        self.load_centros_layer()
    
    def create_add_tab(self):
        """Pestaña para agregar afiliados"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Grupo: Agregar afiliado
        group = QGroupBox("Opciones de Agregado")
        group_layout = QVBoxLayout()
        
        info_label = QLabel("Seleccione el método para agregar un nuevo afiliado:")
        group_layout.addWidget(info_label)
        
        # Botón: Click en mapa
        self.btn_add_point = QPushButton("Agregar afiliado (click en mapa)")
        self.btn_add_point.clicked.connect(self.activar_modo_click)
        group_layout.addWidget(self.btn_add_point)
        
        help_label1 = QLabel("• Permite agregar un afiliado haciendo click en el mapa")
        help_label1.setStyleSheet("color: gray; font-size: 10px;")
        group_layout.addWidget(help_label1)
        
        group_layout.addSpacing(10)
        
        # Botón: Modo nativo
        self.btn_add_native = QPushButton("Agregar afiliado (modo QGIS)")
        self.btn_add_native.clicked.connect(self.activar_modo_nativo)
        group_layout.addWidget(self.btn_add_native)
        
        help_label2 = QLabel("• Usa las herramientas nativas de QGIS para agregar puntos")
        help_label2.setStyleSheet("color: gray; font-size: 10px;")
        group_layout.addWidget(help_label2)
        
        group_layout.addStretch()
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        widget.setLayout(layout)
        return widget
    
    def create_manage_tab(self):
        """Pestaña para gestionar y filtrar afiliados"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Gestión de Afiliados")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Grupo de filtros
        filter_group = QGroupBox("Filtros de Búsqueda")
        filter_layout = QGridLayout()
        
        # Fila 1: Nombre y Apellido
        filter_layout.addWidget(QLabel("Nombre:"), 0, 0)
        self.filter_nombre = QLineEdit()
        self.filter_nombre.setPlaceholderText("Buscar por nombre...")
        filter_layout.addWidget(self.filter_nombre, 0, 1)
        
        filter_layout.addWidget(QLabel("Apellido:"), 0, 2)
        self.filter_apellido = QLineEdit()
        self.filter_apellido.setPlaceholderText("Buscar por apellido...")
        filter_layout.addWidget(self.filter_apellido, 0, 3)
        
        # Fila 2: Código y CI
        filter_layout.addWidget(QLabel("Código:"), 1, 0)
        self.filter_codigo = QLineEdit()
        self.filter_codigo.setPlaceholderText("Buscar por código...")
        filter_layout.addWidget(self.filter_codigo, 1, 1)
        
        filter_layout.addWidget(QLabel("CI:"), 1, 2)
        self.filter_ci = QLineEdit()
        self.filter_ci.setPlaceholderText("Buscar por carnet...")
        filter_layout.addWidget(self.filter_ci, 1, 3)
        
        # Fila 3: Estado
        filter_layout.addWidget(QLabel("Estado:"), 2, 0)
        self.filter_estado = QComboBox()
        self.filter_estado.addItems(["Todos", "Sin ubicar", "Cambio de dirección", "Ubicados"])
        filter_layout.addWidget(self.filter_estado, 2, 1)
        
        # Botones de filtro
        btn_filter_layout = QHBoxLayout()
        self.btn_buscar = QPushButton("🔍 Buscar")
        self.btn_buscar.clicked.connect(self.buscar_afiliados)
        btn_filter_layout.addWidget(self.btn_buscar)
        
        self.btn_limpiar_filtros = QPushButton("✖ Limpiar Filtros")
        self.btn_limpiar_filtros.clicked.connect(self.limpiar_filtros)
        btn_filter_layout.addWidget(self.btn_limpiar_filtros)
        btn_filter_layout.addStretch()
        
        filter_layout.addLayout(btn_filter_layout, 3, 0, 1, 4)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Info de resultados
        self.label_resultados = QLabel("Total: 0 afiliados")
        self.label_resultados.setStyleSheet("font-weight: bold; color: #0066cc;")
        layout.addWidget(self.label_resultados)
        
        # Tabla (SOLO 5 COLUMNAS: ID, CI, Nombre, Apellido, Dirección)
        self.table_all = QTableWidget()
        self.table_all.setColumnCount(5)
        self.table_all.setHorizontalHeaderLabels(["ID", "CI", "Nombre", "Apellido", "Dirección"])
        self.table_all.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_all.setSelectionMode(QTableWidget.SingleSelection)
        self.table_all.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Menú contextual
        self.table_all.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_all.customContextMenuRequested.connect(self.mostrar_menu_contextual_afiliado)
        
        # Ajustar columnas
        header = self.table_all.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        # Doble clic para ver detalles
        self.table_all.doubleClicked.connect(self.ver_detalles_afiliado)
        
        layout.addWidget(self.table_all)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        self.btn_ver_detalles = QPushButton("📋 Ver Detalles")
        self.btn_ver_detalles.clicked.connect(self.ver_detalles_afiliado)
        self.btn_ver_detalles.setEnabled(False)
        btn_layout.addWidget(self.btn_ver_detalles)
        
        self.btn_ubicar_afiliado = QPushButton("📍 Ubicar en Mapa")
        self.btn_ubicar_afiliado.clicked.connect(self.ubicar_afiliado_desde_gestion)
        self.btn_ubicar_afiliado.setEnabled(False)
        btn_layout.addWidget(self.btn_ubicar_afiliado)

        self.btn_resumen_mapa = QPushButton("Resumen en Mapa")
        self.btn_resumen_mapa.clicked.connect(self.activar_resumen_mapa)
        btn_layout.addWidget(self.btn_resumen_mapa)
        
        self.btn_refresh_all = QPushButton("🔄 Actualizar")
        self.btn_refresh_all.clicked.connect(self.load_all_afiliados)
        btn_layout.addWidget(self.btn_refresh_all)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Conectar señal de selección
        self.table_all.itemSelectionChanged.connect(self.on_manage_selection_changed)
        
        widget.setLayout(layout)
        
        # Cargar todos los datos inicialmente
        self.load_all_afiliados()
        
        return widget
    
    def create_unlocated_tab(self):
        """Pestaña para afiliados sin ubicar"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Afiliados Sin Coordenadas")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        self.info_unlocated = QLabel("Selecciona un afiliado y haz click en 'Ubicar en Mapa'")
        layout.addWidget(self.info_unlocated)
        
        # Leyenda de colores
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Leyenda:"))
        
        label_nuevo = QLabel("■ Nuevo")
        label_nuevo.setStyleSheet("color: #0099cc; font-weight: bold;")
        legend_layout.addWidget(label_nuevo)
        
        label_cambio = QLabel("■ Cambio Dirección")
        label_cambio.setStyleSheet("color: #ff9900; font-weight: bold;")
        legend_layout.addWidget(label_cambio)
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        # Tabla (actualizada: ID, Nombre Completo, Dirección, CI)
        self.table_unlocated = QTableWidget()
        self.table_unlocated.setColumnCount(4)
        self.table_unlocated.setHorizontalHeaderLabels(["ID", "Nombre Completo", "Dirección", "CI"])
        self.table_unlocated.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_unlocated.setSelectionMode(QTableWidget.SingleSelection)
        self.table_unlocated.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Menú contextual
        self.table_unlocated.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_unlocated.customContextMenuRequested.connect(self.mostrar_menu_contextual_afiliado)
        
        # Ajustar columnas
        header = self.table_unlocated.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table_unlocated)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_ubicar_unlocated = QPushButton("📍 Ubicar en Mapa")
        self.btn_ubicar_unlocated.clicked.connect(self.ubicar_afiliado_seleccionado)
        self.btn_ubicar_unlocated.setEnabled(False)
        btn_layout.addWidget(self.btn_ubicar_unlocated)
        
        self.btn_refresh_unlocated = QPushButton("🔄 Actualizar")
        self.btn_refresh_unlocated.clicked.connect(self.load_unlocated_afiliados)
        btn_layout.addWidget(self.btn_refresh_unlocated)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Conectar señal de selección
        self.table_unlocated.itemSelectionChanged.connect(self.on_unlocated_selection_changed)
        
        widget.setLayout(layout)
        
        # Cargar datos
        self.load_unlocated_afiliados()
        
        return widget
    
    def create_centros_tab(self):
        """Pestaña para gestionar centros de interés"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Gestión de Centros de Interés")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Grupo de filtros
        filter_group = QGroupBox("Búsqueda")
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Nombre:"))
        self.filter_centro_nombre = QLineEdit()
        self.filter_centro_nombre.setPlaceholderText("Buscar por nombre...")
        filter_layout.addWidget(self.filter_centro_nombre)
        
        filter_layout.addWidget(QLabel("Tipo:"))
        self.filter_centro_tipo = QLineEdit()
        self.filter_centro_tipo.setPlaceholderText("Buscar por tipo...")
        filter_layout.addWidget(self.filter_centro_tipo)
        
        self.btn_buscar_centros = QPushButton("🔍 Buscar")
        self.btn_buscar_centros.clicked.connect(self.buscar_centros)
        filter_layout.addWidget(self.btn_buscar_centros)
        
        self.btn_limpiar_centros = QPushButton("✖ Limpiar")
        self.btn_limpiar_centros.clicked.connect(self.limpiar_filtros_centros)
        filter_layout.addWidget(self.btn_limpiar_centros)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Info de resultados
        self.label_centros_resultados = QLabel("Total: 0 centros")
        self.label_centros_resultados.setStyleSheet("font-weight: bold; color: #0066cc;")
        layout.addWidget(self.label_centros_resultados)
        
        # Tabla de centros
        self.table_centros = QTableWidget()
        self.table_centros.setColumnCount(5)
        self.table_centros.setHorizontalHeaderLabels(["ID", "Nombre", "Tipo", "Dirección", "Coordenadas"])
        self.table_centros.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_centros.setSelectionMode(QTableWidget.SingleSelection)
        self.table_centros.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Ajustar columnas
        header = self.table_centros.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table_centros)

        # Grupo: análisis por buffer
        buffer_group = QGroupBox("Análisis de Afiliados por Buffer")
        buffer_layout = QVBoxLayout()

        buffer_controls = QHBoxLayout()
        buffer_controls.addWidget(QLabel("Radio (metros):"))
        self.buffer_radio_metros = QSpinBox()
        self.buffer_radio_metros.setRange(10, 50000)
        self.buffer_radio_metros.setValue(300)
        buffer_controls.addWidget(self.buffer_radio_metros)

        self.btn_generar_buffer = QPushButton("⭕ Generar Buffer")
        self.btn_generar_buffer.clicked.connect(self.generar_buffer_centro)
        buffer_controls.addWidget(self.btn_generar_buffer)

        self.btn_limpiar_buffer = QPushButton("🧹 Limpiar Buffer")
        self.btn_limpiar_buffer.clicked.connect(self.limpiar_buffer_centro)
        buffer_controls.addWidget(self.btn_limpiar_buffer)
        buffer_controls.addStretch()

        buffer_layout.addLayout(buffer_controls)

        self.label_buffer_resultados = QLabel("Buffer: sin análisis")
        self.label_buffer_resultados.setStyleSheet("font-weight: bold; color: #8a2b2b;")
        buffer_layout.addWidget(self.label_buffer_resultados)

        self.table_buffer_afiliados = QTableWidget()
        self.table_buffer_afiliados.setColumnCount(6)
        self.table_buffer_afiliados.setHorizontalHeaderLabels([
            "ID", "CI", "Nombre", "Apellido", "Distancia (m)", "Dirección"
        ])
        self.table_buffer_afiliados.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_buffer_afiliados.setSelectionMode(QTableWidget.SingleSelection)
        self.table_buffer_afiliados.setEditTriggers(QTableWidget.NoEditTriggers)

        buffer_header = self.table_buffer_afiliados.horizontalHeader()
        buffer_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        buffer_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        buffer_header.setSectionResizeMode(2, QHeaderView.Stretch)
        buffer_header.setSectionResizeMode(3, QHeaderView.Stretch)
        buffer_header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        buffer_header.setSectionResizeMode(5, QHeaderView.Stretch)

        buffer_layout.addWidget(self.table_buffer_afiliados)
        buffer_group.setLayout(buffer_layout)
        layout.addWidget(buffer_group)
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        
        self.btn_agregar_centro = QPushButton("➕ Agregar Centro")
        self.btn_agregar_centro.clicked.connect(self.agregar_centro_click)
        btn_layout.addWidget(self.btn_agregar_centro)
        
        self.btn_editar_centro = QPushButton("✏️ Editar")
        self.btn_editar_centro.clicked.connect(self.editar_centro)
        self.btn_editar_centro.setEnabled(False)
        btn_layout.addWidget(self.btn_editar_centro)
        
        self.btn_eliminar_centro = QPushButton("🗑️ Eliminar")
        self.btn_eliminar_centro.clicked.connect(self.eliminar_centro)
        self.btn_eliminar_centro.setEnabled(False)
        btn_layout.addWidget(self.btn_eliminar_centro)
        
        self.btn_refresh_centros = QPushButton("🔄 Actualizar")
        self.btn_refresh_centros.clicked.connect(self.load_centros_interes)
        btn_layout.addWidget(self.btn_refresh_centros)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Conectar señal de selección
        self.table_centros.itemSelectionChanged.connect(self.on_centro_selection_changed)
        
        widget.setLayout(layout)
        
        # Cargar datos
        self.load_centros_interes()
        
        return widget
    
    def create_import_tab(self):
        """Pestaña para importar datos"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Grupo: Importar Access
        group = QGroupBox("Importar Desde Access")
        group_layout = QVBoxLayout()
        
        info_label = QLabel(
            "Permite importar afiliados desde una base de datos Microsoft Access.\n"
            "Los afiliados se importarán sin coordenadas y deberás ubicarlos\n"
            "manualmente usando la pestaña 'Sin Ubicar'."
        )
        group_layout.addWidget(info_label)
        
        group_layout.addSpacing(10)
        
        self.btn_import = QPushButton("Seleccionar Archivo Access")
        self.btn_import.clicked.connect(self.importar_desde_access)
        group_layout.addWidget(self.btn_import)
        
        group_layout.addStretch()
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        widget.setLayout(layout)
        return widget
    
    def create_config_tab(self):
        """Pestaña de configuración"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Grupo: Configuración BD
        group = QGroupBox("Configuración de Base de Datos")
        group_layout = QVBoxLayout()
        
        info_label = QLabel(
            "Configure la conexión a la base de datos PostgreSQL/PostGIS.\n"
            "Esta configuración es necesaria para almacenar los datos de los afiliados."
        )
        group_layout.addWidget(info_label)
        
        group_layout.addSpacing(10)
        
        self.btn_config = QPushButton("Configurar Conexión")
        self.btn_config.clicked.connect(self.show_db_config)
        group_layout.addWidget(self.btn_config)
        
        group_layout.addStretch()
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        widget.setLayout(layout)
        return widget
    
    # --- Métodos auxiliares ---
    
    def load_all_afiliados(self):
        """Carga todos los afiliados en la tabla con nuevos campos"""
        afiliados = get_all_afiliados()
        
        # Aplicar filtro de estado si no es "Todos"
        estado_filtro = self.filter_estado.currentText()
        if estado_filtro == "Sin ubicar":
            afiliados = [a for a in afiliados if a.get('lon') is None or a.get('lat') is None]
        elif estado_filtro == "Cambio de dirección":
            afiliados = [a for a in afiliados if a.get('estado') == 'cambio_direccion']
        elif estado_filtro == "Ubicados":
            afiliados = [a for a in afiliados if a.get('lon') is not None and a.get('lat') is not None and a.get('estado') == 'normal']
        
        self.table_all.setRowCount(0)
        
        for afiliado in afiliados:
            row = self.table_all.rowCount()
            self.table_all.insertRow(row)
            
            # SOLO 5 COLUMNAS: ID, CI, Nombre, Apellido, Dirección
            self.table_all.setItem(row, 0, QTableWidgetItem(str(afiliado['id'])))
            self.table_all.setItem(row, 1, QTableWidgetItem(afiliado['carnet_id']))
            self.table_all.setItem(row, 2, QTableWidgetItem(afiliado['nombres']))
            self.table_all.setItem(row, 3, QTableWidgetItem(afiliado['apellidos']))
            self.table_all.setItem(row, 4, QTableWidgetItem(afiliado['direccion']))
            
            # Colorear según estado
            color = self.get_color_by_estado(afiliado['estado'])
            if color:
                for col in range(5):
                    item = self.table_all.item(row, col)
                    if item:
                        item.setBackground(color)
        
        self.label_resultados.setText(f"Total: {len(afiliados)} afiliados")
        self.search_highlight_ids = []
        print(f"[PLUGIN] {len(afiliados)} afiliados cargados en tabla")
    
    def buscar_afiliados(self):
        """Busca afiliados según los filtros aplicados"""
        # Obtener valores de filtros
        nombre = self.filter_nombre.text().strip()
        apellido = self.filter_apellido.text().strip()
        codigo = self.filter_codigo.text().strip()
        ci = self.filter_ci.text().strip()
        estado_filtro = self.filter_estado.currentText()
        
        # Buscar
        afiliados = search_afiliados(
            nombre=nombre if nombre else None,
            apellido=apellido if apellido else None,
            codigo=codigo if codigo else None,
            carnet_id=ci if ci else None
        )
        
        # Aplicar filtro de estado
        if estado_filtro == "Sin ubicar":
            afiliados = [a for a in afiliados if a.get('lon') is None or a.get('lat') is None]
        elif estado_filtro == "Cambio de dirección":
            afiliados = [a for a in afiliados if a.get('estado') == 'cambio_direccion']
        elif estado_filtro == "Ubicados":
            afiliados = [a for a in afiliados if a.get('lon') is not None and a.get('lat') is not None and a.get('estado') == 'normal']
        
        # Mostrar resultados
        self.table_all.setRowCount(0)
        
        for afiliado in afiliados:
            row = self.table_all.rowCount()
            self.table_all.insertRow(row)
            
            self.table_all.setItem(row, 0, QTableWidgetItem(str(afiliado['id'])))
            self.table_all.setItem(row, 1, QTableWidgetItem(afiliado['carnet_id']))
            self.table_all.setItem(row, 2, QTableWidgetItem(afiliado['nombres']))
            self.table_all.setItem(row, 3, QTableWidgetItem(afiliado['apellidos']))
            self.table_all.setItem(row, 4, QTableWidgetItem(afiliado['direccion']))
            
            # Colorear según estado
            color = self.get_color_by_estado(afiliado['estado'])
            if color:
                for col in range(5):
                    item = self.table_all.item(row, col)
                    if item:
                        item.setBackground(color)
        
        self.label_resultados.setText(f"Resultados: {len(afiliados)} afiliados encontrados")
        self.search_highlight_ids = [a['id'] for a in afiliados]
        self._apply_map_highlight()
        print(f"[PLUGIN] Búsqueda: {len(afiliados)} resultados")
    
    def limpiar_filtros(self):
        """Limpia todos los filtros y recarga datos"""
        self.filter_nombre.clear()
        self.filter_apellido.clear()
        self.filter_codigo.clear()
        self.filter_ci.clear()
        self.filter_estado.setCurrentIndex(0)  # "Todos"
        self.search_highlight_ids = []
        self.load_all_afiliados()
        self._apply_map_highlight()
    
    def on_manage_selection_changed(self):
        """Maneja cambio de selección en tabla de gestión"""
        has_selection = len(self.table_all.selectedItems()) > 0
        self.btn_ver_detalles.setEnabled(has_selection)
        
        # Habilitar botón ubicar solo si hay selección y no tiene coordenadas
        if has_selection:
            selected_rows = self.table_all.selectionModel().selectedRows()
            if selected_rows:
                row = selected_rows[0].row()
                afiliado_id = int(self.table_all.item(row, 0).text())
                
                # Obtener datos completos del afiliado
                afiliado = get_afiliado_by_id(afiliado_id)
                if afiliado:
                    # Habilitar ubicar solo si NO tiene coordenadas
                    tiene_coords = afiliado.get('lon') is not None and afiliado.get('lat') is not None
                    self.btn_ubicar_afiliado.setEnabled(not tiene_coords)
                else:
                    self.btn_ubicar_afiliado.setEnabled(False)
        else:
            self.btn_ubicar_afiliado.setEnabled(False)
    
    def ver_detalles_afiliado(self):
        """Abre diálogo con todos los detalles del afiliado seleccionado"""
        selected_rows = self.table_all.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Advertencia", "Selecciona un afiliado primero")
            return
        
        # Obtener ID del afiliado
        row = selected_rows[0].row()
        afiliado_id = int(self.table_all.item(row, 0).text())
        
        # Obtener detalles completos
        afiliado = get_afiliado_by_id(afiliado_id)
        
        if not afiliado:
            QMessageBox.critical(self, "Error", "No se pudo cargar los detalles del afiliado")
            return
        
        # Mostrar diálogo de detalles
        from .detalle_afiliado_dialog import DetalleAfiliadoDialog
        dialog = DetalleAfiliadoDialog(afiliado, self, self.iface)
        dialog.exec_()

    def activar_resumen_mapa(self):
        """Activa seleccion puntual en mapa para abrir resumen rapido de afiliado."""
        canvas = self.iface.mapCanvas()
        self.previous_map_tool = canvas.mapTool()
        self.map_tool = MapClickTool(canvas, self.on_resumen_map_clicked)
        canvas.setMapTool(self.map_tool)

        self.iface.messageBar().pushMessage(
            "ACLIFIM",
            "Haz clic sobre un afiliado en el mapa para ver su resumen.",
            level=0,
            duration=5
        )

    def on_resumen_map_clicked(self, point):
        """Maneja el clic en mapa para mostrar dialogo resumido de afiliado."""
        from qgis.core import QgsCoordinateTransform, QgsGeometry, QgsRectangle

        afiliado_id = None
        layer = get_or_create_layer()

        if not layer:
            QMessageBox.warning(self, "Advertencia", "No se pudo cargar la capa de afiliados.")
        else:
            try:
                canvas = self.iface.mapCanvas()
                canvas_crs = canvas.mapSettings().destinationCrs()
                layer_crs = layer.crs()

                click_point = point
                if canvas_crs != layer_crs:
                    transform = QgsCoordinateTransform(canvas_crs, layer_crs, QgsProject.instance())
                    click_point = transform.transform(point)

                # Tolerancia aproximada de seleccion (en unidades de capa)
                tol = canvas.mapUnitsPerPixel() * 8
                rect = QgsRectangle(
                    click_point.x() - tol,
                    click_point.y() - tol,
                    click_point.x() + tol,
                    click_point.y() + tol
                )

                click_geom = QgsGeometry.fromPointXY(QgsPointXY(click_point.x(), click_point.y()))
                nearest_feature = None
                nearest_dist = None

                for feat in layer.getFeatures(rect):
                    geom = feat.geometry()
                    if not geom or geom.isNull():
                        continue

                    dist = geom.distance(click_geom)
                    if nearest_dist is None or dist < nearest_dist:
                        nearest_dist = dist
                        nearest_feature = feat

                if nearest_feature is not None and nearest_feature['id'] is not None:
                    afiliado_id = int(nearest_feature['id'])

            except Exception as e:
                print(f"[PLUGIN] Error al identificar afiliado en mapa: {e}")

        # Restaurar herramienta de mapa
        canvas = self.iface.mapCanvas()
        if hasattr(self, 'previous_map_tool') and self.previous_map_tool:
            canvas.setMapTool(self.previous_map_tool)
        else:
            canvas.unsetMapTool(self.map_tool)

        if afiliado_id is None:
            QMessageBox.information(
                self,
                "Sin afiliado",
                "No se encontro un afiliado en el punto seleccionado."
            )
            return

        afiliado = get_afiliado_by_id(afiliado_id)
        if not afiliado:
            QMessageBox.warning(self, "Advertencia", "No se pudieron cargar los datos del afiliado.")
            return

        dialog = ResumenAfiliadoDialog(afiliado, self)
        dialog.exec_()
    
    def mostrar_menu_contextual_afiliado(self, position):
        """Muestra menú contextual para afiliados"""
        # Determinar qué tabla disparó el evento
        sender = self.sender()
        
        # Verificar si hay una fila seleccionada
        if not sender.selectionModel().selectedRows():
            return
        
        # Crear menú
        menu = QMenu()
        
        # Obtener ID del afiliado para verificar si tiene coordenadas
        row = sender.selectionModel().selectedRows()[0].row()
        afiliado_id = int(sender.item(row, 0).text())
        afiliado = get_afiliado_by_id(afiliado_id)
        
        # Acción: Ver detalles
        action_detalles = QAction("📋 Ver Detalles", self)
        action_detalles.triggered.connect(lambda: self.ver_detalles_desde_menu(sender))
        menu.addAction(action_detalles)
        
        # Acción: Exportar PDF
        action_pdf = QAction("📄 Exportar a PDF", self)
        action_pdf.triggered.connect(lambda: self.exportar_afiliado_pdf(sender))
        menu.addAction(action_pdf)
        
        # Acción: Cambiar Dirección (solo si tiene coordenadas)
        if afiliado and afiliado.get('lon') is not None and afiliado.get('lat') is not None:
            menu.addSeparator()
            action_cambiar_dir = QAction("📍 Cambiar Dirección", self)
            action_cambiar_dir.triggered.connect(lambda: self.cambiar_direccion_desde_menu(sender))
            menu.addAction(action_cambiar_dir)
        
        # Mostrar menú en la posición del cursor
        menu.exec_(sender.viewport().mapToGlobal(position))
    
    def ver_detalles_desde_menu(self, tabla):
        """Abre detalles del afiliado desde menú contextual"""
        selected_rows = tabla.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        afiliado_id = int(tabla.item(row, 0).text())
        
        # Obtener detalles completos
        afiliado = get_afiliado_by_id(afiliado_id)
        
        if not afiliado:
            QMessageBox.critical(self, "Error", "No se pudo cargar los detalles del afiliado")
            return
        
        # Mostrar diálogo
        from .detalle_afiliado_dialog import DetalleAfiliadoDialog
        dialog = DetalleAfiliadoDialog(afiliado, self, self.iface)
        dialog.exec_()
    
    def exportar_afiliado_pdf(self, tabla):
        """Exporta afiliado a PDF desde menú contextual"""
        selected_rows = tabla.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        afiliado_id = int(tabla.item(row, 0).text())
        
        # Obtener detalles completos
        afiliado = get_afiliado_by_id(afiliado_id)
        
        if not afiliado:
            QMessageBox.critical(self, "Error", "No se pudo cargar los detalles del afiliado")
            return
        
        # Exportar a PDF
        exporter = PDFExporter()
        exporter.export_afiliado(afiliado, self)
    
    def cambiar_direccion_desde_menu(self, tabla):
        """Cambia dirección de afiliado desde menú contextual"""
        selected_rows = tabla.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        afiliado_id = int(tabla.item(row, 0).text())
        
        # Obtener detalles completos
        afiliado = get_afiliado_by_id(afiliado_id)
        
        if not afiliado:
            QMessageBox.critical(self, "Error", "No se pudo cargar los detalles del afiliado")
            return
        
        # Verificar que tenga coordenadas
        if afiliado.get('lon') is None or afiliado.get('lat') is None:
            QMessageBox.warning(self, "Advertencia", "Este afiliado no tiene coordenadas asignadas")
            return
        
        # Mostrar diálogo de confirmación
        from .cambio_direccion_dialog import CambioDireccionDialog
        nombre_completo = f"{afiliado.get('nombres', '')} {afiliado.get('apellidos', '')}" .strip()
        dialog = CambioDireccionDialog(nombre_completo, self)
        
        if dialog.exec_() == QDialog.Accepted:
            motivo = dialog.get_motivo()
            
            # Llamar a la función que elimina geometría y cambia estado
            from ..modules.access_importer import cambiar_direccion_afiliado
            success, msg = cambiar_direccion_afiliado(afiliado_id, motivo)
            
            if success:
                QMessageBox.information(
                    self,
                    "Cambio Registrado",
                    f"El cambio de dirección se registró correctamente.\n\n"
                    f"El afiliado '{nombre_completo}' ahora aparecerá en la lista 'Sin Ubicar'.\n"
                    f"Ubíquelo nuevamente en el mapa desde esa lista."
                )
                # Recargar datos y refrescar mapa
                try:
                    self.load_all_afiliados()
                except Exception as e:
                    print(f"[PLUGIN] Error al recargar afiliados: {e}")
                
                try:
                    self.load_unlocated_afiliados()
                except Exception as e:
                    print(f"[PLUGIN] Error al recargar sin ubicar: {e}")
                
                try:
                    self.refresh_layer()
                except Exception as e:
                    print(f"[PLUGIN] Error al refrescar capa: {e}")
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"No se pudo registrar el cambio de dirección:\n\n{msg}"
                )
    
    def ubicar_afiliado_desde_gestion(self):
        """Activa el modo de ubicar afiliado desde la pestaña de gestión"""
        selected_rows = self.table_all.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Advertencia", "Selecciona un afiliado primero")
            return
        
        # Obtener datos del afiliado
        row = selected_rows[0].row()
        afiliado_id = int(self.table_all.item(row, 0).text())
        nombre = self.table_all.item(row, 2).text()
        apellido = self.table_all.item(row, 3).text()
        
        # Verificar que no tenga coordenadas
        afiliado = get_afiliado_by_id(afiliado_id)
        if not afiliado:
            QMessageBox.critical(self, "Error", "No se encontró el afiliado")
            return
        
        if afiliado.get('lon') is not None and afiliado.get('lat') is not None:
            QMessageBox.information(
                self,
                "Afiliado ya ubicado",
                f"{nombre} {apellido} ya tiene coordenadas.\n\nSi deseas cambiarlo, primero debes marcarlo como cambio de dirección desde Access."
            )
            return
        
        # Guardar ID del afiliado seleccionado
        self.selected_afiliado_id = afiliado_id
        
        # Activar modo de selección en mapa
        QMessageBox.information(
            self,
            "Ubicar en mapa",
            f"Haz clic en el mapa para ubicar a:\n\n{nombre} {apellido}"
        )
        
        canvas = self.iface.mapCanvas()
        self.previous_map_tool = canvas.mapTool()
        self.map_tool = MapClickTool(canvas, self.on_ubicar_point_selected)
        canvas.setMapTool(self.map_tool)
        
        self.showMinimized()
        print(f"[PLUGIN] Modo ubicar activado para afiliado ID: {afiliado_id}")
    
    def get_color_by_estado(self, estado):
        """Retorna color según el estado del afiliado"""
        if estado == 'nuevo':
            return QColor(144, 238, 144)  # Verde claro (LightGreen)
        elif estado == 'cambio_direccion':
            return QColor(135, 206, 250)  # Azul cielo claro (LightSkyBlue)
        else:
            return None  # Sin color (normal)
    
    def load_unlocated_afiliados(self):
        """Carga afiliados sin ubicar en la tabla con nuevos campos"""
        # Verificar que la tabla exista
        if not hasattr(self, 'table_unlocated'):
            print("[PLUGIN] tabla_unlocated no existe aún")
            return
        
        afiliados = get_afiliados_sin_coordenadas()
        self.table_unlocated.setRowCount(0)
        
        if len(afiliados) == 0:
            self.info_unlocated.setText("✅ Todos los afiliados tienen coordenadas asignadas")
            self.btn_ubicar_unlocated.setEnabled(False)
        else:
            # Contar por estado
            nuevos = sum(1 for a in afiliados if a.get('estado') == 'nuevo')
            cambios = sum(1 for a in afiliados if a.get('estado') == 'cambio_direccion')
            
            info_text = f"📍 {len(afiliados)} afiliados sin ubicar"
            if nuevos > 0:
                info_text += f" ({nuevos} nuevos"
            if cambios > 0:
                info_text += f", {cambios} cambio dirección)" if nuevos > 0 else f" ({cambios} cambio dirección)"
            if nuevos > 0 and cambios == 0:
                info_text += ")"
            
            self.info_unlocated.setText(info_text)
            
            for afiliado in afiliados:
                row = self.table_unlocated.rowCount()
                self.table_unlocated.insertRow(row)
                
                # Actualizar columnas con nuevos campos
                self.table_unlocated.setItem(row, 0, QTableWidgetItem(str(afiliado['id'])))
                nombre_completo = f"{afiliado['nombres']} {afiliado['apellidos']}"
                self.table_unlocated.setItem(row, 1, QTableWidgetItem(nombre_completo))
                self.table_unlocated.setItem(row, 2, QTableWidgetItem(afiliado['direccion']))
                self.table_unlocated.setItem(row, 3, QTableWidgetItem(afiliado.get('carnet_id', '')))
                
                # Colorear según estado
                color = self.get_color_by_estado(afiliado.get('estado', 'normal'))
                if color:
                    for col in range(4):
                        item = self.table_unlocated.item(row, col)
                        if item:
                            item.setBackground(color)
        
        print(f"[PLUGIN] {len(afiliados)} afiliados sin ubicar cargados")
    
    def on_unlocated_selection_changed(self):
        """Maneja cambio de selección en tabla de sin ubicar"""
        selected = self.table_unlocated.selectedItems()
        self.btn_ubicar_unlocated.setEnabled(len(selected) > 0)
    
    def ubicar_afiliado_seleccionado(self):
        """Activa modo de ubicación para afiliado seleccionado"""
        selected = self.table_unlocated.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "Selecciona un afiliado primero")
            return
        
        row = self.table_unlocated.currentRow()
        afiliado_id = int(self.table_unlocated.item(row, 0).text())
        nombre = self.table_unlocated.item(row, 1).text()
        
        # Guardar ID para callback
        self.selected_afiliado_id = afiliado_id
        
        # Activar herramienta de click
        canvas = self.iface.mapCanvas()
        self.previous_map_tool = canvas.mapTool()
        self.map_tool = MapClickTool(canvas, self.on_ubicar_point_selected)
        canvas.setMapTool(self.map_tool)
        
        # Mensaje
        self.iface.messageBar().pushMessage(
            "ACLIFIM",
            f"Haz click en el mapa para ubicar a '{nombre}'",
            level=0,
            duration=5
        )
        
        print(f"[PLUGIN] Modo ubicación activado para ID {afiliado_id}")
        self.showMinimized()
    
    def on_ubicar_point_selected(self, point):
        """Callback cuando se ubica un afiliado sin coordenadas"""
        from qgis.core import QgsCoordinateTransform, QgsProject, QgsCoordinateReferenceSystem
        
        print(f"[PLUGIN] Punto seleccionado para ubicación: {point.x()}, {point.y()}")
        
        # Obtener datos del afiliado desde la BD
        afiliado = get_afiliado_by_id(self.selected_afiliado_id)
        if not afiliado:
            QMessageBox.critical(self, "Error", "No se encontró el afiliado")
            # Restaurar herramienta
            canvas = self.iface.mapCanvas()
            if hasattr(self, 'previous_map_tool') and self.previous_map_tool:
                canvas.setMapTool(self.previous_map_tool)
            else:
                canvas.unsetMapTool(self.map_tool)
            self.showNormal()
            return
        
        nombre = f"{afiliado['nombres']} {afiliado['apellidos']}"
        
        # Crear marcador temporal
        canvas = self.iface.mapCanvas()
        self.rubber_band = QgsRubberBand(canvas, QgsWkbTypes.PointGeometry)
        self.rubber_band.setColor(QColor(255, 0, 0, 180))
        self.rubber_band.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.rubber_band.setIconSize(5)
        self.rubber_band.setWidth(1)
        self.rubber_band.addPoint(point)
        
        # Confirmar
        reply = QMessageBox.question(
            self,
            "Confirmar ubicación",
            f"¿Ubicar a '{nombre}' en estas coordenadas?\n\n"
            f"Lon: {point.x():.6f}\nLat: {point.y():.6f}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        # Limpiar marcador
        if self.rubber_band:
            canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None
        
        if reply == QMessageBox.Yes:
            # Transformar coordenadas
            canvas_crs = canvas.mapSettings().destinationCrs()
            target_crs = QgsCoordinateReferenceSystem("EPSG:4326")
            
            if canvas_crs != target_crs:
                transform = QgsCoordinateTransform(canvas_crs, target_crs, QgsProject.instance())
                transformed_point = transform.transform(point)
            else:
                transformed_point = point
            
            # Actualizar en BD
            success, msg = update_afiliado_coordinates(self.selected_afiliado_id, transformed_point)
            
            if success:
                QMessageBox.information(self, "Éxito", f"Afiliado '{nombre}' ubicado correctamente")
                self.load_all_afiliados()
                self.load_unlocated_afiliados()  # Actualizar lista de sin ubicar
                self.refresh_layer()
            else:
                QMessageBox.critical(self, "Error", msg)
        
        # Restaurar herramienta
        if hasattr(self, 'previous_map_tool') and self.previous_map_tool:
            canvas.setMapTool(self.previous_map_tool)
        else:
            canvas.unsetMapTool(self.map_tool)
        
        self.showNormal()
        self.activateWindow()
    
    def load_afiliados_layer(self):
        """Carga o recarga la capa de afiliados desde PostGIS"""
        try:
            layer = force_reload_afiliados_layer()
            if layer:
                try:
                    node = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
                    if node:
                        node.setItemVisibilityChecked(True)
                except Exception:
                    pass
                print(f"[PLUGIN] Capa de afiliados lista: {layer.featureCount()} features")
            else:
                print("[PLUGIN] No se pudo cargar la capa de afiliados")
            return layer
        except Exception as e:
            print(f"[PLUGIN] Error al cargar capa de afiliados: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def load_centros_layer(self):
        """Carga o recarga la capa de centros de interés desde PostGIS"""
        try:
            from ..modules.map_tools import get_or_create_centros_layer
            layer = get_or_create_centros_layer()
            
            if layer:
                print(f"[PLUGIN] Capa de centros cargada: {layer.name()}")
                print(f"[PLUGIN] Tipo de proveedor: {layer.providerType()}")
                print(f"[PLUGIN] Features en capa: {layer.featureCount()}")
                
                # Si es PostGIS, recargar datos desde la BD
                if layer.providerType() == "postgres":
                    layer.dataProvider().reloadData()
                    layer.updateExtents()
                    layer.triggerRepaint()
                    print("[PLUGIN] Datos de centros recargados desde PostGIS")

                try:
                    node = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
                    if node:
                        node.setItemVisibilityChecked(True)
                except Exception:
                    pass
                
                self.iface.mapCanvas().refresh()
                return layer
            else:
                print("[PLUGIN] No se pudo cargar la capa de centros")
                return None
                
        except Exception as e:
            print(f"[PLUGIN] Error al cargar capa de centros: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def refresh_layer(self):
        """Refresca las capas de afiliados y centros de interés"""
        self.load_afiliados_layer()
        self.load_centros_layer()
        self._apply_map_highlight()

    def _apply_map_highlight(self):
        """Aplica resaltado en mapa priorizando el buffer sobre la búsqueda."""
        if self.buffer_highlight_ids:
            highlight_afiliados_by_ids(self.buffer_highlight_ids)
            return

        if self.search_highlight_ids:
            highlight_afiliados_by_ids(self.search_highlight_ids)
            return

        clear_afiliados_highlight()

    def limpiar_buffer_centro(self):
        """Limpia visual y resultados del buffer de centros."""
        if self.buffer_rubber_band:
            try:
                self.iface.mapCanvas().scene().removeItem(self.buffer_rubber_band)
            except Exception:
                pass
            self.buffer_rubber_band = None

        self.buffer_highlight_ids = []
        self.table_buffer_afiliados.setRowCount(0)
        self.label_buffer_resultados.setText("Buffer: sin análisis")
        self._apply_map_highlight()
        self.iface.mapCanvas().refresh()

    def generar_buffer_centro(self):
        """Genera un buffer alrededor del centro seleccionado y lista afiliados dentro."""
        selected_rows = self.table_centros.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Advertencia", "Selecciona un centro de interés primero")
            return

        row = selected_rows[0].row()
        centro_id = int(self.table_centros.item(row, 0).text())
        radio_metros = self.buffer_radio_metros.value()

        centro = get_centro_by_id(centro_id)
        if not centro or centro.get('lon') is None or centro.get('lat') is None:
            QMessageBox.warning(self, "Advertencia", "El centro seleccionado no tiene coordenadas válidas")
            return

        self.limpiar_buffer_centro()

        self.buffer_rubber_band = draw_centro_buffer(
            self.iface,
            centro['lon'],
            centro['lat'],
            radio_metros
        )

        if not self.buffer_rubber_band:
            QMessageBox.warning(
                self,
                "Advertencia",
                "No se pudo dibujar el área del buffer en el mapa."
            )

        afiliados = get_afiliados_en_radio_centro(centro_id, radio_metros)
        self.table_buffer_afiliados.setRowCount(0)

        for afiliado in afiliados:
            table_row = self.table_buffer_afiliados.rowCount()
            self.table_buffer_afiliados.insertRow(table_row)

            self.table_buffer_afiliados.setItem(table_row, 0, QTableWidgetItem(str(afiliado['id'])))
            self.table_buffer_afiliados.setItem(table_row, 1, QTableWidgetItem(afiliado.get('carnet_id', '')))
            self.table_buffer_afiliados.setItem(table_row, 2, QTableWidgetItem(afiliado.get('nombres', '')))
            self.table_buffer_afiliados.setItem(table_row, 3, QTableWidgetItem(afiliado.get('apellidos', '')))

            distancia = afiliado.get('distancia_m')
            distancia_txt = f"{distancia:.1f}" if distancia is not None else ""
            self.table_buffer_afiliados.setItem(table_row, 4, QTableWidgetItem(distancia_txt))
            self.table_buffer_afiliados.setItem(table_row, 5, QTableWidgetItem(afiliado.get('direccion', '')))

        centro_nombre = centro.get('nombre', f"ID {centro_id}")
        self.label_buffer_resultados.setText(
            f"Buffer '{centro_nombre}' ({radio_metros} m): {len(afiliados)} afiliados"
        )

        self.buffer_highlight_ids = [a['id'] for a in afiliados]
        self._apply_map_highlight()

        if self.buffer_rubber_band:
            buffer_geom = self.buffer_rubber_band.asGeometry()
            if buffer_geom and not buffer_geom.isNull():
                self.iface.mapCanvas().setExtent(buffer_geom.boundingBox())

        self.iface.mapCanvas().refresh()
    
    # --- Métodos de acciones ---

    def activar_modo_click(self):
        print("[PLUGIN] Activando modo click")
        canvas = self.iface.mapCanvas()
        self.previous_map_tool = canvas.mapTool()  # Guardar herramienta actual
        self.map_tool = MapClickTool(canvas, self.on_point_selected)
        canvas.setMapTool(self.map_tool)
        
        # Mostrar mensaje al usuario
        self.iface.messageBar().pushMessage(
            "ACLIFIM",
            "Haz click en el mapa para ubicar al afiliado",
            level=0,  # Info
            duration=5
        )
        
        self.close()  # Cerrar el diálogo al activar el modo click

    def on_point_selected(self, point):
        print("[PLUGIN] Procesando punto seleccionado")
        
        # Crear marcador temporal (rubber band) para mostrar donde se agregará el punto
        canvas = self.iface.mapCanvas()
        self.rubber_band = QgsRubberBand(canvas, QgsWkbTypes.PointGeometry)
        self.rubber_band.setColor(QColor(255, 0, 0, 180))  # Rojo con transparencia
        self.rubber_band.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.rubber_band.setIconSize(5)  # Tamaño más pequeño para que coincida con los puntos de la capa
        self.rubber_band.setWidth(1)
        self.rubber_band.addPoint(point)
        
        print("[PLUGIN] Marcador temporal creado en el mapa")
        
        # Mostrar formulario para ingresar datos
        form = AfiliadoForm()
        result = form.exec_()
        
        # Limpiar el rubber band después del formulario
        if self.rubber_band:
            canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None
            print("[PLUGIN] Marcador temporal eliminado")
        
        if result == QDialog.Accepted:
            # Obtener datos del formulario
            data = form.get_data()
            
            # Validar que al menos el nombre esté lleno
            if not data['nombre'].strip():
                QMessageBox.warning(
                    None,
                    "Advertencia",
                    "El campo 'Nombre' es obligatorio"
                )
                return
            
            # Agregar el punto con los datos
            success = add_point_with_data(point, data)
            
            if success:
                self.iface.messageBar().pushMessage(
                    "ACLIFIM",
                    f"Afiliado '{data['nombre']}' agregado exitosamente",
                    level=3,  # Success
                    duration=3
                )
            else:
                QMessageBox.critical(
                    None,
                    "Error",
                    "No se pudo agregar el afiliado"
                )
        else:
            print("[PLUGIN] Usuario canceló, punto no agregado")
        
        # Restaurar herramienta anterior
        if hasattr(self, 'previous_map_tool') and self.previous_map_tool:
            canvas.setMapTool(self.previous_map_tool)
        else:
            canvas.unsetMapTool(self.map_tool)
    
    def activar_modo_nativo(self):
        """
        Método alternativo: usa las herramientas nativas de QGIS
        Activa el modo de edición de la capa y la herramienta de agregar puntos
        """
        from ..modules.map_tools import get_or_create_layer
        
        # Obtener o crear la capa
        layer = get_or_create_layer()
        
        # Hacer la capa activa
        self.iface.setActiveLayer(layer)
        
        # Activar modo de edición
        if not layer.isEditable():
            layer.startEditing()
            print("[PLUGIN] Modo de edición activado")
        
        # Activar la herramienta de agregar puntos de QGIS
        self.iface.actionAddFeature().trigger()
        
        # Mostrar mensaje
        self.iface.messageBar().pushMessage(
            "ACLIFIM",
            "Haz click en el mapa para ubicar al afiliado. Rellena el formulario que aparecerá.",
            level=0,
            duration=5
        )
        
        print("[PLUGIN] Herramienta nativa de agregar puntos activada")
        
        self.close()
    
    def show_db_config(self):
        """Muestra el diálogo de configuración de base de datos"""
        dialog = DatabaseConfigDialog(self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.refresh_layer()
            self.load_all_afiliados()
            self.load_centros_interes()
            self.iface.messageBar().pushMessage(
                "ACLIFIM",
                "Configuración guardada y capas recargadas",
                level=3,  # Success
                duration=3
            )
            print("[PLUGIN] Configuración de BD actualizada")
    
    def importar_desde_access(self):
        """Importa datos desde un archivo Access con soporte para contraseñas"""
        from qgis.PyQt.QtWidgets import QInputDialog, QLineEdit
        
        # Abrir diálogo para seleccionar archivo
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar base de datos Access",
            "",
            "Access Database (*.mdb *.accdb)"
        )
        
        if not file_path:
            return
        
        print(f"[PLUGIN] Archivo seleccionado: {file_path}")
        
        # Intentar conexión sin contraseña primero
        importer = AccessImporter(file_path)
        password = None
        
        # Intentar conectar para verificar si necesita contraseña
        success, msg = importer.connect_to_access()
        
        # Si falla, verificar si es por contraseña
        if not success:
            msg_lower = msg.lower()
            if "password" in msg_lower or "contraseña" in msg_lower or "cannot open" in msg_lower:
                # Pedir contraseña al usuario
                password, ok = QInputDialog.getText(
                    self,
                    "Contraseña Requerida",
                    "La base de datos Access está protegida con contraseña.\n\n"
                    "Ingrese la contraseña:",
                    QLineEdit.Password
                )
                
                if not ok or not password:
                    importer.close()
                    return
                
                # Reintentar con contraseña
                success, msg = importer.connect_to_access(password=password)
                
                if not success:
                    QMessageBox.critical(
                        self,
                        "Error de Conexión",
                        f"No se pudo conectar con la contraseña proporcionada:\n\n{msg}\n\n"
                        "Verifica que:\n"
                        "• La contraseña sea correcta\n"
                        "• Tengas instalado el controlador ODBC de Microsoft Access\n"
                        "• La base de datos no esté corrupta"
                    )
                    importer.close()
                    return
            else:
                # Error diferente (no relacionado con contraseña)
                QMessageBox.critical(
                    self,
                    "Error de Conexión",
                    f"No se pudo conectar a la base de datos Access:\n\n{msg}\n\n"
                    "Verifica que tengas instalado el controlador ODBC de Microsoft Access.\n"
                    "Consulta TROUBLESHOOTING.md para más ayuda."
                )
                importer.close()
                return
        
        # Cerrar la conexión de prueba
        importer.close()
        
        # Ahora usar el método automático completo con la contraseña (si la hay)
        print(f"[PLUGIN] Iniciando importación automática{' con contraseña' if password else ''}...")
        
        # Crear diálogo de progreso
        progress = QProgressDialog("Conectando a Access...", "Cancelar", 0, 5, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        progress.setMinimumWidth(450)
        progress.setFixedHeight(120)
        progress.show()
        
        # Variable para controlar cancelación
        cancelled = [False]
        
        # Función callback para actualizar progreso
        def update_progress(current, total, message):
            if progress.wasCanceled():
                cancelled[0] = True
                raise Exception("Importación cancelada por el usuario")
            progress.setMaximum(total)
            progress.setValue(current)
            progress.setLabelText(message)
            # Procesar eventos para que la UI se actualice
            from qgis.PyQt.QtWidgets import QApplication
            QApplication.processEvents()
        
        # Ejecutar importación automática
        importer = AccessImporter(file_path)
        try:
            success, result = importer.auto_detect_and_import(
                password=password,
                progress_callback=update_progress
            )
        except Exception as e:
            progress.close()
            if cancelled[0]:
                QMessageBox.information(
                    self,
                    "Importación Cancelada",
                    "La importación fue cancelada por el usuario."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error durante la importación:\n\n{str(e)}"
                )
            return
        
        progress.close()
        
        if success:
            # Mostrar estadísticas
            stats = result
            mensaje = (
                f"✅ Importación completada exitosamente\n\n"
                f"📊 Estadísticas:\n"
                f"  • Nuevos: {stats['nuevos']}\n"
                f"  • Actualizados: {stats['actualizados']}\n"
                f"  • Cambios de dirección: {stats['cambios_direccion']}\n"
                f"  • Eliminados (bajas): {stats['eliminados']}\n"
                f"  • Total procesados: {stats['total_procesados']}\n"
            )
            
            if stats['errores'] > 0:
                mensaje += f"  ⚠️ Errores: {stats['errores']}\n"
            
            if stats['nuevos'] > 0 or stats['cambios_direccion'] > 0:
                mensaje += f"\n💡 Ve a la pestaña 'Sin Ubicar' para ubicar los afiliados en el mapa."
            
            QMessageBox.information(
                self,
                "Importación Exitosa",
                mensaje
            )
            print(f"[PLUGIN] Importación exitosa: {stats}")
            
            # Actualizar tabla
            self.load_all_afiliados()
        else:
            QMessageBox.critical(
                self,
                "Error en Importación",
                f"No se pudo completar la importación:\n\n{result}"
            )
            print(f"[PLUGIN] Error en importación: {result}")
    
    # ============================================================
    # MÉTODOS PARA GESTIÓN DE CENTROS DE INTERÉS
    # ============================================================
    
    def load_centros_interes(self):
        """Carga todos los centros de interés en la tabla"""
        try:
            # Obtener filtros
            nombre_filtro = self.filter_centro_nombre.text().strip()
            tipo_filtro = self.filter_centro_tipo.text().strip()
            
            # Buscar centros
            if nombre_filtro or tipo_filtro:
                centros = search_centros_interes(nombre_filtro, tipo_filtro)
            else:
                centros = get_all_centros_interes()
            
            # Limpiar tabla
            self.table_centros.setRowCount(0)
            
            # Llenar tabla
            for centro in centros:
                row = self.table_centros.rowCount()
                self.table_centros.insertRow(row)
                
                # ID
                self.table_centros.setItem(row, 0, QTableWidgetItem(str(centro['id'])))
                
                # Nombre
                self.table_centros.setItem(row, 1, QTableWidgetItem(centro['nombre']))
                
                # Tipo
                self.table_centros.setItem(row, 2, QTableWidgetItem(centro['tipo']))
                
                # Dirección
                direccion = centro.get('direccion', '') or ''
                self.table_centros.setItem(row, 3, QTableWidgetItem(direccion))
                
                # Coordenadas
                if centro.get('lon') and centro.get('lat'):
                    coords = f"{centro['lon']:.6f}, {centro['lat']:.6f}"
                else:
                    coords = "Sin coordenadas"
                self.table_centros.setItem(row, 4, QTableWidgetItem(coords))
            
            # Actualizar contador
            self.label_centros_resultados.setText(f"Total: {len(centros)} centros")
            print(f"[PLUGIN] {len(centros)} centros cargados")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron cargar los centros de interés:\n{str(e)}"
            )
            print(f"[PLUGIN] Error al cargar centros: {e}")
    
    def buscar_centros(self):
        """Busca centros con los filtros aplicados"""
        self.load_centros_interes()
    
    def limpiar_filtros_centros(self):
        """Limpia los filtros de búsqueda"""
        self.filter_centro_nombre.clear()
        self.filter_centro_tipo.clear()
        self.load_centros_interes()
    
    def on_centro_selection_changed(self):
        """Habilita o deshabilita botones según la selección"""
        has_selection = len(self.table_centros.selectedItems()) > 0
        self.btn_editar_centro.setEnabled(has_selection)
        self.btn_eliminar_centro.setEnabled(has_selection)
    
    def agregar_centro_click(self):
        """Activa el modo de hacer clic en el mapa para agregar un centro"""
        QMessageBox.information(
            self,
            "Seleccionar ubicación",
            "Haz clic en el mapa para seleccionar la ubicación del nuevo centro de interés."
        )
        
        # Cambiar a herramienta de clic en mapa
        self.centro_tool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.centro_tool.canvasClicked.connect(self.on_centro_map_clicked)
        self.iface.mapCanvas().setMapTool(self.centro_tool)
        print("[PLUGIN] Modo agregar centro activado")
    
    def on_centro_map_clicked(self, point, button):
        """Callback cuando se hace clic en el mapa para agregar centro"""
        try:
            # Restaurar herramienta predeterminada
            self.iface.mapCanvas().unsetMapTool(self.centro_tool)
            
            # Abrir formulario de centro
            dialog = CentroInteresForm(point)
            if dialog.exec_():
                # Obtener datos
                data = dialog.get_data()
                
                # Guardar en BD
                success, msg = create_centro_interes(
                    data['nombre'],
                    data['tipo'],
                    data['descripcion'],
                    data['direccion'],
                    point
                )
                
                if success:
                    QMessageBox.information(
                        self,
                        "Centro Agregado",
                        f"El centro '{data['nombre']}' ha sido agregado exitosamente."
                    )
                    print(f"[PLUGIN] Centro agregado: {data['nombre']}")
                    
                    # Recargar tabla
                    self.load_centros_interes()
                    
                    # Actualizar capa
                    self.refresh_layer()
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"No se pudo agregar el centro:\n{msg}"
                    )
                    print(f"[PLUGIN] Error al agregar centro: {msg}")
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al agregar centro:\n{str(e)}"
            )
            print(f"[PLUGIN] Error en on_centro_map_clicked: {e}")
    
    def editar_centro(self):
        """Edita el centro seleccionado"""
        selected_rows = self.table_centros.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        try:
            # Obtener ID del centro
            row = selected_rows[0].row()
            centro_id = int(self.table_centros.item(row, 0).text())
            
            # Obtener datos completos del centro
            centro = get_centro_by_id(centro_id)
            if not centro:
                QMessageBox.warning(self, "Error", "No se encontró el centro")
                return
            
            # Crear punto con coordenadas actuales
            point = QgsPointXY(centro['lon'], centro['lat'])
            
            # Abrir formulario de edición
            dialog = CentroInteresForm(point, centro_data=centro)
            if dialog.exec_():
                # Obtener datos actualizados
                data = dialog.get_data()
                
                # Actualizar en BD
                success, msg = update_centro_interes(
                    centro_id,
                    data['nombre'],
                    data['tipo'],
                    data['descripcion'],
                    data['direccion'],
                    point
                )
                
                if success:
                    QMessageBox.information(
                        self,
                        "Centro Actualizado",
                        f"El centro ha sido actualizado exitosamente."
                    )
                    print(f"[PLUGIN] Centro actualizado: {centro_id}")
                    
                    # Recargar tabla
                    self.load_centros_interes()
                    
                    # Actualizar capa
                    self.refresh_layer()
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"No se pudo actualizar el centro:\n{msg}"
                    )
                    print(f"[PLUGIN] Error al actualizar centro: {msg}")
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al editar centro:\n{str(e)}"
            )
            print(f"[PLUGIN] Error en editar_centro: {e}")
    
    def eliminar_centro(self):
        """Elimina el centro seleccionado"""
        selected_rows = self.table_centros.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        try:
            # Obtener datos del centro
            row = selected_rows[0].row()
            centro_id = int(self.table_centros.item(row, 0).text())
            nombre = self.table_centros.item(row, 1).text()
            
            # Confirmar eliminación
            reply = QMessageBox.question(
                self,
                "Confirmar Eliminación",
                f"¿Está seguro de que desea eliminar el centro '{nombre}'?\n\nEsta acción no se puede deshacer.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Eliminar de BD
                success, msg = delete_centro_interes(centro_id)
                
                if success:
                    QMessageBox.information(
                        self,
                        "Centro Eliminado",
                        f"El centro ha sido eliminado exitosamente."
                    )
                    print(f"[PLUGIN] Centro eliminado: {centro_id}")
                    
                    # Recargar tabla
                    self.load_centros_interes()
                    
                    # Actualizar capa
                    self.refresh_layer()
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"No se pudo eliminar el centro:\n{msg}"
                    )
                    print(f"[PLUGIN] Error al eliminar centro: {msg}")
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al eliminar centro:\n{str(e)}"
            )
            print(f"[PLUGIN] Error en eliminar_centro: {e}")
