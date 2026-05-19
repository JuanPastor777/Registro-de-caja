import sys
import os
from datetime import date

# --- SOLUCIÓN AL ERROR DE IMPORTACIÓN ---
# Esto agrega la carpeta raíz a la ruta de búsqueda de Python
ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_raiz not in sys.path:
    sys.path.append(ruta_raiz)
    # También agregamos models específicamente por si acaso
    sys.path.append(os.path.join(ruta_raiz, "models"))

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QMessageBox,
    QApplication,
    QHBoxLayout
)

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator, QFont

# Ahora las importaciones deberían funcionar
from database.conexion import DatabaseConnection
from models.dao import AperturaCierreDAO, CajaDAO


class VentanaAperturaCierre(QWidget):

    caja_actualizada = pyqtSignal()

    def __init__(self, usuario_id, modo="APERTURA"):
        super().__init__()

        self.db = DatabaseConnection()

        self.usuario_id = usuario_id
        self.modo = modo

        self.denominaciones = [200, 100, 50, 20, 10, 5, 1]

        self.inputs = {}
        self.labels_monto = {}

        self.ap_dao = AperturaCierreDAO(self.db)
        self.caja_dao = CajaDAO(self.db)

        self.init_ui()

    def init_ui(self):

        self.setWindowTitle(f"Control de Caja - {self.modo}")
        self.setFixedWidth(450)

        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)

        layout_principal = QVBoxLayout(self)

        # ─────────────────────────────────────────────
        # TÍTULO
        # ─────────────────────────────────────────────
        lbl_titulo = QLabel(f"REGISTRO DE {self.modo}")

        lbl_titulo.setFont(QFont("Arial", 14, QFont.Bold))
        lbl_titulo.setAlignment(Qt.AlignCenter)

        layout_principal.addWidget(lbl_titulo)

        # ─────────────────────────────────────────────
        # GRUPO EFECTIVO
        # ─────────────────────────────────────────────
        grupo_efectivo = QGroupBox("Desglose de Efectivo")

        grid = QGridLayout()

        # SOLO NÚMEROS
        validador = QIntValidator(0, 9999)

        for i, den in enumerate(self.denominaciones):

            # DENOMINACIÓN
            grid.addWidget(QLabel(f"Q {den}.00"), i, 0)

            # CONTROLES
            layout_cant = QHBoxLayout()

            # BOTÓN MENOS
            btn_menos = QPushButton("-")

            btn_menos.setFixedSize(30, 30)

            btn_menos.setStyleSheet("""
                background-color: #f3f4f6;
                border: 1px solid #d1d5db;
            """)

            btn_menos.clicked.connect(
                lambda ch, d=den: self.ajustar_cantidad(d, -1)
            )

            # INPUT
            edit = QLineEdit("0")

            edit.setFixedWidth(60)
            edit.setAlignment(Qt.AlignCenter)

            edit.setValidator(validador)

            edit.textChanged.connect(self.recalcular)

            self.inputs[den] = edit

            # BOTÓN MÁS
            btn_mas = QPushButton("+")

            btn_mas.setFixedSize(30, 30)

            btn_mas.setStyleSheet("""
                background-color: #f3f4f6;
                border: 1px solid #d1d5db;
            """)

            btn_mas.clicked.connect(
                lambda ch, d=den: self.ajustar_cantidad(d, 1)
            )

            # AGREGAR CONTROLES
            layout_cant.addWidget(btn_menos)
            layout_cant.addWidget(edit)
            layout_cant.addWidget(btn_mas)

            grid.addLayout(layout_cant, i, 1)

            # SUBTOTAL
            lbl_sub = QLabel("Q 0.00")

            lbl_sub.setAlignment(Qt.AlignRight)

            grid.addWidget(lbl_sub, i, 2)

            self.labels_monto[den] = lbl_sub

        grupo_efectivo.setLayout(grid)

        layout_principal.addWidget(grupo_efectivo)

        # ─────────────────────────────────────────────
        # TOTAL
        # ─────────────────────────────────────────────
        self.lbl_total = QLabel("TOTAL: Q 0.00")

        self.lbl_total.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #dc2626;
            margin: 10px;
        """)

        self.lbl_total.setAlignment(Qt.AlignCenter)

        layout_principal.addWidget(self.lbl_total)

        # ─────────────────────────────────────────────
        # BOTÓN GUARDAR
        # ─────────────────────────────────────────────
        self.btn_guardar = QPushButton(f"CONFIRMAR {self.modo}")

        color = "#10b981" if self.modo == "APERTURA" else "#ef4444"

        self.btn_guardar.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 12px;
                font-weight: bold;
                border-radius: 5px;
            }}

            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)

        self.btn_guardar.clicked.connect(self.guardar_en_db)

        layout_principal.addWidget(self.btn_guardar)

    # ─────────────────────────────────────────────
    # AJUSTAR CANTIDAD
    # ─────────────────────────────────────────────
    def ajustar_cantidad(self, den, cambio):

        try:
            actual = int(self.inputs[den].text() or 0)

            nuevo = max(0, actual + cambio)

            self.inputs[den].setText(str(nuevo))

        except:
            self.inputs[den].setText("0")

    # ─────────────────────────────────────────────
    # RECALCULAR TOTAL
    # ─────────────────────────────────────────────
    def recalcular(self):

        total = 0.0

        for den, edit in self.inputs.items():

            try:
                cantidad = int(edit.text() or 0)

                subtotal = den * cantidad

                total += subtotal

                self.labels_monto[den].setText(
                    f"Q {subtotal:,.2f}"
                )

            except:
                pass

        self.lbl_total.setText(f"TOTAL: Q {total:,.2f}")

        return total

    # ─────────────────────────────────────────────
    # GUARDAR EN BASE DE DATOS
    # ─────────────────────────────────────────────
    def guardar_en_db(self):

        monto = self.recalcular()

        try:

            # ─────────────────────────────
            # APERTURA
            # ─────────────────────────────
            if self.modo == "APERTURA":

                # VALIDAR SI YA EXISTE UNA CAJA ABIERTA
                caja_abierta = self.db.fetch_one("""
                    SELECT id_apertura
                    FROM apertura_cierre
                    WHERE fecha_hora_cierre IS NULL
                    LIMIT 1
                """)

                if caja_abierta:

                    QMessageBox.warning(
                        self,
                        "Caja abierta",
                        "Ya existe una caja abierta. Debe cerrarla antes de abrir otra."
                    )

                    return

                # OBTENER O CREAR CAJA DEL DÍA
                caja = self.caja_dao.obtener_por_fecha(date.today())

                id_caja = (
                    caja.id_caja
                    if caja
                    else self.caja_dao.crear(date.today())
                )

                # ABRIR CAJA
                if self.ap_dao.abrir(
                    id_caja,
                    self.usuario_id,
                    monto
                ):

                    QMessageBox.information(
                        self,
                        "Éxito",
                        f"Caja abierta con Q{monto:,.2f}"
                    )

                    self.caja_actualizada.emit()

                    self.close()

            # ─────────────────────────────
            # CIERRE
            # ─────────────────────────────
            else:

                activa = self.ap_dao.obtener_activa_por_usuario(
                    self.usuario_id
                )

                if not activa:

                    QMessageBox.warning(
                        self,
                        "Caja",
                        "No existe una caja abierta para cerrar."
                    )

                    return

                if self.ap_dao.cerrar(
                    activa.id_apertura,
                    monto
                ):

                    QMessageBox.information(
                        self,
                        "Éxito",
                        "Caja cerrada correctamente"
                    )

                    self.caja_actualizada.emit()

                    self.close()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar: {e}"
            )


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Usuario de prueba
    ventana = VentanaAperturaCierre(
        usuario_id=2,
        modo="APERTURA"
    )

    ventana.show()

    sys.exit(app.exec_())