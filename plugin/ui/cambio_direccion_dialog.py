"""
Diálogo para confirmar cambio de dirección de un afiliado
"""
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QRadioButton,
    QButtonGroup,
    QGroupBox
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont


class CambioDireccionDialog(QDialog):
    """Diálogo para confirmar cambio de dirección con selección de motivo"""
    
    def __init__(self, afiliado_nombre, parent=None):
        super().__init__(parent)
        self.afiliado_nombre = afiliado_nombre
        self.motivo_seleccionado = None
        
        self.setWindowTitle("⚠️ Cambio de Dirección")
        self.setModal(True)
        self.resize(500, 350)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Título del afiliado
        titulo = QLabel(f"Cambio de dirección para:")
        titulo.setStyleSheet("color: #2c3e50; font-size: 11pt;")
        layout.addWidget(titulo)
        
        nombre_label = QLabel(f"👤 {self.afiliado_nombre}")
        nombre_font = QFont()
        nombre_font.setBold(True)
        nombre_font.setPointSize(12)
        nombre_label.setFont(nombre_font)
        nombre_label.setStyleSheet("color: #2c3e50; padding: 5px; background-color: #ecf0f1; border-radius: 4px;")
        nombre_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(nombre_label)
        
        layout.addSpacing(10)
        
        # Grupo de motivos
        motivo_group = QGroupBox("Motivo del cambio de dirección:")
        motivo_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #34495e;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        motivo_layout = QVBoxLayout()
        motivo_layout.setSpacing(10)
        
        # Grupo de botones de radio
        self.btn_group = QButtonGroup(self)
        
        # Opciones de motivo
        self.rb_mudanza = QRadioButton("🏠 Mudanza del afiliado")
        self.rb_mudanza.setStyleSheet("font-size: 10pt; padding: 5px;")
        self.btn_group.addButton(self.rb_mudanza, 1)
        motivo_layout.addWidget(self.rb_mudanza)
        
        self.rb_correccion = QRadioButton("✏️ Corrección de error en dato original")
        self.rb_correccion.setStyleSheet("font-size: 10pt; padding: 5px;")
        self.btn_group.addButton(self.rb_correccion, 2)
        motivo_layout.addWidget(self.rb_correccion)
        
        self.rb_otro = QRadioButton("📝 Otro motivo")
        self.rb_otro.setStyleSheet("font-size: 10pt; padding: 5px;")
        self.btn_group.addButton(self.rb_otro, 3)
        motivo_layout.addWidget(self.rb_otro)
        
        # Seleccionar primera opción por defecto
        self.rb_mudanza.setChecked(True)
        
        motivo_group.setLayout(motivo_layout)
        layout.addWidget(motivo_group)
        
        layout.addSpacing(10)
        
        # Mensaje de advertencia
        warning_box = QLabel()
        warning_box.setText(
            "⚠️ <b>IMPORTANTE:</b><br><br>"
            "• La ubicación actual se eliminará del mapa<br>"
            "• El afiliado aparecerá en la lista 'Sin Ubicar'<br>"
            "• Deberá ubicarlo nuevamente en el mapa"
        )
        warning_box.setWordWrap(True)
        warning_box.setStyleSheet("""
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 4px;
            padding: 12px;
            color: #856404;
            font-size: 9pt;
        """)
        layout.addWidget(warning_box)
        
        layout.addStretch()
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setMinimumWidth(120)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_layout.addWidget(btn_cancelar)
        
        btn_continuar = QPushButton("Continuar")
        btn_continuar.clicked.connect(self.on_continuar)
        btn_continuar.setMinimumWidth(120)
        btn_continuar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_layout.addWidget(btn_continuar)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def on_continuar(self):
        """Guarda el motivo seleccionado y acepta el diálogo"""
        # Obtener el motivo según el botón seleccionado
        if self.rb_mudanza.isChecked():
            self.motivo_seleccionado = "mudanza"
        elif self.rb_correccion.isChecked():
            self.motivo_seleccionado = "correccion"
        elif self.rb_otro.isChecked():
            self.motivo_seleccionado = "otro"
        
        self.accept()
    
    def get_motivo(self):
        """Retorna el motivo seleccionado"""
        return self.motivo_seleccionado
