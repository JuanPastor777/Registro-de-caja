import sys
import os

# Configuración de rutas
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_raiz)
sys.path.append(os.path.join(ruta_raiz, 'models'))

from models.empresa_envio import EmpresaEnvio
from database.conexion import DatabaseConnection


class EmpresaEnvioService:
    def __init__(self, db_connection):
        self.db = db_connection

    #  CREAR
    def crear_empresa(self, nombre, telefono):
        query = """
            INSERT INTO public.empresa_envio (nombre, telefono)
            VALUES (%s, %s)
        """
        return self.db.execute_query(query, (nombre, telefono))

    # ACTUALIZAR
    def actualizar_empresa(self, id_empresa, nombre, telefono):
        query = """
            UPDATE public.empresa_envio
            SET nombre = %s, telefono = %s
            WHERE id_empresa = %s
        """
        params = (nombre, telefono, id_empresa)
        return self.db.execute_query(query, params)

    # LISTAR
    def listar_empresas(self):
        query = "SELECT * FROM public.empresa_envio ORDER BY id_empresa ASC"
        resultados = self.db.fetch_all(query)
        return [EmpresaEnvio.from_dict(e) for e in resultados] if resultados else []

    # BUSCAR POR NOMBRE
    def buscar_por_nombre(self, nombre_buscado):
        query = "SELECT * FROM public.empresa_envio WHERE nombre ILIKE %s"
        params = (f"%{nombre_buscado}%",)
        resultados = self.db.fetch_all(query, params)
        return [EmpresaEnvio.from_dict(e) for e in resultados] if resultados else []

    # ELIMINAR
    def eliminar_empresa(self, id_empresa):
        query = "DELETE FROM public.empresa_envio WHERE id_empresa = %s"
        return self.db.execute_query(query, (id_empresa,))


if __name__ == "__main__":
    try:
        db = DatabaseConnection()
        service = EmpresaEnvioService(db)

        while True:
            print("\n--- MODULO EMPRESA DE ENVÍO ---")
            print("1. Listar empresas")
            print("2. Crear empresa")
            print("3. Buscar y editar")
            print("4. Eliminar")
            print("5. Salir")

            op = input("Seleccione: ")

            # LISTAR
            if op == "1":
                empresas = service.listar_empresas()
                for e in empresas:
                    print(f"ID: {e.id_empresa} | {e.nombre} | Tel: {e.telefono}")

            # CREAR
            elif op == "2":
                nombre = input("Nombre: ")
                telefono = input("Teléfono: ")
                service.crear_empresa(nombre, telefono)
                print("Empresa creada.")

            # BUSCAR Y EDITAR
            elif op == "3":
                nom = input("Nombre a buscar: ")
                encontrados = service.buscar_por_nombre(nom)

                if encontrados:
                    print(f"\nResultados ({len(encontrados)}):")
                    for idx, e in enumerate(encontrados):
                        print(f"{idx + 1}. ID: {e.id_empresa} | {e.nombre} | {e.telefono}")

                    sel = int(input("\nSeleccione número (0 cancelar): "))
                    if sel > 0:
                        emp = encontrados[sel - 1]

                        nuevo_nombre = input(f"Nuevo nombre [{emp.nombre}]: ") or emp.nombre
                        nuevo_tel = input(f"Nuevo teléfono [{emp.telefono}]: ") or emp.telefono

                        service.actualizar_empresa(emp.id_empresa, nuevo_nombre, nuevo_tel)
                        print(" Actualizado correctamente.")
                else:
                    print("No encontrado.")

            # ELIMINAR
            elif op == "4":
                id_emp = input("ID a eliminar: ")
                service.eliminar_empresa(id_emp)
                print(" Eliminado.")

            elif op == "5":
                break

    except Exception as e:
        print(f" Error: {e}")