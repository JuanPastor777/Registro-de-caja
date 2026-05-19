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

# --- MENU DE PRUEBAS ---
if __name__ == "__main__":
    try:
        db = DatabaseConnection()
        service = GastoService(db)

        while True:
            print("\n--- MÓDULO DE GASTOS ---")
            print("1. Listar gastos")
            print("2. Crear gasto")
            print("3. Buscar y editar")
            print("4. Eliminar")
            print("5. Salir")

            op = input("Seleccione: ")

            # LISTAR
            if op == "1":
                gastos = service.listar_gastos()
                for g in gastos:
                    print(f"ID: {g.id_gasto} | {g.tipo_gasto} | Q{g.monto} | {g.descripcion}")

            # CREAR
            elif op == "2":
                print("\nTipos disponibles:")
                print(f"1. {Gasto.TIPO_PROVEEDOR}")
                print(f"2. {Gasto.TIPO_SUELDOS}")
                print(f"3. {Gasto.TIPO_SERVICIOS}")
                print(f"4. {Gasto.TIPO_INSUMOS}")
                print(f"5. {Gasto.TIPO_DEVOLUCION}")

                tipo_op = input("Seleccione tipo: ")

                tipos = {
                    "1": Gasto.TIPO_PROVEEDOR,
                    "2": Gasto.TIPO_SUELDOS,
                    "3": Gasto.TIPO_SERVICIOS,
                    "4": Gasto.TIPO_INSUMOS,
                    "5": Gasto.TIPO_DEVOLUCION
                }

                tipo = tipos.get(tipo_op, "OTRO")

                id_mov = input("ID Movimiento FK: ")
                desc = input("Descripción: ")
                monto = float(input("Monto: "))

                service.crear_gasto(id_mov, tipo, desc, monto)
                print(" Gasto registrado.")

            # BUSCAR Y EDITAR
            elif op == "3":
                tipo = input("Tipo a buscar: ")
                encontrados = service.buscar_por_tipo(tipo)

                if encontrados:
                    print(f"\nResultados ({len(encontrados)}):")
                    for idx, g in enumerate(encontrados):
                        print(f"{idx + 1}. ID: {g.id_gasto} | {g.tipo_gasto} | Q{g.monto}")

                    sel = int(input("\nSeleccione número (0 cancelar): "))
                    if sel > 0:
                        g_ed = encontrados[sel - 1]

                        nueva_desc = input(f"Descripción [{g_ed.descripcion}]: ") or g_ed.descripcion
                        nuevo_monto = input(f"Monto [{g_ed.monto}]: ")
                        nuevo_monto = float(nuevo_monto) if nuevo_monto else g_ed.monto

                        service.actualizar_gasto(
                            g_ed.id_gasto,
                            g_ed.id_movimiento_fk,
                            g_ed.tipo_gasto,
                            nueva_desc,
                            nuevo_monto
                        )
                        print("Actualizado.")
                else:
                    print(" No encontrado.")

            # ELIMINAR
            elif op == "4":
                id_g = input("ID a eliminar: ")
                service.eliminar_gasto(id_g)
                print(" Eliminado.")

            elif op == "5":
                break

    except Exception as e:
        print(f" Error: {e}")