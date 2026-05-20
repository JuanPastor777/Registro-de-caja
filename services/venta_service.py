# services/venta_service.py
import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.conexion import DatabaseConnection


class ServiceVenta:
    """Servicio para gestionar ventas"""

    def __init__(self, id_usuario_actual: int = None):
        self.db = DatabaseConnection()
        self.id_usuario_actual = id_usuario_actual or self._obtener_usuario_por_defecto()

    def _obtener_usuario_por_defecto(self) -> int:
        try:
            query = "SELECT id_usuario FROM public.usuario WHERE estado = true LIMIT 1"
            result = self.db.fetch_one(query)
            return result['id_usuario'] if result else 1
        except:
            return 1

    def _obtener_caja_del_dia(self) -> int | None:
        query = "SELECT id_caja FROM public.caja WHERE fecha = CURRENT_DATE"
        resultado = self.db.fetch_one(query)
        return resultado['id_caja'] if resultado else None

    def _obtener_apertura_activa(self) -> dict | None:
        query = """
            SELECT id_apertura, id_caja_fk, monto_inicial, monto_final
            FROM public.apertura_cierre
            WHERE fecha_hora_cierre IS NULL
            ORDER BY fecha_hora_apertura DESC LIMIT 1
        """
        return self.db.fetch_one(query)

    def verificar_caja_abierta(self) -> dict:
        apertura = self._obtener_apertura_activa()
        if not apertura:
            return {
                'success': False,
                'message': 'No hay una caja abierta. Debe abrir caja primero.'
            }
        caja = self._obtener_caja_del_dia()
        if not caja:
            return {
                'success': False,
                'message': 'No hay caja registrada para hoy.'
            }
        return {
            'success': True,
            'id_apertura': apertura['id_apertura'],
            'id_caja': caja
        }

    def obtener_cliente(self, id_cliente: int) -> dict | None:
        query = "SELECT id_cliente, nombre, apellido, telefono FROM public.cliente WHERE id_cliente = %s"
        return self.db.fetch_one(query, (id_cliente,))

    def obtener_producto(self, id_producto: int) -> dict | None:
        query = """
            SELECT id_producto, nombre, marca, modelo, precio_costo 
            FROM public.producto WHERE id_producto = %s
        """
        return self.db.fetch_one(query, (id_producto,))

    def registrar_venta(
            self,
            id_cliente: int,
            forma_pago: str,
            tipo_documento: str,
            numero_documento_manual: str,
            es_envio: bool = False,
            id_empresa_fk: int = None,
            numero_guia: str = None,
            precio_envio: float = 0,
            producto_pagado: bool = True,
            productos: list = None,
            pagos_mixtos: dict = None
    ) -> dict:
        """
        Registra una venta completa con sus detalles y movimiento de caja.
        - productos: lista de dict con id_producto, cantidad, precio_unitario, descuento,
                     aumento_porcentaje, aumento_monto
        - pagos_mixtos: dict con claves 'EF', 'TC/TD', 'TF', 'DP' y montos (solo para forma 'MIXTO')
        """
        try:
            # Validar documento
            if not tipo_documento or tipo_documento not in ('FAC', 'REC'):
                return {'success': False, 'message': 'Tipo de documento inválido. Use FAC o REC.'}
            if not numero_documento_manual or not str(numero_documento_manual).strip():
                return {'success': False, 'message': 'Debe ingresar el número de documento.'}
            numero_documento = f"{tipo_documento}-{str(numero_documento_manual).strip()}"

            # Verificar caja abierta
            caja_verificada = self.verificar_caja_abierta()
            if not caja_verificada['success']:
                return caja_verificada
            id_caja = caja_verificada['id_caja']
            id_apertura = caja_verificada['id_apertura']

            # Verificar cliente
            cliente = self.obtener_cliente(id_cliente)
            if not cliente:
                return {'success': False, 'message': f'Cliente ID {id_cliente} no encontrado'}

            if not productos:
                return {'success': False, 'message': 'Debe agregar al menos un producto'}

            # Calcular total
            total = 0.0
            for item in productos:
                subtotal = (float(item['cantidad']) * float(item['precio_unitario'])) - float(item.get('descuento', 0))
                total += subtotal
            total += float(precio_envio or 0)

            nombre_cliente = (f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}").strip()

            # Preparar movimiento de caja
            tipo_movimiento = 'INGRESO' if producto_pagado else 'CUENTA_POR_COBRAR'
            descripcion_movimiento = f"Venta {numero_documento} - {nombre_cliente}"
            if forma_pago == 'MIXTO' and pagos_mixtos:
                detalle_mixto = " | ".join(f"{k}:Q{v:.2f}" for k, v in pagos_mixtos.items() if v > 0)
                descripcion_movimiento = f"Venta MIXTA {numero_documento} - {nombre_cliente} [{detalle_mixto}]"

            # Crear movimiento principal
            query_movimiento = """
                INSERT INTO public.movimiento_caja
                (id_caja_fk, tipo_movimiento, descripcion, monto, id_usuario_fk, fecha_hora)
                VALUES (%s, %s, %s, %s, %s, NOW())
                RETURNING id_movimiento
            """
            resultado_mov = self.db.fetch_one(query_movimiento, (
                id_caja, tipo_movimiento, descripcion_movimiento, total, self.id_usuario_actual))
            if not resultado_mov:
                return {'success': False, 'message': 'Error al crear movimiento'}
            id_movimiento = resultado_mov['id_movimiento']

            # Si es pago mixto, registrar movimientos individuales por cada forma de pago (ingresos adicionales)
            if forma_pago == 'MIXTO' and pagos_mixtos:
                nombres_forma = {'EF': 'Efectivo', 'TC/TD': 'Tarjeta', 'TF': 'Transferencia', 'DP': 'Depósito'}
                for fp_codigo, fp_monto in pagos_mixtos.items():
                    if fp_monto > 0:
                        desc_fp = f"Pago mixto {nombres_forma.get(fp_codigo, fp_codigo)} - {numero_documento}"
                        self.db.fetch_one("""
                            INSERT INTO public.movimiento_caja
                            (id_caja_fk, tipo_movimiento, descripcion, monto, id_usuario_fk, fecha_hora)
                            VALUES (%s, 'INGRESO', %s, %s, %s, NOW())
                            RETURNING id_movimiento
                        """, (id_caja, desc_fp, fp_monto, self.id_usuario_actual))

            # Crear venta
            query_venta = """
                INSERT INTO public.venta
                (id_movimiento_fk, id_cliente_fk, numero_documento, forma_pago, total,
                 es_envio, id_empresa_fk, numero_guia, producto_pagado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_venta
            """
            resultado_venta = self.db.fetch_one(query_venta, (
                id_movimiento, id_cliente, numero_documento, forma_pago, total,
                es_envio, id_empresa_fk, numero_guia, producto_pagado))
            if not resultado_venta:
                return {'success': False, 'message': 'Error al registrar venta'}
            id_venta = resultado_venta['id_venta']

            # Insertar detalles de venta (con soporte para aumentos/descuentos)
            for item in productos:
                subtotal = (float(item['cantidad']) * float(item['precio_unitario'])) - float(item.get('descuento', 0))
                aumento_porcentaje = item.get('aumento_porcentaje', 0)
                aumento_monto = item.get('aumento_monto', 0)
                query_detalle = """
                    INSERT INTO public.detalle_venta
                    (id_venta_fk, id_producto_fk, cantidad, precio_unitario, subtotal, descuento,
                     aumento_porcentaje, aumento_monto)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.db.execute_query(query_detalle, (
                    id_venta, item['id_producto'], item['cantidad'],
                    item['precio_unitario'], subtotal, item.get('descuento', 0),
                    aumento_porcentaje, aumento_monto))

            # Si no está pagado, crear cuenta por cobrar
            if not producto_pagado:
                query_cuenta = """
                    INSERT INTO public.cuenta_por_cobrar
                    (id_movimiento_fk, numero_documento, monto, id_venta_fk, pagado)
                    VALUES (%s, %s, %s, %s, false)
                """
                self.db.execute_query(query_cuenta, (id_movimiento, numero_documento, total, id_venta))

            # Actualizar monto final en la apertura (solo si el producto fue pagado)
            if producto_pagado:
                query_update_apertura = """
                    UPDATE public.apertura_cierre
                    SET monto_final = COALESCE(monto_final, monto_inicial) + %s
                    WHERE id_apertura = %s
                """
                self.db.execute_query(query_update_apertura, (total, id_apertura))

            return {
                'success': True,
                'message': 'Venta registrada exitosamente',
                'id_venta': id_venta,
                'numero_documento': numero_documento,
                'total': float(total)
            }

        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    # ==================== MÉTODOS ADICIONALES ====================

    def listar_empresas_envio(self) -> list:
        """Retorna lista de empresas de envío"""
        query = "SELECT id_empresa, nombre, telefono FROM public.empresa_envio ORDER BY nombre"
        return self.db.fetch_all(query) or []

    def listar_clientes(self) -> list:
        query = "SELECT id_cliente, nombre, apellido, telefono FROM public.cliente ORDER BY nombre"
        return self.db.fetch_all(query) or []

    def listar_productos(self) -> list:
        query = """
            SELECT id_producto, nombre, marca, modelo, precio_costo 
            FROM public.producto ORDER BY nombre
        """
        productos = self.db.fetch_all(query) or []
        for p in productos:
            if p.get('precio_costo'):
                p['precio_costo'] = float(p['precio_costo'])
        return productos

    def obtener_venta(self, id_venta: int) -> dict:
        query = """
            SELECT v.id_venta, v.numero_documento, v.forma_pago, v.total,
                   v.es_envio, v.numero_guia, m.fecha_hora as fecha_venta,
                   c.id_cliente, c.nombre, c.apellido, c.telefono,
                   e.id_empresa, e.nombre as empresa_envio
            FROM public.venta v
            JOIN public.movimiento_caja m ON v.id_movimiento_fk = m.id_movimiento
            JOIN public.cliente c ON v.id_cliente_fk = c.id_cliente
            LEFT JOIN public.empresa_envio e ON v.id_empresa_fk = e.id_empresa
            WHERE v.id_venta = %s
        """
        venta = self.db.fetch_one(query, (id_venta,))
        if venta and venta.get('total'):
            venta['total'] = float(venta['total'])
            query_detalles = """
                SELECT dv.cantidad, dv.precio_unitario, dv.subtotal, dv.descuento,
                       p.id_producto, p.nombre, p.marca, p.modelo, p.precio_costo,
                       dv.aumento_porcentaje, dv.aumento_monto
                FROM public.detalle_venta dv
                JOIN public.producto p ON dv.id_producto_fk = p.id_producto
                WHERE dv.id_venta_fk = %s
            """
            detalles = self.db.fetch_all(query_detalles, (id_venta,))
            for d in detalles:
                for col in ['precio_unitario', 'subtotal', 'precio_costo', 'aumento_monto']:
                    if d.get(col):
                        d[col] = float(d[col])
            venta['productos'] = detalles
        return venta

    def listar_ventas_dia(self) -> list:
        query = """
            SELECT v.id_venta, v.numero_documento, v.forma_pago, v.total,
                   v.es_envio, v.numero_guia, m.fecha_hora,
                   c.id_cliente, c.nombre, c.apellido
            FROM public.venta v
            JOIN public.movimiento_caja m ON v.id_movimiento_fk = m.id_movimiento
            JOIN public.cliente c ON v.id_cliente_fk = c.id_cliente
            WHERE DATE(m.fecha_hora) = CURRENT_DATE
            ORDER BY m.fecha_hora DESC
        """
        ventas = self.db.fetch_all(query) or []
        for v in ventas:
            if v.get('total'):
                v['total'] = float(v['total'])
        return ventas

    def reporte_ventas_diario(self) -> dict:
        ventas = self.listar_ventas_dia()
        total_ventas = sum(float(v['total']) for v in ventas) if ventas else 0
        ventas_efectivo = sum(float(v['total']) for v in ventas if v['forma_pago'] == 'EF')
        ventas_tarjeta = sum(float(v['total']) for v in ventas if v['forma_pago'] == 'TC/TD')
        ventas_transferencia = sum(float(v['total']) for v in ventas if v['forma_pago'] == 'TF')
        ventas_envio = sum(float(v['total']) for v in ventas if v['es_envio'])
        return {
            'fecha': date.today(),
            'total_ventas': total_ventas,
            'cantidad': len(ventas),
            'desglose': {
                'efectivo': ventas_efectivo,
                'tarjeta': ventas_tarjeta,
                'transferencia': ventas_transferencia,
                'envio': ventas_envio
            },
            'ventas': ventas
        }

    def reporte_ventas_mensual(self, anio: int, mes: int) -> list:
        query = """
            SELECT v.id_venta, v.numero_documento, v.forma_pago, v.total,
                   v.es_envio, m.fecha_hora,
                   c.nombre, c.apellido
            FROM public.venta v
            JOIN public.movimiento_caja m ON v.id_movimiento_fk = m.id_movimiento
            JOIN public.cliente c ON v.id_cliente_fk = c.id_cliente
            WHERE EXTRACT(YEAR FROM m.fecha_hora) = %s 
              AND EXTRACT(MONTH FROM m.fecha_hora) = %s
            ORDER BY m.fecha_hora
        """
        ventas = self.db.fetch_all(query, (anio, mes)) or []
        for v in ventas:
            if v.get('total'):
                v['total'] = float(v['total'])
        return ventas

    def listar_cuentas_pendientes(self) -> list:
        query = """
            SELECT id_cuenta, numero_documento, monto, id_venta_fk
            FROM public.cuenta_por_cobrar 
            WHERE pagado = false
            ORDER BY id_cuenta
        """
        cuentas = self.db.fetch_all(query) or []
        for c in cuentas:
            if c.get('monto'):
                c['monto'] = float(c['monto'])
        return cuentas

    def marcar_cuenta_pagada(self, id_cuenta: int) -> dict:
        try:
            query = "UPDATE public.cuenta_por_cobrar SET pagado = true WHERE id_cuenta = %s"
            self.db.execute_query(query, (id_cuenta,))
            return {'success': True, 'message': 'Cuenta marcada como pagada'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}