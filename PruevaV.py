import psycopg2
from datetime import datetime
from config.db_config import DatabaseConfig

# ==========================================
# FUNCIÓN GLOBAL DE CONEXIÓN
# ==========================================
def getConexion():
    try:
        params = DatabaseConfig.get_connection_params()
        conexion = psycopg2.connect(**params)
        conexion.set_client_encoding('UTF8')
        return conexion
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

# ==========================================
# CLASES DE ENTIDAD (BASE DE DATOS)
# ==========================================

class Caja:
    def __init__(self, fecha=None):
        self.fecha = fecha if fecha else datetime.now().date()

    def guardar(self):
        conexion = getConexion()
        id_generado = None
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "INSERT INTO caja (fecha) VALUES (%s) RETURNING id_caja"
                cursor.execute(sql, (self.fecha,))
                id_generado = cursor.fetchone()[0]
                conexion.commit()
            except Exception as e:
                print(f"❌ Error al crear caja: {e}")
            finally:
                conexion.close()
        return id_generado

class MovimientoCaja:
    def __init__(self, id_caja, tipo, descripcion, monto):
        self.id_caja = id_caja
        self.tipo = tipo
        self.descripcion = descripcion
        self.monto = monto
        self.fecha_hora = datetime.now()

    def guardar(self):
        conexion = getConexion()
        id_generado = None
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO movimiento_caja (id_caja_fk, tipo_movimiento, descripcion, monto, fecha_hora) 
                         VALUES (%s, %s, %s, %s, %s) RETURNING id_movimiento"""
                cursor.execute(sql, (self.id_caja, self.tipo, self.descripcion, self.monto, self.fecha_hora))
                id_generado = cursor.fetchone()[0]
                conexion.commit()
            except Exception as e:
                print(f"❌ Error al crear movimiento: {e}")
            finally:
                conexion.close()
        return id_generado

class Venta:
    def __init__(self, id_cliente, id_movimiento, num_doc, forma_pago, es_envio):
        self.id_cliente = id_cliente
        self.id_movimiento = id_movimiento
        self.num_doc = num_doc
        self.forma_pago = forma_pago
        self.es_envio = es_envio
        self.total = 0

    def guardar(self):
        conexion = getConexion()
        id_v = None
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO venta (id_cliente_fk, id_movimiento_fk, numero_documento, forma_pago, total, es_envio) 
                         VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_venta"""
                cursor.execute(sql, (self.id_cliente, self.id_movimiento, self.num_doc, self.forma_pago, self.total, self.es_envio))
                id_v = cursor.fetchone()[0]
                conexion.commit()
            except Exception as e:
                print(f"❌ Error en cabecera de venta: {e}")
            finally:
                conexion.close()
        return id_v

class DetalleVenta:
    def __init__(self, id_venta, id_producto, cantidad, precio):
        self.id_venta = id_venta
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.precio = precio
        self.subtotal = cantidad * precio

    def guardar(self):
        conexion = getConexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Insertar el detalle
                sql_det = """INSERT INTO detalle_venta (id_venta_fk, id_producto_fk, cantidad, precio_unitario, subtotal) 
                             VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql_det, (self.id_venta, self.id_producto, self.cantidad, self.precio, self.subtotal))
                # Actualizar el total de la venta principal
                sql_upd = "UPDATE venta SET total = total + %s WHERE id_venta = %s"
                cursor.execute(sql_upd, (self.subtotal, self.id_venta))
                conexion.commit()
                print(f"   ➕ Producto ID {self.id_producto} agregado. Subtotal: Q{self.subtotal}")
            except Exception as e:
                print(f"❌ Error en detalle: {e}")
            finally:
                conexion.close()

# ==========================================
# LÓGICA DE INTERFAZ Y FLUJO
# ==========================================

def menu_apertura():
    print("\n=== APERTURA DE CAJA (BILLETES) ===")
    total_inicial = 0
    billetes = {200:0, 100:0, 50:0, 20:0, 10:0, 5:0, 1:0}
    for d in billetes:
        cant = int(input(f"Billetes de Q{d}: "))
        total_inicial += (d * cant)
    
    # Proceso de guardado en BD
    caja_obj = Caja()
    id_caja = caja_obj.guardar()
    if id_caja:
        mov = MovimientoCaja(id_caja, "APERTURA", "Fondo inicial de caja", total_inicial)
        id_mov = mov.guardar()
        print(f"✅ Caja abierta con Q{total_inicial}. Movimiento ID: {id_mov}")
        return id_mov
    return None

def realizar_venta(id_mov_activo):
    print("\n--- NUEVA VENTA ---")
    try:
        id_cli = int(input("ID del Cliente (ej. 1): "))
        num_doc = input("Número de factura: ")
        pago = input("Forma de pago: ")
        envio = input("¿Es envío? (1: SI / 2: NO): ") == "1"

        venta = Venta(id_cli, id_mov_activo, num_doc, pago, envio)
        id_v = venta.guardar()

        if id_v:
            print(f"✅ Venta {id_v} creada. Ingrese productos.")
            while True:
                id_p_input = input("\nID Producto (0 para finalizar): ")
                if id_p_input == "0": break
                
                cant = int(input("Cantidad: "))
                prec = float(input("Precio: "))
                
                det = DetalleVenta(id_v, int(id_p_input), cant, prec)
                det.guardar()
            print(f"✅ Venta {id_v} finalizada.")
    except ValueError:
        print("❌ Error: Ingrese solo números en los campos de ID/Monto.")

# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("SISTEMA DE GESTIÓN INTEGRADO")
    id_mov = menu_apertura()
    
    if id_mov:
        while True:
            print("\n1. Registrar Venta")
            print("2. Salir")
            op = input("Seleccione: ")
            
            if op == "1":
                realizar_venta(id_mov)
            elif op == "2":
                print("Cerrando sistema...")
                break
            else:
                print("Opción inválida.")