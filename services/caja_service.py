# Servicio de caja y autenticación — conectado a Supabase PostgreSQL
# Tablas: usuario (sin s), caja, apertura_cierre (con id_caja_fk)

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.conexion import DatabaseConnection
from models.usuario import Usuario


class CajaService:
    """Servicio para manejar la caja y autenticación"""

    def __init__(self):
        self.db = DatabaseConnection()

    # ──────────────────────────────────────────────────────────────
    def obtener_usuarios_activos(self):
        """
        Obtiene usuarios activos desde la tabla 'usuario'.
        Retorna lista de dicts: id_usuario, nombre, usuario, rol.
        """
        query = """
            SELECT id_usuario, nombre, usuario, rol
            FROM   usuario
            WHERE  estado = TRUE
            ORDER  BY nombre
        """
        rows = self.db.fetch_all(query)
        return [
            {
                'id_usuario': row['id_usuario'],
                'nombre':     row['nombre'],
                'usuario':    row['usuario'],
                'rol':        row['rol'],
            }
            for row in rows
        ]

    # ──────────────────────────────────────────────────────────────
    def autenticar_usuario(self, id_usuario, password):
        """
        Autentica por id_usuario y contraseña.
        Retorna: (success: bool, mensaje: str, usuario_dict | None)
        """
        query = """
            SELECT id_usuario, nombre, usuario, password, rol, estado, fecha_creacion
            FROM   usuario
            WHERE  id_usuario = %s
        """
        row = self.db.fetch_one(query, (id_usuario,))

        if not row:
            return False, "Usuario no encontrado", None

        if not row['estado']:
            return False, "Usuario desactivado, contacte al administrador", None

        usuario = Usuario.from_dict(dict(row))

        if not usuario.verificar_password(password):
            return False, "Contraseña incorrecta", None

        return True, "Bienvenido", usuario.to_dict()

    # ──────────────────────────────────────────────────────────────
    def hay_caja_abierta(self):
        """
        Verifica si existe una caja abierta.
        """
        query = """
            SELECT id_apertura
            FROM apertura_cierre
            WHERE fecha_hora_cierre IS NULL
            LIMIT 1
        """

        row = self.db.fetch_one(query)
        return row is not None

    # ──────────────────────────────────────────────────────────────
    def registrar_apertura_caja(self, id_usuario, monto_inicial):
        """
        Abre la caja:
          1) Verifica si ya existe una caja abierta.
          2) Inserta en 'caja' (fecha de hoy) → obtiene id_caja.
          3) Inserta en 'apertura_cierre' vinculando id_caja e id_usuario.
        Retorna id_apertura (int) o None si falló.
        """

        # Verificar si ya hay una caja abierta
        if self.hay_caja_abierta():
            print("Ya existe una caja abierta. Debe cerrarse antes de abrir otra.")
            return None

        # Paso 1 — crear registro de caja del día
        caja_row = self.db.fetch_one(
            "INSERT INTO caja (fecha) VALUES (CURRENT_DATE) RETURNING id_caja"
        )

        if not caja_row:
            print("No se pudo crear registro en tabla 'caja'")
            return None

        id_caja = caja_row['id_caja']

        # Paso 2 — registrar apertura
        apertura_row = self.db.fetch_one(
            """
            INSERT INTO apertura_cierre
                (id_caja_fk, id_usuario_fk, fecha_hora_apertura, monto_inicial)
            VALUES (%s, %s, NOW(), %s)
            RETURNING id_apertura
            """,
            (id_caja, id_usuario, monto_inicial)
        )

        if not apertura_row:
            print("No se pudo registrar apertura de caja")
            return None

        id_apertura = apertura_row['id_apertura']

        print(f"Apertura registrada — id_apertura={id_apertura}, id_caja={id_caja}")

        return id_apertura

    # ──────────────────────────────────────────────────────────────
    def registrar_cierre_caja(self, id_apertura, monto_final):
        """
        Cierra la caja actualizando fecha_hora_cierre y monto_final.
        Retorna True si tuvo éxito.
        """
        ok = self.db.execute_query(
            """
            UPDATE apertura_cierre
            SET    fecha_hora_cierre = NOW(),
                   monto_final       = %s
            WHERE  id_apertura = %s
            """,
            (monto_final, id_apertura)
        )

        if ok:
            print(f"Cierre registrado — id_apertura={id_apertura}")
        else:
            print("No se pudo registrar el cierre de caja")

        return ok
