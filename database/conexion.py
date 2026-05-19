import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db_config import DatabaseConfig

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    raise ImportError(
        "psycopg2 no está instalado.\n"
        "Ejecuta:  pip install psycopg2-binary"
    )


class DatabaseConnection:
    """Maneja la conexión con Supabase PostgreSQL"""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establece conexión y fija zona horaria de Guatemala"""
        try:
            params = DatabaseConfig.get_connection_params()
            self.connection = psycopg2.connect(**params)
            self.connection.autocommit = False

            # 👇 Fijar zona horaria a Guatemala
            with self.connection.cursor() as cur:
                cur.execute("SET TIME ZONE 'America/Guatemala'")

            self.cursor = self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            print("Conexión establecida (zona: America/Guatemala).")
            return True
        except psycopg2.OperationalError as e:
            print(f"Error al conectar: {e}")
            return False

    def disconnect(self):
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
            if self.connection:
                self.connection.close()
                self.connection = None
        except Exception as e:
            print(f"Error al cerrar conexión: {e}")

    def _ensure_connected(self):
        if self.connection is None or self.connection.closed:
            return self.connect()
        return True

    def execute_query(self, query, params=None):
        if not self._ensure_connected():
            return False
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()
            print(f"Error en execute_query: {e}")
            return False

    def fetch_one(self, query, params=None):
        if not self._ensure_connected():
            return None
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.fetchone()
        except Exception as e:
            self.connection.rollback()
            print(f"Error en fetch_one: {e}")
            return None

    def fetch_all(self, query, params=None):
        if not self._ensure_connected():
            return []
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.fetchall()
        except Exception as e:
            self.connection.rollback()
            print(f"Error en fetch_all: {e}")
            return []

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()