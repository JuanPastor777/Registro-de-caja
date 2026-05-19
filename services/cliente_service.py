import sys
import os
import sys
import os

ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_raiz)
import psycopg2
from config.db_config import DatabaseConfig


class DatabaseConnection:

    def __init__(self):
        params = DatabaseConfig.get_connection_params()
        self.conn = psycopg2.connect(**params)
        self.conn.set_client_encoding('UTF8')

    def execute_query(self, query, params=None):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        cursor.close()

    def fetch_all(self, query, params=None):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()
        cursor.close()
        return data

class Cliente:
    def __init__(self, id_cliente=None, nombre="", apellido="", telefono=""):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono

    @staticmethod
    def from_db(row):
        return Cliente(row[0], row[1], row[3], row[2])  
        

class ClienteDAO:

    def __init__(self, db):
        self.db = db

    def crear(self, cliente):
        query = "INSERT INTO cliente (nombre, telefono, apellido) VALUES (%s, %s, %s)"
        self.db.execute_query(query, (cliente.nombre, cliente.telefono, cliente.apellido))

    def listar(self):
        datos = self.db.fetch_all("SELECT * FROM cliente")
        return [Cliente.from_db(d) for d in datos]

    def eliminar(self, id_cliente):
        self.db.execute_query(
            "DELETE FROM cliente WHERE id_cliente = %s",
            (id_cliente,)
        )

    def actualizar(self, cliente):
        query = """
        UPDATE cliente 
        SET nombre=%s, telefono=%s, apellido=%s 
        WHERE id_cliente=%s
        """
        self.db.execute_query(
            query,
            (cliente.nombre, cliente.telefono, cliente.apellido, cliente.id_cliente)
        )

class ClienteService:

    def __init__(self):
        self.db = DatabaseConnection()
        self.dao = ClienteDAO(self.db)

    def crear(self, nombre, apellido, telefono):
        self.dao.crear(Cliente(nombre=nombre, apellido=apellido, telefono=telefono))

    def listar(self):
        return self.dao.listar()

    def eliminar(self, id_cliente):
        self.dao.eliminar(id_cliente)

    def actualizar(self, id_cliente, nombre, apellido, telefono):
        self.dao.actualizar(Cliente(id_cliente, nombre, apellido, telefono))

if __name__ == "__main__":
    service = ClienteService()

    while True:
        print("\n--- CLIENTES ---")
        print("1. Crear")
        print("2. Listar")
        print("3. Editar")
        print("4. Eliminar")
        print("5. Salir")

        op = input("Opción: ")

        if op == "1":
            n = input("Nombre: ")
            a = input("Apellido: ")
            t = input("Teléfono: ")
            service.crear(n, a, t)

        elif op == "2":
            for c in service.listar():
                print(c.id_cliente, c.nombre, c.apellido, c.telefono)

        elif op == "3":
            idc = input("ID: ")
            n = input("Nuevo nombre: ")
            a = input("Nuevo apellido: ")
            t = input("Teléfono: ")
            service.actualizar(idc, n, a, t)

        elif op == "4":
            idc = input("ID: ")
            service.eliminar(idc)

        elif op == "5":
            break