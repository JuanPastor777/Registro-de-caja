import psycopg2
import secrets
import string
from config.db_config import DatabaseConfig 

class Usuario:
    def __init__(self, nombre=None, usuario=None, password=None, rol=None, estado=True):
        self.nombre = nombre
        self.usuario = usuario
        self.password = password
        self.rol = rol
        self.estado = estado

    @staticmethod
    def get_conexion():
        try:
            params = DatabaseConfig.get_connection_params()
            conexion = psycopg2.connect(**params)
            conexion.set_client_encoding('UTF8')
            return conexion
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return None

    @staticmethod
    def generar_password(longitud=12):
        caracteres = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(caracteres) for _ in range(longitud))

    def guardar(self):
        """Inserta el objeto actual en la base de datos"""
        conexion = self.get_conexion()
        if not conexion: return

        try:
            cursor = conexion.cursor()
            query = """
                INSERT INTO usuario (nombre, usuario, password, rol, estado)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (self.nombre, self.usuario, self.password, self.rol, self.estado))
            conexion.commit()
            print(f"\n✅ Usuario '{self.usuario}' creado y HABILITADO.")
            cursor.close()
            conexion.close()
        except Exception as e:
            print(f"❌ Error al guardar: {e}")

    @classmethod
    def cambiar_estado(cls, username, nuevo_estado):
        """Método de clase para actualizar el estado sin instanciar todo el objeto"""
        conexion = cls.get_conexion()
        if not conexion: return

        estado_texto = "HABILITADO" if nuevo_estado else "DESHABILITADO"
        try:
            cursor = conexion.cursor()
            query = "UPDATE usuario SET estado = %s WHERE usuario = %s"
            cursor.execute(query, (nuevo_estado, username))
            
            if cursor.rowcount > 0:
                conexion.commit()
                print(f"\n🔄 El usuario '{username}' ahora está {estado_texto}.")
            else:
                print(f"\n❌ No se encontró el usuario '{username}'.")
            
            cursor.close()
            conexion.close()
        except Exception as e:
            print(f"❌ Error al actualizar estado: {e}")

# =========================
# LÓGICA DE INTERFAZ (CLI)
# =========================

def menu_crear_usuario():
    nombre = input("Nombre completo: ")
    username = input("Nombre de usuario: ")
    
    print("\n¿Desea generar una contraseña automática?")
    op_pass = input("1. Sí / 2. No: ")
    
    password = Usuario.generar_password() if op_pass == "1" else input("Ingrese contraseña: ")
    if op_pass == "1": print(f"🔑 Generada: {password}")
    
    rol = input("Rol: ")
    
    # Creamos la instancia y guardamos
    nuevo_user = Usuario(nombre, username, password, rol)
    nuevo_user.guardar()

def menu_gestionar_estado():
    username = input("Ingrese el nombre de usuario a gestionar: ")
    print(f"\n¿Qué desea hacer con el usuario '{username}'?")
    print("1. Habilitar (Set True)")
    print("2. Deshabilitar (Set False)")
    op = input("Seleccione: ")

    estado = True if op == "1" else False
    Usuario.cambiar_estado(username, estado)

if __name__ == "__main__":
    while True:
        print("\n=== GESTIÓN DE USUARIOS (POO) ===")
        print("1. Crear nuevo usuario")
        print("2. Habilitar/Deshabilitar usuario")
        print("3. Salir")

        op = input("Seleccione una opción: ")

        if op == "1":
            menu_crear_usuario()
        elif op == "2":
            menu_gestionar_estado()
        elif op == "3":
            print("Saliendo...")
            break
        else:
            print("❌ Opción inválida.")