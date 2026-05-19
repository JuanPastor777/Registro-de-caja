# UI/reportes_ui.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QDateEdit, QComboBox, QHeaderView, QGroupBox,
    QMessageBox, QFileDialog, QApplication
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.conexion import DatabaseConnection
from services.reporte_service import ReporteService
from Utils.export_excel import ExportadorExcel


class VentanaReportes(QWidget):
    def __init__(self, usuario_data):
        super().__init__()

        self.usuario_data = usuario_data
        self.db = DatabaseConnection()
        self.reporte_service = ReporteService()

        self.init_ui()
        self.cargar_usuarios()

    def init_ui(self):
        self.setWindowTitle("Reportes Gerenciales - Tech Shop")
        self.resize(1200, 700)

        layout = QVBoxLayout()
        layout.setSpacing(20)

        titulo = QLabel("Reportes Avanzados")
        titulo.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(titulo)

        # =========================
        # PANEL DE FILTROS
        # =========================
        grupo_filtros = QGroupBox("Filtros")
        grupo_filtros.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
            }
        """)

        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(10)

        self.fecha_desde = QDateEdit()
        self.fecha_desde.setDate(QDate.currentDate().addDays(-30))
        self.fecha_desde.setCalendarPopup(True)

        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setCalendarPopup(True)

        filtros_layout.addWidget(QLabel("Desde:"))
        filtros_layout.addWidget(self.fecha_desde)

        filtros_layout.addWidget(QLabel("Hasta:"))
        filtros_layout.addWidget(self.fecha_hasta)

        self.combo_usuario = QComboBox()
        self.combo_usuario.addItem("Todos", None)

        filtros_layout.addWidget(QLabel("Cajero:"))
        filtros_layout.addWidget(self.combo_usuario)

        self.combo_forma_pago = QComboBox()
        self.combo_forma_pago.addItem("Todos", None)

        for fp in ["EF", "TC/TD", "TF", "DP", "COD"]:
            self.combo_forma_pago.addItem(fp, fp)

        filtros_layout.addWidget(QLabel("Forma pago:"))
        filtros_layout.addWidget(self.combo_forma_pago)

        btn_aplicar = QPushButton("Aplicar filtros")
        btn_aplicar.clicked.connect(self.cargar_reporte)

        filtros_layout.addWidget(btn_aplicar)

        grupo_filtros.setLayout(filtros_layout)

        layout.addWidget(grupo_filtros)

        # =========================
        # TABLA
        # =========================
        self.tabla = QTableWidget()

        self.tabla.setColumnCount(8)

        self.tabla.setHorizontalHeaderLabels([
            "Fecha",
            "Documento",
            "Cliente",
            "Total",
            "Forma pago",
            "Usuario",
            "Envío",
            "Guía"
        ])

        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)

        layout.addWidget(self.tabla)

        # =========================
        # BOTÓN EXPORTAR
        # =========================
        btn_exportar = QPushButton("Exportar a Excel (formato original)")
        btn_exportar.clicked.connect(self.exportar_reporte)

        btn_exportar.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #059669;
            }
        """)

        layout.addWidget(btn_exportar)

        self.setLayout(layout)

    def cargar_usuarios(self):
        try:
            query = """
                SELECT id_usuario, nombre
                FROM usuario
                WHERE estado = true
                ORDER BY nombre
            """

            usuarios = self.db.fetch_all(query)

            for u in usuarios:
                self.combo_usuario.addItem(
                    u['nombre'],
                    u['id_usuario']
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron cargar los usuarios:\n{str(e)}"
            )

    def cargar_reporte(self):
        try:
            desde = self.fecha_desde.date().toPyDate()
            hasta = self.fecha_hasta.date().toPyDate()

            usuario_id = self.combo_usuario.currentData()
            forma_pago = self.combo_forma_pago.currentData()

            ventas = self.reporte_service.obtener_ventas(
                desde,
                hasta,
                usuario_id,
                forma_pago
            )

            self.tabla.setRowCount(len(ventas))

            for i, v in enumerate(ventas):

                self.tabla.setItem(
                    i, 0,
                    QTableWidgetItem(str(v['fecha_hora'])[:19])
                )

                self.tabla.setItem(
                    i, 1,
                    QTableWidgetItem(v.get('numero_documento', ''))
                )

                cliente = f"{v.get('cliente_nombre', '')} {v.get('cliente_apellido', '')}".strip()

                self.tabla.setItem(
                    i, 2,
                    QTableWidgetItem(cliente)
                )

                self.tabla.setItem(
                    i, 3,
                    QTableWidgetItem(f"Q{float(v['total']):,.2f}")
                )

                self.tabla.setItem(
                    i, 4,
                    QTableWidgetItem(v.get('forma_pago', ''))
                )

                self.tabla.setItem(
                    i, 5,
                    QTableWidgetItem(v.get('usuario_nombre', ''))
                )

                self.tabla.setItem(
                    i, 6,
                    QTableWidgetItem(
                        "Sí" if v.get('es_envio') else "No"
                    )
                )

                self.tabla.setItem(
                    i, 7,
                    QTableWidgetItem(v.get('numero_guia', ''))
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar el reporte:\n{str(e)}"
            )

    def exportar_reporte(self):
        try:
            desde = self.fecha_desde.date().toPyDate()
            hasta = self.fecha_hasta.date().toPyDate()

            usuario_id = self.combo_usuario.currentData()
            forma_pago = self.combo_forma_pago.currentData()

            ventas = self.reporte_service.obtener_ventas(
                desde,
                hasta,
                usuario_id,
                forma_pago
            )

            if not ventas:
                QMessageBox.warning(
                    self,
                    "Sin datos",
                    "No hay ventas en el período seleccionado."
                )
                return

            # Obtener productos de cada venta
            for v in ventas:
                v['productos'] = self.reporte_service.obtener_detalles_venta(
                    v['id_venta']
                )

            # Agrupar por día
            diarios = {}

            for v in ventas:
                fecha_str = v['fecha_hora'].date().isoformat()

                if fecha_str not in diarios:
                    diarios[fecha_str] = []

                diarios[fecha_str].append(v)

            nombre_mes = desde.strftime("%B").upper()

            exportador = ExportadorExcel(
                ventas,
                diarios,
                nombre_mes
            )

            ruta, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar reporte",
                f"Reporte_{nombre_mes}.xlsx",
                "Excel files (*.xlsx)"
            )

            if ruta:
                exportador.generar(ruta)

                QMessageBox.information(
                    self,
                    "Éxito",
                    f"Reporte guardado en:\n{ruta}"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo generar el reporte:\n{str(e)}"
            )


# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Usuario de prueba
    usuario_demo = {
        "id_usuario": 1,
        "nombre": "Administrador"
    }

    ventana = VentanaReportes(usuario_demo)
    ventana.show()

    sys.exit(app.exec_())