import sys
import os
from datetime import datetime

# Configuración de rutas para que reconozca los modelos y la base de datos
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_raiz)

from models.apertura_cierre import AperturaCierre
from database.conexion import DatabaseConnection
from Utils.tiempo import ahora_local

class CajaService:
    def __init__(self, db_connection):
        self.db = db_connection

    def conteo_dinero_inicial(self):
        """Suma las denominaciones de Quetzales para la apertura."""
        print("\n--- DESGLOSE PARA APERTURA (Q) ---")
        billetes = [1,5,10,20,50,100,200]
        total = 0
        for b in billetes:
            try:
                cantidad = int(input(f"Cantidad de billetes de Q{b}: ") or 0)
                total += (b * cantidad)
            except ValueError:
                print("❌ Por favor ingresa solo números.")
        return total

    def abrir_caja(self, id_caja, id_usuario):
        monto_ini = self.conteo_dinero_inicial()
        query = """
            INSERT INTO public.apertura_cierre 
            (id_caja_fk, id_usuario_fk, fecha_hora_apertura, monto_inicial, monto_final)
            VALUES (%s, %s, %s, %s, %s) RETURNING id_apertura
        """
        ahora = ahora_local()
        params = (id_caja, id_usuario, ahora, monto_ini, monto_ini)
        res = self.db.fetch_one(query, params)
        if res:
            print(f"✅ Caja abierta con ID: {res['id_apertura']} | Monto: Q{monto_ini}")
            return res['id_apertura']
        return None

    def registrar_transaccion(self, id_apertura, monto, tipo="INGRESO"):
        """Suma o resta al monto_final actual de la tabla."""
        ajuste = monto if tipo == "INGRESO" else -monto
        
        query = """
            UPDATE public.apertura_cierre 
            SET monto_final = monto_final + %s
            WHERE id_apertura = %s
            RETURNING monto_final
        """
        res = self.db.fetch_one(query, (ajuste, id_apertura))
        if res:
            print(f"💰 Movimiento: {tipo} de Q{monto}. Saldo actual: Q{res['monto_final']}")
        return res

    def cerrar_caja_definitivo(self, id_apertura):
        fecha_cierre = ahora_local()

        query = """
            UPDATE public.apertura_cierre
            SET fecha_hora_cierre = %s
            WHERE id_apertura = %s
        """

        resultado = self.db.execute_query(
            query,
            (fecha_cierre, id_apertura)
        )

        if resultado:
            print(f"🔒 Turno cerrado exitosamente a las {fecha_cierre.strftime('%H:%M:%S')}")
        else:
            print("❌ No se pudo cerrar el turno")
# --- PRUEBA INTERACTIVA ---
if __name__ == "__main__":
    try:
        db = DatabaseConnection()
        caja = CajaService(db)
        
        print("\n--- PRUEBA DE CAJA ---")
        # Ejemplo con los datos de tu tabla (Caja 3, Usuario 2)
        id_ap = caja.abrir_caja(id_caja=3, id_usuario=2)
        
        if id_ap:
            print("\nIngrese un valor para simular un ingreso...")
            monto = float(input("Monto: Q"))
            caja.registrar_transaccion(id_ap, monto, "INGRESO")
            
            print("\n Ingrese un valor para simular un egreso...")
            monto = float(input("Monto: Q"))
            caja.registrar_transaccion(id_ap, monto, "EGRESO")
            
            input("\nPresiona Enter para CERRAR LA CAJA...")
            caja.cerrar_caja_definitivo(id_ap)
            
    except Exception as e:
        print(f"❌ Error: {e}")