import sys
import os
import random
import string

# --- FIX DE RUTAS PARA EVITAR EL ERROR DE IMPORTACIÓN ---
ruta_ui = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.dirname(ruta_ui)
# Agregamos las carpetas al sistema para que Python encuentre todo
for r in [ruta_raiz, os.path.join(ruta_raiz, 'models')]:
    if r not in sys.path:
        sys.path.insert(0, r)

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QCheckBox, QMessageBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

try:
    from database.conexion import DatabaseConnection
    from models.usuario import Usuario
    from models.dao import UsuarioDAO
except ImportError:
    # Intento alternativo si no están en la carpeta models
    #from usuario import Usuario
    #from dao import UsuarioDAO
    from database.conexion import DatabaseConnection

class VentanaGestionUsuarios(QWidget):
    def __init__(self, usuario_data=None):
        super().__init__()
        self.db = DatabaseConnection()
        self.dao = UsuarioDAO(self.db)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Control de Usuarios - POS")
        self.setGeometry(100, 100, 1150, 650)
        self.setStyleSheet("background-color: #f9fafb;")

        layout_principal = QVBoxLayout(self)
        
        # Título
        header = QLabel("GESTIÓN DE ACCESOS Y PERSONAL")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: #111827; margin: 10px;")
        layout_principal.addWidget(header)

        cuerpo = QHBoxLayout()

        # --- PANEL IZQUIERDO: REGISTRO ---
        self.group_registro = QGroupBox("Nuevo Usuario / Edición")
        self.group_registro.setFixedWidth(380)
        self.group_registro.setStyleSheet("""
            QGroupBox { border: 2px solid #F5C800; border-radius: 12px; margin-top: 10px; padding: 15px; background-color: white; font-weight: bold; }
            QLineEdit, QComboBox { padding: 8px; border: 1px solid #D1D5DB; border-radius: 6px; }
        """)
        
        form_ly = QFormLayout()
        
        self.txt_nombre = QLineEdit()
        self.txt_user = QLineEdit()
        
        # Layout para password con generador
        pass_layout = QHBoxLayout()
        self.txt_pass = QLineEdit()
        self.txt_pass.setPlaceholderText("Clave...")
        self.btn_gen = QPushButton("⚡")
        self.btn_gen.setToolTip("Generar clave aleatoria")
        self.btn_gen.setFixedWidth(40)
        self.btn_gen.setStyleSheet("background-color: #F5C800; font-weight: bold; border-radius: 5px;")
        self.btn_gen.clicked.connect(self.generar_password)
        pass_layout.addWidget(self.txt_pass)
        pass_layout.addWidget(self.btn_gen)

        self.cmb_rol = QComboBox()
        self.cmb_rol.addItems(["ADMIN", "CAJERO"])
        
        self.chk_estado = QCheckBox("Usuario Activo")
        self.chk_estado.setChecked(True)
        self.chk_estado.setStyleSheet("color: #059669; font-weight: bold;")

        form_ly.addRow("Nombre:", self.txt_nombre)
        form_ly.addRow("Username:", self.txt_user)
        form_ly.addRow("Password:", pass_layout)
        form_ly.addRow("Rol:", self.cmb_rol)
        form_ly.addRow(self.chk_estado)

        self.btn_guardar = QPushButton("CREAR USUARIO")
        self.btn_guardar.setStyleSheet("background-color: #F5C800; padding: 12px; font-weight: bold; border-radius: 8px;")
        self.btn_guardar.clicked.connect(self.registrar)
        form_ly.addRow(self.btn_guardar)

        self.group_registro.setLayout(form_ly)
        cuerpo.addWidget(self.group_registro)

        # --- PANEL DERECHO: TABLA Y ACCIONES ---
        derecha_layout = QVBoxLayout()
        
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "User", "Rol", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #E5E7EB;")
        
        # Botones de acción rápida
        btns_accion = QHBoxLayout()
        self.btn_estado = QPushButton("HABILITAR / DESHABILITAR SELECCIONADO")
        self.btn_estado.setStyleSheet("background-color: #374151; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.btn_estado.clicked.connect(self.cambiar_estado_usuario)
        
        btns_accion.addWidget(self.btn_estado)
        
        derecha_layout.addWidget(self.tabla)
        derecha_layout.addLayout(btns_accion)
        
        cuerpo.addLayout(derecha_layout)
        layout_principal.addLayout(cuerpo)
        
        self.cargar_datos()

    def generar_password(self):
        caracteres = string.ascii_letters + string.digits
        pwd = ''.join(random.choice(caracteres) for _ in range(8))
        self.txt_pass.setText(pwd)
        self.txt_pass.setEchoMode(QLineEdit.Normal)
        QMessageBox.information(self, "Contraseña", f"Se ha generado: {pwd}")

    def cargar_datos(self):
        usuarios = self.dao.listar_todos()
        self.tabla.setRowCount(len(usuarios))
        for i, u in enumerate(usuarios):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(u.id_usuario)))
            self.tabla.setItem(i, 1, QTableWidgetItem(u.nombre))
            self.tabla.setItem(i, 2, QTableWidgetItem(u.usuario))
            self.tabla.setItem(i, 3, QTableWidgetItem(u.rol))
            
            estado_str = "🟢 ACTIVO" if u.estado else "🔴 INACTIVO"
            item_est = QTableWidgetItem(estado_str)
            item_est.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 4, item_est)

    def cambiar_estado_usuario(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Atención", "Seleccione un usuario de la tabla.")
            return

        id_u = int(self.tabla.item(fila, 0).text())
        # Buscamos el objeto usuario para invertir su estado
        usuarios = self.dao.listar_todos()
        u_sel = next((x for x in usuarios if x.id_usuario == id_u), None)

        if u_sel:
            nuevo_estado = not u_sel.estado
            # Llamada a la base de datos para actualizar solo el estado
            query = "UPDATE usuario SET estado = %s WHERE id_usuario = %s"
            self.db.execute_query(query, (nuevo_estado, id_u))
            
            self.cargar_datos()
            msg = "habilitado" if nuevo_estado else "deshabilitado"
            QMessageBox.information(self, "Éxito", f"Usuario {u_sel.usuario} {msg}.")

    def registrar(self):
        if not self.txt_nombre.text() or not self.txt_user.text():
            QMessageBox.warning(self, "Campos obligatorios", "Llene el nombre y usuario.")
            return

        nuevo = Usuario(
            nombre=self.txt_nombre.text().upper(),
            usuario=self.txt_user.text().lower(),
            password=self.txt_pass.text(),
            rol=self.cmb_rol.currentText(),
            estado=self.chk_estado.isChecked()
        )

        if self.dao.crear(nuevo):
            QMessageBox.information(self, "OK", "Guardado.")
            self.cargar_datos()
            self.txt_nombre.clear(); self.txt_user.clear(); self.txt_pass.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = VentanaGestionUsuarios()
    win.show()
    sys.exit(app.exec_())