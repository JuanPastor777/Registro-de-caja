import sys
import os

# 👇 SOLUCIÓN PARA RUTAS EN EJECUTABLES (.EXE)
# Detecta si el programa corre desde VS Code o ya compilado como ejecutable frozen por PyInstaller
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if base_dir not in sys.path:
    sys.path.append(base_dir)

try:
    from config.db_config import DatabaseConfig
except ImportError:
    # Intento de respaldo si la estructura de paquetes cambia al empaquetar
    try:
        from db_config import DatabaseConfig
    except ImportError:
        raise ImportError("No se pudo encontrar el módulo DatabaseConfig en el sistema.")

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    raise ImportError(
        "psycopg2 no está instalado.\n"
        "Ejecuta:  pip install psycopg2-binary"
    )


class DatabaseConnection:
    """Maneja la conexión con la base de datos PostgreSQL local"""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establece conexión y fija zona horaria de Guatemala"""
        try:
            params = DatabaseConfig.get_connection_params()
            self.connection = psycopg2.connect(**params)
            self.connection.autocommit = False

            # Fijar zona horaria a Guatemala
            with self.connection.cursor() as cur:
                cur.execute("SET TIME ZONE 'America/Guatemala'")

            # Se mantiene RealDictCursor para que el backend lea los campos como diccionarios
            self.cursor = self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            print("Conexión establecida localmente (zona: America/Guatemala).")
            return True
        except psycopg2.OperationalError as e:
            # 👇 TIP DE ORO: Si el .exe falla, creará este archivo de texto a la par para decirte exactamente por qué
            try:
                folder_log = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()
                ruta_log = os.path.join(folder_log, "error_conexion_log.txt")
                with open(ruta_log, "w", encoding="utf-8") as f:
                    f.write(f"--- ERROR DE CONEXIÓN EN TU BASE DE DATOS LOCAL ---\n\n")
                    f.write(f"Detalle técnico del fallo: {str(e)}\n\n")
                    f.write(
                        f"Parámetros intentados: Host: {params.get('host')}, Puerto: {params.get('port')}, Usuario: {params.get('user')}\n")
                    f.write(f"¿Verificaste que la contraseña en db_config.py coincida con la de DBeaver?\n")
            except Exception:
                pass

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
            if self.connection:
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
            if self.connection:
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
            if self.connection:
                self.connection.rollback()
            print(f"Error en fetch_all: {e}")
            return []

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()