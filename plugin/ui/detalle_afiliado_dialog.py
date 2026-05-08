"""
Diálogo para mostrar todos los detalles de un afiliado
"""
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QGroupBox,
    QGridLayout,
    QScrollArea,
    QWidget,
    QTabWidget
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont

# Importar catálogos de códigos
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.catalogos import get_limitacion_descripcion, get_ambulacion_descripcion
from utils.pdf_exporter import PDFExporter


class DetalleAfiliadoDialog(QDialog):
    """Muestra todos los detalles de un afiliado con diseño de pestañas y dos columnas"""
    
    def __init__(self, afiliado, parent=None):
        super().__init__(parent)
        self.afiliado = afiliado
        nombre_completo = f"{afiliado.get('nombres', '')} {afiliado.get('apellidos', '')}".strip()
        self.setWindowTitle(f"📋 Detalles del Afiliado - {nombre_completo or 'Sin nombre'}")
        self.resize(800, 700)
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz con diseño de pestañas"""
        main_layout = QVBoxLayout()
        
        # Título con nombre del afiliado
        nombre_completo = f"{self.afiliado.get('nombres', '')} {self.afiliado.get('apellidos', '')}".strip()
        title = QLabel(f"👤 {nombre_completo or 'Sin nombre'}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        main_layout.addWidget(title)
        
        # Widget de pestañas
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
                font-weight: bold;
            }
        """)
        
        # Pestañas con emojis
        tab_widget.addTab(self.create_tab_identificacion(), "🆔 Identificación")
        tab_widget.addTab(self.create_tab_ubicacion(), "📍 Ubicación")
        tab_widget.addTab(self.create_tab_medicos(), "🏥 Médicos")
        tab_widget.addTab(self.create_tab_familiares(), "👨‍👩‍👧 Familiares")
        tab_widget.addTab(self.create_tab_laborales(), "💼 Laborales")
        tab_widget.addTab(self.create_tab_organizacion(), "🏛️ Organización")
        
        main_layout.addWidget(tab_widget)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # Botón Exportar PDF
        btn_pdf = QPushButton("📄 Exportar PDF")
        btn_pdf.clicked.connect(self.exportar_pdf)
        btn_pdf.setMinimumWidth(140)
        btn_pdf.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_layout.addWidget(btn_pdf)
        
        # Botón Cerrar
        btn_cerrar = QPushButton("✖ Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        btn_cerrar.setMinimumWidth(120)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_layout.addWidget(btn_cerrar)
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
    
    # ============= PESTAÑAS CON 2 COLUMNAS =============
    
    def create_tab_identificacion(self):
        """Pestaña de identificación y datos personales con 2 columnas"""
        widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Grid con 2 columnas
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(15)
        
        row = 0
        # Columna 1 y 2
        self.add_grid_field(grid, row, 0, "Código:", self.afiliado.get('codigo'))
        self.add_grid_field(grid, row, 2, "CI (Carnet):", self.afiliado.get('carnet_id'))
        
        row += 1
        self.add_grid_field(grid, row, 0, "Folio:", self.afiliado.get('folio'))
        self.add_grid_field(grid, row, 2, "ID Sistema:", self.afiliado.get('id'))
        
        row += 1
        self.add_section_title(grid, row, "DATOS PERSONALES")
        
        row += 1
        self.add_grid_field(grid, row, 0, "Nombres:", self.afiliado.get('nombres'))
        self.add_grid_field(grid, row, 2, "Apellidos:", self.afiliado.get('apellidos'))
        
        row += 1
        self.add_grid_field(grid, row, 0, "Sexo:", self.afiliado.get('sexo'))
        self.add_grid_field(grid, row, 2, "Edad:", self.afiliado.get('edad'))
        
        row += 1
        self.add_section_title(grid, row, "NACIMIENTO")
        
        row += 1
        fecha_nac = self.format_date(self.afiliado.get('fecha_nacimiento'))
        self.add_grid_field(grid, row, 0, "Fecha Nacimiento:", fecha_nac)
        self.add_grid_field(grid, row, 2, "Lugar Nacimiento:", self.afiliado.get('lugar_nacimiento'))
        
        row += 1
        self.add_grid_field(grid, row, 0, "Nacionalidad:", self.afiliado.get('nacionalidad'))
        self.add_grid_field(grid, row, 2, "Ciudadanía:", self.afiliado.get('ciudadania'))
        
        main_layout.addLayout(grid)
        main_layout.addStretch()
        widget.setLayout(main_layout)
        
        # Scroll
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        return scroll
    
    def create_tab_ubicacion(self):
        """Pestaña de ubicación con 2 columnas"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(15)
        
        row = 0
        self.add_grid_field(grid, row, 0, "Dirección:", self.afiliado.get('direccion'))
        self.add_grid_field(grid, row, 2, "Reparto:", self.afiliado.get('reparto'))
        
        row += 1
        self.add_grid_field(grid, row, 0, "Locación:", self.afiliado.get('locacion'))
        self.add_grid_field(grid, row, 2, "Teléfono:", self.afiliado.get('telefono'))
        
        row += 1
        self.add_grid_field(grid, row, 0, "Tipo Teléfono:", self.afiliado.get('tipo_telefono'))
        
        row += 1
        self.add_separator(grid, row)
        
        row += 1
        lon = self.afiliado.get('lon')
        lat = self.afiliado.get('lat')
        if lon and lat:
            self.add_grid_field(grid, row, 0, "Longitud:", f"{lon:.6f}")
            self.add_grid_field(grid, row, 2, "Latitud:", f"{lat:.6f}")
        else:
            self.add_grid_field(grid, row, 0, "Coordenadas GPS:", "Sin ubicar")
        
        layout.addLayout(grid)
        layout.addStretch()
        widget.setLayout(layout)
        
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        return scroll
    
    def create_tab_medicos(self):
        """Pestaña de datos médicos con 2 columnas"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(15)
        
        row = 0
        # Limitación - mostrar descripción legible
        limitacion_cod = self.afiliado.get('limitacion_cod') or self.afiliado.get('limitacion')
        limitacion_desc = get_limitacion_descripcion(limitacion_cod)
        self.add_grid_field(grid, row, 0, "Limitación:", limitacion_desc)
        
        # Ambulación - mostrar descripción legible
        ambulacion_cod = self.afiliado.get('ambulacion_cod') or self.afiliado.get('nivel_ambulacion')
        ambulacion_desc = get_ambulacion_descripcion(ambulacion_cod)
        self.add_grid_field(grid, row, 2, "Nivel Ambulación:", ambulacion_desc)
        
        row += 1
        self.add_separator(grid, row)
        
        row += 1
        self.add_grid_field(grid, row, 0, "Causa:", self.afiliado.get('causa'))
        self.add_grid_field(grid, row, 2, "Discapacidad Asociada:", self.afiliado.get('discap_asociada'))
        
        layout.addLayout(grid)
        layout.addStretch()
        widget.setLayout(layout)
        
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        return scroll
    
    def create_tab_familiares(self):
        """Pestaña de datos familiares con 2 columnas"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(15)
        
        row = 0
        self.add_grid_field(grid, row, 0, "Hijo de:", self.afiliado.get('hijo_de'))
        self.add_grid_field(grid, row, 2, "Estado Civil:", self.afiliado.get('estado_civil'))
        
        row += 1
        self.add_grid_field(grid, row, 0, "Número de Hijos:", self.afiliado.get('no_hijos'))
        self.add_grid_field(grid, row, 2, "Conviventes:", self.afiliado.get('conviventes'))
        
        row += 1
        self.add_grid_field(grid, row, 0, "Personas Dependientes:", self.afiliado.get('no_personas_dep'))
        
        layout.addLayout(grid)
        layout.addStretch()
        widget.setLayout(layout)
        
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        return scroll
    
    def create_tab_laborales(self):
        """Pestaña de datos laborales y educativos con 2 columnas"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(15)
        
        row = 0
        self.add_grid_field(grid, row, 0, "Ocupación:", self.afiliado.get('ocupacion'))
        self.add_grid_field(grid, row, 2, "Centro Trabajo/Estudio:", self.afiliado.get('centro_trabajo'))
        
        row += 1
        ingreso = self.afiliado.get('ingreso_mensual')
        ingreso_str = f"${ingreso:.2f}" if ingreso else "No especificado"
        self.add_grid_field(grid, row, 0, "Ingreso Mensual:", ingreso_str)
        
        row += 1
        self.add_separator(grid, row)
        
        row += 1
        self.add_grid_field(grid, row, 0, "Grado Escolar:", self.afiliado.get('grado_escolar'))
        self.add_grid_field(grid, row, 2, "Especialidad:", self.afiliado.get('especialidad'))
        
        layout.addLayout(grid)
        layout.addStretch()
        widget.setLayout(layout)
        
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        return scroll
    
    def create_tab_organizacion(self):
        """Pestaña de datos de organización y administrativos con 2 columnas"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(15)
        
        row = 0
        self.add_grid_field(grid, row, 0, "Área:", self.afiliado.get('area'))
        self.add_grid_field(grid, row, 2, "Jefe de Núcleo:", self.afiliado.get('jefe_nucleo'))
        
        row += 1
        cuota = self.afiliado.get('cuota')
        cuota_str = f"${cuota:.2f}" if cuota else "No especificado"
        self.add_grid_field(grid, row, 0, "Cuota:", cuota_str)
        
        row += 1
        self.add_separator(grid, row)
        
        row += 1
        fecha_ingr = self.format_date(self.afiliado.get('fecha_ingreso'))
        self.add_grid_field(grid, row, 0, "Fecha Ingreso:", fecha_ingr)
        
        fecha_alta = self.format_date(self.afiliado.get('fecha_alta'))
        self.add_grid_field(grid, row, 2, "Fecha Alta:", fecha_alta)
        
        row += 1
        fecha_baja = self.format_date(self.afiliado.get('fecha_baja'))
        self.add_grid_field(grid, row, 0, "Fecha Baja:", fecha_baja)
        self.add_grid_field(grid, row, 2, "Motivo Baja:", self.afiliado.get('motivo_baja'))
        
        row += 1
        self.add_separator(grid, row)
        
        row += 1
        estado = self.afiliado.get('estado', 'normal')
        estado_display = {
            'nuevo': '🆕 Nuevo (sin ubicar)',
            'cambio_direccion': '📍 Cambio de dirección (re-ubicar)',
            'normal': '✅ Normal'
        }.get(estado, estado)
        self.add_grid_field(grid, row, 0, "Estado:", estado_display)
        
        row += 1
        fecha_creacion = self.format_datetime(self.afiliado.get('fecha_creacion'))
        self.add_grid_field(grid, row, 0, "Fecha Creación:", fecha_creacion)
        
        row += 1
        fecha_mod = self.format_datetime(self.afiliado.get('fecha_modificacion'))
        self.add_grid_field(grid, row, 0, "Última Modificación:", fecha_mod)
        
        layout.addLayout(grid)
        layout.addStretch()
        widget.setLayout(layout)
        
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        return scroll
    
    # ============= MÉTODOS AUXILIARES PARA GRID =============
    
    def add_grid_field(self, grid, row, col, label_text, value):
        """Agrega un campo al grid (label + valor en columnas específicas)"""
        # Label
        label = QLabel(label_text)
        label_font = QFont()
        label_font.setBold(True)
        label.setFont(label_font)
        label.setStyleSheet("color: #34495e;")
        grid.addWidget(label, row, col)
        
        # Formatear valor
        if value is None or str(value).strip() == '':
            value_text = "No especificado"
            value_style = "color: #95a5a6; font-style: italic;"
        else:
            value_text = str(value)
            value_style = "color: #2c3e50;"
        
        value_label = QLabel(value_text)
        value_label.setWordWrap(True)
        value_label.setStyleSheet(value_style)
        value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        grid.addWidget(value_label, row, col + 1)
    
    def add_section_title(self, grid, row, title_text):
        """Agrega un título de sección que ocupa todas las columnas"""
        title = QLabel(title_text)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title.setFont(title_font)
        title.setStyleSheet("""
            color: #2c3e50; 
            background-color: #ecf0f1; 
            padding: 8px; 
            border-radius: 4px;
            margin-top: 10px;
        """)
        grid.addWidget(title, row, 0, 1, 4)
    
    def add_separator(self, grid, row):
        """Agrega una línea separadora"""
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #bdc3c7; margin: 10px 0;")
        grid.addWidget(separator, row, 0, 1, 4)
    
    def format_date(self, date_value):
        """Formatea una fecha"""
        if not date_value:
            return "No especificado"
        
        try:
            if hasattr(date_value, 'strftime'):
                return date_value.strftime('%d/%m/%Y')
            else:
                return str(date_value)
        except Exception:
            return str(date_value)
    
    def format_datetime(self, datetime_value):
        """Formatea una fecha y hora"""
        if not datetime_value:
            return "No especificado"
        
        try:
            if hasattr(datetime_value, 'strftime'):
                return datetime_value.strftime('%d/%m/%Y %H:%M:%S')
            else:
                return str(datetime_value)
        except Exception:
            return str(datetime_value)
    
    def exportar_pdf(self):
        """Exporta la información del afiliado a PDF"""
        exporter = PDFExporter()
        exporter.export_afiliado(self.afiliado, self)