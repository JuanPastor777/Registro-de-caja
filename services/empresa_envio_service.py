import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.conexion import DatabaseConnection
from models.empresa_envio import EmpresaEnvio
# Importamos el DAO real desde tu archivo dao.py
from models.dao import EmpresaEnvioDAO

class EmpresaEnvioService:
    def __init__(self, db_connection: DatabaseConnection = None):
        if db_connection is None:
            self.db = DatabaseConnection()
        else:
            self.db = db_connection
        self.dao = EmpresaEnvioDAO(self.db)

    def crear_empresa(self, nombre: str, telefono: str = None) -> dict | None:
        nueva = EmpresaEnvio(nombre=nombre, telefono=telefono)
        id_empresa = self.dao.crear(nueva)
        if id_empresa:
            nueva.id_empresa = id_empresa
            return nueva.to_dict()
        return None

    def listar_empresas(self) -> list[dict]:
        empresas = self.dao.listar_todas()  # devuelve lista de objetos EmpresaEnvio
        return [e.to_dict() for e in empresas]

    def obtener_empresa(self, id_empresa: int) -> dict | None:
        # Si tu DAO no tiene buscar_por_id, puedes implementarlo aquí
        # Pero por ahora asumimos que solo necesitas listar
        for e in self.dao.listar_todas():
            if e.id_empresa == id_empresa:
                return e.to_dict()
        return None