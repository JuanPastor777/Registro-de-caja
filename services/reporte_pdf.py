# services/reporte_pdf.py
import io
from datetime import datetime, date
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

class GeneradorPDF:
    def __init__(self, db_connection):
        self.db = db_connection

    def _estilos(self):
        estilos = getSampleStyleSheet()
        estilos.add(ParagraphStyle(name='Titulo', parent=estilos['Heading1'],
                                   fontSize=20, textColor=colors.HexColor('#F5C800'),
                                   alignment=TA_CENTER, spaceAfter=20))
        estilos.add(ParagraphStyle(name='Subtitulo', parent=estilos['Heading2'],
                                   fontSize=14, textColor=colors.HexColor('#1E293B'),
                                   alignment=TA_CENTER, spaceAfter=12))
        estilos.add(ParagraphStyle(name='EncabezadoTabla', parent=estilos['Normal'],
                                   fontSize=10, textColor=colors.white, alignment=TA_CENTER,
                                   backColor=colors.HexColor('#F5C800')))
        estilos.add(ParagraphStyle(name='Total', parent=estilos['Normal'],
                                   fontSize=12, textColor=colors.HexColor('#10B981'),
                                   alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        return estilos

    def _crear_tabla(self, datos, encabezados=None, anchos=None, alineacion='CENTER'):
        if encabezados:
            tabla_datos = [encabezados] + datos
        else:
            tabla_datos = datos
        tabla = Table(tabla_datos, colWidths=anchos, repeatRows=1)
        estilo = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F5C800')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ])
        # Alternar filas
        for i in range(1, len(tabla_datos)):
            if i % 2 == 0:
                estilo.add('BACKGROUND', (0,i), (-1,i), colors.HexColor('#F9FAFB'))
        # Alineación por defecto en las celdas de datos
        for i in range(1, len(tabla_datos)):
            estilo.add('ALIGN', (0,i), (-1,i), alineacion)
        tabla.setStyle(estilo)
        return tabla

    def _obtener_datos_caja_dia(self, fecha):
        """Obtiene monto inicial y final de la caja para una fecha específica."""
        query_apertura = """
            SELECT ac.monto_inicial, ac.monto_final
            FROM apertura_cierre ac
            JOIN caja c ON ac.id_caja_fk = c.id_caja
            WHERE c.fecha = %s AND ac.estado = 'CERRADO'
            ORDER BY ac.fecha_hora_apertura DESC LIMIT 1
        """
        resultado = self.db.fetch_one(query_apertura, (fecha,))
        if resultado:
            return float(resultado['monto_inicial']), float(resultado['monto_final'] or 0)
        # Si no hay cierre, buscar apertura abierta
        query_abierta = """
            SELECT ac.monto_inicial, ac.monto_final
            FROM apertura_cierre ac
            JOIN caja c ON ac.id_caja_fk = c.id_caja
            WHERE c.fecha = %s AND ac.estado = 'ABIERTO'
            ORDER BY ac.fecha_hora_apertura DESC LIMIT 1
        """
        resultado = self.db.fetch_one(query_abierta, (fecha,))
        if resultado:
            return float(resultado['monto_inicial']), float(resultado['monto_final'] or 0)
        return 0, 0

    def reporte_diario_caja(self, fecha):
        """Genera PDF similar al Excel sin sucursal Guate, unificando ventas."""
        from services.reporte_service import ReporteService
        rs = ReporteService()

        # Datos de caja
        monto_inicial, monto_final = self._obtener_datos_caja_dia(fecha)

        # Ventas del día
        ventas = rs.obtener_ventas(fecha, fecha)

        # Gastos del día
        gastos = rs.obtener_gastos(fecha, fecha)

        # Comisiones (ventas por usuario)
        comisiones = rs.obtener_resumen_por_usuario(fecha, fecha)

        # Calcular totales de ingresos/egresos
        total_ingresos = sum(v['total'] for v in ventas if v.get('producto_pagado', True))
        total_egresos = sum(g['monto'] for g in gastos)
        monto_esperado = monto_inicial + total_ingresos - total_egresos

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.7*inch, bottomMargin=0.7*inch)
        estilos = self._estilos()
        story = []

        # Encabezado
        story.append(Paragraph("TEC SHOP", estilos['Titulo']))
        story.append(Paragraph("Control de Caja Diario", estilos['Subtitulo']))
        story.append(Paragraph(f"Fecha: {fecha.strftime('%d/%m/%Y')}", estilos['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Resumen de caja
        story.append(Paragraph("Resumen de Caja", estilos['Heading2']))
        resumen_datos = [
            ["Monto Inicial", f"Q {monto_inicial:,.2f}"],
            ["Total Ingresos", f"Q {total_ingresos:,.2f}"],
            ["Total Egresos", f"Q {total_egresos:,.2f}"],
            ["Monto Final Esperado", f"Q {monto_esperado:,.2f}"],
            ["Monto Final Real", f"Q {monto_final:,.2f}"]
        ]
        tabla_resumen = Table(resumen_datos, colWidths=[2.5*inch, 2*inch])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F3F4F6')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ]))
        story.append(tabla_resumen)
        story.append(Spacer(1, 0.2*inch))

        # Ventas del día
        story.append(Paragraph("Ventas del Día", estilos['Heading2']))
        if ventas:
            total_efectivo = sum(v['total'] for v in ventas if v['forma_pago'] == 'EF')
            total_tarjeta = sum(v['total'] for v in ventas if v['forma_pago'] == 'TC/TD')
            total_transferencia = sum(v['total'] for v in ventas if v['forma_pago'] == 'TF')
            total_deposito = sum(v['total'] for v in ventas if v['forma_pago'] == 'DP')
            total_envio = sum(v['total'] for v in ventas if v.get('es_envio', False))

            desglose_datos = [
                ["Forma de Pago", "Total"],
                ["Efectivo", f"Q {total_efectivo:,.2f}"],
                ["Tarjeta", f"Q {total_tarjeta:,.2f}"],
                ["Transferencia", f"Q {total_transferencia:,.2f}"],
                ["Depósito", f"Q {total_deposito:,.2f}"],
                ["Envíos (COD)", f"Q {total_envio:,.2f}"],
            ]
            tabla_desglose = self._crear_tabla(desglose_datos, anchos=[3*inch, 2*inch], alineacion='RIGHT')
            story.append(tabla_desglose)
            story.append(Spacer(1, 0.2*inch))

            # Detalle de ventas
            encabezados = ["Doc.", "Cliente", "Forma Pago", "Total"]
            datos_ventas = []
            for v in ventas:
                cliente = f"{v.get('cliente_nombre','')} {v.get('cliente_apellido','')}".strip()
                datos_ventas.append([
                    v.get('numero_documento', ''),
                    cliente,
                    v.get('forma_pago', ''),
                    f"Q {v['total']:,.2f}"
                ])
            tabla_ventas = self._crear_tabla(datos_ventas, encabezados, [1.5*inch, 2.5*inch, 1.5*inch, 1.5*inch])
            story.append(tabla_ventas)
        else:
            story.append(Paragraph("No hubo ventas en este día.", estilos['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Gastos
        story.append(Paragraph("Gastos del Día", estilos['Heading2']))
        if gastos:
            datos_gastos = [["Concepto", "Tipo", "Monto"]]
            for g in gastos:
                datos_gastos.append([
                    g.get('descripcion', ''),
                    g.get('tipo_gasto', ''),
                    f"Q {g['monto']:,.2f}"
                ])
            tabla_gastos = self._crear_tabla(datos_gastos, anchos=[3*inch, 1.5*inch, 1.5*inch])
            story.append(tabla_gastos)
        else:
            story.append(Paragraph("No se registraron gastos.", estilos['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Comisiones
        story.append(Paragraph("Control de Comisiones", estilos['Heading2']))
        if comisiones:
            datos_comision = [["Vendedor", "Total Vendido", "Comisión (2%)"]]
            for c in comisiones:
                comision = c['total_vendido'] * 0.02
                datos_comision.append([
                    c['nombre'],
                    f"Q {c['total_vendido']:,.2f}",
                    f"Q {comision:,.2f}"
                ])
            tabla_comision = self._crear_tabla(datos_comision, anchos=[2.5*inch, 2*inch, 2*inch])
            story.append(tabla_comision)
        else:
            story.append(Paragraph("Sin ventas para comisiones.", estilos['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer

    def reporte_mensual_ventas(self, anio, mes):
        """Reporte mensual resumido usando ventas del mes completo."""
        from services.reporte_service import ReporteService
        from datetime import timedelta
        rs = ReporteService()

        # Primer día del mes
        fecha_inicio = date(anio, mes, 1)
        # Último día del mes
        if mes == 12:
            fecha_fin = date(anio, 12, 31)
        else:
            fecha_fin = date(anio, mes + 1, 1) - timedelta(days=1)

        ventas = rs.obtener_ventas(fecha_inicio, fecha_fin)

        if not ventas:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = [Paragraph(f"No hay ventas en {fecha_inicio.strftime('%B %Y')}", self._estilos()['Normal'])]
            doc.build(story)
            buffer.seek(0)
            return buffer

        total_ventas = sum(v['total'] for v in ventas)
        cantidad = len(ventas)
        ticket_promedio = total_ventas / cantidad if cantidad else 0

        # Desglose por forma de pago
        total_efectivo = sum(v['total'] for v in ventas if v['forma_pago'] == 'EF')
        total_tarjeta = sum(v['total'] for v in ventas if v['forma_pago'] == 'TC/TD')
        total_transferencia = sum(v['total'] for v in ventas if v['forma_pago'] == 'TF')
        total_deposito = sum(v['total'] for v in ventas if v['forma_pago'] == 'DP')
        total_envio = sum(v['total'] for v in ventas if v.get('es_envio', False))

        # Ventas por día
        ventas_por_dia = {}
        for v in ventas:
            # v['fecha_hora'] puede ser datetime o date
            fecha_hora = v['fecha_hora']
            if hasattr(fecha_hora, 'date'):
                dia = fecha_hora.date().day
            else:
                dia = fecha_hora.day
            ventas_por_dia[dia] = ventas_por_dia.get(dia, 0) + v['total']

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=0.5 * inch)
        estilos = self._estilos()
        story = []

        nombre_mes = fecha_inicio.strftime('%B %Y').upper()
        story.append(Paragraph(f"TEC SHOP - Reporte Mensual {nombre_mes}", estilos['Titulo']))
        story.append(Spacer(1, 0.2 * inch))

        # Resumen
        resumen_datos = [
            ["Total Ventas", f"Q {total_ventas:,.2f}"],
            ["Cantidad de Ventas", f"{cantidad}"],
            ["Ticket Promedio", f"Q {ticket_promedio:,.2f}"],
        ]
        tabla_resumen = Table(resumen_datos, colWidths=[2 * inch, 2 * inch])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F4F6')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        story.append(tabla_resumen)
        story.append(Spacer(1, 0.2 * inch))

        # Desglose formas de pago
        desglose_datos = [
            ["Forma de Pago", "Monto"],
            ["Efectivo", f"Q {total_efectivo:,.2f}"],
            ["Tarjeta", f"Q {total_tarjeta:,.2f}"],
            ["Transferencia", f"Q {total_transferencia:,.2f}"],
            ["Depósito", f"Q {total_deposito:,.2f}"],
            ["Envíos (COD)", f"Q {total_envio:,.2f}"],
        ]
        tabla_desglose = self._crear_tabla(desglose_datos, anchos=[2.5 * inch, 2.5 * inch], alineacion='RIGHT')
        story.append(tabla_desglose)
        story.append(Spacer(1, 0.2 * inch))

        # Ventas por día
        datos_diarios = [["Día", "Total Ventas"]]
        for dia in sorted(ventas_por_dia.keys()):
            datos_diarios.append([str(dia), f"Q {ventas_por_dia[dia]:,.2f}"])
        tabla_diaria = self._crear_tabla(datos_diarios, anchos=[1.5 * inch, 2.5 * inch])
        story.append(tabla_diaria)

        doc.build(story)
        buffer.seek(0)
        return buffer