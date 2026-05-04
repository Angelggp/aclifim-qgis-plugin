"""
Diálogo de configuración de la base de datos
"""
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QDialogButtonBox,
    QLabel,
    QGroupBox,
    QMessageBox,
    QProgressBar
)
from qgis.PyQt.QtCore import Qt
from ..modules.db_connection import DatabaseManager
import json
import os


class DatabaseConfigDialog(QDialog):
    """Diálogo para configurar la conexión a PostgreSQL"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Base de Datos")
        self.resize(500, 400)
        
        self.config_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'db_config.json'
        )
        
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout()
        
        # Información
        info_label = QLabel(
            "Configura la conexión a PostgreSQL/PostGIS.\n"
            "El plugin creará automáticamente la base de datos y tabla si no existen."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Grupo de conexión
        connection_group = QGroupBox("Datos de Conexión")
        form_layout = QFormLayout()
        
        self.host_input = QLineEdit()
        self.host_input.setText("localhost")
        self.host_input.setPlaceholderText("localhost o IP del servidor")
        form_layout.addRow("Host:", self.host_input)
        
        self.port_input = QLineEdit()
        self.port_input.setText("5432")
        self.port_input.setPlaceholderText("5432")
        form_layout.addRow("Puerto:", self.port_input)
        
        self.user_input = QLineEdit()
        self.user_input.setText("postgres")
        self.user_input.setPlaceholderText("postgres")
        form_layout.addRow("Usuario:", self.user_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Contraseña del usuario")
        form_layout.addRow("Contraseña:", self.password_input)
        
        self.dbname_input = QLineEdit()
        self.dbname_input.setText("aclifim_db")
        self.dbname_input.setPlaceholderText("aclifim_db")
        form_layout.addRow("Nombre BD:", self.dbname_input)
        
        connection_group.setLayout(form_layout)
        layout.addWidget(connection_group)
        
        # Botón probar conexión
        self.test_button = QPushButton("Probar Conexión e Inicializar BD")
        self.test_button.clicked.connect(self.test_and_initialize)
        layout.addWidget(self.test_button)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Label de estado
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Botones de diálogo
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_config(self):
        """Carga la configuración guardada si existe"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.host_input.setText(config.get('host', 'localhost'))
                    self.port_input.setText(config.get('port', '5432'))
                    self.user_input.setText(config.get('user', 'postgres'))
                    # No cargar la contraseña por seguridad
                    self.dbname_input.setText(config.get('dbname', 'aclifim_db'))
                    print("[CONFIG] Configuración cargada")
            except Exception as e:
                print(f"[CONFIG] Error al cargar config: {e}")
    
    def save_config(self):
        """Guarda la configuración"""
        config = {
            'host': self.host_input.text(),
            'port': self.port_input.text(),
            'user': self.user_input.text(),
            'password': self.password_input.text(),  # En producción, encriptar
            'dbname': self.dbname_input.text()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print("[CONFIG] Configuración guardada")
            return True
        except Exception as e:
            print(f"[CONFIG] Error al guardar: {e}")
            return False
    
    def get_db_manager(self):
        """Retorna una instancia de DatabaseManager con los datos del formulario"""
        return DatabaseManager(
            host=self.host_input.text(),
            port=self.port_input.text(),
            user=self.user_input.text(),
            password=self.password_input.text(),
            dbname=self.dbname_input.text()
        )
    
    def test_and_initialize(self):
        """Prueba la conexión e inicializa la base de datos"""
        self.status_label.setText("Probando conexión...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        self.test_button.setEnabled(False)
        
        db = self.get_db_manager()
        success, messages = db.initialize_database()
        
        self.progress_bar.setVisible(False)
        self.test_button.setEnabled(True)
        
        if success:
            message = "✅ Inicialización exitosa:\n\n" + "\n".join(f"• {msg}" for msg in messages)
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: green;")
            QMessageBox.information(self, "Éxito", message)
        else:
            message = "❌ Error durante la inicialización:\n\n" + "\n".join(messages)
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "Error", message)
    
    def accept(self):
        """Sobrescribe accept para guardar configuración antes de cerrar"""
        if self.save_config():
            super().accept()
        else:
            QMessageBox.warning(
                self,
                "Advertencia",
                "No se pudo guardar la configuración"
            )
