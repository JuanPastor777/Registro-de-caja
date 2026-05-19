import psycopg2
from datetime import datetime
from config.db_config import DatabaseConfig

def getConexion():
    try:
        conn_str = DatabaseConfig.get_connection_string()
        conexion = psycopg2.connect(conn_str)
        conexion.set_client_encoding('UTF8')
        return conexion
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

# ==========================================
# CLASES CON PERSISTENCIA (CAMPOS COMPLETOS)
# ==========================================

class EmpresaEnvio:
    def __init__(self, nombre, telefono):
        self.nombre = nombre
        self.telefono = telefono

    def guardar(self):
        conexion = getConexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                # El ID de empresa es automático (SERIAL)
                sql = "INSERT INTO public.empresa_envio (nombre, telefono) VALUES (%s, %s)"
                cursor.execute(sql, (self.nombre, self.telefono))
                conexion.commit()
                print("✅ Empresa guardada.")
            except Exception as e: print(f"❌ Error: {e}")
            finally: conexion.close()

class Gasto:
    def __init__(self, id_mov, tipo, descripcion, monto):
        self.id_mov = id_mov
        self.tipo = tipo
        self.descripcion = descripcion
        self.monto = monto

    def guardar(self):
        conexion = getConexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Asumimos que id_gasto es SERIAL
                sql = "INSERT INTO public.gasto (id_movimiento_fk, tipo_gasto, descripcion, monto) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (self.id_mov, self.tipo, self.descripcion, self.monto))
                conexion.commit()
                print("✅ Gasto guardado.")
            except Exception as e: print(f"❌ Error: {e}")
            finally: conexion.close()

class CuentaPorCobrar:
    def __init__(self, id_mov, id_empresa, documento, monto, guia):
        self.id_mov = id_mov
        self.id_empresa = id_empresa
        self.documento = documento
        self.monto = monto
        self.guia = guia

    def guardar(self):
        conexion = getConexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                # ID Cuenta es SERIAL
                sql = "INSERT INTO public.cuenta_por_cobrar (id_movimiento_fk, id_empresa_fk, numero_documento, monto, numero_guia) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (self.id_mov, self.id_empresa, self.documento, self.monto, self.guia))
                conexion.commit()
                print("✅ Cuenta por cobrar guardada.")
            except Exception as e: print(f"❌ Error: {e}")
            finally: conexion.close()

class Apartado:
    def __init__(self, id_cliente, id_producto, total, fecha, estado):
        self.id_cliente = id_cliente
        self.id_producto = id_producto
        self.total = total
        self.fecha = fecha
        self.estado = estado

    def guardar(self):
        conexion = getConexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                # ID Apartado es SERIAL
                sql = "INSERT INTO public.apartado (id_cliente_fk, id_producto_fk, total_producto, fecha_inicio, estado) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (self.id_cliente, self.id_producto, self.total, self.fecha, self.estado))
                conexion.commit()
                print("✅ Apartado guardado.")
            except Exception as e: print(f"❌ Error: {e}")
            finally: conexion.close()

class DetalleApartado:
    def __init__(self, id_apartado, id_mov, fecha_pago, monto):
        self.id_apartado = id_apartado
        self.id_mov = id_mov
        self.fecha_pago = fecha_pago
        self.monto = monto

    def guardar(self):
        conexion = getConexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                # ID Detalle es SERIAL
                sql = "INSERT INTO public.detalle_apartado (id_apartado_fk, id_movimiento_fk, fecha_pago, monto) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (self.id_apartado, self.id_mov, self.fecha_pago, self.monto))
                conexion.commit()
                print("✅ Pago de apartado guardado.")
            except Exception as e: print(f"❌ Error: {e}")
            finally: conexion.close()

# El menú se mantiene igual que antes, el cambio está dentro de las clases de arriba.
# ==========================================
# MENÚ DE PRUEBA EN CONSOLA
# ==========================================
def menu():
    while True:
        print("\n--- SISTEMA DE GESTIÓN ---")
        print("1. Empresa Envío | 2. Gasto | 3. Cuenta Cobrar | 4. Apartado | 5. Pago Apartado | 6. Salir | ")
        op = input("Seleccione una opción: ")

        try:
            if op == "1":
                EmpresaEnvio(input("Nombre: "), input("Teléfono: ")).guardar()
            elif op == "2":
                Gasto(input("ID Movimiento: "), input("Tipo: "), input("Descripción: "), input("Monto: ")).guardar()
            elif op == "3":
                CuentaPorCobrar(input("ID Mov: "), input("ID Empresa: "), input("Doc: "), input("Monto: "), input("Guía: ")).guardar()
            elif op == "4":
                Apartado(input("ID Cliente: "), input("ID Producto: "), input("Total: "), input("Fecha (YYYY-MM-DD): "), input("Estado: ")).guardar()
            elif op == "5":
                DetalleApartado(input("ID Apartado: "), input("ID Movimiento: "), input("Fecha (YYYY-MM-DD): "), input("Monto: ")).guardar()
            
            elif op == "6":
                print("Saliendo...")
                break
        except Exception as e:
            print(f"❌ Error al capturar datos: {e}")

if __name__ == "__main__":
    menu()