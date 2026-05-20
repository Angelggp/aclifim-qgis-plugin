"""
Dialogo resumido de afiliado para consulta rapida desde el mapa.
"""
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout,
    QPushButton,
    QFrame
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont, QPixmap

from ..modules.access_importer import get_afiliado_foto_bytes
from ..utils.catalogos import get_limitacion_descripcion


class ResumenAfiliadoDialog(QDialog):
    """Muestra datos principales de un afiliado en formato compacto."""

    def __init__(self, afiliado, parent=None):
        super().__init__(parent)
        self.afiliado = afiliado

        nombre = f"{afiliado.get('nombres', '')} {afiliado.get('apellidos', '')}".strip() or "Sin nombre"
        self.setWindowTitle(f"Resumen - {nombre}")
        self.setMinimumWidth(430)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        header = QFrame()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 8, 8, 8)
        header_layout.setSpacing(12)

        photo_label = QLabel()
        photo_label.setFixedSize(90, 110)
        photo_label.setAlignment(Qt.AlignCenter)
        photo_label.setStyleSheet("border: 1px solid #bfbfbf; background: #f7f7f7;")
        self._load_photo(photo_label)
        header_layout.addWidget(photo_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        nombre = f"{self.afiliado.get('nombres', '')} {self.afiliado.get('apellidos', '')}".strip() or "Sin nombre"
        nombre_label = QLabel(nombre)
        nombre_font = QFont()
        nombre_font.setPointSize(12)
        nombre_font.setBold(True)
        nombre_label.setFont(nombre_font)
        info_layout.addWidget(nombre_label)

        carnet = self.afiliado.get('carnet_id') or "No especificado"
        carnet_label = QLabel(f"Carnet: {carnet}")
        info_layout.addWidget(carnet_label)

        edad = self.afiliado.get('edad')
        edad_label = QLabel(f"Edad: {edad if edad is not None else 'No especificada'}")
        info_layout.addWidget(edad_label)

        info_layout.addStretch()
        header_layout.addLayout(info_layout, 1)
        header.setLayout(header_layout)
        layout.addWidget(header)

        data_grid = QGridLayout()
        data_grid.setHorizontalSpacing(14)
        data_grid.setVerticalSpacing(7)

        row = 0
        self._add_field(data_grid, row, "Direccion:", self.afiliado.get('direccion'))
        row += 1

        limitacion_cod = self.afiliado.get('limitacion_cod') or self.afiliado.get('limitacion')
        self._add_field(data_grid, row, "Limitacion:", get_limitacion_descripcion(limitacion_cod))
        row += 1

        estado = self.afiliado.get('estado') or "normal"
        self._add_field(data_grid, row, "Estado:", self._estado_texto(estado))

        layout.addLayout(data_grid)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _load_photo(self, label):
        """Carga foto del afiliado desde BD (si existe)."""
        photo_bytes = get_afiliado_foto_bytes(self.afiliado.get('id'))
        if photo_bytes:
            pixmap = QPixmap()
            if pixmap.loadFromData(photo_bytes):
                label.setPixmap(
                    pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
                return

        label.setText("Sin foto")

    def _add_field(self, grid, row, label_text, value):
        label = QLabel(label_text)
        label_font = QFont()
        label_font.setBold(True)
        label.setFont(label_font)
        grid.addWidget(label, row, 0, Qt.AlignTop)

        value_text = "No especificado" if value is None or str(value).strip() == "" else str(value)
        value_label = QLabel(value_text)
        value_label.setWordWrap(True)
        value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        grid.addWidget(value_label, row, 1)

    def _estado_texto(self, estado):
        return {
            "nuevo": "Nuevo (sin ubicar)",
            "cambio_direccion": "Cambio de direccion",
            "normal": "Normal"
        }.get(estado, str(estado))
