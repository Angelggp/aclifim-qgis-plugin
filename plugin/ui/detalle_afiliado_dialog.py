"""
Dialogo para mostrar todos los detalles de un afiliado en una sola pagina.
"""
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QGridLayout,
    QScrollArea,
    QWidget,
    QMessageBox,
    QGroupBox,
    QFileDialog,
    QFrame
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont, QPixmap

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.catalogos import get_limitacion_descripcion, get_ambulacion_descripcion
from utils.pdf_exporter import PDFExporter
from .cambio_direccion_dialog import CambioDireccionDialog
from ..modules.access_importer import cambiar_direccion_afiliado


class DetalleAfiliadoDialog(QDialog):
    """Muestra los detalles de un afiliado en una vista unica y ordenada por secciones."""

    def __init__(self, afiliado, parent=None, iface=None):
        super().__init__(parent)
        self.afiliado = afiliado
        self.iface = iface
        self.parent_dialog = parent

        self.photo_registry_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "afiliados_fotos.json"
        )
        self.photo_label = None
        self.photo_path = self.get_photo_path()

        nombre_completo = f"{afiliado.get('nombres', '')} {afiliado.get('apellidos', '')}".strip()
        self.setWindowTitle(f"Detalles del Afiliado - {nombre_completo or 'Sin nombre'}")
        self.resize(860, 760)

        self.init_ui()

    def init_ui(self):
        """Inicializa interfaz en una sola pagina con secciones."""
        main_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(14, 14, 14, 14)
        content_layout.setSpacing(12)

        content_layout.addWidget(self.create_header_card())

        content_layout.addWidget(self.create_section_identificacion())
        content_layout.addWidget(self.create_section_ubicacion())
        content_layout.addWidget(self.create_section_medicos())
        content_layout.addWidget(self.create_section_familiares())
        content_layout.addWidget(self.create_section_laborales())
        content_layout.addWidget(self.create_section_organizacion())
        content_layout.addStretch()

        content.setLayout(content_layout)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        lon = self.afiliado.get('lon')
        lat = self.afiliado.get('lat')
        if lon is not None and lat is not None:
            btn_cambiar_dir = QPushButton("Cambiar Direccion")
            btn_cambiar_dir.clicked.connect(self.cambiar_direccion)
            btn_cambiar_dir.setMinimumWidth(160)
            btn_layout.addWidget(btn_cambiar_dir)

        btn_pdf = QPushButton("Exportar PDF")
        btn_pdf.clicked.connect(self.exportar_pdf)
        btn_pdf.setMinimumWidth(140)
        btn_layout.addWidget(btn_pdf)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        btn_cerrar.setMinimumWidth(120)
        btn_layout.addWidget(btn_cerrar)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def create_header_card(self):
        """Crea encabezado tipo carnet con foto pequena y datos principales."""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        photo_col = QVBoxLayout()
        photo_col.setSpacing(6)

        self.photo_label = QLabel()
        self.photo_label.setFixedSize(110, 130)
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setStyleSheet("border: 1px solid #bfbfbf; background: #f7f7f7;")
        photo_col.addWidget(self.photo_label)

        btn_photo = QPushButton("Agregar Imagen")
        btn_photo.clicked.connect(self.seleccionar_imagen)
        photo_col.addWidget(btn_photo)

        btn_remove_photo = QPushButton("Quitar Imagen")
        btn_remove_photo.clicked.connect(self.quitar_imagen)
        photo_col.addWidget(btn_remove_photo)

        layout.addLayout(photo_col)

        info_col = QVBoxLayout()
        info_col.setSpacing(6)

        nombre_completo = f"{self.afiliado.get('nombres', '')} {self.afiliado.get('apellidos', '')}".strip() or "Sin nombre"
        lbl_nombre = QLabel(nombre_completo)
        nombre_font = QFont()
        nombre_font.setPointSize(14)
        nombre_font.setBold(True)
        lbl_nombre.setFont(nombre_font)
        info_col.addWidget(lbl_nombre)

        info_grid = QGridLayout()
        info_grid.setHorizontalSpacing(20)
        info_grid.setVerticalSpacing(6)

        self.add_grid_field(info_grid, 0, 0, "Codigo:", self.afiliado.get('codigo'))
        self.add_grid_field(info_grid, 0, 2, "CI:", self.afiliado.get('carnet_id'))
        self.add_grid_field(info_grid, 1, 0, "ID Sistema:", self.afiliado.get('id'))
        self.add_grid_field(info_grid, 1, 2, "Estado:", self.get_estado_display())

        info_col.addLayout(info_grid)
        info_col.addStretch()
        layout.addLayout(info_col, 1)

        card.setLayout(layout)
        self.update_photo_preview()
        return card

    def create_section_identificacion(self):
        group = QGroupBox("Identificacion y Datos Personales")
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(8)

        row = 0
        self.add_grid_field(grid, row, 0, "Folio:", self.afiliado.get('folio'))
        self.add_grid_field(grid, row, 2, "Sexo:", self.afiliado.get('sexo'))

        row += 1
        self.add_grid_field(grid, row, 0, "Edad:", self.afiliado.get('edad'))
        self.add_grid_field(grid, row, 2, "Fecha Nacimiento:", self.format_date(self.afiliado.get('fecha_nacimiento')))

        row += 1
        self.add_grid_field(grid, row, 0, "Lugar Nacimiento:", self.afiliado.get('lugar_nacimiento'))
        self.add_grid_field(grid, row, 2, "Nacionalidad:", self.afiliado.get('nacionalidad'))

        row += 1
        self.add_grid_field(grid, row, 0, "Ciudadania:", self.afiliado.get('ciudadania'))

        group.setLayout(grid)
        return group

    def create_section_ubicacion(self):
        group = QGroupBox("Ubicacion y Contacto")
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(8)

        row = 0
        self.add_grid_field(grid, row, 0, "Direccion:", self.afiliado.get('direccion'))
        self.add_grid_field(grid, row, 2, "Reparto:", self.afiliado.get('reparto'))

        row += 1
        self.add_grid_field(grid, row, 0, "Locacion:", self.afiliado.get('locacion'))
        self.add_grid_field(grid, row, 2, "Telefono:", self.afiliado.get('telefono'))

        row += 1
        self.add_grid_field(grid, row, 0, "Tipo Telefono:", self.afiliado.get('tipo_telefono'))

        row += 1
        lon = self.afiliado.get('lon')
        lat = self.afiliado.get('lat')
        if lon is not None and lat is not None:
            self.add_grid_field(grid, row, 0, "Longitud:", f"{lon:.6f}")
            self.add_grid_field(grid, row, 2, "Latitud:", f"{lat:.6f}")
        else:
            self.add_grid_field(grid, row, 0, "Coordenadas GPS:", "Sin ubicar")

        group.setLayout(grid)
        return group

    def create_section_medicos(self):
        group = QGroupBox("Datos Medicos")
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(8)

        limitacion_cod = self.afiliado.get('limitacion_cod') or self.afiliado.get('limitacion')
        ambulacion_cod = self.afiliado.get('ambulacion_cod') or self.afiliado.get('nivel_ambulacion')

        row = 0
        self.add_grid_field(grid, row, 0, "Limitacion:", get_limitacion_descripcion(limitacion_cod))
        self.add_grid_field(grid, row, 2, "Nivel Ambulacion:", get_ambulacion_descripcion(ambulacion_cod))

        row += 1
        self.add_grid_field(grid, row, 0, "Causa:", self.afiliado.get('causa'))
        self.add_grid_field(grid, row, 2, "Discapacidad Asociada:", self.afiliado.get('discap_asociada'))

        group.setLayout(grid)
        return group

    def create_section_familiares(self):
        group = QGroupBox("Datos Familiares")
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(8)

        row = 0
        self.add_grid_field(grid, row, 0, "Hijo de:", self.afiliado.get('hijo_de'))
        self.add_grid_field(grid, row, 2, "Estado Civil:", self.afiliado.get('estado_civil'))

        row += 1
        self.add_grid_field(grid, row, 0, "Numero de Hijos:", self.afiliado.get('no_hijos'))
        self.add_grid_field(grid, row, 2, "Conviventes:", self.afiliado.get('conviventes'))

        row += 1
        self.add_grid_field(grid, row, 0, "Personas Dependientes:", self.afiliado.get('no_personas_dep'))

        group.setLayout(grid)
        return group

    def create_section_laborales(self):
        group = QGroupBox("Datos Laborales y Educativos")
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(8)

        row = 0
        self.add_grid_field(grid, row, 0, "Ocupacion:", self.afiliado.get('ocupacion'))
        self.add_grid_field(grid, row, 2, "Centro Trabajo/Estudio:", self.afiliado.get('centro_trabajo'))

        row += 1
        ingreso = self.afiliado.get('ingreso_mensual')
        ingreso_txt = f"${ingreso:.2f}" if ingreso else "No especificado"
        self.add_grid_field(grid, row, 0, "Ingreso Mensual:", ingreso_txt)

        row += 1
        self.add_grid_field(grid, row, 0, "Grado Escolar:", self.afiliado.get('grado_escolar'))
        self.add_grid_field(grid, row, 2, "Especialidad:", self.afiliado.get('especialidad'))

        group.setLayout(grid)
        return group

    def create_section_organizacion(self):
        group = QGroupBox("Organizacion y Administracion")
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(8)

        row = 0
        self.add_grid_field(grid, row, 0, "Area:", self.afiliado.get('area'))
        self.add_grid_field(grid, row, 2, "Jefe de Nucleo:", self.afiliado.get('jefe_nucleo'))

        row += 1
        cuota = self.afiliado.get('cuota')
        cuota_txt = f"${cuota:.2f}" if cuota else "No especificado"
        self.add_grid_field(grid, row, 0, "Cuota:", cuota_txt)

        row += 1
        self.add_grid_field(grid, row, 0, "Fecha Ingreso:", self.format_date(self.afiliado.get('fecha_ingreso')))
        self.add_grid_field(grid, row, 2, "Fecha Alta:", self.format_date(self.afiliado.get('fecha_alta')))

        row += 1
        self.add_grid_field(grid, row, 0, "Fecha Baja:", self.format_date(self.afiliado.get('fecha_baja')))
        self.add_grid_field(grid, row, 2, "Motivo Baja:", self.afiliado.get('motivo_baja'))

        row += 1
        self.add_grid_field(grid, row, 0, "Fecha Creacion:", self.format_datetime(self.afiliado.get('fecha_creacion')))
        self.add_grid_field(grid, row, 2, "Ultima Modificacion:", self.format_datetime(self.afiliado.get('fecha_modificacion')))

        group.setLayout(grid)
        return group

    def add_grid_field(self, grid, row, col, label_text, value):
        """Agrega un campo (etiqueta + valor) a un grid."""
        label = QLabel(label_text)
        label_font = QFont()
        label_font.setBold(True)
        label.setFont(label_font)
        grid.addWidget(label, row, col)

        if value is None or str(value).strip() == "":
            value_text = "No especificado"
            style = "color: #777777;"
        else:
            value_text = str(value)
            style = "color: #222222;"

        value_label = QLabel(value_text)
        value_label.setWordWrap(True)
        value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        value_label.setStyleSheet(style)
        grid.addWidget(value_label, row, col + 1)

    def format_date(self, date_value):
        if not date_value:
            return "No especificado"
        try:
            if hasattr(date_value, 'strftime'):
                return date_value.strftime('%d/%m/%Y')
            return str(date_value)
        except Exception:
            return str(date_value)

    def format_datetime(self, datetime_value):
        if not datetime_value:
            return "No especificado"
        try:
            if hasattr(datetime_value, 'strftime'):
                return datetime_value.strftime('%d/%m/%Y %H:%M:%S')
            return str(datetime_value)
        except Exception:
            return str(datetime_value)

    def get_estado_display(self):
        estado = self.afiliado.get('estado', 'normal')
        return {
            'nuevo': 'Nuevo (sin ubicar)',
            'cambio_direccion': 'Cambio de direccion (reubicar)',
            'normal': 'Normal'
        }.get(estado, str(estado))

    def load_photo_registry(self):
        """Lee el registro local de fotos por ID de afiliado."""
        if not os.path.exists(self.photo_registry_path):
            return {}

        try:
            with open(self.photo_registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def save_photo_registry(self, data):
        """Guarda el registro local de fotos por ID de afiliado."""
        try:
            with open(self.photo_registry_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la imagen del afiliado.\n\n{e}")
            return False

    def get_photo_path(self):
        """Obtiene la ruta de imagen asociada al afiliado actual."""
        afiliado_id = self.afiliado.get('id')
        if afiliado_id is None:
            return None

        registry = self.load_photo_registry()
        path = registry.get(str(afiliado_id))
        if path and os.path.exists(path):
            return path
        return None

    def set_photo_path(self, path):
        """Asocia (o quita) una ruta de imagen para el afiliado actual."""
        afiliado_id = self.afiliado.get('id')
        if afiliado_id is None:
            return False

        registry = self.load_photo_registry()
        key = str(afiliado_id)

        if path:
            registry[key] = path
        elif key in registry:
            del registry[key]

        return self.save_photo_registry(registry)

    def update_photo_preview(self):
        """Actualiza el preview de la foto tipo carnet."""
        if not self.photo_label:
            return

        if self.photo_path and os.path.exists(self.photo_path):
            pixmap = QPixmap(self.photo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.photo_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.photo_label.setPixmap(scaled)
                self.photo_label.setText("")
                return

        self.photo_label.setPixmap(QPixmap())
        self.photo_label.setText("Sin imagen")

    def seleccionar_imagen(self):
        """Selecciona una imagen para el afiliado."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Imagen del Afiliado",
            "",
            "Imagenes (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return

        if self.set_photo_path(file_path):
            self.photo_path = file_path
            self.update_photo_preview()

    def quitar_imagen(self):
        """Quita la imagen asociada al afiliado."""
        if self.set_photo_path(None):
            self.photo_path = None
            self.update_photo_preview()

    def exportar_pdf(self):
        """Exporta la informacion del afiliado a PDF."""
        exporter = PDFExporter()
        exporter.export_afiliado(self.afiliado, self)

    def cambiar_direccion(self):
        """Inicia el proceso de cambio de direccion del afiliado."""
        nombre_completo = f"{self.afiliado.get('nombres', '')} {self.afiliado.get('apellidos', '')}".strip()

        dialog = CambioDireccionDialog(nombre_completo, self)

        if dialog.exec_() == QDialog.Accepted:
            motivo = dialog.get_motivo()
            afiliado_id = self.afiliado.get('id')

            success, msg = cambiar_direccion_afiliado(afiliado_id, motivo)

            if success:
                QMessageBox.information(
                    self,
                    "Cambio Registrado",
                    f"El cambio de direccion se registro correctamente.\n\n"
                    f"El afiliado '{nombre_completo}' ahora aparecera en la lista 'Sin Ubicar'.\n"
                    f"Ubicalo nuevamente en el mapa desde esa lista."
                )

                self.accept()

                if hasattr(self.parent_dialog, 'load_all_afiliados'):
                    try:
                        self.parent_dialog.load_all_afiliados()
                    except Exception as e:
                        print(f"[DEBUG] Error al recargar afiliados: {e}")

                if hasattr(self.parent_dialog, 'load_unlocated_afiliados') and hasattr(self.parent_dialog, 'table_unlocated'):
                    try:
                        self.parent_dialog.load_unlocated_afiliados()
                    except Exception as e:
                        print(f"[DEBUG] Error al recargar sin ubicar: {e}")

                if hasattr(self.parent_dialog, 'refresh_layer'):
                    try:
                        self.parent_dialog.refresh_layer()
                    except Exception as e:
                        print(f"[DEBUG] Error al refrescar capa: {e}")
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"No se pudo registrar el cambio de direccion:\n\n{msg}"
                )
