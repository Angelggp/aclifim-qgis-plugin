from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QDialogButtonBox
)


class AfiliadoForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Datos del Afiliado")
        self.resize(400, 200)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Formulario
        form_layout = QFormLayout()
        
        self.nombre_input = QLineEdit()
        self.direccion_input = QLineEdit()
        self.municipio_input = QLineEdit()
        
        form_layout.addRow("Nombre:", self.nombre_input)
        form_layout.addRow("Dirección:", self.direccion_input)
        form_layout.addRow("Municipio:", self.municipio_input)
        
        layout.addLayout(form_layout)
        
        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_data(self):
        """Retorna los datos ingresados en el formulario"""
        return {
            'nombre': self.nombre_input.text(),
            'direccion': self.direccion_input.text(),
            'municipio': self.municipio_input.text()
        }
