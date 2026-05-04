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
    QWidget
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont


class DetalleAfiliadoDialog(QDialog):
    """Muestra todos los detalles de un afiliado"""
    
    def __init__(self, afiliado, parent=None):
        super().__init__(parent)
        self.afiliado = afiliado
        self.setWindowTitle(f"Detalles del Afiliado - {afiliado.get('nombres', '')} {afiliado.get('apellidos', '')}")
        self.resize(700, 600)
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        main_layout = QVBoxLayout()
        
        # Título
        title = QLabel(f"📋 Información Completa del Afiliado")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Scroll area para todo el contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Grupo 1: Identificación
        scroll_layout.addWidget(self.create_identificacion_group())
        
        # Grupo 2: Datos Demográficos
        scroll_layout.addWidget(self.create_demograficos_group())
        
        # Grupo 3: Ubicación y Contacto
        scroll_layout.addWidget(self.create_ubicacion_group())
        
        # Grupo 4: Datos Familiares
        scroll_layout.addWidget(self.create_familiares_group())
        
        # Grupo 5: Datos Médicos
        scroll_layout.addWidget(self.create_medicos_group())
        
        # Grupo 6: Datos Laborales/Educativos
        scroll_layout.addWidget(self.create_laborales_group())
        
        # Grupo 7: Organización
        scroll_layout.addWidget(self.create_organizacion_group())
        
        # Grupo 8: Fechas Administrativas
        scroll_layout.addWidget(self.create_fechas_group())
        
        # Grupo 9: Estado del Sistema
        scroll_layout.addWidget(self.create_estado_group())
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        # Botón cerrar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        btn_cerrar.setMinimumWidth(100)
        btn_layout.addWidget(btn_cerrar)
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
    
    def create_identificacion_group(self):
        """Grupo de identificación"""
        group = QGroupBox("👤 Identificación")
        layout = QGridLayout()
        
        row = 0
        self.add_field(layout, row, "Código:", self.afiliado.get('codigo'))
        self.add_field(layout, row, "CI (Carnet):", self.afiliado.get('carnet_id'), col_offset=2)
        
        row += 1
        self.add_field(layout, row, "Folio:", self.afiliado.get('folio'))
        self.add_field(layout, row, "ID Sistema:", self.afiliado.get('id'), col_offset=2)
        
        row += 1
        self.add_field(layout, row, "Nombres:", self.afiliado.get('nombres'), span=3)
        
        row += 1
        self.add_field(layout, row, "Apellidos:", self.afiliado.get('apellidos'), span=3)
        
        group.setLayout(layout)
        return group
    
    def create_demograficos_group(self):
        """Grupo de datos demográficos"""
        group = QGroupBox("🌍 Datos Demográficos")
        layout = QGridLayout()
        
        row = 0
        self.add_field(layout, row, "Sexo:", self.afiliado.get('sexo'))
        self.add_field(layout, row, "Edad:", self.afiliado.get('edad'), col_offset=2)
        
        row += 1
        fecha_nac = self.format_date(self.afiliado.get('fecha_nacimiento'))
        self.add_field(layout, row, "Fecha Nacimiento:", fecha_nac, span=3)
        
        row += 1
        self.add_field(layout, row, "Lugar Nacimiento:", self.afiliado.get('lugar_nacimiento'), span=3)
        
        row += 1
        self.add_field(layout, row, "Nacionalidad:", self.afiliado.get('nacionalidad'))
        self.add_field(layout, row, "Ciudadanía:", self.afiliado.get('ciudadania'), col_offset=2)
        
        group.setLayout(layout)
        return group
    
    def create_ubicacion_group(self):
        """Grupo de ubicación y contacto"""
        group = QGroupBox("📍 Ubicación y Contacto")
        layout = QGridLayout()
        
        row = 0
        self.add_field(layout, row, "Dirección:", self.afiliado.get('direccion'), span=3)
        
        row += 1
        self.add_field(layout, row, "Reparto:", self.afiliado.get('reparto'))
        self.add_field(layout, row, "Locación:", self.afiliado.get('locacion'), col_offset=2)
        
        row += 1
        self.add_field(layout, row, "Teléfono:", self.afiliado.get('telefono'))
        self.add_field(layout, row, "Tipo Tel.:", self.afiliado.get('tipo_telefono'), col_offset=2)
        
        row += 1
        lon = self.afiliado.get('lon')
        lat = self.afiliado.get('lat')
        coordenadas = f"{lon:.6f}, {lat:.6f}" if lon and lat else "Sin ubicar"
        self.add_field(layout, row, "Coordenadas:", coordenadas, span=3)
        
        group.setLayout(layout)
        return group
    
    def create_familiares_group(self):
        """Grupo de datos familiares"""
        group = QGroupBox("👨‍👩‍👧‍👦 Datos Familiares")
        layout = QGridLayout()
        
        row = 0
        self.add_field(layout, row, "Hijo de:", self.afiliado.get('hijo_de'), span=3)
        
        row += 1
        self.add_field(layout, row, "Estado Civil:", self.afiliado.get('estado_civil'))
        self.add_field(layout, row, "N° Hijos:", self.afiliado.get('no_hijos'), col_offset=2)
        
        row += 1
        self.add_field(layout, row, "Conviventes:", self.afiliado.get('conviventes'))
        self.add_field(layout, row, "Personas Dep.:", self.afiliado.get('no_personas_dep'), col_offset=2)
        
        group.setLayout(layout)
        return group
    
    def create_medicos_group(self):
        """Grupo de datos médicos"""
        group = QGroupBox("🏥 Datos Médicos / Discapacidad")
        layout = QGridLayout()
        
        row = 0
        self.add_field(layout, row, "Limitación:", self.afiliado.get('limitacion'))
        self.add_field(layout, row, "Código:", self.afiliado.get('limitacion_cod'), col_offset=2)
        
        row += 1
        self.add_field(layout, row, "Nivel Ambulación:", self.afiliado.get('nivel_ambulacion'))
        self.add_field(layout, row, "Código:", self.afiliado.get('ambulacion_cod'), col_offset=2)
        
        row += 1
        self.add_field(layout, row, "Causa:", self.afiliado.get('causa'), span=3)
        
        row += 1
        self.add_field(layout, row, "Discap. Asociada:", self.afiliado.get('discap_asociada'), span=3)
        
        group.setLayout(layout)
        return group
    
    def create_laborales_group(self):
        """Grupo de datos laborales y educativos"""
        group = QGroupBox("💼 Datos Laborales y Educativos")
        layout = QGridLayout()
        
        row = 0
        self.add_field(layout, row, "Ocupación:", self.afiliado.get('ocupacion'), span=3)
        
        row += 1
        self.add_field(layout, row, "Centro Trabajo/Estudio:", self.afiliado.get('centro_trabajo'), span=3)
        
        row += 1
        ingreso = self.afiliado.get('ingreso_mensual')
        ingreso_str = f"${ingreso:.2f}" if ingreso else "No especificado"
        self.add_field(layout, row, "Ingreso Mensual:", ingreso_str)
        
        row += 1
        self.add_field(layout, row, "Grado Escolar:", self.afiliado.get('grado_escolar'))
        self.add_field(layout, row, "Especialidad:", self.afiliado.get('especialidad'), col_offset=2)
        
        group.setLayout(layout)
        return group
    
    def create_organizacion_group(self):
        """Grupo de datos de organización"""
        group = QGroupBox("🏛️ Organización ACLIFIM")
        layout = QGridLayout()
        
        row = 0
        self.add_field(layout, row, "Área:", self.afiliado.get('area'))
        cuota = self.afiliado.get('cuota')
        cuota_str = f"${cuota:.2f}" if cuota else "No especificado"
        self.add_field(layout, row, "Cuota:", cuota_str, col_offset=2)
        
        row += 1
        self.add_field(layout, row, "Jefe de Núcleo:", self.afiliado.get('jefe_nucleo'))
        self.add_field(layout, row, "Org. Rev.:", self.afiliado.get('org_rev'), col_offset=2)
        
        group.setLayout(layout)
        return group
    
    def create_fechas_group(self):
        """Grupo de fechas administrativas"""
        group = QGroupBox("📅 Fechas Administrativas")
        layout = QGridLayout()
        
        row = 0
        fecha_ingr = self.format_date(self.afiliado.get('fecha_ingreso'))
        self.add_field(layout, row, "Fecha Ingreso:", fecha_ingr)
        
        fecha_alta = self.format_date(self.afiliado.get('fecha_alta'))
        self.add_field(layout, row, "Fecha Alta:", fecha_alta, col_offset=2)
        
        row += 1
        fecha_baja = self.format_date(self.afiliado.get('fecha_baja'))
        self.add_field(layout, row, "Fecha Baja:", fecha_baja)
        self.add_field(layout, row, "Motivo Baja:", self.afiliado.get('motivo_baja'), col_offset=2)
        
        group.setLayout(layout)
        return group
    
    def create_estado_group(self):
        """Grupo de estado del sistema"""
        group = QGroupBox("⚙️ Estado del Sistema")
        layout = QGridLayout()
        
        row = 0
        estado = self.afiliado.get('estado', 'normal')
        estado_display = {
            'nuevo': '🆕 Nuevo (sin ubicar)',
            'cambio_direccion': '📍 Cambio de dirección (re-ubicar)',
            'normal': '✅ Normal'
        }.get(estado, estado)
        self.add_field(layout, row, "Estado:", estado_display)
        
        row += 1
        fecha_creacion = self.format_datetime(self.afiliado.get('fecha_creacion'))
        self.add_field(layout, row, "Creado:", fecha_creacion, span=3)
        
        row += 1
        fecha_mod = self.format_datetime(self.afiliado.get('fecha_modificacion'))
        self.add_field(layout, row, "Última Modificación:", fecha_mod, span=3)
        
        group.setLayout(layout)
        return group
    
    def add_field(self, layout, row, label_text, value, col_offset=0, span=1):
        """Agrega un campo al layout"""
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label, row, col_offset)
        
        value_label = QLabel(str(value) if value is not None else "No especificado")
        value_label.setWordWrap(True)
        
        if span > 1:
            layout.addWidget(value_label, row, col_offset + 1, 1, span)
        else:
            layout.addWidget(value_label, row, col_offset + 1)
    
    def format_date(self, date_value):
        """Formatea una fecha"""
        if not date_value:
            return "No especificado"
        
        try:
            if hasattr(date_value, 'strftime'):
                return date_value.strftime('%d/%m/%Y')
            else:
                return str(date_value)
        except:
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
        except:
            return str(datetime_value)
