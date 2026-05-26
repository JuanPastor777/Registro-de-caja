# UI/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                              QPushButton, QMessageBox, QHBoxLayout, QFrame,
                              QGraphicsDropShadowEffect, QSizePolicy)
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
        self.setFixedHeight(46)
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
                    border-radius: 10px;
                    text-align: left;
                    padding: 10px 16px;
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
                    border-radius: 10px;
                    text-align: left;
                    padding: 10px 16px;
                    font-size: 13px;
                    font-family: 'Segoe UI';
                }}
                QPushButton:hover {{
                    background-color: {C_SIDEBAR_HOVER};
                    color: {C_WHITE};
                }}
            """)

class DashCard(QFrame):
    def __init__(self, icon: str, title: str, subtitle: str,
                 bg: str = C_WHITE, parent=None):
        super().__init__(parent)
        self.setFixedHeight(110)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-radius: 16px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(16)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 28))
        icon_lbl.setFixedWidth(50)
        icon_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(icon_lbl)

        text_lay = QVBoxLayout()
        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 13, QFont.Bold))
        t.setStyleSheet(f"color: {C_GRAY_700}; background: transparent;")
        s = QLabel(subtitle)
        s.setFont(QFont("Segoe UI", 10))
        s.setStyleSheet(f"color: {C_GRAY_400}; background: transparent;")
        text_lay.addWidget(t)
        text_lay.addWidget(s)
        text_lay.addStretch()
        lay.addLayout(text_lay)

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
        self.setGeometry(100, 100, 1280, 740)
        self.setMinimumSize(1050, 620)
        self.setStyleSheet(f"background-color: {C_CONTENT_BG};")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central.setLayout(main_layout)

        self.sidebar = self._crear_sidebar()
        main_layout.addWidget(self.sidebar)

        self.content_area = QWidget()
        self.content_area.setStyleSheet(f"background-color: {C_CONTENT_BG};")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(32, 28, 32, 28)
        self.content_area.setLayout(self.content_layout)
        main_layout.addWidget(self.content_area, 1)

    def _crear_sidebar(self):
        sidebar = QFrame()
        self.sidebar_width = 255
        self.sidebar_collapsed = False
        sidebar.setFixedWidth(self.sidebar_width)
        sidebar.setStyleSheet(f"background-color: {C_SIDEBAR_BG};")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(4, 0)
        shadow.setColor(QColor(0, 0, 0, 80))
        sidebar.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 28, 14, 20)
        layout.setSpacing(8)

        # Botón toggle
        toggle_btn = QPushButton("☰")
        toggle_btn.setFixedSize(40, 40)
        toggle_btn.setStyleSheet("background-color: transparent; color: white; font-size: 20px; border: none;")
        toggle_btn.clicked.connect(self.toggle_sidebar)
        layout.addWidget(toggle_btn, alignment=Qt.AlignLeft)

        # Logo - SIN FONDO AMARILLO Y CENTRADO
        self.logo_frame = QFrame()
        self.logo_frame.setStyleSheet("background-color: transparent; border: none;")
        logo_lay = QHBoxLayout(self.logo_frame)
        logo_lay.setContentsMargins(0, 0, 0, 0)
        logo_lay.setSpacing(0)

        # Cargar el logo desde assets/logo.png
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png")
        self.logo_pixmap = QPixmap(logo_path)
        self.logo_label = QLabel()
        if not self.logo_pixmap.isNull():
            self.logo_label.setPixmap(self.logo_pixmap.scaled(160, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.logo_label.setAlignment(Qt.AlignCenter)
        else:
            self.logo_label.setText("🏪")
            self.logo_label.setFont(QFont("Segoe UI Emoji", 28))
            self.logo_label.setAlignment(Qt.AlignCenter)
        
        logo_lay.addWidget(self.logo_label)
        logo_lay.addStretch()
        
        # Centrar el logo_frame horizontalmente
        logo_container = QHBoxLayout()
        logo_container.addStretch()
        logo_container.addWidget(self.logo_frame)
        logo_container.addStretch()
        layout.addLayout(logo_container)
        layout.addSpacing(20)

        sep_lbl = QLabel("MENÚ PRINCIPAL")
        sep_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        sep_lbl.setStyleSheet(f"color: #4B5563; letter-spacing: 1.5px; padding: 10px 6px 4px 6px;")
        self.sep_lbl = sep_lbl
        layout.addWidget(sep_lbl)

        nav_items = [
            ("🏠", "Dashboard",  self.show_dashboard),
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

        # Espacio flexible para empujar el panel de usuario hacia abajo
        layout.addStretch()

        # Panel usuario - MEJORADO PARA CERRAR SESIÓN
        self.user_frame = QFrame()
        self.user_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #1F2937;
                border-radius: 14px;
            }}
        """)
        u_lay = QVBoxLayout(self.user_frame)
        u_lay.setContentsMargins(14, 12, 14, 12)
        u_lay.setSpacing(6)

        self.avatar_lbl = QLabel("👤  " + self.usuario_data['nombre'])
        self.avatar_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.avatar_lbl.setStyleSheet(f"color: {C_WHITE}; background: transparent;")
        u_lay.addWidget(self.avatar_lbl)

        self.rol_lbl = QLabel(f"🔑  {self.usuario_data['rol'].capitalize()}")
        self.rol_lbl.setFont(QFont("Segoe UI", 9))
        self.rol_lbl.setStyleSheet(f"color: {C_GRAY_400}; background: transparent;")
        u_lay.addWidget(self.rol_lbl)

        u_lay.addSpacing(8)
        
        self.logout_btn = QPushButton("⏻   Cerrar Sesión")
        self.logout_btn.setFixedHeight(34)
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {C_ACCENT_RED};
                border: 1px solid #3B1414;
                border-radius: 8px;
                font-size: 12px;
                font-family: 'Segoe UI';
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #3B1414;
            }}
        """)
        self.logout_btn.clicked.connect(self.cerrar_sesion)
        u_lay.addWidget(self.logout_btn)

        layout.addWidget(self.user_frame)
        layout.addSpacing(4)

        sidebar.setLayout(layout)
        return sidebar

    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed
        new_width = 70 if self.sidebar_collapsed else 255
        self.sidebar.setFixedWidth(new_width)
        # Ajustar textos de botones
        for btn in self.sidebar_btns:
            btn.update_text(not self.sidebar_collapsed)
        # Ajustar logo: cambiar tamaño según colapsado
        if self.sidebar_collapsed:
            if not self.logo_pixmap.isNull():
                self.logo_label.setPixmap(self.logo_pixmap.scaled(45, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.logo_label.setFont(QFont("Segoe UI Emoji", 20))
            self.sep_lbl.setVisible(False)
            # Ajustar panel usuario para colapsado
            self.avatar_lbl.setText("👤")
            self.rol_lbl.setText("")
            self.logout_btn.setText("⏻")
            self.logout_btn.setFixedWidth(36)
            self.logout_btn.setFixedHeight(36)
        else:
            if not self.logo_pixmap.isNull():
                self.logo_label.setPixmap(self.logo_pixmap.scaled(160, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.logo_label.setFont(QFont("Segoe UI Emoji", 28))
            self.sep_lbl.setVisible(True)
            # Restaurar panel usuario para expandido
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

    def _page_header(self, icon: str, titulo: str, subtitulo: str = ""):
        hdr = QFrame()
        hdr.setStyleSheet("background: transparent;")
        h = QHBoxLayout(hdr)
        h.setContentsMargins(0, 0, 0, 0)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 26))
        icon_lbl.setStyleSheet("background: transparent;")
        h.addWidget(icon_lbl)

        txt = QVBoxLayout()
        t = QLabel(titulo)
        t.setFont(QFont("Segoe UI", 18, QFont.Bold))
        t.setStyleSheet(f"color: {C_GRAY_700}; background: transparent;")
        txt.addWidget(t)
        if subtitulo:
            s = QLabel(subtitulo)
            s.setFont(QFont("Segoe UI", 10))
            s.setStyleSheet(f"color: {C_GRAY_400}; background: transparent;")
            txt.addWidget(s)
        h.addLayout(txt)
        h.addStretch()
        return hdr

    def show_dashboard(self):
        self.limpiar_contenido()
        hdr = self._page_header("🏠", f"Bienvenido, {self.usuario_data['nombre']}",
                                f"Rol: {self.usuario_data['rol'].capitalize()}")
        self.content_layout.addWidget(hdr)
        self.content_layout.addSpacing(20)
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        cards_row.addWidget(DashCard("🏦", "Caja", "Gestionar apertura y cierre", C_WHITE))
        cards_row.addWidget(DashCard("🛍️", "Ventas", "Registrar nuevas ventas", C_WHITE))
        cards_row.addWidget(DashCard("📦", "Inventario", "Productos y stock", C_WHITE))
        self.content_layout.addLayout(cards_row)
        self.content_layout.addSpacing(16)
        cards_row2 = QHBoxLayout()
        cards_row2.setSpacing(16)
        cards_row2.addWidget(DashCard("👥", "Clientes", "Base de clientes", C_WHITE))
        cards_row2.addWidget(DashCard("📋", "Apartados", "Reservas y apartados", C_WHITE))
        if self.usuario_data['rol'].lower() in ['gerente', 'supervisor', 'admin', 'administrador']:
            cards_row2.addWidget(DashCard("📊", "Reportes", "Informes y estadísticas", C_WHITE))
        self.content_layout.addLayout(cards_row2)
        self.content_layout.addStretch()

    def show_ventas(self):
        self.limpiar_contenido()
        hdr = self._page_header("🛍️", "Ventas", "Registrar y gestionar ventas")
        self.content_layout.addWidget(hdr)
        self.content_layout.addSpacing(12)
        widget = VentanasVentas(self.usuario_data, self.id_caja_actual)
        self.content_layout.addWidget(widget)

    def show_clientes(self):
        self.limpiar_contenido()
        hdr = self._page_header("👥", "Clientes", "Administrar base de clientes")
        self.content_layout.addWidget(hdr)
        self.content_layout.addSpacing(12)
        widget = VentanaClientes()
        self.content_layout.addWidget(widget)

    def show_productos(self):
        self.limpiar_contenido()
        hdr = self._page_header("📦", "Productos", "Inventario y catálogo")
        self.content_layout.addWidget(hdr)
        self.content_layout.addSpacing(12)
        widget = VentanaProductos()
        self.content_layout.addWidget(widget)

    def show_caja(self):
        self.limpiar_contenido()
        hdr = self._page_header("🏦", "Caja", "Apertura, cierre y movimientos")
        self.content_layout.addWidget(hdr)
        self.content_layout.addSpacing(12)
        widget = VentanaCaja(self.usuario_data)
        self.content_layout.addWidget(widget)
        widget.caja_abierta_signal.connect(self.actualizar_id_caja)

    def show_apartados(self):
        self.limpiar_contenido()
        hdr = self._page_header("📋", "Apartados", "Reservas y apartados de clientes")
        self.content_layout.addWidget(hdr)
        self.content_layout.addSpacing(12)
        widget = VentanaApartados(self.usuario_data['id_usuario'], self.id_caja_actual)
        self.content_layout.addWidget(widget)

    def show_reportes(self):
        self.limpiar_contenido()
        hdr = self._page_header("📊", "Reportes", "Informes y análisis de ventas")
        self.content_layout.addWidget(hdr)
        self.content_layout.addSpacing(12)
        widget = VentanaReportes(self.usuario_data)
        self.content_layout.addWidget(widget)

    def show_usuarios(self):
        self.limpiar_contenido()
        hdr = self._page_header("🔐", "Usuarios", "Administrar cuentas del personal")
        self.content_layout.addWidget(hdr)
        self.content_layout.addSpacing(12)
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