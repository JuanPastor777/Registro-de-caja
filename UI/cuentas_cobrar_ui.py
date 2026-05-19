# ventana_cuentas_por_cobrar.py

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QLineEdit
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# =========================================================
# CONEXIÓN Y SERVICE
# =========================================================
from database.conexion import DatabaseConnection
from services.cuentas_por_cobrar_service import CuentaPorCobrarService


# =========================================================
# VENTANA PRINCIPAL
# =========================================================
class VentanaCuentasPorCobrar(QWidget):

    def __init__(self, id_caja_actual=None, id_usuario_actual=None):

        super().__init__()

        self.db = DatabaseConnection()

        self.service = CuentaPorCobrarService()

        self.id_caja_actual = id_caja_actual
        self.id_usuario_actual = id_usuario_actual

        self.init_ui()

        self.cargar_cuentas()

    # =====================================================
    # INTERFAZ
    # =====================================================
    def init_ui(self):

        self.setWindowTitle("Cuentas Por Cobrar")

        layout = QVBoxLayout()

        layout.setSpacing(20)

        # =================================================
        # HEADER
        # =================================================
        header = QHBoxLayout()

        title = QLabel("Cuentas Por Cobrar")

        title.setFont(QFont("Segoe UI", 18, QFont.Bold))

        header.addWidget(title)

        header.addStretch()

        refresh_btn = QPushButton("Actualizar")

        refresh_btn.setCursor(Qt.PointingHandCursor)

        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5C800;
                border: none;
                border-radius: 10px;
                padding: 10px 18px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #E6BB00;
            }
        """)

        refresh_btn.clicked.connect(self.cargar_cuentas)

        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # =================================================
        # BÚSQUEDAS
        # =================================================
        search_layout = QHBoxLayout()

        self.input_guia = QLineEdit()

        self.input_guia.setPlaceholderText("Buscar por guía...")

        self.input_guia.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #E5E7EB;
                background-color: white;
            }
        """)

        search_layout.addWidget(self.input_guia)

        self.input_empresa = QLineEdit()

        self.input_empresa.setPlaceholderText("Buscar por empresa...")

        self.input_empresa.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #E5E7EB;
                background-color: white;
            }
        """)

        search_layout.addWidget(self.input_empresa)

        buscar_btn = QPushButton("Buscar")

        buscar_btn.setCursor(Qt.PointingHandCursor)

        buscar_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5C800;
                border: none;
                border-radius: 10px;
                padding: 10px 18px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #E6BB00;
            }
        """)

        buscar_btn.clicked.connect(self.buscar_cuentas)

        search_layout.addWidget(buscar_btn)

        layout.addLayout(search_layout)

        # =================================================
        # TABLA
        # =================================================
        self.table = QTableWidget()

        self.table.setColumnCount(7)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Documento",
            "Guía",
            "Empresa",
            "Monto",
            "Estado",
            "Acciones"
        ])

        # =================================================
        # OCULTAR NUMERACIÓN LATERAL
        # =================================================
        self.table.verticalHeader().setVisible(False)

        # =================================================
        # HEADER TABLA
        # =================================================
        header = self.table.horizontalHeader()

        header.setSectionResizeMode(QHeaderView.Stretch)

        # =================================================
        # MÁS ESPACIO EN ACCIONES
        # =================================================
        header.setSectionResizeMode(
            6,
            QHeaderView.ResizeToContents
        )

        # =================================================
        # ALTURA FILAS
        # =================================================
        self.table.verticalHeader().setDefaultSectionSize(60)

        # =================================================
        # CONFIGURACIONES TABLA
        # =================================================
        self.table.setAlternatingRowColors(True)

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.table.setShowGrid(True)

        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E7EB;
                border-radius: 14px;
                background-color: white;
                gridline-color: #E5E7EB;
                font-size: 13px;
            }

            QHeaderView::section {
                background-color: #F9FAFB;
                padding: 14px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #E5E7EB;
            }

            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F3F4F6;
            }

            QTableWidget::item:selected {
                background-color: #FEF3C7;
                color: black;
            }
        """)

        layout.addWidget(self.table)

        self.setLayout(layout)

    # =====================================================
    # CARGAR CUENTAS
    # =====================================================
    def cargar_cuentas(self):

        cuentas = self.service.listar_pendientes()

        self.table.setRowCount(len(cuentas))

        for row, cuenta in enumerate(cuentas):

            # =============================================
            # ID
            # =============================================
            self.table.setItem(
                row,
                0,
                QTableWidgetItem(str(cuenta.id_cuenta))
            )

            # =============================================
            # DOCUMENTO
            # =============================================
            self.table.setItem(
                row,
                1,
                QTableWidgetItem(cuenta.numero_documento)
            )

            # =============================================
            # OBTENER DATOS VENTA
            # =============================================
            venta = self.db.fetch_one(
                """
                SELECT
                    v.numero_guia,
                    ee.nombre AS empresa
                FROM venta v

                LEFT JOIN empresa_envio ee
                    ON v.id_empresa_fk = ee.id_empresa

                WHERE v.id_venta = %s
                """,
                (cuenta.id_venta_fk,)
            )

            guia = ""
            empresa = ""

            if venta:

                guia = venta['numero_guia'] or ""
                empresa = venta['empresa'] or ""

            # =============================================
            # GUÍA
            # =============================================
            self.table.setItem(
                row,
                2,
                QTableWidgetItem(guia)
            )

            # =============================================
            # EMPRESA
            # =============================================
            self.table.setItem(
                row,
                3,
                QTableWidgetItem(empresa)
            )

            # =============================================
            # MONTO
            # =============================================
            self.table.setItem(
                row,
                4,
                QTableWidgetItem(f"Q{cuenta.monto}")
            )

            # =============================================
            # ESTADO
            # =============================================
            estado_label = QLabel()

            if cuenta.pagado:

                estado_label.setText("PAGADO")

                estado_label.setStyleSheet("""
                    color: #10B981;
                    font-weight: bold;
                """)

            else:

                estado_label.setText("PENDIENTE")

                estado_label.setStyleSheet("""
                    color: #EF4444;
                    font-weight: bold;
                """)

            estado_label.setAlignment(Qt.AlignCenter)

            self.table.setCellWidget(
                row,
                5,
                estado_label
            )

            # =============================================
            # ACCIONES
            # =============================================
            contenedor_acciones = QWidget()

            contenedor_acciones.setStyleSheet("""
                background-color: transparent;
            """)

            acciones_layout = QHBoxLayout()

            acciones_layout.setContentsMargins(
                10,
                8,
                10,
                8
            )

            acciones_layout.setSpacing(8)

            acciones_layout.setAlignment(Qt.AlignCenter)

            # =============================================
            # BOTÓN PAGAR
            # =============================================
            pagar_btn = QPushButton("💰 Pagar")

            pagar_btn.setCursor(Qt.PointingHandCursor)

            pagar_btn.setMinimumWidth(120)

            pagar_btn.setMinimumHeight(36)

            pagar_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F5C800;
                    color: black;
                    border: none;
                    border-radius: 10px;
                    padding: 8px 14px;
                    font-weight: bold;
                    font-size: 12px;
                }

                QPushButton:hover {
                    background-color: #E6BB00;
                }

                QPushButton:pressed {
                    background-color: #D4AA00;
                }
            """)

            pagar_btn.clicked.connect(
                lambda checked, c=cuenta:
                self.registrar_pago(c)
            )

            acciones_layout.addWidget(pagar_btn)

            contenedor_acciones.setLayout(
                acciones_layout
            )

            self.table.setCellWidget(
                row,
                6,
                contenedor_acciones
            )

    # =====================================================
    # BUSCAR
    # =====================================================
    def buscar_cuentas(self):

        guia = self.input_guia.text()

        empresa = self.input_empresa.text()

        resultados = self.service.buscar_por_guia_empresa(
            guia,
            empresa
        )

        self.table.setRowCount(len(resultados))

        for row, cuenta in enumerate(resultados):

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(str(cuenta['id_cuenta']))
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(cuenta['numero_documento'])
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(cuenta['numero_guia'] or "")
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(cuenta['empresa'] or "")
            )

            self.table.setItem(
                row,
                4,
                QTableWidgetItem(f"Q{cuenta['monto']}")
            )

            # =============================================
            # ESTADO
            # =============================================
            estado_label = QLabel()

            if cuenta['pagado']:

                estado_label.setText("PAGADO")

                estado_label.setStyleSheet("""
                    color: #10B981;
                    font-weight: bold;
                """)

            else:

                estado_label.setText("PENDIENTE")

                estado_label.setStyleSheet("""
                    color: #EF4444;
                    font-weight: bold;
                """)

            estado_label.setAlignment(Qt.AlignCenter)

            self.table.setCellWidget(
                row,
                5,
                estado_label
            )

            # =============================================
            # ACCIONES
            # =============================================
            contenedor_acciones = QWidget()

            contenedor_acciones.setStyleSheet("""
                background-color: transparent;
            """)

            acciones_layout = QHBoxLayout()

            acciones_layout.setContentsMargins(
                10,
                8,
                10,
                8
            )

            acciones_layout.setSpacing(8)

            acciones_layout.setAlignment(Qt.AlignCenter)

            if not cuenta['pagado']:

                # =========================================
                # BOTÓN PAGAR
                # =========================================
                pagar_btn = QPushButton("💰 Pagar")

                pagar_btn.setCursor(Qt.PointingHandCursor)

                pagar_btn.setMinimumWidth(120)

                pagar_btn.setMinimumHeight(36)

                pagar_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #F5C800;
                        color: black;
                        border: none;
                        border-radius: 10px;
                        padding: 8px 14px;
                        font-weight: bold;
                        font-size: 12px;
                    }

                    QPushButton:hover {
                        background-color: #E6BB00;
                    }

                    QPushButton:pressed {
                        background-color: #D4AA00;
                    }
                """)

                pagar_btn.clicked.connect(
                    lambda checked,
                    id_cuenta=cuenta['id_cuenta']:
                    self.registrar_pago_por_id(id_cuenta)
                )

                acciones_layout.addWidget(pagar_btn)

            contenedor_acciones.setLayout(
                acciones_layout
            )

            self.table.setCellWidget(
                row,
                6,
                contenedor_acciones
            )

    # =====================================================
    # REGISTRAR PAGO
    # =====================================================
    def registrar_pago(self, cuenta):

        if not self.id_caja_actual:

            QMessageBox.warning(
                self,
                "Error",
                "Debe abrir caja primero"
            )

            return

        confirmacion = QMessageBox.question(
            self,
            "Confirmar Pago",
            f"""
¿Registrar pago de la cuenta?

Documento:
{cuenta.numero_documento}

Monto:
Q{cuenta.monto}
            """,
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmacion == QMessageBox.Yes:

            resultado = self.service.registrar_pago_en_caja(
                cuenta.id_cuenta,
                self.id_caja_actual,
                self.id_usuario_actual
            )

            if resultado:

                QMessageBox.information(
                    self,
                    "Éxito",
                    "Pago registrado correctamente"
                )

                self.cargar_cuentas()

            else:

                QMessageBox.critical(
                    self,
                    "Error",
                    "No se pudo registrar el pago"
                )

    # =====================================================
    # REGISTRAR PAGO POR ID
    # =====================================================
    def registrar_pago_por_id(self, id_cuenta):

        if not self.id_caja_actual:

            QMessageBox.warning(
                self,
                "Error",
                "Debe abrir caja primero"
            )

            return

        resultado = self.service.registrar_pago_en_caja(
            id_cuenta,
            self.id_caja_actual,
            self.id_usuario_actual
        )

        if resultado:

            QMessageBox.information(
                self,
                "Éxito",
                "Pago registrado correctamente"
            )

            self.buscar_cuentas()

        else:

            QMessageBox.critical(
                self,
                "Error",
                "No se pudo registrar el pago"
            )


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":

    app = QApplication(sys.argv)

    # IDs de prueba
    id_caja_actual = 1
    id_usuario_actual = 1

    ventana = VentanaCuentasPorCobrar(
        id_caja_actual=id_caja_actual,
        id_usuario_actual=id_usuario_actual
    )

    ventana.resize(1250, 650)

    ventana.show()

    sys.exit(app.exec_())