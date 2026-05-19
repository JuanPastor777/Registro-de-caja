# services/reporte_service.py
from database.conexion import DatabaseConnection
from datetime import datetime

class ReporteService:
    def __init__(self):
        self.db = DatabaseConnection()

    def obtener_ventas(self, fecha_desde, fecha_hasta, usuario_id=None, forma_pago=None):
        """Ventas en el rango de fechas con filtros opcionales de usuario y forma de pago."""
        query = """
            SELECT 
                v.id_venta,
                v.numero_documento,
                v.forma_pago,
                v.total,
                v.es_envio,
                v.numero_guia,
                m.fecha_hora,
                c.id_cliente,
                c.nombre AS cliente_nombre,
                c.apellido AS cliente_apellido,
                u.id_usuario,
                u.nombre AS usuario_nombre,
                ee.nombre AS empresa_envio
            FROM venta v
            JOIN movimiento_caja m ON v.id_movimiento_fk = m.id_movimiento
            JOIN cliente c ON v.id_cliente_fk = c.id_cliente
            JOIN usuario u ON m.id_usuario_fk = u.id_usuario
            LEFT JOIN empresa_envio ee ON v.id_empresa_fk = ee.id_empresa
            WHERE DATE(m.fecha_hora) BETWEEN %s AND %s
        """
        params = [fecha_desde, fecha_hasta]

        if usuario_id:
            query += " AND u.id_usuario = %s"
            params.append(usuario_id)
        if forma_pago:
            query += " AND v.forma_pago = %s"
            params.append(forma_pago)

        query += " ORDER BY m.fecha_hora ASC"
        resultados = self.db.fetch_all(query, tuple(params))
        return resultados

    def obtener_detalles_venta(self, id_venta):
        """Productos de una venta específica."""
        query = """
            SELECT 
                p.nombre AS producto_nombre,
                p.marca,
                p.modelo,
                dv.cantidad,
                dv.precio_unitario,
                dv.subtotal,
                dv.descuento
            FROM detalle_venta dv
            JOIN producto p ON dv.id_producto_fk = p.id_producto
            WHERE dv.id_venta_fk = %s
        """
        return self.db.fetch_all(query, (id_venta,))

    def obtener_resumen_por_usuario(self, fecha_desde, fecha_hasta, usuario_id=None):
        """Totales por usuario (para comisiones)."""
        query = """
            SELECT 
                u.id_usuario,
                u.nombre,
                COUNT(v.id_venta) AS num_ventas,
                COALESCE(SUM(v.total), 0) AS total_vendido
            FROM venta v
            JOIN movimiento_caja m ON v.id_movimiento_fk = m.id_movimiento
            JOIN usuario u ON m.id_usuario_fk = u.id_usuario
            WHERE DATE(m.fecha_hora) BETWEEN %s AND %s
        """
        params = [fecha_desde, fecha_hasta]
        if usuario_id:
            query += " AND u.id_usuario = %s"
            params.append(usuario_id)
        query += " GROUP BY u.id_usuario, u.nombre ORDER BY u.nombre"
        return self.db.fetch_all(query, tuple(params))

    def obtener_gastos(self, fecha_desde, fecha_hasta):
        """Gastos en el período."""
        query = """
            SELECT g.*, m.fecha_hora, u.nombre AS usuario_nombre
            FROM gasto g
            JOIN movimiento_caja m ON g.id_movimiento_fk = m.id_movimiento
            JOIN usuario u ON m.id_usuario_fk = u.id_usuario
            WHERE DATE(m.fecha_hora) BETWEEN %s AND %s
            ORDER BY m.fecha_hora
        """
        return self.db.fetch_all(query, (fecha_desde, fecha_hasta))

    def obtener_apartados(self, fecha_desde, fecha_hasta, estado=None):
        """Apartados activos/completados en el período."""
        query = """
            SELECT 
                a.id_apartado,
                a.total_producto,
                a.fecha_inicio,
                a.estado,
                c.nombre AS cliente_nombre,
                c.apellido AS cliente_apellido,
                p.nombre AS producto_nombre,
                COALESCE(SUM(da.monto), 0) AS total_pagado
            FROM apartado a
            JOIN cliente c ON a.id_cliente_fk = c.id_cliente
            JOIN producto p ON a.id_producto_fk = p.id_producto
            LEFT JOIN detalle_apartado da ON a.id_apartado = da.id_apartado_fk
            WHERE a.fecha_inicio BETWEEN %s AND %s
        """
        params = [fecha_desde, fecha_hasta]
        if estado:
            query += " AND a.estado = %s"
            params.append(estado)
        query += " GROUP BY a.id_apartado, c.nombre, c.apellido, p.nombre ORDER BY a.fecha_inicio"
        return self.db.fetch_all(query, tuple(params))

    def obtener_turno_actual(self, id_caja_actual):
        """Datos del turno abierto actual."""
        query = """
            SELECT 
                ac.id_apertura,
                ac.fecha_hora_apertura,
                ac.monto_inicial,
                u.nombre AS usuario_nombre
            FROM apertura_cierre ac
            JOIN usuario u ON ac.id_usuario_fk = u.id_usuario
            WHERE ac.id_caja_fk = %s AND ac.estado = 'ABIERTO'
        """
        return self.db.fetch_one(query, (id_caja_actual,))

    def obtener_movimientos_turno(self, id_apertura):
        """Movimientos del turno actual."""
        query = """
            SELECT 
                m.fecha_hora,
                m.tipo_movimiento,
                m.descripcion,
                m.monto,
                u.nombre AS usuario_nombre
            FROM movimiento_caja m
            JOIN usuario u ON m.id_usuario_fk = u.id_usuario
            WHERE m.id_caja_fk = (SELECT id_caja_fk FROM apertura_cierre WHERE id_apertura = %s)
              AND m.fecha_hora >= (SELECT fecha_hora_apertura FROM apertura_cierre WHERE id_apertura = %s)
            ORDER BY m.fecha_hora
        """
        return self.db.fetch_all(query, (id_apertura, id_apertura))