"""
Data Access Objects para todas las entidades del sistema
Utiliza la conexión existente de conexion.py
"""

from datetime import date, datetime
from database.conexion  import DatabaseConnection
from models.usuario import Usuario
from models.caja import Caja
from models.apertura_cierre import AperturaCierre
from models.movimiento import MovimientoCaja
from models.cliente import Cliente
from models.producto import Producto
from models.venta import Venta
from models.detalle_venta import DetalleVenta
from models.apartado import Apartado
from models.detalle_apartado import DetalleApartado
from models.gasto import Gasto
from models.cuenta_por_cobrar import CuentaPorCobrar
from models.empresa_envio import EmpresaEnvio

# ==================== USUARIO DAO ====================

class UsuarioDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def autenticar(self, username: str, password_input: str) -> Usuario | None:
        query = """
            SELECT id_usuario, nombre, usuario, password, rol, estado, fecha_creacion
            FROM public.usuario WHERE usuario = %s AND estado = true
        """
        resultado = self.db.fetch_one(query, (username,))
        if resultado:
            user = Usuario.from_dict(resultado)
            if user.verificar_password(password_input):
                return user
        return None

    def crear(self, usuario: Usuario) -> int | None:
        query = """
            INSERT INTO public.usuario (nombre, usuario, password, rol, estado)
            VALUES (%s, %s, %s, %s, %s) RETURNING id_usuario
        """
        resultado = self.db.fetch_one(query, (usuario.nombre, usuario.usuario,
                                              usuario.password, usuario.rol, usuario.estado))
        return resultado['id_usuario'] if resultado else None

    def listar_todos(self) -> list[Usuario]:
        query = "SELECT id_usuario, nombre, usuario, password, rol, estado, fecha_creacion FROM public.usuario ORDER BY nombre"
        resultados = self.db.fetch_all(query)
        return [Usuario.from_dict(r) for r in resultados]

    def obtener_por_rol(self, rol: str) -> list[Usuario]:
        query = "SELECT id_usuario, nombre, usuario, password, rol, estado, fecha_creacion FROM public.usuario WHERE rol = %s"
        resultados = self.db.fetch_all(query, (rol,))
        return [Usuario.from_dict(r) for r in resultados]


# ==================== CAJA Y APERTURA DAO ====================

class CajaDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def crear(self, fecha: date) -> int | None:
        query = "INSERT INTO public.caja (fecha) VALUES (%s) RETURNING id_caja"
        resultado = self.db.fetch_one(query, (fecha,))
        return resultado['id_caja'] if resultado else None

    def obtener_por_fecha(self, fecha: date) -> Caja | None:
        query = "SELECT id_caja, fecha FROM public.caja WHERE fecha = %s"
        resultado = self.db.fetch_one(query, (fecha,))
        return Caja.from_dict(resultado) if resultado else None


class AperturaCierreDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def abrir(self, id_caja_fk: int, id_usuario_fk: int, monto_inicial: float) -> int | None:
        query = """
            INSERT INTO public.apertura_cierre (id_caja_fk, id_usuario_fk, 
                                                 fecha_hora_apertura, monto_inicial)
            VALUES (%s, %s, NOW(), %s) RETURNING id_apertura
        """
        resultado = self.db.fetch_one(query, (id_caja_fk, id_usuario_fk, monto_inicial))
        return resultado['id_apertura'] if resultado else None

    def cerrar(self, id_apertura: int, monto_final: float) -> bool:
        query = """
            UPDATE public.apertura_cierre 
            SET fecha_hora_cierre = NOW(), monto_final = %s
            WHERE id_apertura = %s AND fecha_hora_cierre IS NULL
        """
        return self.db.execute_query(query, (monto_final, id_apertura))

    def obtener_activa_por_usuario(self, id_usuario_fk: int) -> AperturaCierre | None:
        query = """
            SELECT ac.id_apertura, ac.id_caja_fk, ac.id_usuario_fk, 
                   ac.fecha_hora_apertura, ac.monto_inicial, 
                   ac.fecha_hora_cierre, ac.monto_final
            FROM public.apertura_cierre ac
            WHERE ac.id_usuario_fk = %s AND ac.fecha_hora_cierre IS NULL
            ORDER BY ac.fecha_hora_apertura DESC LIMIT 1
        """
        resultado = self.db.fetch_one(query, (id_usuario_fk,))
        return AperturaCierre.from_dict(resultado) if resultado else None

    def obtener_por_caja(self, id_caja_fk: int) -> list[AperturaCierre]:
        query = """
            SELECT id_apertura, id_caja_fk, id_usuario_fk, fecha_hora_apertura,
                   monto_inicial, fecha_hora_cierre, monto_final
            FROM public.apertura_cierre WHERE id_caja_fk = %s
            ORDER BY fecha_hora_apertura
        """
        resultados = self.db.fetch_all(query, (id_caja_fk,))
        return [AperturaCierre.from_dict(r) for r in resultados]


# ==================== MOVIMIENTO CAJA DAO ====================

class MovimientoCajaDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def crear(self, movimiento: MovimientoCaja) -> int | None:
        query = """
            INSERT INTO public.movimiento_caja (id_caja_fk, tipo_movimiento, 
                                                 descripcion, monto, id_usuario_fk)
            VALUES (%s, %s, %s, %s, %s) RETURNING id_movimiento
        """
        resultado = self.db.fetch_one(query, (movimiento.id_caja_fk, movimiento.tipo_movimiento,
                                              movimiento.descripcion, movimiento.monto,
                                              movimiento.id_usuario_fk))
        return resultado['id_movimiento'] if resultado else None

    def listar_por_caja(self, id_caja_fk: int) -> list[MovimientoCaja]:
        query = """
            SELECT id_movimiento, id_caja_fk, tipo_movimiento, descripcion,
                   monto, fecha_hora, id_usuario_fk
            FROM public.movimiento_caja WHERE id_caja_fk = %s
            ORDER BY fecha_hora
        """
        resultados = self.db.fetch_all(query, (id_caja_fk,))
        return [MovimientoCaja.from_dict(r) for r in resultados]

    def total_ingresos_por_caja(self, id_caja_fk: int) -> float:
        query = """
            SELECT COALESCE(SUM(monto), 0) FROM public.movimiento_caja
            WHERE id_caja_fk = %s AND tipo_movimiento = 'INGRESO'
        """
        resultado = self.db.fetch_one(query, (id_caja_fk,))
        return float(resultado['sum']) if resultado else 0

    def total_egresos_por_caja(self, id_caja_fk: int) -> float:
        query = """
            SELECT COALESCE(SUM(monto), 0) FROM public.movimiento_caja
            WHERE id_caja_fk = %s AND tipo_movimiento = 'EGRESO'
        """
        resultado = self.db.fetch_one(query, (id_caja_fk,))
        return float(resultado['sum']) if resultado else 0


# ==================== CLIENTE DAO ====================

class ClienteDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def crear(self, cliente: Cliente) -> int | None:
        query = """
            INSERT INTO public.cliente (nombre, apellido, telefono)
            VALUES (%s, %s, %s) RETURNING id_cliente
        """
        resultado = self.db.fetch_one(query, (cliente.nombre, cliente.apellido, cliente.telefono))
        return resultado['id_cliente'] if resultado else None

    def obtener_por_id(self, id_cliente: int) -> Cliente | None:
        query = "SELECT id_cliente, nombre, apellido, telefono FROM public.cliente WHERE id_cliente = %s"
        resultado = self.db.fetch_one(query, (id_cliente,))
        return Cliente.from_dict(resultado) if resultado else None

    def listar_todos(self) -> list[Cliente]:
        query = "SELECT id_cliente, nombre, apellido, telefono FROM public.cliente ORDER BY nombre"
        resultados = self.db.fetch_all(query)
        return [Cliente.from_dict(r) for r in resultados]

    def buscar_por_nombre(self, texto: str) -> list[Cliente]:
        query = """
            SELECT id_cliente, nombre, apellido, telefono FROM public.cliente
            WHERE nombre ILIKE %s OR apellido ILIKE %s
            ORDER BY nombre LIMIT 20
        """
        like = f"%{texto}%"
        resultados = self.db.fetch_all(query, (like, like))
        return [Cliente.from_dict(r) for r in resultados]


# ==================== PRODUCTO DAO ====================

class ProductoDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def crear(self, producto: Producto) -> int | None:
        query = """
            INSERT INTO public.producto (nombre, marca, modelo, descripcion, precio_costo)
            VALUES (%s, %s, %s, %s, %s) RETURNING id_producto
        """
        resultado = self.db.fetch_one(query, (producto.nombre, producto.marca,
                                              producto.modelo, producto.descripcion,
                                              producto.precio_costo))
        return resultado['id_producto'] if resultado else None

    def obtener_por_id(self, id_producto: int) -> Producto | None:
        query = "SELECT id_producto, nombre, marca, modelo, descripcion, precio_costo FROM public.producto WHERE id_producto = %s"
        resultado = self.db.fetch_one(query, (id_producto,))
        return Producto.from_dict(resultado) if resultado else None

    def listar_todos(self) -> list[Producto]:
        query = "SELECT id_producto, nombre, marca, modelo, descripcion, precio_costo FROM public.producto ORDER BY nombre"
        resultados = self.db.fetch_all(query)
        return [Producto.from_dict(r) for r in resultados]

    def buscar_por_nombre(self, texto: str) -> list[Producto]:
        query = """
            SELECT id_producto, nombre, marca, modelo, descripcion, precio_costo
            FROM public.producto WHERE nombre ILIKE %s OR marca ILIKE %s
            ORDER BY nombre LIMIT 20
        """
        like = f"%{texto}%"
        resultados = self.db.fetch_all(query, (like, like))
        return [Producto.from_dict(r) for r in resultados]


# ==================== VENTA Y DETALLE DAO ====================

class VentaDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.movimiento_dao = MovimientoCajaDAO(db)
        self.cliente_dao = ClienteDAO(db)
        self.empresa_dao = EmpresaEnvioDAO(db)

    def registrar_venta_completa(self, venta: Venta, detalles: list[DetalleVenta]) -> int | None:
        """
        Registra una venta completa con su movimiento de caja y detalles
        """
        # 1. Crear movimiento de caja
        movimiento = MovimientoCaja(
            id_caja_fk=venta.id_movimiento_fk,
            tipo_movimiento=MovimientoCaja.TIPO_INGRESO,
            descripcion=f"Venta {venta.numero_documento}",
            monto=venta.total,
            id_usuario_fk=venta.id_movimiento_fk
        )
        id_movimiento = self.movimiento_dao.crear(movimiento)
        if not id_movimiento:
            return None

        # 2. Crear venta
        venta.id_movimiento_fk = id_movimiento
        query_venta = """
            INSERT INTO public.venta (id_movimiento_fk, id_cliente_fk, numero_documento,
                                      forma_pago, total, es_envio, id_empresa_fk, numero_guia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_venta
        """
        resultado = self.db.fetch_one(query_venta, (
            venta.id_movimiento_fk, venta.id_cliente_fk, venta.numero_documento,
            venta.forma_pago, venta.total, venta.es_envio,
            venta.id_empresa_fk, venta.numero_guia
        ))

        if not resultado:
            return None

        id_venta = resultado['id_venta']

        # 3. Crear detalles de venta
        for detalle in detalles:
            detalle.id_venta_fk = id_venta
            detalle.calcular_subtotal()
            query_detalle = """
                INSERT INTO public.detalle_venta (id_venta_fk, id_producto_fk, cantidad,
                                                   precio_unitario, subtotal, descuento)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.db.execute_query(query_detalle, (
                detalle.id_venta_fk, detalle.id_producto_fk, detalle.cantidad,
                detalle.precio_unitario, detalle.subtotal, detalle.descuento
            ))

        # 4. Si es envío, crear cuenta por cobrar
        if venta.es_envio:
            query_cuenta = """
                INSERT INTO public.cuenta_por_cobrar (id_movimiento_fk, numero_documento,
                                                       monto, id_venta_fk, pagado)
                VALUES (%s, %s, %s, %s, false)
            """
            self.db.execute_query(query_cuenta, (
                id_movimiento, venta.numero_documento, venta.total, id_venta
            ))

        return id_venta

    def listar_ventas_por_mes(self, anio: int, mes: int) -> list[dict]:
        query = """
            SELECT v.id_venta, v.numero_documento, c.nombre as cliente_nombre,
                   c.apellido as cliente_apellido, v.forma_pago, v.total,
                   m.fecha_hora, v.es_envio, v.numero_guia, e.nombre as empresa_envio
            FROM public.venta v
            JOIN public.movimiento_caja m ON v.id_movimiento_fk = m.id_movimiento
            JOIN public.cliente c ON v.id_cliente_fk = c.id_cliente
            LEFT JOIN public.empresa_envio e ON v.id_empresa_fk = e.id_empresa
            WHERE EXTRACT(YEAR FROM m.fecha_hora) = %s 
              AND EXTRACT(MONTH FROM m.fecha_hora) = %s
            ORDER BY m.fecha_hora
        """
        return self.db.fetch_all(query, (anio, mes))


# ==================== APARTADO DAO ====================

class ApartadoDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.movimiento_dao = MovimientoCajaDAO(db)

    def crear_con_primer_abono(self, apartado: Apartado, monto_abono: float,
                               id_caja_fk: int, id_usuario_fk: int) -> int | None:
        """
        Crea un apartado y registra el primer abono (10%)
        """
        # 1. Crear apartado
        query_apartado = """
            INSERT INTO public.apartado (id_cliente_fk, id_producto_fk,
                                         total_producto, fecha_inicio, estado)
            VALUES (%s, %s, %s, %s, %s) RETURNING id_apartado
        """
        resultado = self.db.fetch_one(query_apartado, (
            apartado.id_cliente_fk, apartado.id_producto_fk,
            apartado.total_producto, apartado.fecha_inicio, apartado.estado
        ))

        if not resultado:
            return None

        id_apartado = resultado['id_apartado']

        # 2. Crear movimiento de caja
        movimiento = MovimientoCaja(
            id_caja_fk=id_caja_fk,
            tipo_movimiento=MovimientoCaja.TIPO_INGRESO,
            descripcion=f"Abono a apartado {id_apartado}",
            monto=monto_abono,
            id_usuario_fk=id_usuario_fk
        )
        id_movimiento = self.movimiento_dao.crear(movimiento)

        if not id_movimiento:
            return None

        # 3. Crear detalle de apartado
        query_detalle = """
            INSERT INTO public.detalle_apartado (id_apartado_fk, id_movimiento_fk,
                                                  fecha_pago, monto)
            VALUES (%s, %s, CURRENT_DATE, %s)
        """
        self.db.execute_query(query_detalle, (id_apartado, id_movimiento, monto_abono))

        return id_apartado

    def registrar_abono(self, id_apartado: int, monto: float,
                        id_caja_fk: int, id_usuario_fk: int) -> bool:
        """Registra un abono a un apartado existente"""
        # 1. Crear movimiento de caja
        movimiento = MovimientoCaja(
            id_caja_fk=id_caja_fk,
            tipo_movimiento=MovimientoCaja.TIPO_INGRESO,
            descripcion=f"Abono a apartado {id_apartado}",
            monto=monto,
            id_usuario_fk=id_usuario_fk
        )
        id_movimiento = self.movimiento_dao.crear(movimiento)

        if not id_movimiento:
            return False

        # 2. Crear detalle de apartado
        query_detalle = """
            INSERT INTO public.detalle_apartado (id_apartado_fk, id_movimiento_fk,
                                                  fecha_pago, monto)
            VALUES (%s, %s, CURRENT_DATE, %s)
        """
        self.db.execute_query(query_detalle, (id_apartado, id_movimiento, monto))

        # 3. Verificar si completó el total
        query_total = """
            SELECT a.total_producto, COALESCE(SUM(da.monto), 0) as total_abonado
            FROM public.apartado a
            LEFT JOIN public.detalle_apartado da ON a.id_apartado = da.id_apartado_fk
            WHERE a.id_apartado = %s
            GROUP BY a.total_producto
        """
        resultado = self.db.fetch_one(query_total, (id_apartado,))

        if resultado and resultado['total_abonado'] >= resultado['total_producto']:
            self.db.execute_query(
                "UPDATE public.apartado SET estado = 'COMPLETADO' WHERE id_apartado = %s",
                (id_apartado,)
            )

        return True

    def cancelar_apartado(self, id_apartado: int, monto_a_devolver: float,
                          id_caja_fk: int, id_usuario_fk: int) -> bool:
        """Cancela un apartado y registra la devolución como gasto"""
        # 1. Crear movimiento de egreso para la devolución
        movimiento = MovimientoCaja(
            id_caja_fk=id_caja_fk,
            tipo_movimiento=MovimientoCaja.TIPO_EGRESO,
            descripcion=f"Devolución cancelación apartado {id_apartado}",
            monto=monto_a_devolver,
            id_usuario_fk=id_usuario_fk
        )
        id_movimiento = self.movimiento_dao.crear(movimiento)

        if not id_movimiento:
            return False

        # 2. Registrar gasto por devolución
        query_gasto = """
            INSERT INTO public.gasto (id_movimiento_fk, tipo_gasto, descripcion, monto)
            VALUES (%s, %s, %s, %s)
        """
        self.db.execute_query(query_gasto, (
            id_movimiento, Gasto.TIPO_DEVOLUCION,
            f"Devolución por cancelación de apartado {id_apartado}", monto_a_devolver
        ))

        # 3. Cambiar estado del apartado
        self.db.execute_query(
            "UPDATE public.apartado SET estado = 'CANCELADO' WHERE id_apartado = %s",
            (id_apartado,)
        )

        return True

    def listar_activos(self) -> list[Apartado]:
        query = """
            SELECT id_apartado, id_cliente_fk, id_producto_fk, total_producto,
                   fecha_inicio, estado
            FROM public.apartado WHERE estado = 'ACTIVO'
            ORDER BY fecha_inicio
        """
        resultados = self.db.fetch_all(query)
        return [Apartado.from_dict(r) for r in resultados]


# ==================== GASTO DAO ====================

class GastoDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.movimiento_dao = MovimientoCajaDAO(db)

    def registrar_gasto(self, gasto: Gasto, id_caja_fk: int, id_usuario_fk: int) -> int | None:
        """Registra un gasto con su movimiento de caja"""
        movimiento = MovimientoCaja(
            id_caja_fk=id_caja_fk,
            tipo_movimiento=MovimientoCaja.TIPO_EGRESO,
            descripcion=gasto.descripcion or f"Gasto: {gasto.tipo_gasto}",
            monto=gasto.monto,
            id_usuario_fk=id_usuario_fk
        )
        id_movimiento = self.movimiento_dao.crear(movimiento)

        if not id_movimiento:
            return None

        gasto.id_movimiento_fk = id_movimiento
        query_gasto = """
            INSERT INTO public.gasto (id_movimiento_fk, tipo_gasto, descripcion, monto)
            VALUES (%s, %s, %s, %s) RETURNING id_gasto
        """
        resultado = self.db.fetch_one(query_gasto, (
            gasto.id_movimiento_fk, gasto.tipo_gasto, gasto.descripcion, gasto.monto
        ))

        return resultado['id_gasto'] if resultado else None


# ==================== CUENTA POR COBRAR DAO ====================

class CuentaPorCobrarDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def listar_pendientes(self) -> list[CuentaPorCobrar]:
        query = """
            SELECT id_cuenta, id_movimiento_fk, numero_documento,
                   monto, id_venta_fk, pagado
            FROM public.cuenta_por_cobrar WHERE pagado = false
            ORDER BY id_cuenta
        """
        resultados = self.db.fetch_all(query)
        return [CuentaPorCobrar.from_dict(r) for r in resultados]

    def marcar_pagado(self, id_cuenta: int) -> bool:
        query = "UPDATE public.cuenta_por_cobrar SET pagado = true WHERE id_cuenta = %s"
        return self.db.execute_query(query, (id_cuenta,))


# ==================== EMPRESA ENVIO DAO ====================

class EmpresaEnvioDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def listar_todas(self) -> list[EmpresaEnvio]:
        query = "SELECT id_empresa, nombre, telefono FROM public.empresa_envio ORDER BY nombre"
        resultados = self.db.fetch_all(query)
        return [EmpresaEnvio.from_dict(r) for r in resultados]

    def crear(self, empresa: EmpresaEnvio) -> int | None:
        query = "INSERT INTO public.empresa_envio (nombre, telefono) VALUES (%s, %s) RETURNING id_empresa"
        resultado = self.db.fetch_one(query, (empresa.nombre, empresa.telefono))
        return resultado['id_empresa'] if resultado else None


# ==================== REPORTES DAO ====================

class ReportesDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def reporte_caja_dia(self, fecha: date, id_caja_fk: int = None) -> dict:
        """Genera el reporte de caja para un día específico"""

        # Buscar caja si no se especifica
        if id_caja_fk is None:
            query_caja = "SELECT id_caja FROM public.caja WHERE fecha = %s"
            resultado = self.db.fetch_one(query_caja, (fecha,))
            if resultado:
                id_caja_fk = resultado['id_caja']
            else:
                return {}

        # Monto inicial del día
        query_apertura = """
            SELECT monto_inicial FROM public.apertura_cierre ac
            JOIN public.caja c ON ac.id_caja_fk = c.id_caja
            WHERE c.id_caja = %s AND DATE(ac.fecha_hora_apertura) = %s
            ORDER BY ac.fecha_hora_apertura LIMIT 1
        """
        resultado = self.db.fetch_one(query_apertura, (id_caja_fk, fecha))
        monto_inicial = float(resultado['monto_inicial']) if resultado else 0

        # Totales del día
        query_totales = """
            SELECT 
                COALESCE(SUM(CASE WHEN tipo_movimiento = 'INGRESO' THEN monto ELSE 0 END), 0) as total_ingresos,
                COALESCE(SUM(CASE WHEN tipo_movimiento = 'EGRESO' THEN monto ELSE 0 END), 0) as total_egresos
            FROM public.movimiento_caja
            WHERE id_caja_fk = %s AND DATE(fecha_hora) = %s
        """
        totales = self.db.fetch_one(query_totales, (id_caja_fk, fecha))

        total_ingresos = float(totales['total_ingresos']) if totales else 0
        total_egresos = float(totales['total_egresos']) if totales else 0

        # Movimientos del día
        query_movimientos = """
            SELECT id_movimiento, tipo_movimiento, descripcion, monto, 
                   fecha_hora, id_usuario_fk, u.nombre as usuario_nombre
            FROM public.movimiento_caja m
            LEFT JOIN public.usuario u ON m.id_usuario_fk = u.id_usuario
            WHERE m.id_caja_fk = %s AND DATE(m.fecha_hora) = %s
            ORDER BY m.fecha_hora
        """
        movimientos = self.db.fetch_all(query_movimientos, (id_caja_fk, fecha))

        return {
            'fecha': fecha,
            'id_caja': id_caja_fk,
            'monto_inicial': monto_inicial,
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'monto_final': monto_inicial + total_ingresos - total_egresos,
            'movimientos': movimientos
        }

    def reporte_ventas_mensual(self, anio: int, mes: int) -> dict:
        """Genera el reporte de ventas mensual similar al Excel"""
        ventas_dao = VentaDAO(self.db)
        ventas = ventas_dao.listar_ventas_por_mes(anio, mes)

        # Estadísticas
        total_ventas = sum(v['total'] for v in ventas) if ventas else 0
        ventas_efectivo = sum(v['total'] for v in ventas if v['forma_pago'] == 'EF')
        ventas_tarjeta = sum(v['total'] for v in ventas if v['forma_pago'] == 'TC/TD')
        ventas_transferencia = sum(v['total'] for v in ventas if v['forma_pago'] == 'TF')
        ventas_envio = sum(v['total'] for v in ventas if v['es_envio'] == True)

        # Envíos por empresa
        envios_por_empresa = {}
        for v in ventas:
            if v['es_envio'] and v['empresa_envio']:
                envios_por_empresa[v['empresa_envio']] = envios_por_empresa.get(v['empresa_envio'], 0) + 1

        return {
            'anio': anio,
            'mes': mes,
            'total_ventas': total_ventas,
            'cantidad_ventas': len(ventas),
            'desglose_forma_pago': {
                'efectivo': ventas_efectivo,
                'tarjeta': ventas_tarjeta,
                'transferencia': ventas_transferencia,
                'envio': ventas_envio
            },
            'envios_por_empresa': envios_por_empresa,
            'ventas': ventas
        }