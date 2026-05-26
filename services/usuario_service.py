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

