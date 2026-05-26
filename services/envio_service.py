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


