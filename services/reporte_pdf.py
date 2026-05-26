import io
from datetime import datetime, date
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT


def to_float(valor):
    """Convierte Decimal, int, float a float de forma segura."""
    if valor is None:
        return 0.0
    try:
        return float(valor)
    except:
        return 0.0


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
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5C800')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        for i in range(1, len(tabla_datos)):
            if i % 2 == 0:
                estilo.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F9FAFB'))
        for i in range(1, len(tabla_datos)):
            estilo.add('ALIGN', (0, i), (-1, i), alineacion)
        tabla.setStyle(estilo)
        return tabla

    def _obtener_datos_caja_dia(self, fecha):
        query_apertura = """
            SELECT ac.monto_inicial, ac.monto_final
            FROM apertura_cierre ac
            JOIN caja c ON ac.id_caja_fk = c.id_caja
            WHERE c.fecha = %s AND ac.estado = 'CERRADO'
            ORDER BY ac.fecha_hora_apertura DESC LIMIT 1
        """
        resultado = self.db.fetch_one(query_apertura, (fecha,))
        if resultado:
            return to_float(resultado['monto_inicial']), to_float(resultado['monto_final'] or 0)
        query_abierta = """
            SELECT ac.monto_inicial, ac.monto_final
            FROM apertura_cierre ac
            JOIN caja c ON ac.id_caja_fk = c.id_caja
            WHERE c.fecha = %s AND ac.estado = 'ABIERTO'
            ORDER BY ac.fecha_hora_apertura DESC LIMIT 1
        """
        resultado = self.db.fetch_one(query_abierta, (fecha,))
        if resultado:
            return to_float(resultado['monto_inicial']), to_float(resultado['monto_final'] or 0)
        return 0, 0

    # --------------------------------------------------------------
    # REPORTE DIARIO DE CAJA (formato similar al Excel sin sucursal Guate)
    # --------------------------------------------------------------
    def reporte_diario_caja(self, fecha):
        from services.reporte_service import ReporteService
        rs = ReporteService()
        monto_inicial, monto_final = self._obtener_datos_caja_dia(fecha)
        ventas = rs.obtener_ventas(fecha, fecha)
        gastos = rs.obtener_gastos(fecha, fecha)
        comisiones = rs.obtener_resumen_por_usuario(fecha, fecha)
        total_ingresos = sum(to_float(v['total']) for v in ventas if v.get('producto_pagado', True))
        total_egresos = sum(to_float(g['monto']) for g in gastos)
        monto_esperado = monto_inicial + total_ingresos - total_egresos

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.7 * inch, bottomMargin=0.7 * inch)
        estilos = self._estilos()
        story = []

        story.append(Paragraph("TEC SHOP", estilos['Titulo']))
        story.append(Paragraph("Control de Caja Diario", estilos['Subtitulo']))
        story.append(Paragraph(f"Fecha: {fecha.strftime('%d/%m/%Y')}", estilos['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        story.append(Paragraph("Resumen de Caja", estilos['Heading2']))
        resumen_datos = [
            ["Monto Inicial", f"Q {monto_inicial:,.2f}"],
            ["Total Ingresos", f"Q {total_ingresos:,.2f}"],
            ["Total Egresos", f"Q {total_egresos:,.2f}"],
            ["Monto Final Esperado", f"Q {monto_esperado:,.2f}"],
            ["Monto Final Real", f"Q {monto_final:,.2f}"]
        ]
        tabla_resumen = Table(resumen_datos, colWidths=[2.5 * inch, 2 * inch])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        story.append(tabla_resumen)
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("Ventas del Día", estilos['Heading2']))
        if ventas:
            total_efectivo = sum(to_float(v['total']) for v in ventas if v['forma_pago'] == 'EF')
            total_tarjeta = sum(to_float(v['total']) for v in ventas if v['forma_pago'] == 'TC/TD')
            total_transferencia = sum(to_float(v['total']) for v in ventas if v['forma_pago'] == 'TF')
            total_deposito = sum(to_float(v['total']) for v in ventas if v['forma_pago'] == 'DP')
            total_envio = sum(to_float(v['total']) for v in ventas if v.get('es_envio', False))

            desglose_datos = [
                ["Forma de Pago", "Total"],
                ["Efectivo", f"Q {total_efectivo:,.2f}"],
                ["Tarjeta", f"Q {total_tarjeta:,.2f}"],
                ["Transferencia", f"Q {total_transferencia:,.2f}"],
                ["Depósito", f"Q {total_deposito:,.2f}"],
                ["Envíos (COD)", f"Q {total_envio:,.2f}"],
            ]
            tabla_desglose = self._crear_tabla(desglose_datos, anchos=[3 * inch, 2 * inch], alineacion='RIGHT')
            story.append(tabla_desglose)
            story.append(Spacer(1, 0.2 * inch))

            encabezados = ["Doc.", "Cliente", "Forma Pago", "Total"]
            datos_ventas = []
            for v in ventas:
                cliente = f"{v.get('cliente_nombre', '')} {v.get('cliente_apellido', '')}".strip()
                datos_ventas.append([
                    v.get('numero_documento', ''),
                    cliente,
                    v.get('forma_pago', ''),
                    f"Q {to_float(v['total']):,.2f}"
                ])
            tabla_ventas = self._crear_tabla(datos_ventas, encabezados,
                                             [1.5 * inch, 2.5 * inch, 1.5 * inch, 1.5 * inch])
            story.append(tabla_ventas)
        else:
            story.append(Paragraph("No hubo ventas en este día.", estilos['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        story.append(Paragraph("Gastos del Día", estilos['Heading2']))
        if gastos:
            datos_gastos = [["Concepto", "Tipo", "Monto"]]
            for g in gastos:
                datos_gastos.append([
                    g.get('descripcion', ''),
                    g.get('tipo_gasto', ''),
                    f"Q {to_float(g['monto']):,.2f}"
                ])
            tabla_gastos = self._crear_tabla(datos_gastos, anchos=[3 * inch, 1.5 * inch, 1.5 * inch])
            story.append(tabla_gastos)
        else:
            story.append(Paragraph("No se registraron gastos.", estilos['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        story.append(Paragraph("Control de Comisiones", estilos['Heading2']))
        if comisiones:
            datos_comision = [["Vendedor", "Total Vendido", "Comisión (2%)"]]
            for c in comisiones:
                comision = to_float(c['total_vendido']) * 0.02
                datos_comision.append([
                    c['nombre'],
                    f"Q {to_float(c['total_vendido']):,.2f}",
                    f"Q {comision:,.2f}"
                ])
            tabla_comision = self._crear_tabla(datos_comision, anchos=[2.5 * inch, 2 * inch, 2 * inch])
            story.append(tabla_comision)
        else:
            story.append(Paragraph("Sin ventas para comisiones.", estilos['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer

    # --------------------------------------------------------------
    # REPORTE MENSUAL DE VENTAS (resumen ejecutivo)
    # --------------------------------------------------------------
    def reporte_mensual_ventas(self, anio, mes):
        from services.reporte_service import ReporteService
        rs = ReporteService()
        fecha_inicio = date(anio, mes, 1)
        if mes == 12:
            fecha_fin = date(anio + 1, 1, 1) - date(1, 1, 1).days
        else:
            fecha_fin = date(anio, mes + 1, 1) - date(1, 1, 1).days
        ventas = rs.obtener_ventas(fecha_inicio, fecha_fin)

        if not ventas:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = [Paragraph(f"No hay ventas en {fecha_inicio.strftime('%B %Y')}", self._estilos()['Normal'])]
            doc.build(story)
            buffer.seek(0)
            return buffer

        total_ventas = sum(to_float(v['total']) for v in ventas)
        cantidad = len(ventas)
        ticket_promedio = total_ventas / cantidad if cantidad else 0

        total_efectivo = sum(to_float(v['total']) for v in ventas if v['forma_pago'] == 'EF')
        total_tarjeta = sum(to_float(v['total']) for v in ventas if v['forma_pago'] == 'TC/TD')
        total_transferencia = sum(to_float(v['total']) for v in ventas if v['forma_pago'] == 'TF')
        total_deposito = sum(to_float(v['total']) for v in ventas if v['forma_pago'] == 'DP')
        total_envio = sum(to_float(v['total']) for v in ventas if v.get('es_envio', False))

        ventas_por_dia = {}
        for v in ventas:
            dia = v['fecha_hora'].day if hasattr(v['fecha_hora'], 'day') else v['fecha_hora'].date().day
            ventas_por_dia[dia] = ventas_por_dia.get(dia, 0) + to_float(v['total'])

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=0.5 * inch)
        estilos = self._estilos()
        story = []

        nombre_mes = fecha_inicio.strftime('%B %Y').upper()
        story.append(Paragraph(f"TEC SHOP - Reporte Mensual {nombre_mes}", estilos['Titulo']))
        story.append(Spacer(1, 0.2 * inch))

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

        datos_diarios = [["Día", "Total Ventas"]]
        for dia in sorted(ventas_por_dia.keys()):
            datos_diarios.append([str(dia), f"Q {ventas_por_dia[dia]:,.2f}"])
        tabla_diaria = self._crear_tabla(datos_diarios, anchos=[1.5 * inch, 2.5 * inch])
        story.append(tabla_diaria)

        doc.build(story)
        buffer.seek(0)
        return buffer

    # --------------------------------------------------------------
    # REPORTE DE CIERRE DE TURNO (con desglose preciso de formas de pago)
    # --------------------------------------------------------------
    def reporte_cierre_turno(self, id_apertura: int, ruta_guardado: str = None):
        """
        Genera un PDF con el detalle completo del cierre de turno.
        Incluye conteo de billetes, movimientos, gastos y cuentas por cobrar
        **solo del turno actual**.
        El desglose de ventas por forma de pago se calcula desde las tablas
        venta y detalle_pago_mixto para garantizar precisión.
        """
        # Obtener datos del turno (incluyendo fechas)
        query_turno = """
            SELECT ac.id_apertura, ac.fecha_hora_apertura, ac.fecha_hora_cierre,
                   ac.monto_inicial, ac.monto_final, ac.monto_esperado, ac.diferencia,
                   u.nombre AS cajero_apertura, uc.nombre AS cajero_cierre,
                   ac.observacion_apertura, ac.observacion_cierre,
                   ac.id_caja_fk
            FROM apertura_cierre ac
            LEFT JOIN usuario u ON ac.id_usuario_fk = u.id_usuario
            LEFT JOIN usuario uc ON ac.id_usuario_cierre_fk = uc.id_usuario
            WHERE ac.id_apertura = %s
        """
        turno = self.db.fetch_one(query_turno, (id_apertura,))
        if not turno:
            raise ValueError(f"No se encontró el turno con id {id_apertura}")

        fecha_inicio = turno['fecha_hora_apertura']
        fecha_fin = turno['fecha_hora_cierre'] or datetime.now()
        id_caja = turno['id_caja_fk']

        # Detalles del conteo de billetes
        query_detalle = """
            SELECT denominacion, cantidad, subtotal
            FROM detalle_cierre
            WHERE id_apertura_fk = %s
            ORDER BY denominacion DESC
        """
        detalles_cierre = self.db.fetch_all(query_detalle, (id_apertura,)) or []

        # =========================================================
        # MOVIMIENTOS (para la tabla detallada)
        # =========================================================
        query_movimientos = """
            SELECT 
                mc.fecha_hora, 
                mc.tipo_movimiento, 
                mc.descripcion, 
                mc.monto, 
                u.nombre AS usuario,
                COALESCE(
                    (SELECT dpm.forma_pago 
                     FROM detalle_pago_mixto dpm 
                     JOIN venta v2 ON dpm.id_venta_fk = v2.id_venta
                     WHERE v2.id_movimiento_fk = mc.id_movimiento 
                       AND dpm.monto = mc.monto
                     LIMIT 1),
                    (SELECT v.forma_pago 
                     FROM venta v 
                     WHERE v.id_movimiento_fk = mc.id_movimiento 
                       AND v.forma_pago != 'MIXTO'
                     LIMIT 1),
                    (SELECT da.forma_pago 
                     FROM detalle_apartado da 
                     WHERE da.id_movimiento_fk = mc.id_movimiento
                     LIMIT 1),
                    'N/A'
                ) AS forma_pago_detalle
            FROM movimiento_caja mc
            LEFT JOIN usuario u ON mc.id_usuario_fk = u.id_usuario
            WHERE mc.id_caja_fk = %s
              AND mc.fecha_hora >= %s
              AND mc.fecha_hora <= %s
            ORDER BY mc.fecha_hora
        """
        movimientos = self.db.fetch_all(query_movimientos, (id_caja, fecha_inicio, fecha_fin)) or []
        forma_map = {
            'EF': 'Efectivo', 'EFECTIVO': 'Efectivo',
            'TC/TD': 'Tarjeta', 'TARJETA': 'Tarjeta',
            'TF': 'Transferencia', 'TRANSFERENCIA': 'Transferencia',
            'DP': 'Depósito', 'DEPOSITO': 'Depósito',
            'MIXTO': 'Mixto', 'N/A': 'N/A'
        }
        for m in movimientos:
            fp = m.get('forma_pago_detalle')
            m['forma_pago_legible'] = forma_map.get(fp.upper(), fp) if fp else '—'
            m['monto'] = to_float(m['monto'])

        # =========================================================
        # GASTOS (solo del turno)
        # =========================================================
        query_gastos = """
            SELECT g.tipo_gasto, g.descripcion, g.monto, mc.fecha_hora
            FROM gasto g
            JOIN movimiento_caja mc ON g.id_movimiento_fk = mc.id_movimiento
            WHERE mc.id_caja_fk = %s
              AND mc.fecha_hora >= %s
              AND mc.fecha_hora <= %s
            ORDER BY mc.fecha_hora
        """
        gastos = self.db.fetch_all(query_gastos, (id_caja, fecha_inicio, fecha_fin)) or []
        for g in gastos:
            g['monto'] = to_float(g['monto'])

        # =========================================================
        # CUENTAS POR COBRAR (solo del turno)
        # =========================================================
        query_cuentas = """
            SELECT cpc.numero_documento, cpc.monto, v.numero_guia, ee.nombre AS empresa
            FROM cuenta_por_cobrar cpc
            JOIN movimiento_caja mc ON cpc.id_movimiento_fk = mc.id_movimiento
            JOIN venta v ON cpc.id_venta_fk = v.id_venta
            LEFT JOIN empresa_envio ee ON v.id_empresa_fk = ee.id_empresa
            WHERE mc.id_caja_fk = %s
              AND mc.fecha_hora >= %s
              AND mc.fecha_hora <= %s
              AND cpc.pagado = false
        """
        cuentas = self.db.fetch_all(query_cuentas, (id_caja, fecha_inicio, fecha_fin)) or []
        for c in cuentas:
            c['monto'] = to_float(c['monto'])

        # =========================================================
        # DESGLOSE DE VENTAS POR FORMA DE PAGO
        # (Consulta directa a ventas y detalle_pago_mixto)
        # =========================================================
        # Ventas normales (no mixtas) del turno
        query_ventas_normales = """
            SELECT v.forma_pago, SUM(v.total) as total
            FROM venta v
            JOIN movimiento_caja mc ON v.id_movimiento_fk = mc.id_movimiento
            WHERE mc.id_caja_fk = %s
              AND mc.fecha_hora >= %s
              AND mc.fecha_hora <= %s
              AND v.producto_pagado = true
              AND v.forma_pago != 'MIXTO'
            GROUP BY v.forma_pago
        """
        normales = self.db.fetch_all(query_ventas_normales, (id_caja, fecha_inicio, fecha_fin)) or []
        # Ventas mixtas (suma por tipo de pago desde detalle_pago_mixto)
        query_mixtas = """
            SELECT dpm.forma_pago, SUM(dpm.monto) as total
            FROM detalle_pago_mixto dpm
            JOIN venta v ON dpm.id_venta_fk = v.id_venta
            JOIN movimiento_caja mc ON v.id_movimiento_fk = mc.id_movimiento
            WHERE mc.id_caja_fk = %s
              AND mc.fecha_hora >= %s
              AND mc.fecha_hora <= %s
              AND v.producto_pagado = true
            GROUP BY dpm.forma_pago
        """
        mixtas = self.db.fetch_all(query_mixtas, (id_caja, fecha_inicio, fecha_fin)) or []

        # Acumular totales
        total_efectivo = 0.0
        total_tarjeta = 0.0
        total_transferencia = 0.0
        total_deposito = 0.0

        for n in normales:
            fp = n['forma_pago']
            monto = to_float(n['total'])
            if fp == 'EF':
                total_efectivo += monto
            elif fp == 'TC/TD':
                total_tarjeta += monto
            elif fp == 'TF':
                total_transferencia += monto
            elif fp == 'DP':
                total_deposito += monto

        for m in mixtas:
            fp = m['forma_pago']
            monto = to_float(m['total'])
            if fp in ('EFECTIVO', 'EF'):
                total_efectivo += monto
            elif fp in ('TARJETA', 'TC/TD'):
                total_tarjeta += monto
            elif fp in ('TRANSFERENCIA', 'TF'):
                total_transferencia += monto
            elif fp in ('DEPOSITO', 'DP'):
                total_deposito += monto

        # =========================================================
        # CREACIÓN DEL PDF
        # =========================================================
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.7 * inch, bottomMargin=0.7 * inch)
        estilos = self._estilos()
        story = []

        # Encabezado
        story.append(Paragraph("TEC SHOP", estilos['Titulo']))
        story.append(Paragraph("Reporte de Cierre de Turno", estilos['Subtitulo']))
        story.append(Spacer(1, 0.2 * inch))

        # Datos del turno
        story.append(Paragraph("Datos del Turno", estilos['Heading2']))
        datos_turno = [
            ["Fecha apertura:", fecha_inicio.strftime('%d/%m/%Y %H:%M:%S')],
            ["Fecha cierre:", fecha_fin.strftime('%d/%m/%Y %H:%M:%S') if turno['fecha_hora_cierre'] else "Abierto"],
            ["Cajero apertura:", turno['cajero_apertura']],
            ["Cajero cierre:", turno['cajero_cierre'] or "-"],
            ["Monto inicial:", f"Q {to_float(turno['monto_inicial']):,.2f}"],
            ["Monto esperado:", f"Q {to_float(turno['monto_esperado']):,.2f}"],
            ["Monto contado:", f"Q {to_float(turno['monto_final']):,.2f}"],
            ["Diferencia:", f"Q {to_float(turno['diferencia']):,.2f}"],
        ]
        tabla_datos = Table(datos_turno, colWidths=[2.5 * inch, 2.5 * inch])
        tabla_datos.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        story.append(tabla_datos)
        story.append(Spacer(1, 0.2 * inch))

        # Conteo de billetes
        story.append(Paragraph("Conteo de Efectivo al Cierre", estilos['Heading2']))
        if detalles_cierre:
            datos_billetes = [["Denominación", "Cantidad", "Subtotal"]]
            total_contado = 0
            for d in detalles_cierre:
                subtotal = to_float(d['subtotal'])
                datos_billetes.append([
                    f"Q {d['denominacion']}.00",
                    d['cantidad'],
                    f"Q {subtotal:,.2f}"
                ])
                total_contado += subtotal
            datos_billetes.append(["", "TOTAL", f"Q {total_contado:,.2f}"])
            tabla_billetes = self._crear_tabla(datos_billetes, anchos=[1.5 * inch, 1.5 * inch, 1.5 * inch])
            story.append(tabla_billetes)
        else:
            story.append(Paragraph("No se registró conteo de billetes.", estilos['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Resumen de ventas por forma de pago (datos precisos)
        story.append(Paragraph("Resumen de Ventas del Turno", estilos['Heading2']))
        resumen_ventas = [
            ["Forma de Pago", "Total"],
            ["Efectivo", f"Q {total_efectivo:,.2f}"],
            ["Tarjeta", f"Q {total_tarjeta:,.2f}"],
            ["Transferencia", f"Q {total_transferencia:,.2f}"],
            ["Depósito", f"Q {total_deposito:,.2f}"],
        ]
        tabla_resumen = self._crear_tabla(resumen_ventas, anchos=[2.5 * inch, 2.5 * inch], alineacion='RIGHT')
        story.append(tabla_resumen)
        story.append(Spacer(1, 0.3 * inch))

        # Movimientos detallados (solo para mostrar, no afecta el resumen)
        story.append(Paragraph("Movimientos del Turno", estilos['Heading2']))
        if movimientos:
            datos_mov = [["Fecha/Hora", "Tipo", "Forma Pago", "Descripción", "Monto"]]
            for m in movimientos:
                # Truncar descripción a 45 caracteres para mejor visualización
                desc = m['descripcion'][:45] if m['descripcion'] else ""
                datos_mov.append([
                    m['fecha_hora'].strftime('%d/%m %H:%M'),
                    m['tipo_movimiento'][:8],
                    m.get('forma_pago_legible', '—'),
                    desc,
                    f"Q {m['monto']:,.2f}" if m['monto'] else "Q 0.00"
                ])

            tabla_mov = Table(datos_mov, colWidths=[1.0 * inch, 0.75 * inch, 0.9 * inch, 2.2 * inch, 1.0 * inch])

            # Estilo optimizado para tabla de movimientos
            estilo_mov = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5C800')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7),
                ('FONTSIZE', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                ('TOPPADDING', (0, 0), (-1, 0), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 1), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWHEIGHT', (0, 1), (-1, -1), 16),
            ])

            # Aplicar colores alternados
            for i in range(1, len(datos_mov)):
                if i % 2 == 0:
                    estilo_mov.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F9FAFB'))

            # Alineaciones específicas
            for i in range(len(datos_mov)):
                estilo_mov.add('ALIGN', (0, i), (0, i), 'CENTER')  # Fecha
                estilo_mov.add('ALIGN', (1, i), (1, i), 'CENTER')  # Tipo
                estilo_mov.add('ALIGN', (2, i), (2, i), 'CENTER')  # Forma Pago
                estilo_mov.add('ALIGN', (3, i), (3, i), 'LEFT')  # Descripción
                estilo_mov.add('ALIGN', (4, i), (4, i), 'RIGHT')  # Monto

            tabla_mov.setStyle(estilo_mov)
            story.append(tabla_mov)
        else:
            story.append(Paragraph("No hay movimientos en este turno.", estilos['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Gastos
        story.append(Paragraph("Gastos Registrados", estilos['Heading2']))
        if gastos:
            datos_gastos = [["Fecha", "Tipo", "Descripción", "Monto"]]
            for g in gastos:
                datos_gastos.append([
                    g['fecha_hora'].strftime('%d/%m/%Y'),
                    g['tipo_gasto'],
                    g['descripcion'][:50],
                    f"Q {g['monto']:,.2f}"
                ])
            tabla_gastos = self._crear_tabla(datos_gastos, anchos=[1.2 * inch, 1.2 * inch, 2.5 * inch, 1.2 * inch])
            story.append(tabla_gastos)
        else:
            story.append(Paragraph("No se registraron gastos.", estilos['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Cuentas por cobrar pendientes
        story.append(Paragraph("Cuentas por Cobrar Generadas (Pendientes)", estilos['Heading2']))
        if cuentas:
            datos_cuentas = [["Documento", "Monto", "Guía", "Empresa"]]
            for c in cuentas:
                datos_cuentas.append([
                    c['numero_documento'],
                    f"Q {c['monto']:,.2f}",
                    c['numero_guia'] or "",
                    c['empresa'] or ""
                ])
            tabla_cuentas = self._crear_tabla(datos_cuentas, anchos=[1.5 * inch, 1.5 * inch, 1.5 * inch, 2 * inch])
            story.append(tabla_cuentas)
        else:
            story.append(Paragraph("No hay cuentas por cobrar pendientes generadas en este turno.", estilos['Normal']))

        # Generar PDF
        doc.build(story)
        buffer.seek(0)

        # Guardar en disco
        if not ruta_guardado:
            from pathlib import Path
            docs_dir = Path.home() / "Documents" / "ReportesCaja"
            docs_dir.mkdir(parents=True, exist_ok=True)
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_guardado = str(docs_dir / f"Cierre_Turno_{id_apertura}_{fecha_str}.pdf")

        with open(ruta_guardado, 'wb') as f:
            f.write(buffer.getbuffer())
        return ruta_guardado