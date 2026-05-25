# services/apartado_service.py
import sys
import os
from datetime import date, datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.conexion import DatabaseConnection
from models.apartado import Apartado


class ApartadoService:
    """Servicio para gestionar apartados"""
    
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
        """Verifica si hay una caja abierta"""
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
    
    # =========================================================
    # CREAR APARTADO
    # =========================================================
    
    def crear_apartado(self, data: dict) -> dict:
        """
        Crea un nuevo apartado
        
        data debe contener:
        - id_cliente_fk
        - id_producto_fk
        - monto_original
        - descuento_pactado (opcional)
        - incremento_pactado (opcional)
        - es_envio (opcional)
        - id_empresa_fk (opcional, si es_envio=True)
        - numero_guia (opcional)
        - forma_pago_acordada (opcional)
        """
        try:
            # Calcular monto_final
            monto_original = float(data['monto_original'])
            descuento = float(data.get('descuento_pactado', 0))
            incremento = float(data.get('incremento_pactado', 0))
            monto_final = monto_original - descuento + incremento
            
            query = """
                INSERT INTO apartado (
                    id_cliente_fk, id_producto_fk, total_producto,
                    fecha_inicio, estado, monto_original,
                    descuento_pactado, monto_final, es_envio,
                    id_empresa_fk, numero_guia, forma_pago_acordada,
                    incremento_pactado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_apartado
            """
            
            params = (
                data['id_cliente_fk'],
                data['id_producto_fk'],
                monto_final,  # total_producto = monto_final
                data.get('fecha_inicio', date.today()),
                'ACTIVO',
                monto_original,
                descuento,
                monto_final,
                data.get('es_envio', False),
                data.get('id_empresa_fk'),
                data.get('numero_guia'),
                data.get('forma_pago_acordada'),
                incremento
            )
            
            resultado = self.db.fetch_one(query, params)
            
            if resultado:
                return {
                    'success': True,
                    'message': 'Apartado creado exitosamente',
                    'id_apartado': resultado['id_apartado'],
                    'monto_original': monto_original,
                    'descuento': descuento,
                    'incremento': incremento,
                    'monto_final': monto_final
                }
            
            return {'success': False, 'message': 'Error al crear apartado'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    # =========================================================
    # REGISTRAR PAGO/ABONO
    # =========================================================
    
    def registrar_pago(self, id_apartado: int, monto: float, forma_pago: str,
                       tipo_documento: str, numero_documento: str,
                       pagos_mixtos: dict = None, id_caja: int = None) -> dict:
        """
        Registra un pago/abono para un apartado.

        - Efectivo (EF): crea movimiento_caja INGRESO y suma al monto_final de apertura.
        - Transferencia/Depósito/Tarjeta: crea movimiento_caja INGRESO (para trazabilidad)
          pero NO suma al monto_final de apertura (no es dinero físico en caja).
        """
        try:
            # Verificar caja abierta (necesaria para todas las formas de pago)
            caja_verificada = self.verificar_caja_abierta()
            if not caja_verificada['success']:
                return caja_verificada

            id_caja_mov = caja_verificada['id_caja']
            id_apertura = caja_verificada['id_apertura']

            # Obtener apartado
            apartado = self.obtener_detalle_apartado(id_apartado)
            if not apartado:
                return {'success': False, 'message': 'Apartado no encontrado'}

            if apartado['estado'] != 'ACTIVO':
                return {'success': False, 'message': f'Apartado está {apartado["estado"]}'}

            # Verificar saldo
            total_pagado = self.obtener_total_pagado(id_apartado)
            saldo = round(float(apartado['monto_final']) - total_pagado, 2)

            if monto > saldo:
                return {'success': False, 'message': f'El monto excede el saldo pendiente (Q{saldo:.2f})'}

            numero_documento_completo = f"{tipo_documento}-{numero_documento}"
            descripcion = f"Pago [{forma_pago}] apartado #{id_apartado} - {apartado['cliente_nombre']} - {numero_documento_completo}"

            # Crear movimiento de caja (igual que ventas, siempre 'INGRESO')
            resultado_mov = self.db.fetch_one(
                """
                INSERT INTO movimiento_caja
                (id_caja_fk, tipo_movimiento, descripcion, monto, id_usuario_fk, fecha_hora)
                VALUES (%s, 'INGRESO', %s, %s, %s, NOW())
                RETURNING id_movimiento
                """,
                (id_caja_mov, descripcion, monto, self.id_usuario_actual)
            )

            if not resultado_mov:
                return {'success': False, 'message': 'Error al crear movimiento en caja'}

            id_movimiento = resultado_mov['id_movimiento']

            # Solo efectivo suma al conteo físico de la apertura
            if forma_pago == 'EF':
                self.db.execute_query(
                    """
                    UPDATE apertura_cierre
                    SET monto_final = COALESCE(monto_final, monto_inicial) + %s
                    WHERE id_apertura = %s
                    """,
                    (monto, id_apertura)
                )

            # Registrar detalle del pago (guardamos forma_pago para poder desglosar en caja)
            self.db.execute_query(
                """
                INSERT INTO detalle_apartado
                (id_apartado_fk, id_movimiento_fk, fecha_pago, monto, forma_pago)
                VALUES (%s, %s, CURRENT_DATE, %s, %s)
                """,
                (id_apartado, id_movimiento, monto, forma_pago)
            )

            # Verificar si se completó el apartado
            nuevo_total_pagado = round(total_pagado + monto, 2)
            if nuevo_total_pagado >= round(float(apartado['monto_final']), 2):
                self.db.execute_query(
                    "UPDATE apartado SET estado = 'COMPLETADO' WHERE id_apartado = %s",
                    (id_apartado,)
                )
                mensaje = "✅ Apartado completado exitosamente"
            else:
                saldo_restante = round(float(apartado['monto_final']) - nuevo_total_pagado, 2)
                mensaje = f"💰 Pago registrado. Saldo restante: Q{saldo_restante:.2f}"

            return {
                'success': True,
                'message': mensaje,
                'id_movimiento': id_movimiento,
                'monto_pagado': monto,
                'saldo_restante': float(apartado['monto_final']) - nuevo_total_pagado
            }

        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    # =========================================================
    # CONSULTAS
    # =========================================================
    
    def obtener_apartados_pendientes(self) -> list[dict]:
        """Obtiene apartados ACTIVOS con saldo pendiente"""
        query = """
            SELECT 
                a.id_apartado,
                a.monto_original,
                a.descuento_pactado,
                a.incremento_pactado,
                a.monto_final,
                a.fecha_inicio,
                a.estado,
                a.es_envio,
                a.id_empresa_fk,
                a.numero_guia,
                a.forma_pago_acordada,
                c.id_cliente,
                c.nombre as cliente_nombre,
                c.apellido as cliente_apellido,
                c.telefono as cliente_telefono,
                p.id_producto,
                p.nombre as producto_nombre,
                p.marca,
                p.modelo,
                p.precio_costo,
                ee.nombre as empresa_envio_nombre,
                COALESCE(SUM(da.monto), 0) as total_pagado
            FROM apartado a
            JOIN cliente c ON a.id_cliente_fk = c.id_cliente
            JOIN producto p ON a.id_producto_fk = p.id_producto
            LEFT JOIN detalle_apartado da ON a.id_apartado = da.id_apartado_fk
            LEFT JOIN empresa_envio ee ON a.id_empresa_fk = ee.id_empresa
            WHERE a.estado = 'ACTIVO'
            GROUP BY 
                a.id_apartado, c.id_cliente, c.nombre, c.apellido, c.telefono,
                p.id_producto, p.nombre, p.marca, p.modelo, p.precio_costo,
                ee.nombre
            HAVING COALESCE(SUM(da.monto), 0) < a.monto_final
            ORDER BY a.fecha_inicio ASC
        """
        resultados = self.db.fetch_all(query) or []
        
        for r in resultados:
            r['saldo_pendiente'] = round(float(r['monto_final']) - float(r['total_pagado']), 2)
            r['porcentaje_pagado'] = (float(r['total_pagado']) / float(r['monto_final'])) * 100 if r['monto_final'] > 0 else 0
        
        return resultados
    
    def obtener_todos_apartados(self) -> list[dict]:
        """Obtiene TODOS los apartados"""
        query = """
            SELECT 
                a.id_apartado,
                a.monto_original,
                a.descuento_pactado,
                a.incremento_pactado,
                a.monto_final,
                a.fecha_inicio,
                a.estado,
                a.es_envio,
                a.numero_guia,
                c.nombre as cliente_nombre,
                c.apellido as cliente_apellido,
                p.nombre as producto_nombre,
                COALESCE(SUM(da.monto), 0) as total_pagado
            FROM apartado a
            JOIN cliente c ON a.id_cliente_fk = c.id_cliente
            JOIN producto p ON a.id_producto_fk = p.id_producto
            LEFT JOIN detalle_apartado da ON a.id_apartado = da.id_apartado_fk
            GROUP BY a.id_apartado, c.nombre, c.apellido, p.nombre
            ORDER BY a.fecha_inicio DESC
        """
        return self.db.fetch_all(query) or []
    
    def obtener_detalle_apartado(self, id_apartado: int) -> dict | None:
        """Obtiene detalle completo de un apartado"""
        query = """
            SELECT 
                a.*,
                c.nombre as cliente_nombre,
                c.apellido as cliente_apellido,
                c.telefono as cliente_telefono,
                p.nombre as producto_nombre,
                p.marca,
                p.modelo,
                p.precio_costo,
                ee.nombre as empresa_envio_nombre,
                COALESCE(SUM(da.monto), 0) as total_pagado,
                COUNT(da.id_detalle) as num_pagos
            FROM apartado a
            JOIN cliente c ON a.id_cliente_fk = c.id_cliente
            JOIN producto p ON a.id_producto_fk = p.id_producto
            LEFT JOIN detalle_apartado da ON a.id_apartado = da.id_apartado_fk
            LEFT JOIN empresa_envio ee ON a.id_empresa_fk = ee.id_empresa
            WHERE a.id_apartado = %s
            GROUP BY 
                a.id_apartado, c.nombre, c.apellido, c.telefono,
                p.nombre, p.marca, p.modelo, p.precio_costo, ee.nombre
        """
        resultado = self.db.fetch_one(query, (id_apartado,))
        if resultado:
            resultado['saldo_pendiente'] = round(float(resultado['monto_final']) - float(resultado['total_pagado']), 2)
        return resultado
    
    def obtener_historial_pagos(self, id_apartado: int) -> list[dict]:
        """Obtiene historial de pagos de un apartado"""
        query = """
            SELECT 
                da.id_detalle,
                da.fecha_pago,
                da.monto,
                mc.tipo_movimiento,
                mc.descripcion,
                mc.fecha_hora,
                u.nombre as usuario_nombre
            FROM detalle_apartado da
            JOIN movimiento_caja mc ON da.id_movimiento_fk = mc.id_movimiento
            JOIN usuario u ON mc.id_usuario_fk = u.id_usuario
            WHERE da.id_apartado_fk = %s
            ORDER BY da.fecha_pago DESC
        """
        return self.db.fetch_all(query, (id_apartado,)) or []
    
    def obtener_total_pagado(self, id_apartado: int) -> float:
        """Obtiene el total pagado de un apartado"""
        query = """
            SELECT COALESCE(SUM(monto), 0) as total
            FROM detalle_apartado
            WHERE id_apartado_fk = %s
        """
        resultado = self.db.fetch_one(query, (id_apartado,))
        return float(resultado['total']) if resultado else 0
    
    # =========================================================
    # CANCELAR APARTADO
    # =========================================================
    
    def cancelar_apartado(self, id_apartado: int) -> dict:
        """Cancela un apartado. El dinero ya pagado NO se devuelve — queda registrado como ingreso."""
        try:
            apartado = self.obtener_detalle_apartado(id_apartado)
            if not apartado:
                return {'success': False, 'message': 'Apartado no encontrado'}
            
            if apartado['estado'] != 'ACTIVO':
                return {'success': False, 'message': f'No se puede cancelar un apartado {apartado["estado"]}'}
            
            total_pagado = float(apartado['total_pagado'])
            
            # Cambiar estado a CANCELADO
            # El dinero pagado permanece como INGRESO en caja (no se genera egreso)
            self.db.execute_query(
                "UPDATE apartado SET estado = 'CANCELADO' WHERE id_apartado = %s",
                (id_apartado,)
            )
            
            if total_pagado > 0:
                return {
                    'success': True,
                    'message': (
                        f'Apartado cancelado. '
                        f'El cliente había pagado Q{total_pagado:.2f} — '
                        f'este monto queda registrado como ingreso en caja (no se devuelve).'
                    ),
                    'monto_retenido': total_pagado
                }
            
            return {'success': True, 'message': 'Apartado cancelado exitosamente'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    # =========================================================
    # LISTAR CATÁLOGOS
    # =========================================================
    
    def listar_clientes(self) -> list:
        query = "SELECT id_cliente, nombre, apellido, telefono FROM cliente ORDER BY nombre"
        return self.db.fetch_all(query) or []
    
    def listar_productos(self) -> list:
        query = "SELECT id_producto, nombre, marca, modelo, precio_costo FROM producto ORDER BY nombre"
        return self.db.fetch_all(query) or []
    
    def listar_empresas_envio(self) -> list:
        query = "SELECT id_empresa, nombre, telefono FROM empresa_envio ORDER BY nombre"
        return self.db.fetch_all(query) or []
    
    def obtener_estado_caja(self) -> dict:
        """Verifica si hay caja abierta"""
        query = """
            SELECT ac.id_apertura, ac.id_caja_fk
            FROM apertura_cierre ac
            WHERE ac.fecha_hora_cierre IS NULL
            ORDER BY ac.fecha_hora_apertura DESC
            LIMIT 1
        """
        resultado = self.db.fetch_one(query)
        if resultado:
            return {'abierta': True, 'id_caja': resultado['id_caja_fk']}
        return {'abierta': False, 'id_caja': None}