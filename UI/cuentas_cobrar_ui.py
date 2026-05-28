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
    QLineEdit,
    QScrollArea,          # ← AGREGADO para responsividad
    QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.conexion import DatabaseConnection
from services.cuentas_por_cobrar_service import CuentaPorCobrarService


class VentanaCuentasPorCobrar(QWidget):
    def __init__(self, id_caja_actual=None, id_usuario_actual=None):
        super().__init__()
        self.db = DatabaseConnection()
        self.service = CuentaPorCobrarService()
        self.id_caja_actual = id_caja_actual
        self.id_usuario_actual = id_usuario_actual
        self.init_ui()
        self.cargar_cuentas()

    def init_ui(self):
        self.setWindowTitle("Cuentas Por Cobrar")
        self.setMinimumSize(900, 500)   # Para que se vea bien en 1366x768

        # Scroll principal para toda la ventana
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # ===== HEADER =====
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
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #E6BB00; }
        """)
        refresh_btn.clicked.connect(self.cargar_cuentas)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # ===== BÚSQUEDA =====
        search_layout = QHBoxLayout()
        self.input_guia = QLineEdit()
        self.input_guia.setPlaceholderText("Buscar por guía...")
        self.input_guia.setStyleSheet("padding: 8px; border-radius: 8px; border: 1px solid #E5E7EB;")
        search_layout.addWidget(self.input_guia)

        self.input_empresa = QLineEdit()
        self.input_empresa.setPlaceholderText("Buscar por empresa...")
        self.input_empresa.setStyleSheet("padding: 8px; border-radius: 8px; border: 1px solid #E5E7EB;")
        search_layout.addWidget(self.input_empresa)

        buscar_btn = QPushButton("Buscar")
        buscar_btn.setCursor(Qt.PointingHandCursor)
        buscar_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5C800;
                border: none;
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #E6BB00; }
        """)
        buscar_btn.clicked.connect(self.buscar_cuentas)
        search_layout.addWidget(buscar_btn)
        layout.addLayout(search_layout)

        # ===== TABLA =====
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Documento", "Guía", "Empresa", "Monto", "Estado", "Acciones"])
        self.table.verticalHeader().setVisible(False)
        header_tabla = self.table.horizontalHeader()
        header_tabla.setSectionResizeMode(QHeaderView.Stretch)
        header_tabla.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(55)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
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
                padding: 12px;
                font-weight: bold;
                border-bottom: 1px solid #E5E7EB;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #FEF3C7;
                color: black;
            }
        """)
        layout.addWidget(self.table)

        main_scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_scroll)

    # ==== MÉTODOS DE CARGA Y BÚSQUEDA (sin cambios) ====
    def cargar_cuentas(self):
        cuentas = self.service.listar_pendientes()
        self.table.setRowCount(len(cuentas))
        for row, cuenta in enumerate(cuentas):
            self._cargar_fila(row, cuenta)

    def buscar_cuentas(self):
        guia = self.input_guia.text()
        empresa = self.input_empresa.text()
        resultados = self.service.buscar_por_guia_empresa(guia, empresa)
        self.table.setRowCount(len(resultados))
        for row, cuenta in enumerate(resultados):
            self._cargar_fila_desde_dict(row, cuenta)

    def _cargar_fila(self, row, cuenta):
        self.table.setItem(row, 0, QTableWidgetItem(str(cuenta.id_cuenta)))
        self.table.setItem(row, 1, QTableWidgetItem(cuenta.numero_documento))
        venta = self.db.fetch_one("""
            SELECT v.numero_guia, ee.nombre AS empresa
            FROM venta v
            LEFT JOIN empresa_envio ee ON v.id_empresa_fk = ee.id_empresa
            WHERE v.id_venta = %s
        """, (cuenta.id_venta_fk,))
        guia = venta['numero_guia'] if venta else ""
        empresa = venta['empresa'] if venta else ""
        self.table.setItem(row, 2, QTableWidgetItem(guia or ""))
        self.table.setItem(row, 3, QTableWidgetItem(empresa or ""))
        self.table.setItem(row, 4, QTableWidgetItem(f"Q{cuenta.monto}"))

        estado_label = QLabel("PAGADO" if cuenta.pagado else "PENDIENTE")
        estado_label.setStyleSheet("color: #10B981; font-weight: bold;" if cuenta.pagado else "color: #EF4444; font-weight: bold;")
        estado_label.setAlignment(Qt.AlignCenter)
        self.table.setCellWidget(row, 5, estado_label)

        contenedor = QWidget()
        acciones_layout = QHBoxLayout(contenedor)
        acciones_layout.setContentsMargins(8, 4, 8, 4)
        acciones_layout.setAlignment(Qt.AlignCenter)
        if not cuenta.pagado:
            pagar_btn = QPushButton("💰 Pagar")
            pagar_btn.setCursor(Qt.PointingHandCursor)
            pagar_btn.setMinimumSize(100, 32)
            pagar_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F5C800;
                    border-radius: 8px;
                    padding: 5px 12px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #E6BB00; }
            """)
            pagar_btn.clicked.connect(lambda _, c=cuenta: self.registrar_pago(c))
            acciones_layout.addWidget(pagar_btn)
        self.table.setCellWidget(row, 6, contenedor)

    def _cargar_fila_desde_dict(self, row, cuenta):
        self.table.setItem(row, 0, QTableWidgetItem(str(cuenta['id_cuenta'])))
        self.table.setItem(row, 1, QTableWidgetItem(cuenta['numero_documento']))
        self.table.setItem(row, 2, QTableWidgetItem(cuenta.get('numero_guia', '')))
        self.table.setItem(row, 3, QTableWidgetItem(cuenta.get('empresa', '')))
        self.table.setItem(row, 4, QTableWidgetItem(f"Q{cuenta['monto']}"))
        estado_label = QLabel("PAGADO" if cuenta['pagado'] else "PENDIENTE")
        estado_label.setStyleSheet("color: #10B981; font-weight: bold;" if cuenta['pagado'] else "color: #EF4444; font-weight: bold;")
        estado_label.setAlignment(Qt.AlignCenter)
        self.table.setCellWidget(row, 5, estado_label)
        if not cuenta['pagado']:
            contenedor = QWidget()
            acciones_layout = QHBoxLayout(contenedor)
            acciones_layout.setAlignment(Qt.AlignCenter)
            pagar_btn = QPushButton("💰 Pagar")
            pagar_btn.setMinimumSize(100, 32)
            pagar_btn.setStyleSheet("background-color:#F5C800;border-radius:8px;font-weight:bold;")
            pagar_btn.clicked.connect(lambda _, idc=cuenta['id_cuenta']: self.registrar_pago_por_id(idc))
            acciones_layout.addWidget(pagar_btn)
            self.table.setCellWidget(row, 6, contenedor)
        else:
            self.table.setCellWidget(row, 6, QWidget())

    def registrar_pago(self, cuenta):
        if not self.id_caja_actual:
            QMessageBox.warning(self, "Error", "Debe abrir caja primero")
            return
        if QMessageBox.question(self, "Confirmar Pago", f"¿Registrar pago de {cuenta.numero_documento} por Q{cuenta.monto}?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            resultado = self.service.registrar_pago_en_caja(cuenta.id_cuenta, self.id_caja_actual, self.id_usuario_actual)
            if resultado:
                QMessageBox.information(self, "Éxito", "Pago registrado")
                self.cargar_cuentas()
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar")

    def registrar_pago_por_id(self, id_cuenta):
        if not self.id_caja_actual:
            QMessageBox.warning(self, "Error", "Debe abrir caja primero")
            return
        resultado = self.service.registrar_pago_en_caja(id_cuenta, self.id_caja_actual, self.id_usuario_actual)
        if resultado:
            QMessageBox.information(self, "Éxito", "Pago registrado")
            self.buscar_cuentas()
        else:
            QMessageBox.critical(self, "Error", "No se pudo registrar")


# =========================================================
# MAIN PARA PROBAR DE FORMA INDEPENDIENTE
# =========================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Simular IDs (debes ajustar según tu base de datos)
    ventana = VentanaCuentasPorCobrar(id_caja_actual=1, id_usuario_actual=1)
    ventana.show()
    sys.exit(app.exec_())