import sys
import os

# Configuración de rutas para que reconozca los modelos y la base de datos
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_raiz)
sys.path.append(os.path.join(ruta_raiz, 'models'))

from models.usuario import Usuario
from models.dao import UsuarioDAO
from database.conexion import DatabaseConnection

class UsuarioService:
    def __init__(self, db_connection):
        self.usuario_dao = UsuarioDAO(db_connection)
        self.db = db_connection

    def crear_nuevo_usuario(self, nombre, username, password, rol, estado=True):
        nuevo = Usuario(nombre=nombre, usuario=username, password=password, rol=rol, estado=estado)
        return self.usuario_dao.crear(nuevo)

    def actualizar_datos(self, id_usuario, nombre, username, password, rol, estado):
        query = """
            UPDATE public.usuario 
            SET nombre = %s, usuario = %s, password = %s, rol = %s, estado = %s
            WHERE id_usuario = %s
        """
        params = (nombre, username, password, rol, estado, id_usuario)
        return self.db.execute_query(query, params)

    def listar_usuarios(self):
        query = "SELECT * FROM public.usuario ORDER BY id_usuario ASC"
        resultados = self.db.fetch_all(query)
        return [Usuario.from_dict(u) for u in resultados] if resultados else []

    def buscar_por_nombre_completo(self, nombre_buscado):
        query = "SELECT * FROM public.usuario WHERE nombre ILIKE %s"
        params = (f"%{nombre_buscado}%",)
        resultados = self.db.fetch_all(query, params)
        return [Usuario.from_dict(u) for u in resultados] if resultados else []

    def buscar_por_username(self, user_buscado):
        query = "SELECT * FROM public.usuario WHERE usuario = %s"
        res = self.db.fetch_one(query, (user_buscado,))
        return Usuario.from_dict(res) if res else None

# --- MENÚ DE PRUEBAS PARA EDICIÓN Y LOGIN ---
if __name__ == "__main__":
    try:
        db = DatabaseConnection()
        service = UsuarioService(db)

        while True:
            print("\n--- MÓDULO DE USUARIOS ---")
            print("1. Login (Probar Username)")
            print("2. Buscar y Editar (Nombre/Estado)")
            print("3. Listar Usuarios")
            print("4. Crear Nuevo")
            print("5. Salir")

            op = input("Seleccione: ")

            if op == "1":
                usr = input("Username: ")
                # Simulamos login buscando el user
                user = service.buscar_por_username(usr)
                if user:
                    print(f"✅ Login exitoso. Bienvenido {user.nombre}")
                else:
                    print("❌ Error: Usuario no encontrado.")

            elif op == "2":
                nom = input("Nombre a buscar para editar: ")
                encontrados = service.buscar_por_nombre_completo(nom)

                if encontrados:
                    print(f"\nResultados ({len(encontrados)}):")
                    for idx, e in enumerate(encontrados):
                        print(f"{idx + 1}. ID: {e.id_usuario} | {e.nombre} | Estado: {'Activo' if e.estado else 'Inactivo'}")

                    sel = int(input("\nSeleccione el número para editar (o 0 para cancelar): "))
                    if sel > 0:
                        u_ed = encontrados[sel-1]
                        print(f"\nEditando a: {u_ed.nombre}")

                        # Edición de Nombre
                        nuevo_nombre = input(f"Nuevo nombre [{u_ed.nombre}]: ") or u_ed.nombre

                        # Edición de Estado
                        nuevo_estado = input(f"¿Activo? (s/n) [{'s' if u_ed.estado else 'n'}]: ").lower()
                        est_bool = True if nuevo_estado == 's' else False

                        # Guardar cambios
                        service.actualizar_datos(u_ed.id_usuario, nuevo_nombre, u_ed.usuario, u_ed.password, u_ed.rol, est_bool)
                        print("✅ Datos actualizados en la base de datos.")
                else:
                    print("❌ No se encontraron coincidencias.")

            elif op == "3":
                for u in service.listar_usuarios():
                    print(f"ID: {u.id_usuario} | {u.nombre} | {u.usuario} | {'[Activo]' if u.estado else '[Inactivo]'}")

            elif op == "4":
                n = input("Nombre: "); u = input("User: "); p = input("Pass: "); r = input("Rol: ")
                service.crear_nuevo_usuario(n, u, p, r)
                print("✅ Creado.")

            elif op == "5":
                break

    except Exception as e:
        print(f"❌ Error: {e}")