# services/shift_service.py
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.conexion import DatabaseConnection
from models.shift_model import DetalleEfectivo, AperturaTurno, CierreTurno
from Utils.tiempo import ahora_local


class ShiftService:
    def __init__(self):
        self.db = DatabaseConnection()

    # =========================================================
    # TURNO ACTIVO (cualquier usuario)
    # =========================================================
    def obtener_turno_activo_global(self) -> Optional[Dict]:
        """Retorna el turno abierto sin importar el usuario."""
        query = """
            SELECT
                ac.id_apertura,
                ac.id_caja_fk,
                ac.monto_inicial,
                ac.fecha_hora_apertura,
                ac.observacion_apertura,
                u.nombre  AS usuario_nombre,
                u.id_usuario
            FROM apertura_cierre ac
            JOIN usuario u ON ac.id_usuario_fk = u.id_usuario
            WHERE ac.estado = 'ABIERTO'
            ORDER BY ac.fecha_hora_apertura DESC
            LIMIT 1
        """
        return self.db.fetch_one(query)

    def obtener_turno_activo(self, id_usuario: int) -> Optional[Dict]:
        """Retorna el turno abierto del usuario indicado."""
        query = """
            SELECT id_apertura, id_caja_fk, monto_inicial,
                   fecha_hora_apertura, observacion_apertura
            FROM apertura_cierre
            WHERE id_usuario_fk = %s AND estado = 'ABIERTO'
            ORDER BY fecha_hora_apertura DESC
            LIMIT 1
        """
        return self.db.fetch_one(query, (id_usuario,))

    def hay_caja_abierta(self) -> bool:
        query = "SELECT id_apertura FROM apertura_cierre WHERE estado = 'ABIERTO' LIMIT 1"
        return self.db.fetch_one(query) is not None

    # =========================================================
    # MONTO FINAL DEL ÚLTIMO CIERRE (para mostrar al cajero)
    # =========================================================
    def obtener_monto_ultimo_cierre(self) -> Optional[float]:
        query = """
            SELECT monto_final
            FROM apertura_cierre
            WHERE estado = 'CERRADO'
              AND monto_final IS NOT NULL
            ORDER BY fecha_hora_cierre DESC
            LIMIT 1
        """
        resultado = self.db.fetch_one(query)
        return float(resultado['monto_final']) if resultado else None

    # =========================================================
    # ABRIR TURNO
    # =========================================================

    def abrir_turno(self, apertura: AperturaTurno) -> Optional[int]:
        if self.hay_caja_abierta():
            raise Exception("Ya existe un turno abierto.")

        fecha_hoy = datetime.now().date()
        caja = self.db.fetch_one(
            "SELECT id_caja FROM caja WHERE fecha = %s", (fecha_hoy,)
        )
        if not caja:
            caja = self.db.fetch_one(
                "INSERT INTO caja (fecha) VALUES (%s) RETURNING id_caja",
                (fecha_hoy,)
            )
        if not caja:
            raise Exception("No se pudo crear/obtener la caja del día.")
        id_caja = caja['id_caja']

        # Usar ahora_local() para la apertura
        query = """
            INSERT INTO apertura_cierre
                (id_caja_fk, id_usuario_fk, fecha_hora_apertura,
                 monto_inicial, observacion_apertura, estado)
            VALUES (%s, %s, %s, %s, %s, 'ABIERTO')
            RETURNING id_apertura
        """
        result = self.db.fetch_one(query, (
            id_caja,
            apertura.id_usuario_fk,
            ahora_local(),        # 👈 cambiado
            apertura.monto_inicial,
            apertura.observacion
        ))
        if not result:
            raise Exception("No se pudo registrar la apertura.")
        id_apertura = result['id_apertura']

        for det in apertura.detalles:
            self.db.execute_query("""
                INSERT INTO detalle_apertura (id_apertura_fk, denominacion, cantidad, subtotal)
                VALUES (%s, %s, %s, %s)
            """, (id_apertura, det.denominacion, det.cantidad, det.subtotal))

        return id_apertura

    # =========================================================
    # CALCULAR RESUMEN DE CIERRE
    # =========================================================
    def calcular_resumen_cierre(self, id_apertura: int) -> Dict:
        """
        Devuelve un dict con todos los totales separados por forma de pago
        y el efectivo esperado real (solo efectivo físico).
        """
        apertura = self.db.fetch_one(
            "SELECT monto_inicial, id_caja_fk, fecha_hora_apertura FROM apertura_cierre WHERE id_apertura = %s",
            (id_apertura,)
        )
        if not apertura:
            raise Exception("Apertura no encontrada.")

        monto_inicial = float(apertura['monto_inicial'])
        id_caja = apertura['id_caja_fk']
        desde = apertura['fecha_hora_apertura']

        # --------------------------------------------------
        # VENTAS agrupadas por forma de pago
        # --------------------------------------------------
        query_ventas = """
            SELECT
                v.forma_pago,
                COALESCE(SUM(v.total), 0) AS total
            FROM venta v
            JOIN movimiento_caja mc ON v.id_movimiento_fk = mc.id_movimiento
            WHERE mc.id_caja_fk = %s
              AND mc.fecha_hora >= %s
              AND v.producto_pagado = true
            GROUP BY v.forma_pago
        """
        filas_ventas = self.db.fetch_all(query_ventas, (id_caja, desde))
        ventas_por_forma = {f['forma_pago']: float(f['total']) for f in filas_ventas}

        ventas_efectivo     = ventas_por_forma.get('EFECTIVO', 0.0)
        ventas_transferencia = ventas_por_forma.get('TRANSFERENCIA', 0.0)
        ventas_tarjeta      = ventas_por_forma.get('TARJETA', 0.0)
        ventas_deposito     = ventas_por_forma.get('DEPOSITO', 0.0)

        # --------------------------------------------------
        # CUENTAS POR COBRAR cobradas en EFECTIVO durante el turno
        # --------------------------------------------------
        query_cpc = """
            SELECT COALESCE(SUM(mc.monto), 0) AS total
            FROM movimiento_caja mc
            WHERE mc.id_caja_fk = %s
              AND mc.tipo_movimiento = 'COBRO_CUENTA'
              AND mc.fecha_hora >= %s
        """
        cpc_row = self.db.fetch_one(query_cpc, (id_caja, desde))
        cobros_cuentas = float(cpc_row['total']) if cpc_row else 0.0

        # --------------------------------------------------
        # INGRESOS MANUALES (tipo INGRESO que no son ventas)
        # --------------------------------------------------
        query_ingresos = """
            SELECT COALESCE(SUM(mc.monto), 0) AS total
            FROM movimiento_caja mc
            WHERE mc.id_caja_fk = %s
              AND mc.tipo_movimiento = 'INGRESO'
              AND mc.fecha_hora >= %s
        """
        ing_row = self.db.fetch_one(query_ingresos, (id_caja, desde))
        ingresos_manuales = float(ing_row['total']) if ing_row else 0.0

        # --------------------------------------------------
        # EGRESOS (gastos)
        # --------------------------------------------------
        query_egresos = """
            SELECT COALESCE(SUM(mc.monto), 0) AS total
            FROM movimiento_caja mc
            WHERE mc.id_caja_fk = %s
              AND mc.tipo_movimiento = 'EGRESO'
              AND mc.fecha_hora >= %s
        """
        egr_row = self.db.fetch_one(query_egresos, (id_caja, desde))
        egresos = float(egr_row['total']) if egr_row else 0.0

        # --------------------------------------------------
        # EFECTIVO ESPERADO
        # Solo: monto_inicial + ventas efectivo + cobros cuentas + ingresos manuales - egresos
        # Transferencia, Tarjeta y Deposito NO afectan efectivo físico
        # --------------------------------------------------
        efectivo_esperado = (
            monto_inicial
            + ventas_efectivo
            + cobros_cuentas
            + ingresos_manuales
            - egresos
        )

        return {
            'monto_inicial':       monto_inicial,
            'ventas_efectivo':     ventas_efectivo,
            'ventas_transferencia': ventas_transferencia,
            'ventas_tarjeta':      ventas_tarjeta,
            'ventas_deposito':     ventas_deposito,
            'cobros_cuentas':      cobros_cuentas,
            'ingresos_manuales':   ingresos_manuales,
            'egresos':             egresos,
            'efectivo_esperado':   efectivo_esperado,
        }

    # =========================================================
    # CERRAR TURNO
    # =========================================================
    def cerrar_turno(self, cierre: CierreTurno) -> bool:
        query = """
               UPDATE apertura_cierre
               SET
                   fecha_hora_cierre    = %s,
                   monto_final          = %s,
                   monto_esperado       = %s,
                   diferencia           = %s,
                   observacion_cierre   = %s,
                   estado               = 'CERRADO',
                   id_usuario_cierre_fk = %s
               WHERE id_apertura = %s
                 AND estado = 'ABIERTO'
           """
        ok = self.db.execute_query(query, (
            ahora_local(),  # 👈 cambiado
            cierre.monto_contado,
            cierre.monto_esperado,
            cierre.diferencia,
            cierre.observacion,
            cierre.id_usuario_cierre_fk,
            cierre.id_apertura,
        ))
        if not ok:
            return False

        for det in cierre.detalles_cierre:
            self.db.execute_query("""
                INSERT INTO detalle_cierre (id_apertura_fk, denominacion, cantidad, subtotal)
                VALUES (%s, %s, %s, %s)
            """, (cierre.id_apertura, det.denominacion, det.cantidad, det.subtotal))
        return True

    # =========================================================
    # HISTORIAL DE TURNOS CERRADOS
    # =========================================================
    def obtener_historial_turnos(self, limite: int = 50) -> List[Dict]:
        query = """
            SELECT
                ac.id_apertura,
                ac.fecha_hora_apertura,
                ac.fecha_hora_cierre,
                ac.monto_inicial,
                ac.monto_final,
                ac.monto_esperado,
                ac.diferencia,
                u.nombre        AS usuario_apertura,
                uc.nombre       AS usuario_cierre,
                ac.observacion_apertura,
                ac.observacion_cierre
            FROM apertura_cierre ac
            JOIN usuario u  ON ac.id_usuario_fk        = u.id_usuario
            LEFT JOIN usuario uc ON ac.id_usuario_cierre_fk = uc.id_usuario
            WHERE ac.estado = 'CERRADO'
            ORDER BY ac.fecha_hora_apertura DESC
            LIMIT %s
        """
        return self.db.fetch_all(query, (limite,))

    # =========================================================
    # MOVIMIENTOS DEL TURNO (para tab movimientos)
    # =========================================================
    def obtener_movimientos_turno(self, id_apertura: int) -> List[Dict]:
        query = """
            SELECT
                mc.fecha_hora,
                mc.tipo_movimiento,
                mc.descripcion,
                mc.monto,
                u.nombre AS usuario
            FROM movimiento_caja mc
            JOIN apertura_cierre ac ON mc.id_caja_fk = ac.id_caja_fk
            LEFT JOIN usuario u ON mc.id_usuario_fk = u.id_usuario
            WHERE ac.id_apertura = %s
              AND mc.fecha_hora >= ac.fecha_hora_apertura
            ORDER BY mc.fecha_hora DESC
        """
        return self.db.fetch_all(query, (id_apertura,))