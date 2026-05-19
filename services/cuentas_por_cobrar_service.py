# cuentas_cobrar_service.py

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.conexion import DatabaseConnection

# =========================================================
# MODELO
# =========================================================
class CuentaPorCobrar:

    def __init__(
        self,
        id_cuenta=None,
        id_movimiento_fk=None,
        numero_documento="",
        monto=0,
        id_venta_fk=None,
        pagado=False
    ):

        self.id_cuenta = id_cuenta
        self.id_movimiento_fk = id_movimiento_fk
        self.numero_documento = numero_documento
        self.monto = monto
        self.id_venta_fk = id_venta_fk
        self.pagado = pagado

    @staticmethod
    def from_dict(row):

        return CuentaPorCobrar(
            id_cuenta=row['id_cuenta'],
            id_movimiento_fk=row['id_movimiento_fk'],
            numero_documento=row['numero_documento'],
            monto=row['monto'],
            id_venta_fk=row['id_venta_fk'],
            pagado=row['pagado']
        )


# =========================================================
# DAO
# =========================================================
class CuentaPorCobrarDAO:

    def __init__(self, db):
        self.db = db

    # -----------------------------------------------------
    def crear(self, cuenta):

        query = """
            INSERT INTO cuenta_por_cobrar
            (
                id_movimiento_fk,
                numero_documento,
                monto,
                id_venta_fk,
                pagado
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        return self.db.execute_query(
            query,
            (
                cuenta.id_movimiento_fk,
                cuenta.numero_documento,
                cuenta.monto,
                cuenta.id_venta_fk,
                cuenta.pagado
            )
        )

    # -----------------------------------------------------
    def listar_pendientes(self):

        query = """
            SELECT *
            FROM cuenta_por_cobrar
            WHERE pagado = FALSE
            ORDER BY id_cuenta ASC
        """

        rows = self.db.fetch_all(query)

        return [
            CuentaPorCobrar.from_dict(r)
            for r in rows
        ]

    # -----------------------------------------------------
    def actualizar_estado(self, id_cuenta, pagado):

        query = """
            UPDATE cuenta_por_cobrar
            SET pagado = %s
            WHERE id_cuenta = %s
        """

        return self.db.execute_query(
            query,
            (
                pagado,
                id_cuenta
            )
        )

    # -----------------------------------------------------
    def buscar_por_guia_empresa(self, numero_guia, empresa):

        query = """
            SELECT
                cpc.id_cuenta,
                cpc.numero_documento,
                cpc.monto,
                cpc.pagado,
                v.numero_guia,
                ee.nombre AS empresa
            FROM cuenta_por_cobrar cpc

            INNER JOIN venta v
                ON cpc.id_venta_fk = v.id_venta

            INNER JOIN empresa_envio ee
                ON v.id_empresa_fk = ee.id_empresa

            WHERE
                v.numero_guia ILIKE %s
                AND ee.nombre ILIKE %s

            ORDER BY cpc.id_cuenta ASC
        """

        return self.db.fetch_all(
            query,
            (
                f"%{numero_guia}%",
                f"%{empresa}%"
            )
        )

    # -----------------------------------------------------
    def obtener_por_id(self, id_cuenta):

        query = """
            SELECT *
            FROM cuenta_por_cobrar
            WHERE id_cuenta = %s
        """

        return self.db.fetch_one(query, (id_cuenta,))


# =========================================================
# SERVICE
# =========================================================
class CuentaPorCobrarService:

    def __init__(self):

        self.db = DatabaseConnection()
        self.dao = CuentaPorCobrarDAO(self.db)

    # -----------------------------------------------------
    def registrar_cuenta(
        self,
        id_caja_fk,
        id_usuario_fk,
        numero_documento,
        monto,
        id_venta_fk
    ):

        # ==========================================
        # CREAR MOVIMIENTO EN CAJA
        # ==========================================
        movimiento = self.db.fetch_one(
            """
            INSERT INTO movimiento_caja
            (
                id_caja_fk,
                tipo_movimiento,
                descripcion,
                monto,
                fecha_hora,
                id_usuario_fk
            )
            VALUES
            (
                %s,
                'CUENTA_POR_COBRAR',
                'Registro de cuenta pendiente',
                %s,
                NOW(),
                %s
            )
            RETURNING id_movimiento
            """,
            (
                id_caja_fk,
                monto,
                id_usuario_fk
            )
        )

        if not movimiento:
            print("❌ Error al crear movimiento")
            return False

        # ==========================================
        # CREAR CUENTA POR COBRAR
        # ==========================================
        nueva = CuentaPorCobrar(
            id_movimiento_fk=movimiento['id_movimiento'],
            numero_documento=numero_documento,
            monto=monto,
            id_venta_fk=id_venta_fk,
            pagado=False
        )

        self.dao.crear(nueva)

        print("✅ Cuenta por cobrar registrada")

        return True

    # -----------------------------------------------------
    def listar_pendientes(self):

        return self.dao.listar_pendientes()

    # -----------------------------------------------------
    def editar_estado(self, id_cuenta, pagado):

        return self.dao.actualizar_estado(
            id_cuenta,
            pagado
        )

    # -----------------------------------------------------
    def buscar_por_guia_empresa(
        self,
        numero_guia,
        empresa
    ):

        return self.dao.buscar_por_guia_empresa(
            numero_guia,
            empresa
        )

    # -----------------------------------------------------
    def registrar_pago_en_caja(
        self,
        id_cuenta,
        id_caja_fk,
        id_usuario_fk
    ):

        # ==========================================
        # OBTENER CUENTA
        # ==========================================
        cuenta = self.dao.obtener_por_id(id_cuenta)

        if not cuenta:
            print("❌ Cuenta no encontrada")
            return False

        if cuenta['pagado']:
            print("⚠️ Esta cuenta ya está pagada")
            return False

        # ==========================================
        # REGISTRAR INGRESO EN CAJA
        # ==========================================
        movimiento = self.db.fetch_one(
            """
            INSERT INTO movimiento_caja
            (
                id_caja_fk,
                tipo_movimiento,
                descripcion,
                monto,
                fecha_hora,
                id_usuario_fk
            )
            VALUES
            (
                %s,
                'INGRESO',
                'Pago de cuenta por cobrar',
                %s,
                NOW(),
                %s
            )
            RETURNING id_movimiento
            """,
            (
                id_caja_fk,
                cuenta['monto'],
                id_usuario_fk
            )
        )

        if not movimiento:
            print("❌ Error al registrar ingreso")
            return False

        # ==========================================
        # MARCAR COMO PAGADO
        # ==========================================
        self.dao.actualizar_estado(
            id_cuenta,
            True
        )

        print("✅ Pago registrado en caja")

        return True


# =========================================================
# MENÚ DE PRUEBA
# =========================================================
if __name__ == "__main__":

    service = CuentaPorCobrarService()

    while True:

        print("\n========== CUENTAS POR COBRAR ==========")
        print("1. Registrar cuenta")
        print("2. Ver pendientes")
        print("3. Editar estado")
        print("4. Buscar por guía y empresa")
        print("5. Registrar pago en caja")
        print("6. Salir")

        op = input("Seleccione opción: ")

        # =================================================
        if op == "1":

            id_caja = input("ID caja: ")
            id_usuario = input("ID usuario: ")
            num_doc = input("Número documento: ")
            monto = input("Monto: ")
            id_venta = input("ID venta: ")

            service.registrar_cuenta(
                id_caja,
                id_usuario,
                num_doc,
                monto,
                id_venta
            )

        # =================================================
        elif op == "2":

            pendientes = service.listar_pendientes()

            if pendientes:

                for p in pendientes:

                    print(f"""
----------------------------------
ID CUENTA: {p.id_cuenta}
DOCUMENTO: {p.numero_documento}
MONTO: Q{p.monto}
PAGADO: {'Sí' if p.pagado else 'No'}
----------------------------------
                    """)

            else:
                print("⚠️ No hay cuentas pendientes")

        # =================================================
        elif op == "3":

            id_cuenta = input("ID cuenta: ")

            estado = input("¿Está pagada? (s/n): ").lower()

            pagado = True if estado == 's' else False

            service.editar_estado(
                id_cuenta,
                pagado
            )

            print("✅ Estado actualizado")

        # =================================================
        elif op == "4":

            guia = input("Número guía: ")
            empresa = input("Empresa: ")

            resultados = service.buscar_por_guia_empresa(
                guia,
                empresa
            )

            if resultados:

                for r in resultados:

                    print(f"""
----------------------------------
ID CUENTA: {r['id_cuenta']}
DOCUMENTO: {r['numero_documento']}
EMPRESA: {r['empresa']}
GUÍA: {r['numero_guia']}
MONTO: Q{r['monto']}
PAGADO: {'Sí' if r['pagado'] else 'No'}
----------------------------------
                    """)

            else:
                print("⚠️ No se encontraron resultados")

        # =================================================
        elif op == "5":

            id_cuenta = input("ID cuenta pagada: ")
            id_caja = input("ID caja: ")
            id_usuario = input("ID usuario: ")

            service.registrar_pago_en_caja(
                id_cuenta,
                id_caja,
                id_usuario
            )

        # =================================================
        elif op == "6":

            print("👋 Saliendo...")
            break

        # =================================================
        else:

            print("❌ Opción inválida")