"""
Formulario para agregar/editar Centro de Interés
"""
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QMessageBox,
    QGroupBox,
    QGridLayout
)
from qgis.PyQt.QtCore import Qt


class CentroInteresForm(QDialog):
    """Formulario para crear o editar un centro de interés"""
    
    def __init__(self, point, centro_data=None, parent=None):
        """
        Args:
            point: QgsPointXY con las coordenadas del centro
            centro_data: dict con datos del centro (para edición) o None (para creación)
            parent: Widget padre
        """
        super().__init__(parent)
        self.point = point
        self.centro_data = centro_data
        self.is_edit_mode = centro_data is not None
        
        self.setWindowTitle("Editar Centro de Interés" if self.is_edit_mode else "Nuevo Centro de Interés")
        self.resize(500, 450)
        
        self.init_ui()
        
        if self.is_edit_mode:
            self.load_data()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        
        # Título
        title_text = "Editar información del centro de interés" if self.is_edit_mode else "Agregar nuevo centro de interés"
        title = QLabel(title_text)
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title)
        
        # Grupo de datos
        group = QGroupBox("Información del Centro")
        group_layout = QGridLayout()
        
        # Nombre
        row = 0
        group_layout.addWidget(QLabel("*Nombre:"), row, 0)
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Ej: Hospital Provincial...")
        group_layout.addWidget(self.input_nombre, row, 1)
        
        # Tipo
        row += 1
        group_layout.addWidget(QLabel("*Tipo:"), row, 0)
        self.input_tipo = QComboBox()
        self.input_tipo.setEditable(True)
        self.input_tipo.addItems([
            "Hospital",
            "Policlínico",
            "Clínica",
            "Escuela",
            "Universidad",
            "Parque",
            "Centro Deportivo",
            "Centro Cultural",
            "Biblioteca",
            "Mercado",
            "Farmacia",
            "Banco",
            "Correos",
            "Oficina Gubernamental",
            "Iglesia",
            "Otro"
        ])
        group_layout.addWidget(self.input_tipo, row, 1)
        
        # Dirección
        row += 1
        group_layout.addWidget(QLabel("Dirección:"), row, 0)
        self.input_direccion = QLineEdit()
        self.input_direccion.setPlaceholderText("Dirección del centro...")
        group_layout.addWidget(self.input_direccion, row, 1)
        
        # Descripción
        row += 1
        group_layout.addWidget(QLabel("Descripción:"), row, 0, Qt.AlignTop)
        self.input_descripcion = QTextEdit()
        self.input_descripcion.setPlaceholderText("Descripción adicional del centro de interés...")
        self.input_descripcion.setMaximumHeight(100)
        group_layout.addWidget(self.input_descripcion, row, 1)
        
        # Coordenadas (solo lectura)
        row += 1
        group_layout.addWidget(QLabel("Coordenadas:"), row, 0)
        coord_text = f"{self.point.x():.6f}, {self.point.y():.6f}"
        self.label_coordenadas = QLabel(coord_text)
        self.label_coordenadas.setStyleSheet("color: #0066cc; font-family: monospace;")
        group_layout.addWidget(self.label_coordenadas, row, 1)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # Nota sobre campos obligatorios
        nota = QLabel("* Campos obligatorios")
        nota.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        layout.addWidget(nota)
        
        layout.addStretch()
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancelar)
        
        self.btn_guardar = QPushButton("Guardar" if self.is_edit_mode else "Crear")
        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_guardar.setDefault(True)
        btn_layout.addWidget(self.btn_guardar)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Carga los datos del centro en modo edición"""
        if not self.centro_data:
            return
        
        self.input_nombre.setText(self.centro_data.get('nombre', ''))
        
        tipo = self.centro_data.get('tipo', '')
        index = self.input_tipo.findText(tipo)
        if index >= 0:
            self.input_tipo.setCurrentIndex(index)
        else:
            self.input_tipo.setEditText(tipo)
        
        self.input_direccion.setText(self.centro_data.get('direccion', ''))
        self.input_descripcion.setText(self.centro_data.get('descripcion', ''))
    
    def guardar(self):
        """Valida y guarda los datos"""
        # Validar campos obligatorios
        nombre = self.input_nombre.text().strip()
        tipo = self.input_tipo.currentText().strip()
        
        if not nombre:
            QMessageBox.warning(self, "Campo Requerido", "El nombre es obligatorio")
            self.input_nombre.setFocus()
            return
        
        if not tipo:
            QMessageBox.warning(self, "Campo Requerido", "El tipo es obligatorio")
            self.input_tipo.setFocus()
            return
        
        # Datos válidos
        self.accept()
    
    def get_data(self):
        """Retorna los datos del formulario"""
        return {
            'nombre': self.input_nombre.text().strip(),
            'tipo': self.input_tipo.currentText().strip(),
            'direccion': self.input_direccion.text().strip(),
            'descripcion': self.input_descripcion.toPlainText().strip()
        }
