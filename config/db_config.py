class DatabaseConfig:
    """Configuración de la base de datos LOCAL (DBeaver)"""

    DB_CONFIG = {
        'host': '127.0.0.1',              # Apunta a tu propia computadora (localhost)
        'port': 5432,                     # Puerto estándar de tu PostgreSQL
        'database': 'postgres',           # Nombre de tu base de datos local
        'user': 'postgres',               # Usuario predeterminado
        'password': '1313'  # 👈 REEMPLAZA ESTO CON TU CONTRASEÑA DE DBEAVER
    }

    @staticmethod
    def get_connection_params():
        params = DatabaseConfig.DB_CONFIG.copy()
        # Al ser local, desactivamos SSL para evitar conflictos con el ejecutable y acelerar la conexión
        params['sslmode'] = 'disable'
        return params

    @staticmethod
    def get_connection_string():
        c = DatabaseConfig.DB_CONFIG
        return (
            f"host={c['host']} port={c['port']} "
            f"dbname={c['database']} user={c['user']} "
            f"password={c['password']} sslmode=disable"
        )