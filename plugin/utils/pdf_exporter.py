"""
Módulo para exportar información de afiliados a PDF
"""
import os
from datetime import datetime
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
from qgis.PyQt.QtCore import QStandardPaths

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.catalogos import get_limitacion_descripcion, get_ambulacion_descripcion


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
        doc = SimpleDocTemplate(ruta_archivo, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Título
        nombre_completo = f"{afiliado.get('nombres', '')} {afiliado.get('apellidos', '')}".strip()
        titulo = Paragraph(f"Información del Afiliado<br/>{nombre_completo or 'Sin nombre'}", 
                          self.styles['CustomTitle'])
        story.append(titulo)
        story.append(Spacer(1, 0.1*inch))
        
        # Sección Identificación
        story.append(Paragraph("IDENTIFICACIÓN Y DATOS PERSONALES", self.styles['SectionTitle']))
        data = [
            ["Código:", self._format_value(afiliado.get('codigo')), 
             "CI (Carnet):", self._format_value(afiliado.get('carnet_id'))],
            ["Folio:", self._format_value(afiliado.get('folio')), 
             "ID Sistema:", self._format_value(afiliado.get('id'))],
            ["Nombres:", self._format_value(afiliado.get('nombres')), 
             "Apellidos:", self._format_value(afiliado.get('apellidos'))],
            ["Sexo:", self._format_value(afiliado.get('sexo')), 
             "Edad:", self._format_value(afiliado.get('edad'))],
            ["Fecha Nacimiento:", self._format_date(afiliado.get('fecha_nacimiento')), 
             "Lugar Nacimiento:", self._format_value(afiliado.get('lugar_nacimiento'))],
            ["Nacionalidad:", self._format_value(afiliado.get('nacionalidad')), 
             "Ciudadanía:", self._format_value(afiliado.get('ciudadania'))],
        ]
        story.append(self._create_table(data))
        story.append(Spacer(1, 0.2*inch))
        
        # Sección Ubicación
        story.append(Paragraph("UBICACIÓN Y CONTACTO", self.styles['SectionTitle']))
        lon = afiliado.get('lon')
        lat = afiliado.get('lat')
        coords = f"Lon: {lon:.6f}, Lat: {lat:.6f}" if lon and lat else "Sin ubicar"
        data = [
            ["Dirección:", self._format_value(afiliado.get('direccion')), 
             "Reparto:", self._format_value(afiliado.get('reparto'))],
            ["Locación:", self._format_value(afiliado.get('locacion')), 
             "Teléfono:", self._format_value(afiliado.get('telefono'))],
            ["Tipo Teléfono:", self._format_value(afiliado.get('tipo_telefono')), 
             "Coordenadas GPS:", coords],
        ]
        story.append(self._create_table(data))
        story.append(Spacer(1, 0.2*inch))
        
        # Sección Médicos
        story.append(Paragraph("DATOS MÉDICOS", self.styles['SectionTitle']))
        limitacion_cod = afiliado.get('limitacion_cod') or afiliado.get('limitacion')
        limitacion_desc = get_limitacion_descripcion(limitacion_cod)
        ambulacion_cod = afiliado.get('ambulacion_cod') or afiliado.get('nivel_ambulacion')
        ambulacion_desc = get_ambulacion_descripcion(ambulacion_cod)
        data = [
            ["Limitación:", limitacion_desc, "Ambulación:", ambulacion_desc],
            ["Causa:", self._format_value(afiliado.get('causa')), 
             "Discapacidad Asociada:", self._format_value(afiliado.get('discap_asociada'))],
        ]
        story.append(self._create_table(data))
        story.append(Spacer(1, 0.2*inch))
        
        # Sección Familiares
        story.append(Paragraph("DATOS FAMILIARES", self.styles['SectionTitle']))
        data = [
            ["Hijo de:", self._format_value(afiliado.get('hijo_de')), 
             "Estado Civil:", self._format_value(afiliado.get('estado_civil'))],
            ["Número de Hijos:", self._format_value(afiliado.get('no_hijos')), 
             "Conviventes:", self._format_value(afiliado.get('conviventes'))],
            ["Personas Dependientes:", self._format_value(afiliado.get('no_personas_dep')), "", ""],
        ]
        story.append(self._create_table(data))
        story.append(Spacer(1, 0.2*inch))
        
        # Sección Laborales
        story.append(Paragraph("DATOS LABORALES Y EDUCATIVOS", self.styles['SectionTitle']))
        ingreso = afiliado.get('ingreso_mensual')
        ingreso_str = f"${ingreso:.2f}" if ingreso else "No especificado"
        data = [
            ["Ocupación:", self._format_value(afiliado.get('ocupacion')), 
             "Centro Trabajo/Estudio:", self._format_value(afiliado.get('centro_trabajo'))],
            ["Ingreso Mensual:", ingreso_str, "", ""],
            ["Grado Escolar:", self._format_value(afiliado.get('grado_escolar')), 
             "Especialidad:", self._format_value(afiliado.get('especialidad'))],
        ]
        story.append(self._create_table(data))
        story.append(Spacer(1, 0.2*inch))
        
        # Sección Organización
        story.append(Paragraph("ORGANIZACIÓN Y FECHAS", self.styles['SectionTitle']))
        cuota = afiliado.get('cuota')
        cuota_str = f"${cuota:.2f}" if cuota else "No especificado"
        estado = afiliado.get('estado', 'normal')
        estado_display = {
            'nuevo': 'Nuevo (sin ubicar)',
            'cambio_direccion': 'Cambio de dirección (re-ubicar)',
            'normal': 'Normal'
        }.get(estado, estado)
        data = [
            ["Área:", self._format_value(afiliado.get('area')), 
             "Jefe de Núcleo:", self._format_value(afiliado.get('jefe_nucleo'))],
            ["Cuota:", cuota_str, "", ""],
            ["Fecha Ingreso:", self._format_date(afiliado.get('fecha_ingreso')), 
             "Fecha Alta:", self._format_date(afiliado.get('fecha_alta'))],
            ["Fecha Baja:", self._format_date(afiliado.get('fecha_baja')), 
             "Motivo Baja:", self._format_value(afiliado.get('motivo_baja'))],
            ["Estado:", estado_display, "", ""],
            ["Fecha Creación:", self._format_datetime(afiliado.get('fecha_creacion')), "", ""],
            ["Última Modificación:", self._format_datetime(afiliado.get('fecha_modificacion')), "", ""],
        ]
        story.append(self._create_table(data))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer = Paragraph(
            f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            self.styles['Footer']
        )
        story.append(footer)
        
        # Generar PDF
        doc.build(story)
    
    def _create_table(self, data):
        """Crea una tabla formateada"""
        table = Table(data, colWidths=[1.5*inch, 2.2*inch, 1.5*inch, 2.2*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#2c3e50')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
        ]))
        return table
    
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
