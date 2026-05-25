"""
Módulo para exportar información de afiliados a PDF
"""
import os
import io
from datetime import datetime
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
from qgis.PyQt.QtCore import QStandardPaths

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.catalogos import (
    get_limitacion_descripcion,
    get_ambulacion_descripcion,
    get_causa_descripcion,
    get_grado_escolar_descripcion,
    get_ocupacion_descripcion,
    get_locacion_descripcion,
    get_jefe_nucleo_descripcion
)
from modules.access_importer import get_afiliado_foto_bytes


class PDFExporter:
    """Clase para exportar información de afiliados a PDF"""
    
    def __init__(self):
        self.styles = None
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Crea estilos personalizados para el PDF"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Sección
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor("#010b12"),
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold',
            leftIndent=0,
            alignment=TA_LEFT
        ))
        
        # Footer
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_LEFT,
            leftIndent=0
        ))

        self.styles.add(ParagraphStyle(
            name='Muted',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#5f6b73')
        ))
        
        # Label
        self.styles.add(ParagraphStyle(
            name='Label',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495e'),
            fontName='Helvetica-Bold'
        ))
        
        # Valor
        self.styles.add(ParagraphStyle(
            name='Value',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50')
        ))
    
    def export_afiliado(self, afiliado, parent_widget=None):
        """
        Exporta un afiliado a PDF
        
        Args:
            afiliado: Diccionario con los datos del afiliado
            parent_widget: Widget padre para los diálogos
        
        Returns:
            bool: True si se exportó correctamente
        """
        if not REPORTLAB_AVAILABLE:
            QMessageBox.warning(
                parent_widget,
                "ReportLab no disponible",
                "La librería 'reportlab' no está instalada.\n\n"
                "Para instalarla, ejecuta:\n"
                "pip install reportlab"
            )
            return False
        
        # Generar nombre de archivo sugerido
        nombre = afiliado.get('nombres', '').strip()
        apellidos = afiliado.get('apellidos', '').strip()
        codigo = afiliado.get('codigo', '').strip()
        
        nombre_archivo = f"Afiliado_{codigo}_{apellidos}_{nombre}".replace(' ', '_')
        nombre_archivo = self._sanitize_filename(nombre_archivo) + '.pdf'
        
        # Directorio por defecto (Documentos)
        documentos = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        ruta_default = os.path.join(documentos, nombre_archivo)
        
        # Diálogo para guardar
        ruta_guardar, _ = QFileDialog.getSaveFileName(
            parent_widget,
            "Guardar PDF",
            ruta_default,
            "Archivos PDF (*.pdf)"
        )
        
        if not ruta_guardar:
            return False
        
        try:
            self._generar_pdf(afiliado, ruta_guardar)
            
            QMessageBox.information(
                parent_widget,
                "PDF Generado",
                f"El PDF se ha guardado correctamente en:\n{ruta_guardar}"
            )
            return True
            
        except Exception as e:
            QMessageBox.critical(
                parent_widget,
                "Error al generar PDF",
                f"Ocurrió un error al generar el PDF:\n{str(e)}"
            )
            return False
    
    def _generar_pdf(self, afiliado, ruta_archivo):
        """Genera el archivo PDF con la información del afiliado"""
        doc = SimpleDocTemplate(
            ruta_archivo,
            pagesize=A4,
            rightMargin=52,
            leftMargin=52,
            topMargin=48,
            bottomMargin=24
        )
        
        story = []
        
        nombre_completo = f"{afiliado.get('nombres', '')} {afiliado.get('apellidos', '')}".strip()
        titulo = Paragraph(
            f"Ficha de Afiliado<br/>{nombre_completo or 'Sin nombre'}",
            self.styles['CustomTitle']
        )
        story.append(titulo)
        story.append(Paragraph(
            f"Documento generado por ACLIFIM el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            self.styles['Muted']
        ))
        story.append(Spacer(1, 0.14 * inch))

        story.append(self._build_header_block(afiliado))
        story.append(Spacer(1, 0.18 * inch))

        lon = afiliado.get('lon')
        lat = afiliado.get('lat')
        coords = f"Lon: {lon:.6f}, Lat: {lat:.6f}" if lon is not None and lat is not None else "Sin ubicar"

        story.append(self._create_section_table("Identificación", [
            ("Código", self._format_value(afiliado.get('codigo'))),
            ("CI (Carnet)", self._format_value(afiliado.get('carnet_id'))),
            ("Folio", self._format_value(afiliado.get('folio'))),
            ("ID Sistema", self._format_value(afiliado.get('id'))),
            ("Sexo", self._format_value(afiliado.get('sexo'))),
            ("Edad", self._format_value(afiliado.get('edad'))),
            ("Fecha de Nacimiento", self._format_date(afiliado.get('fecha_nacimiento'))),
            ("Lugar de Nacimiento", self._format_value(afiliado.get('lugar_nacimiento'))),
            ("Nacionalidad", self._format_value(afiliado.get('nacionalidad'))),
            ("Ciudadanía", self._format_value(afiliado.get('ciudadania'))),
        ]))

        story.append(self._create_section_table("Ubicación y Contacto", [
            ("Dirección", self._format_value(afiliado.get('direccion'))),
            ("Reparto", self._format_value(afiliado.get('reparto'))),
            ("Locación", get_locacion_descripcion(afiliado.get('locacion'))),
            ("Teléfono", self._format_value(afiliado.get('telefono'))),
            ("Tipo de Teléfono", self._format_value(afiliado.get('tipo_telefono'))),
            ("Coordenadas GPS", coords),
        ]))

        limitacion_cod = afiliado.get('limitacion_cod') or afiliado.get('limitacion')
        limitacion_desc = get_limitacion_descripcion(limitacion_cod)
        ambulacion_cod = afiliado.get('ambulacion_cod') or afiliado.get('nivel_ambulacion')
        ambulacion_desc = get_ambulacion_descripcion(ambulacion_cod)
        story.append(self._create_section_table("Datos Médicos", [
            ("Limitación", self._format_value(limitacion_desc)),
            ("Tipo de Ambulación", self._format_value(ambulacion_desc)),
            ("Causa", get_causa_descripcion(afiliado.get('causa'))),
            ("Discapacidad Asociada", self._format_value(afiliado.get('discap_asociada'))),
        ]))

        story.append(self._create_section_table("Datos Familiares", [
            ("Hijo de", self._format_value(afiliado.get('hijo_de'))),
            ("Estado Civil", self._format_value(afiliado.get('estado_civil'))),
            ("Número de Hijos", self._format_value(afiliado.get('no_hijos'))),
            ("Conviventes", self._format_value(afiliado.get('conviventes'))),
            ("Personas Dependientes", self._format_value(afiliado.get('no_personas_dep'))),
        ]))

        ingreso = afiliado.get('ingreso_mensual')
        ingreso_str = f"${ingreso:.2f}" if ingreso else "No especificado"
        story.append(self._create_section_table("Datos Laborales y Educativos", [
            ("Ocupación", get_ocupacion_descripcion(afiliado.get('ocupacion'))),
            ("Centro de Trabajo/Estudio", self._format_value(afiliado.get('centro_trabajo'))),
            ("Ingreso Mensual", ingreso_str),
            ("Grado Escolar", get_grado_escolar_descripcion(afiliado.get('grado_escolar'))),
            ("Especialidad", self._format_value(afiliado.get('especialidad'))),
        ]))

        cuota = afiliado.get('cuota')
        cuota_str = f"${cuota:.2f}" if cuota else "No especificado"
        estado = afiliado.get('estado', 'normal')
        estado_display = {
            'nuevo': 'Nuevo (sin ubicar)',
            'cambio_direccion': 'Cambio de dirección (re-ubicar)',
            'normal': 'Normal'
        }.get(estado, estado)
        story.append(self._create_section_table("Organización y Fechas", [
            ("Área", self._format_value(afiliado.get('area'))),
            ("Jefe de Núcleo", get_jefe_nucleo_descripcion(afiliado.get('jefe_nucleo'))),
            ("Cuota", cuota_str),
            ("Estado", estado_display),
            ("Fecha de Ingreso", self._format_date(afiliado.get('fecha_ingreso'))),
            ("Fecha de Alta", self._format_date(afiliado.get('fecha_alta'))),
            ("Fecha de Baja", self._format_date(afiliado.get('fecha_baja'))),
            ("Motivo de Baja", self._format_value(afiliado.get('motivo_baja'))),
            ("Fecha de Creación", self._format_datetime(afiliado.get('fecha_creacion'))),
            ("Última Modificación", self._format_datetime(afiliado.get('fecha_modificacion'))),
        ]))

        story.append(Spacer(1, 0.14 * inch))
        footer = Paragraph(
            f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            self.styles['Footer']
        )
        story.append(footer)
        
        # Generar PDF
        doc.build(story)
    
    def _build_header_block(self, afiliado):
        """Crea un bloque de cabecera con datos principales y foto."""
        estado = afiliado.get('estado', 'normal')
        estado_display = {
            'nuevo': 'Nuevo (sin ubicar)',
            'cambio_direccion': 'Cambio de dirección (re-ubicar)',
            'normal': 'Normal'
        }.get(estado, estado)

        left_data = [
            ["Nombre", self._format_value(f"{afiliado.get('nombres', '')} {afiliado.get('apellidos', '')}".strip())],
            ["Código", self._format_value(afiliado.get('codigo'))],
            ["CI", self._format_value(afiliado.get('carnet_id'))],
            ["Estado", self._format_value(estado_display)],
        ]

        left_table = Table(left_data, colWidths=[1.35 * inch, 4.45 * inch])
        left_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2f3e46')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#22313f')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LINEBELOW', (0, 0), (-1, -2), 0.35, colors.HexColor('#d9e1e5')),
        ]))

        photo_flowable = self._build_photo_flowable(afiliado)

        header_table = Table(
            [[left_table, photo_flowable]],
            colWidths=[5.8 * inch, 1.3 * inch]
        )
        header_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#c8d4dc')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fbfdff')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        return header_table

    def _build_photo_flowable(self, afiliado):
        """Retorna un flowable de foto tipo carnet o placeholder."""
        photo_bytes = get_afiliado_foto_bytes(afiliado.get('id'))
        if photo_bytes:
            try:
                image = RLImage(io.BytesIO(photo_bytes))
                image.drawWidth = 1.1 * inch
                image.drawHeight = 1.35 * inch
                return image
            except Exception:
                pass

        placeholder = Table(
            [[Paragraph("Sin foto", self.styles['Muted'])]],
            colWidths=[1.1 * inch],
            rowHeights=[1.35 * inch]
        )
        placeholder.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#c8d4dc')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f6f8')),
        ]))
        return placeholder

    def _create_section_table(self, title, rows):
        """Crea una sección con título y tabla de pares clave-valor."""
        section_story = [Paragraph(title.upper(), self.styles['SectionTitle'])]
        table_data = [[f"{label}:", self._format_value(value)] for label, value in rows]
        table = Table(table_data, colWidths=[2.05 * inch, 4.95 * inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9.5),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2f3e46')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#22313f')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.45, colors.HexColor('#dfe7ec')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9fbfc')]),
        ]))
        section_story.append(table)
        section_story.append(Spacer(1, 0.14 * inch))
        return Table([[section_story]], colWidths=[7.0 * inch], style=TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
    
    def _format_value(self, value):
        """Formatea un valor para mostrar"""
        if value is None or str(value).strip() == '':
            return "No especificado"
        return str(value)
    
    def _format_date(self, date_value):
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
    
    def _format_datetime(self, datetime_value):
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
    
    def _sanitize_filename(self, filename):
        """Limpia un nombre de archivo de caracteres inválidos"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:200]  # Limitar longitud
