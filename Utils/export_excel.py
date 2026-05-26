# Utils/export_excel.py
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from collections import defaultdict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.conexion import DatabaseConnection

def to_float(valor):
    if valor is None:
        return 0.0
    try:
        return float(valor)
    except:
        return 0.0

class ExportadorExcel:
    def __init__(self, ventas, diarios, nombre_mes):
        """
        ventas: lista de diccionarios con todas las ventas del período
        diarios: NO se usa (se mantiene por compatibilidad, pero ignorado)
        nombre_mes: string "ENERO", "FEBRERO", etc.
        """
        self.ventas = ventas
        self.nombre_mes = nombre_mes.upper()
        self.db = DatabaseConnection()

    def generar(self, ruta):
        wb = openpyxl.Workbook()
        wb.remove(wb.active)
        self._crear_hoja_principal(wb)
        # NO se crean hojas diarias
        wb.save(ruta)

    # --------------------------------------------------------------
    # HOJA PRINCIPAL (ENERO, FEBRERO, ...)
    # --------------------------------------------------------------
    def _crear_hoja_principal(self, wb):
        ws = wb.create_sheet(self.nombre_mes)

        # Estilos
        header_font = Font(bold=True, size=10)
        header_fill = PatternFill(start_color="F5C800", end_color="F5C800", fill_type="solid")
        center_align = Alignment(horizontal="center", vertical="center")
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                             top=Side(style='thin'), bottom=Side(style='thin'))

        # Columnas según el Excel original (dos columnas de monto)
        columnas = [
            "DIA", "FAC./RECI", "NO", "CLIENTE", "PRODUCTO", "Marca", "MODELO",
            "MONTO", "MONTO", "CONSIGNATARIO", "SOPORTE", "BODEGA DE ENTREGA", "OTROS"
        ]
        for col_idx, titulo in enumerate(columnas, start=1):
            cell = ws.cell(row=3, column=col_idx, value=titulo)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thin_border

        fila = 4
        for venta in self.ventas:
            # DIA
            fecha = venta['fecha_hora']
            dia = fecha.day if hasattr(fecha, 'day') else fecha.date().day
            ws.cell(row=fila, column=1, value=dia).alignment = center_align

            # FAC./RECI y NO
            num_doc = venta.get('numero_documento', '')
            tipo_doc = num_doc.split('-')[0] if '-' in num_doc else ''
            ws.cell(row=fila, column=2, value=tipo_doc).alignment = center_align
            ws.cell(row=fila, column=3, value=num_doc).alignment = center_align

            # CLIENTE
            cliente = f"{venta.get('cliente_nombre','')} {venta.get('cliente_apellido','')}".strip()
            ws.cell(row=fila, column=4, value=cliente)

            # PRODUCTO, Marca, MODELO
            productos = venta.get('productos', [])
            if productos:
                p = productos[0]
                ws.cell(row=fila, column=5, value=p.get('producto_nombre', ''))
                ws.cell(row=fila, column=6, value=p.get('marca', ''))
                ws.cell(row=fila, column=7, value=p.get('modelo', ''))
            else:
                ws.cell(row=fila, column=5, value=venta.get('producto_nombre', ''))
                ws.cell(row=fila, column=6, value=venta.get('marca', ''))
                ws.cell(row=fila, column=7, value=venta.get('modelo', ''))

            # MONTO (dos veces, col H y col I)
            total_venta = to_float(venta['total'])
            ws.cell(row=fila, column=8, value=total_venta).number_format = '#,##0.00'
            ws.cell(row=fila, column=9, value=total_venta).number_format = '#,##0.00'

            # CONSIGNATARIO (para envíos)
            consignatario = ""
            if venta.get('es_envio') and venta.get('forma_pago') == 'COD':
                consignatario = venta.get('empresa_envio', '') or venta.get('consignatario', '')
            ws.cell(row=fila, column=10, value=consignatario)

            # SOPORTE
            soporte = "TX"
            if venta.get('es_envio') and venta.get('forma_pago') == 'COD':
                soporte = venta.get('empresa_envio', 'CARGO EXPRESSO')
            ws.cell(row=fila, column=11, value=soporte).alignment = center_align

            # BODEGA DE ENTREGA (siempre XELA)
            ws.cell(row=fila, column=12, value="XELA").alignment = center_align

            # OTROS (pagos mixtos)
            if venta.get('forma_pago') == 'MIXTO':
                detalles = venta.get('pagos_mixtos', [])
                if detalles:
                    texto = ", ".join([f"{d['forma_pago']}: Q{to_float(d['monto']):.2f}" for d in detalles])
                    ws.cell(row=fila, column=13, value=texto)

            fila += 1

        # --- Totales después de los datos ---
        fila += 1

        # ENVIOS Cargo Expresso y FORZA
        ws.cell(row=fila, column=7, value="ENVIOS Cargo Expresso")
        ws.cell(row=fila, column=10, value=f"=COUNTIF(K4:K{fila-1},\"CARGO EXPRESSO\")")
        fila += 1
        ws.cell(row=fila, column=7, value="ENVIOS CON FORZA")
        ws.cell(row=fila, column=10, value=f"=COUNTIF(K4:K{fila-1},\"FORZA\")")
        fila += 2

        # TICKETS (recibos) y FACTURAS
        ws.cell(row=fila, column=5, value="VENTAS DE XELA")
        ws.cell(row=fila, column=6, value="VENTAS DE XELA")
        fila += 1
        ws.cell(row=fila, column=5, value="TOTAL TICKETS")
        ws.cell(row=fila, column=7, value=f"=SUMIF(B4:B{fila-1},\"REC\",H4:H{fila-1})")
        ws.cell(row=fila, column=8, value=f"=SUMIF(B4:B{fila-1},\"REC\",I4:I{fila-1})")
        fila += 1
        ws.cell(row=fila, column=5, value="TOTAL FACTURAS")
        ws.cell(row=fila, column=7, value=f"=SUMIF(B4:B{fila-1},\"FAC\",H4:H{fila-1})")
        ws.cell(row=fila, column=8, value=f"=SUMIF(B4:B{fila-1},\"FAC\",I4:I{fila-1})")
        fila += 1
        ws.cell(row=fila, column=5, value="TOTAL DE VENTA")
        ws.cell(row=fila, column=7, value=f"=+H{fila-2}+H{fila-1}")
        ws.cell(row=fila, column=8, value=f"=+I{fila-2}+I{fila-1}")
        fila += 2
        ws.cell(row=fila, column=5, value="TOTAL XELA")
        ws.cell(row=fila, column=7, value=f"=I{fila-1}+H{fila-1}")
        fila += 2

        # CONTROL COMISIONES
        ws.cell(row=fila, column=1, value="CONTROL COMISIONES")
        fila += 2
        # Agrupar ventas por usuario
        ventas_por_usuario = defaultdict(float)
        for v in self.ventas:
            usuario = v.get('usuario_nombre', '')
            ventas_por_usuario[usuario] += to_float(v['total'])

        ws.cell(row=fila, column=1, value="VENDEDOR")
        ws.cell(row=fila, column=2, value="TOTAL VENDIDO")
        ws.cell(row=fila, column=3, value="COMISIÓN (2%)")
        fila += 1
        for usuario, total in ventas_por_usuario.items():
            ws.cell(row=fila, column=1, value=usuario)
            ws.cell(row=fila, column=2, value=total).number_format = '#,##0.00'
            ws.cell(row=fila, column=3, value=total * 0.02).number_format = '#,##0.00'
            fila += 1
        ws.cell(row=fila, column=2, value=f"=SUM(B{fila-3}:B{fila-1})")
        ws.cell(row=fila, column=3, value=f"=SUM(C{fila-3}:C{fila-1})")

        # Ajustar anchos de columnas
        for col in range(1, 14):
            ws.column_dimensions[get_column_letter(col)].width = 14
        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 18