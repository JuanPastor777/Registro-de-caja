from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QLineEdit, QPushButton,
                             QFrame, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.caja_service import CajaService
from UI.main_window import MainWindow


class LoginWindow(QWidget):


    def __init__(self):
        super().__init__()
        self.caja_service = CajaService()
        self.init_ui()

    def init_ui(self):

        self.setWindowTitle("TEC SHOP - Control de Caja")
        self.setFixedSize(480, 560)

        # Fondo blanco
        self.setStyleSheet("background-color: #ffffff;")

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(50, 50, 50, 50)

        # ── Logo: [TEC] SHOP ──────────────────────────────────────────
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(9)
        logo_layout.setAlignment(Qt.AlignCenter)

        # Caja amarilla "TEC"
        tec_label = QLabel("TEC")
        tec_label.setFont(QFont("Arial", 20, QFont.Bold))
        tec_label.setAlignment(Qt.AlignCenter)
        tec_label.setFixedSize(70, 50)
        tec_label.setStyleSheet("""
            background-color: #F5C800;
            color: #000000;
            border-radius: 8px;
            padding: 1px 5px;
        """)

        # Texto "SHOP"
        shop_label = QLabel("SHOP")
        shop_label.setFont(QFont("Arial", 26, QFont.Bold))
        shop_label.setAlignment(Qt.AlignCenter)
        shop_label.setStyleSheet("color: #111111; background: transparent;")

        logo_layout.addWidget(tec_label)
        logo_layout.addWidget(shop_label)
        main_layout.addLayout(logo_layout)

        main_layout.addSpacing(10)

        # ── Subtítulo ────────────────────────────────────────────────
        subtitle_label = QLabel("Control de Caja · Xela")
        subtitle_label.setFont(QFont("Arial", 11))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #888888; background: transparent;")
        main_layout.addWidget(subtitle_label)

        main_layout.addSpacing(24)

        # ── Banner de error/instrucción (rosado) ─────────────────────
        self.error_banner = QLabel("Selecciona un usuario.")
        self.error_banner.setFont(QFont("Arial", 11, QFont.Bold))
        self.error_banner.setAlignment(Qt.AlignCenter)
        self.error_banner.setFixedHeight(44)
        self.error_banner.setStyleSheet("""
            QLabel {
                background-color: #FFF0F0;
                color: #E05555;
                border: 1px solid #F5C5C5;
                border-radius: 8px;
                padding: 8px 12px;
            }
        """)
        self.error_banner.setVisible(False)   # oculto por defecto
        main_layout.addWidget(self.error_banner)

        main_layout.addSpacing(18)

        # ── Etiqueta USUARIO ─────────────────────────────────────────
        user_label = QLabel("USUARIO")
        user_label.setFont(QFont("Arial", 9, QFont.Bold))
        user_label.setStyleSheet("color: #333333; background: transparent; letter-spacing: 1px;")
        main_layout.addWidget(user_label)

        main_layout.addSpacing(6)

        # ── ComboBox usuarios ─────────────────────────────────────────
        self.user_combo = QComboBox()
        self.user_combo.setFixedHeight(46)
        self.user_combo.setStyleSheet("""
            QComboBox {
                border: 1.5px solid #DDDDDD;
                border-radius: 10px;
                padding: 6px 14px;
                background-color: #F7F7F7;
                color: #333333;
                font-family: Arial;
                font-size: 12px;
            }
            QComboBox:focus {
                border: 1.5px solid #AAAAAA;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 28px;
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #DDDDDD;
                border-radius: 6px;
                background-color: white;
                selection-background-color: #F5C800;
                selection-color: black;
            }
        """)
        self.load_users()
        main_layout.addWidget(self.user_combo)

        main_layout.addSpacing(16)

        # ── Etiqueta CONTRASEÑA ───────────────────────────────────────
        password_label = QLabel("CONTRASEÑA")
        password_label.setFont(QFont("Arial", 9, QFont.Bold))
        password_label.setStyleSheet("color: #333333; background: transparent; letter-spacing: 1px;")
        main_layout.addWidget(password_label)

        main_layout.addSpacing(6)

        # ── Campo contraseña ──────────────────────────────────────────
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setFixedHeight(46)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #DDDDDD;
                border-radius: 10px;
                padding: 6px 14px;
                background-color: #F7F7F7;
                color: #333333;
                font-family: Arial;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1.5px solid #AAAAAA;
                background-color: #F0F0F0;
            }
        """)
        self.password_input.returnPressed.connect(self.handle_login)
        main_layout.addWidget(self.password_input)

        main_layout.addSpacing(24)

        # ── Botón Ingresar (amarillo) ─────────────────────────────────
        self.login_button = QPushButton("→  Ingresar")
        self.login_button.setFixedHeight(50)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #F5C800;
                color: #111111;
                border: none;
                border-radius: 10px;
                font-family: Arial;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #E0B800;
            }
            QPushButton:pressed {
                background-color: #CCA800;
            }
        """)
        self.login_button.clicked.connect(self.handle_login)
        main_layout.addWidget(self.login_button)

        main_layout.addStretch()
        self.setLayout(main_layout)

    # ─────────────────────────────────────────────────────────────────
    def load_users(self):
        """Carga los usuarios activos en el combobox"""
        users = self.caja_service.obtener_usuarios_activos()
        self.user_combo.clear()
        self.user_combo.addItem("— Seleccionar usuario —", None)
        for user in users:
            self.user_combo.addItem(user['nombre'], user['id_usuario'])

    def show_error(self, message: str):
        """Muestra el banner rosado con un mensaje de error."""
        self.error_banner.setText(message)
        self.error_banner.setVisible(True)

    def hide_error(self):
        self.error_banner.setVisible(False)

    def handle_login(self):
        """Maneja el intento de inicio de sesión"""
        user_id = self.user_combo.currentData()
        password = self.password_input.text()

        if user_id is None:
            self.show_error("Selecciona un usuario.")
            return

        if not password:
            self.show_error("Por favor ingrese la contraseña.")
            return

        success, message, user_data = self.caja_service.autenticar_usuario(user_id, password)

        if success:
            self.hide_error()
            QMessageBox.information(self, "Éxito", f"¡Bienvenido {user_data['nombre']}!")
            self.main_window = MainWindow(user_data)
            self.main_window.show()
            self.close()
        else:
            self.show_error(message)
            self.password_input.clear()
            self.password_input.setFocus()