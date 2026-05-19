# utils/tiempo.py
from datetime import datetime, timezone, timedelta

# Zona horaria de Guatemala (UTC-6)
ZONA_GUATEMALA = timezone(timedelta(hours=-6))

def ahora_local():
    """Retorna la hora actual con zona horaria de Guatemala (UTC-6)"""
    return datetime.now(ZONA_GUATEMALA)

def localizar_fecha(fecha_naive):
    """Convierte una fecha sin zona a la zona de Guatemala"""
    if fecha_naive.tzinfo is None:
        return fecha_naive.replace(tzinfo=ZONA_GUATEMALA)
    return fecha_naive.astimezone(ZONA_GUATEMALA)