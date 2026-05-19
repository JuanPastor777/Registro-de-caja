

class DatabaseConfig:
    """Configuracion de la base de datos Supabase"""

    DB_CONFIG = {
        'host': 'db.tlrershlxqyelcxcqgjc.supabase.co',
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Techshopgt4321.'
    }

    @staticmethod
    def get_connection_params():

        params = DatabaseConfig.DB_CONFIG.copy()
        params['sslmode'] = 'require'
        return params

    @staticmethod
    def get_connection_string():
        c = DatabaseConfig.DB_CONFIG
        return (
            f"host={c['host']} port={c['port']} "
            f"dbname={c['database']} user={c['user']} "
            f"password={c['password']} sslmode=require"
        )