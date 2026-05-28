# UI/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                              QPushButton, QMessageBox, QHBoxLayout, QFrame,
                              QGraphicsDropShadowEffect, QSizePolicy, QScrollArea,
                              QApplication)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QPainter, QPalette, QPixmap
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.conexion import DatabaseConnection
from UI.ventas_ui import VentanasVentas
from UI.clientes_ui import VentanaClientes
from UI.productos_ui import VentanaProductos
from UI.caja_ui import VentanaCaja
from UI.apartados_ui import VentanaApartados
from UI.reportes_ui import VentanaReportes
from UI.usuario_ui import VentanaGestionUsuarios

C_AMARILLO      = "#F5C800"
C_AMARILLO_DARK = "#D4A900"
C_SIDEBAR_BG    = "#111827"
C_SIDEBAR_HOVER = "#1F2937"
C_SIDEBAR_TEXT  = "#D1D5DB"
C_SIDEBAR_ACTV  = "#F5C800"
C_CONTENT_BG    = "#F3F4F6"
C_ACCENT_RED    = "#EF4444"
C_WHITE         = "#FFFFFF"
C_GRAY_400      = "#9CA3AF"
C_GRAY_700      = "#374151"

class SidebarButton(QPushButton):
    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self.icon = icon
        self.text = text
        self._active = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(42)
        self.update_text(expanded=True)
        self._apply_style()

    def update_text(self, expanded: bool):
        if expanded:
            self.setText(f"  {self.icon}   {self.text}")
        else:
            self.setText(f"  {self.icon}")

    def set_active(self, active: bool):
        self._active = active
        self._apply_style()

    def _apply_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {C_AMARILLO};
                    color: #111111;
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding: 8px 12px;
                    font-size: 13px;
                    font-weight: bold;
                    font-family: 'Segoe UI';
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {C_SIDEBAR_TEXT};
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding: 8px 12px;
                    font-size: 13px;
                    font-family: 'Segoe UI';
                }}
                QPushButton:hover {{
                    background-color: {C_SIDEBAR_HOVER};
                    color: {C_WHITE};
                }}
            """)

class MainWindow(QMainWindow):
    def __init__(self, usuario_data):
        super().__init__()
        self.usuario_data = usuario_data
        self.db = DatabaseConnection()
        self.id_caja_actual = None
        self._sidebar_buttons: dict[str, SidebarButton] = {}
        self.init_ui()
        self.verificar_caja_abierta()
        self.show_caja()
        self._set_active_btn("Caja")

    def init_ui(self):
        self.setWindowTitle(f"Tec-Shop  ·  {self.usuario_data['nombre']}")
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(900, 500)
        self.setStyleSheet(f"background-color: {C_CONTENT_BG};")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central.setLayout(main_layout)

        self.sidebar_width = 220
        self.sidebar_collapsed = False
        self.sidebar = self._crear_sidebar()
        main_layout.addWidget(self.sidebar)

        self.content_area = QWidget()
        self.content_area.setStyleSheet(f"background-color: {C_CONTENT_BG};")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(24, 20, 24, 20)
        self.content_layout.setSpacing(12)
        self.content_area.setLayout(self.content_layout)

        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setWidget(self.content_area)
        self.content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_layout.addWidget(self.content_scroll, 1)

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        if screen_geometry.width() < 1300:
            QTimer.singleShot(100, self.auto_collapse_sidebar)

        self.showMaximized()

    def auto_collapse_sidebar(self):
        if not self.sidebar_collapsed:
            self.toggle_sidebar()

    def _crear_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(self.sidebar_width)
        sidebar.setStyleSheet(f"background-color: {C_SIDEBAR_BG};")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(4, 0)
        shadow.setColor(QColor(0, 0, 0, 80))
        sidebar.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 24, 12, 16)
        layout.setSpacing(6)

        toggle_btn = QPushButton("☰")
        toggle_btn.setFixedSize(38, 38)
        toggle_btn.setStyleSheet("background-color: transparent; color: white; font-size: 20px; border: none;")
        toggle_btn.clicked.connect(self.toggle_sidebar)
        layout.addWidget(toggle_btn, alignment=Qt.AlignLeft)

        self.logo_frame = QFrame()
        self.logo_frame.setStyleSheet("background-color: transparent; border: none;")
        logo_lay = QHBoxLayout(self.logo_frame)
        logo_lay.setContentsMargins(0, 0, 0, 0)
        logo_lay.setSpacing(0)

        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png")
        self.logo_pixmap = QPixmap(logo_path)
        self.logo_label = QLabel()
        if not self.logo_pixmap.isNull():
            self.logo_label.setPixmap(self.logo_pixmap.scaled(140, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.logo_label.setAlignment(Qt.AlignCenter)
        else:
            self.logo_label.setText("🏪")
            self.logo_label.setFont(QFont("Segoe UI Emoji", 26))
            self.logo_label.setAlignment(Qt.AlignCenter)

        logo_lay.addWidget(self.logo_label)
        logo_lay.addStretch()

        logo_container = QHBoxLayout()
        logo_container.addStretch()
        logo_container.addWidget(self.logo_frame)
        logo_container.addStretch()
        layout.addLayout(logo_container)
        layout.addSpacing(16)

        sep_lbl = QLabel("MENÚ PRINCIPAL")
        sep_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        sep_lbl.setStyleSheet(f"color: #4B5563; letter-spacing: 1.5px; padding: 8px 6px 2px 6px;")
        self.sep_lbl = sep_lbl
        layout.addWidget(sep_lbl)

        nav_items = [
            ("🛍️", "Ventas",     self.show_ventas),
            ("👥", "Clientes",   self.show_clientes),
            ("📦", "Productos",  self.show_productos),
            ("🏦", "Caja",       self.show_caja),
            ("📋", "Apartados",  self.show_apartados),
        ]
        if self.usuario_data['rol'].lower() in ['gerente', 'supervisor', 'admin', 'administrador']:
            nav_items.append(("📊", "Reportes", self.show_reportes))
        if self.usuario_data['rol'].lower() in ['admin', 'administrador']:
            nav_items.append(("🔐", "Usuarios", self.show_usuarios))

        self.sidebar_btns = []
        for icon, texto, callback in nav_items:
            btn = SidebarButton(icon, texto)
            btn.clicked.connect(lambda checked, cb=callback, name=texto: (cb(), self._set_active_btn(name)))
            self._sidebar_buttons[texto] = btn
            self.sidebar_btns.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        self.user_frame = QFrame()
        self.user_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #1F2937;
                border-radius: 12px;
            }}
        """)
        u_lay = QVBoxLayout(self.user_frame)
        u_lay.setContentsMargins(12, 10, 12, 10)
        u_lay.setSpacing(4)

        self.avatar_lbl = QLabel("👤  " + self.usuario_data['nombre'])
        self.avatar_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.avatar_lbl.setStyleSheet(f"color: {C_WHITE}; background: transparent;")
        u_lay.addWidget(self.avatar_lbl)

        self.rol_lbl = QLabel(f"🔑  {self.usuario_data['rol'].capitalize()}")
        self.rol_lbl.setFont(QFont("Segoe UI", 8))
        self.rol_lbl.setStyleSheet(f"color: {C_GRAY_400}; background: transparent;")
        u_lay.addWidget(self.rol_lbl)

        u_lay.addSpacing(6)

        # ========== BOTÓN CERRAR SESIÓN CORREGIDO ==========
        self.logout_btn = QPushButton("⏻   Cerrar Sesión")
        self.logout_btn.setFixedHeight(34)
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {C_WHITE};
                border: 1px solid {C_ACCENT_RED};
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                font-family: 'Segoe UI';
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {C_ACCENT_RED};
                color: {C_WHITE};
            }}
        """)
        self.logout_btn.clicked.connect(self.cerrar_sesion)
        u_lay.addWidget(self.logout_btn)

        layout.addWidget(self.user_frame)
        layout.addSpacing(2)

        sidebar.setLayout(layout)
        return sidebar

    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed
        new_width = 70 if self.sidebar_collapsed else self.sidebar_width
        self.sidebar.setFixedWidth(new_width)
        for btn in self.sidebar_btns:
            btn.update_text(not self.sidebar_collapsed)
        if self.sidebar_collapsed:
            if not self.logo_pixmap.isNull():
                self.logo_label.setPixmap(self.logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.logo_label.setFont(QFont("Segoe UI Emoji", 18))
            self.sep_lbl.setVisible(False)
            self.avatar_lbl.setText("👤")
            self.rol_lbl.setText("")
            self.logout_btn.setText("⏻")
            self.logout_btn.setFixedWidth(34)
            self.logout_btn.setFixedHeight(34)
        else:
            if not self.logo_pixmap.isNull():
                self.logo_label.setPixmap(self.logo_pixmap.scaled(140, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.logo_label.setFont(QFont("Segoe UI Emoji", 26))
            self.sep_lbl.setVisible(True)
            self.avatar_lbl.setText("👤  " + self.usuario_data['nombre'])
            self.rol_lbl.setText(f"🔑  {self.usuario_data['rol'].capitalize()}")
            self.logout_btn.setText("⏻   Cerrar Sesión")
            self.logout_btn.setFixedWidth(9999)
            self.logout_btn.setFixedHeight(34)

    def _set_active_btn(self, nombre: str):
        for name, btn in self._sidebar_buttons.items():
            btn.set_active(name == nombre)

    def verificar_caja_abierta(self):
        query = """
            SELECT ac.id_caja_fk
            FROM apertura_cierre ac
            WHERE ac.fecha_hora_cierre IS NULL
            ORDER BY ac.fecha_hora_apertura DESC
            LIMIT 1
        """
        resultado = self.db.fetch_one(query)
        if resultado:
            self.id_caja_actual = resultado['id_caja_fk']

    def limpiar_contenido(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_ventas(self):
        self.limpiar_contenido()
        widget = VentanasVentas(self.usuario_data, self.id_caja_actual)
        self.content_layout.addWidget(widget)

    def show_clientes(self):
        self.limpiar_contenido()
        widget = VentanaClientes()
        self.content_layout.addWidget(widget)

    def show_productos(self):
        self.limpiar_contenido()
        widget = VentanaProductos()
        self.content_layout.addWidget(widget)

    def show_caja(self):
        self.limpiar_contenido()
        widget = VentanaCaja(self.usuario_data)
        self.content_layout.addWidget(widget)
        widget.caja_abierta_signal.connect(self.actualizar_id_caja)

    def show_apartados(self):
        self.limpiar_contenido()
        widget = VentanaApartados(self.usuario_data['id_usuario'], self.id_caja_actual)
        self.content_layout.addWidget(widget)

    def show_reportes(self):
        self.limpiar_contenido()
        widget = VentanaReportes(self.usuario_data)
        self.content_layout.addWidget(widget)

    def show_usuarios(self):
        self.limpiar_contenido()
        widget = VentanaGestionUsuarios(self.usuario_data)
        self.content_layout.addWidget(widget)

    def actualizar_id_caja(self, id_caja):
        self.id_caja_actual = id_caja

    def cerrar_sesion(self):
        reply = QMessageBox.question(self, 'Cerrar Sesión', '¿Está seguro que desea salir?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            from UI.login_ui import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()