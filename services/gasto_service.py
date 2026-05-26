import sys
import os

# Configuración de rutas
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_raiz)
sys.path.append(os.path.join(ruta_raiz, 'models'))

from models.gasto import Gasto
from database.conexion import DatabaseConnection


class GastoService:
    def __init__(self, db_connection):
        self.db = db_connection

    # CREAR
    def crear_gasto(self, id_movimiento_fk, tipo_gasto, descripcion, monto):
        query = """
            INSERT INTO public.gasto (id_movimiento_fk, tipo_gasto, descripcion, monto)
            VALUES (%s, %s, %s, %s)
        """
        params = (id_movimiento_fk, tipo_gasto, descripcion, monto)
        return self.db.execute_query(query, params)

    # ACTUALIZAR
    def actualizar_gasto(self, id_gasto, id_movimiento_fk, tipo_gasto, descripcion, monto):
        query = """
            UPDATE public.gasto
            SET id_movimiento_fk = %s,
                tipo_gasto = %s,
                descripcion = %s,
                monto = %s
            WHERE id_gasto = %s
        """
        params = (id_movimiento_fk, tipo_gasto, descripcion, monto, id_gasto)
        return self.db.execute_query(query, params)

    #  LISTAR
    def listar_gastos(self):
        query = "SELECT * FROM public.gasto ORDER BY id_gasto ASC"
        resultados = self.db.fetch_all(query)
        return [Gasto.from_dict(g) for g in resultados] if resultados else []

    #  BUSCAR POR TIPO
    def buscar_por_tipo(self, tipo_buscado):
        query = "SELECT * FROM public.gasto WHERE tipo_gasto ILIKE %s"
        params = (f"%{tipo_buscado}%",)
        resultados = self.db.fetch_all(query, params)
        return [Gasto.from_dict(g) for g in resultados] if resultados else []

    # ELIMINAR
    def eliminar_gasto(self, id_gasto):
        query = "DELETE FROM public.gasto WHERE id_gasto = %s"
        return self.db.execute_query(query, (id_gasto,))

