import psycopg2
from config.db_config import DatabaseConfig

def getConexion():
    try:
        params = DatabaseConfig.get_connection_params()
        conexion = psycopg2.connect(**params)
        conexion.set_client_encoding('UTF8')
        return conexion
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

class Cliente:
    def __init__(self, nombre, apellido, telefono=""):
        self.__nombre = nombre
        self.__apellido = apellido
        self.__telefono = telefono

    def guardar(self):
        conexion = getConexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "INSERT INTO cliente (nombre, apellido, telefono) VALUES (%s, %s, %s)"
                cursor.execute(sql, (self.__nombre, self.__apellido, self.__telefono))
                conexion.commit()
                print("✅ Cliente guardado.")
                cursor.close()
                conexion.close()
                return True
            except Exception as e:
                print(f"❌ Error al guardar cliente: {e}")
                conexion.rollback()
                return False
        return False

class Producto:
    # CORREGIDO: El orden ahora es (nombre, marca, modelo, descripcion)
    def __init__(self, nombre, marca, modelo, descripcion):
        self.__nombre = nombre
        self.__marca = marca
        self.__modelo = modelo
        self.__descripcion = descripcion

    def guardar(self):
        conexion = getConexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "INSERT INTO producto (nombre, marca, modelo, descripcion) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (self.__nombre, self.__marca, self.__modelo, self.__descripcion))
                conexion.commit()
                print("✅ Producto guardado.")
                cursor.close()
                conexion.close()
                return True
            except Exception as e:
                print(f"❌ Error al guardar producto: {e}")
                conexion.rollback()
                return False
        return False

# Ejecución de prueba
if __name__ == "__main__":
    print("--- REGISTRO ---")
    nombre = input("Ingrese nombre: ")
    apellido = input("Ingrese apellido: ")
    telefono = input("Ingrese teléfono: ")
    cli = Cliente(nombre, apellido, telefono)
    cli.guardar()

    print("\n--- REGISTRO DE PRODUCTO ---")
    prod_nombre = input("Ingrese nombre del producto: ")
    marca = input("Ingrese marca: ")
    modelo = input("Ingrese modelo: ")
    desc = input("Ingrese descripción: ")
    # CORREGIDO: El orden ahora es (nombre, marca, modelo, descripcion)
    prod = Producto(prod_nombre, marca, modelo, desc)
    prod.guardar()