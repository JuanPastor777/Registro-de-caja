# UI/clientes_ui.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDialog, QFormLayout, QLineEdit, QMessageBox,
                             QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.conexion import DatabaseConnection


class DialogoCliente(QDialog):
    def __init__(self, cliente=None, parent=None):
        super().__init__(parent)
        self.cliente = cliente
        self.db = DatabaseConnection()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Nuevo Cliente" if not self.cliente else "Editar Cliente")
        self.setFixedSize(400, 350)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)

        title = QLabel("Datos del Cliente")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(20)

        form_layout = QFormLayout()

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombres completos")
        self.nombre_input.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #E5E7EB;")
        form_layout.addRow("Nombres:", self.nombre_input)

        self.apellido_input = QLineEdit()
        self.apellido_input.setPlaceholderText("Apellidos")
        self.apellido_input.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #E5E7EB;")
        form_layout.addRow("Apellidos:", self.apellido_input)

        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Telefono")
        self.telefono_input.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #E5E7EB;")
        form_layout.addRow("Telefono:", self.telefono_input)

        layout.addLayout(form_layout)
        layout.addSpacing(30)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("padding: 10px; background-color: #F3F4F6; border-radius: 8px;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Guardar")
        save_btn.setStyleSheet("padding: 10px; background-color: #F5C800; border-radius: 8px; font-weight: bold;")
        save_btn.clicked.connect(self.guardar)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        if self.cliente:
            self.cargar_datos()

    def cargar_datos(self):
        self.nombre_input.setText(self.cliente.get('nombre', ''))
        self.apellido_input.setText(self.cliente.get('apellido', ''))
        self.telefono_input.setText(self.cliente.get('telefono', ''))

    def guardar(self):
        nombre = self.nombre_input.text().strip()
        apellido = self.apellido_input.text().strip()
        telefono = self.telefono_input.text().strip()

        if not nombre:
            QMessageBox.warning(self, "Error", "Nombre es requerido")
            return

        if self.cliente:
            query = "UPDATE cliente SET nombre=%s, apellido=%s, telefono=%s WHERE id_cliente=%s"
            success = self.db.execute_query(query, (nombre, apellido, telefono, self.cliente['id_cliente']))
        else:
            query = "INSERT INTO cliente (nombre, apellido, telefono) VALUES (%s, %s, %s)"
            success = self.db.execute_query(query, (nombre, apellido, telefono))

        if success:
            QMessageBox.information(self, "Exito", "Cliente guardado")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar")


class VentanaClientes(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseConnection()
        self.init_ui()
        self.cargar_clientes()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        header = QHBoxLayout()
        title = QLabel("Gestion de Clientes")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("+ Nuevo Cliente")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5C800;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
        """)
        add_btn.clicked.connect(self.agregar_cliente)
        header.addWidget(add_btn)

        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nombres", "Apellidos", "Telefono", "Acciones"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E7EB;
                border-radius: 12px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                padding: 12px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def cargar_clientes(self):
        query = "SELECT id_cliente, nombre, apellido, telefono FROM cliente ORDER BY id_cliente"
        clientes = self.db.fetch_all(query)

        self.table.setRowCount(len(clientes))

        for row_idx, cliente in enumerate(clientes):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(cliente['id_cliente'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(cliente['nombre']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(cliente.get('apellido') or ''))
            self.table.setItem(row_idx, 3, QTableWidgetItem(cliente.get('telefono') or ''))

            acciones = QWidget()
            acciones_layout = QHBoxLayout()
            acciones_layout.setContentsMargins(4, 4, 4, 4)

            edit_btn = QPushButton("Editar")
            edit_btn.setStyleSheet("padding: 4px 12px; background-color: #F3F4F6; border-radius: 4px;")
            edit_btn.clicked.connect(lambda checked, cli=cliente: self.editar_cliente(cli))
            acciones_layout.addWidget(edit_btn)

            delete_btn = QPushButton("Eliminar")
            delete_btn.setStyleSheet("padding: 4px 12px; background-color: #FEE2E2; color: #EF4444; border-radius: 4px;")
            delete_btn.clicked.connect(lambda checked, cli=cliente: self.eliminar_cliente(cli))
            acciones_layout.addWidget(delete_btn)

            acciones.setLayout(acciones_layout)
            self.table.setCellWidget(row_idx, 4, acciones)

    def agregar_cliente(self):
        dialog = DialogoCliente(self)
        if dialog.exec_():
            self.cargar_clientes()

    def editar_cliente(self, cliente):
        dialog = DialogoCliente(cliente, self)
        if dialog.exec_():
            self.cargar_clientes()

    def eliminar_cliente(self, cliente):
        reply = QMessageBox.question(self, "Confirmar", f"Eliminar a {cliente['nombre']}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            query = "DELETE FROM cliente WHERE id_cliente = %s"
            if self.db.execute_query(query, (cliente['id_cliente'],)):
                QMessageBox.information(self, "Exito", "Cliente eliminado")
                self.cargar_clientes()
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar")