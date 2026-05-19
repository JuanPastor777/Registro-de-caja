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

# backend/producto_dao.py

class Producto:
    def __init__(self, id_producto=None, nombre="", marca="", modelo="", descripcion="", precio_costo=0.0):
        self.id_producto = id_producto
        self.nombre = nombre
        self.marca = marca
        self.modelo = modelo
        self.descripcion = descripcion
        self.precio_costo = precio_costo

    @staticmethod
    def from_db(row):
        # row: id_producto, nombre, marca, modelo, descripcion, precio_costo
        return Producto(
            row[0], row[1], row[2], row[3], row[4], 
            float(row[5]) if row[5] else 0.0
        )
# backend/producto_dao.py (actualizado)

# backend/producto_dao.py

class ProductoDAO:

    def __init__(self, db):
        self.db = db

    def crear(self, producto):
        query = """
        INSERT INTO producto (nombre, marca, modelo, descripcion, precio_costo)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id_producto
        """
        cursor = self.db.conn.cursor()
        cursor.execute(query, (
            producto.nombre, 
            producto.marca, 
            producto.modelo, 
            producto.descripcion, 
            producto.precio_costo
        ))
        self.db.conn.commit()
        id_producto = cursor.fetchone()[0]
        cursor.close()
        return id_producto

    def listar(self, filtros=None):
        """
        Listar productos con filtros opcionales
        filtros: dict con 'nombre', 'marca', 'modelo' opcionales
        """
        query = "SELECT id_producto, nombre, marca, modelo, descripcion, precio_costo FROM producto WHERE 1=1"
        params = []
        
        if filtros:
            if filtros.get('nombre'):
                query += " AND nombre ILIKE %s"
                params.append(f'%{filtros["nombre"]}%')
            if filtros.get('marca'):
                query += " AND marca ILIKE %s"
                params.append(f'%{filtros["marca"]}%')
            if filtros.get('modelo'):
                query += " AND modelo ILIKE %s"
                params.append(f'%{filtros["modelo"]}%')
        
        query += " ORDER BY id_producto"
        datos = self.db.fetch_all(query, params)
        return [Producto.from_db(d) for d in datos]

    def eliminar(self, id_producto):
        self.db.execute_query(
            "DELETE FROM producto WHERE id_producto = %s",
            (id_producto,)
        )

    def actualizar(self, producto):
        query = """
        UPDATE producto 
        SET nombre=%s, marca=%s, modelo=%s, descripcion=%s, precio_costo=%s
        WHERE id_producto=%s
        """
        self.db.execute_query(
            query,
            (
                producto.nombre, 
                producto.marca, 
                producto.modelo, 
                producto.descripcion, 
                producto.precio_costo,
                producto.id_producto
            )
        )
    
    def buscar_por_id(self, id_producto):
        datos = self.db.fetch_all(
            "SELECT id_producto, nombre, marca, modelo, descripcion, precio_costo FROM producto WHERE id_producto = %s", 
            (id_producto,)
        )
        if datos:
            return Producto.from_db(datos[0])
        return None
    
# backend/producto_service.py

class ProductoService:

    def __init__(self):
        self.db = DatabaseConnection()
        self.dao = ProductoDAO(self.db)

    def crear(self, nombre, marca, modelo, descripcion, precio_costo):
        producto = Producto(
            nombre=nombre, 
            marca=marca, 
            modelo=modelo, 
            descripcion=descripcion, 
            precio_costo=precio_costo
        )
        return self.dao.crear(producto)

    def listar(self, nombre=None, marca=None, modelo=None):
        filtros = {}
        if nombre:
            filtros['nombre'] = nombre
        if marca:
            filtros['marca'] = marca
        if modelo:
            filtros['modelo'] = modelo
        return self.dao.listar(filtros)

    def eliminar(self, id_producto):
        self.dao.eliminar(id_producto)

    def actualizar(self, id_producto, nombre, marca, modelo, descripcion, precio_costo):
        producto = Producto(
            id_producto, 
            nombre, 
            marca, 
            modelo, 
            descripcion, 
            precio_costo
        )
        self.dao.actualizar(producto)
    
    def buscar_por_id(self, id_producto):
        return self.dao.buscar_por_id(id_producto)

if __name__ == "__main__":
    service = ProductoService()

    while True:
        print("\n--- PRODUCTOS ---")
        print("1. Crear")
        print("2. Listar")
        print("3. Editar")
        print("4. Eliminar")
        print("5. Salir")

        op = input("Opción: ")

        if op == "1":
            n = input("Nombre: ")
            m = input("Marca: ")
            mo = input("Modelo: ")
            d = input("Descripción: ")
            service.crear(n, m, mo, d)

        elif op == "2":
            for p in service.listar():
                print(p.id_producto, p.nombre, p.marca, p.modelo, p.descripcion)

        elif op == "3":
            idp = input("ID: ")
            n = input("Nombre: ")
            m = input("Marca: ")
            mo = input("Modelo: ")
            d = input("Descripción: ")
            service.actualizar(idp, n, m, mo, d)

        elif op == "4":
            idp = input("ID: ")
            service.eliminar(idp)

        elif op == "5":
            break