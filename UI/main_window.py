# UI/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                              QPushButton, QMessageBox, QHBoxLayout, QFrame,
                              QGraphicsDropShadowEffect, QSizePolicy)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QPainter, QPalette
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
from UI.usuario_ui import VentanaGestionUsuarios   # ← Importación agregada


# ── Paleta de colores ────────────────────────────────────────────────────────
C_AMARILLO      = "#F5C800"
C_AMARILLO_DARK = "#D4A900"
C_SIDEBAR_BG    = "#111827"   # casi negro azulado
C_SIDEBAR_HOVER = "#1F2937"
C_SIDEBAR_TEXT  = "#D1D5DB"
C_SIDEBAR_ACTV  = "#F5C800"
C_CONTENT_BG    = "#F3F4F6"
C_ACCENT_RED    = "#EF4444"
C_WHITE         = "#FFFFFF"
C_GRAY_400      = "#9CA3AF"
C_GRAY_700      = "#374151"


# ── Botón del sidebar con efecto activo ──────────────────────────────────────
class SidebarButton(QPushButton):
    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self._icon = icon
        self._text = text
        self._active = False
        self.setText(f"  {icon}   {text}")
        self.setFixedHeight(46)
        self.setCursor(Qt.PointingHandCursor)
        self._apply_style()

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


# ── Tarjeta del dashboard ────────────────────────────────────────────────────
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


# ── Ventana principal ────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self, usuario_data):
        super().__init__()
        self.usuario_data = usuario_data
        self.db = DatabaseConnection()
        self.id_caja_actual = None
        self._sidebar_buttons: dict[str, SidebarButton] = {}
        self.init_ui()
        self.verificar_caja_abierta()
        # Arrancar directamente en Caja
        self.show_caja()
        self._set_active_btn("Caja")

    # ── UI base ──────────────────────────────────────────────────────────────
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

        sidebar = self._crear_sidebar()
        main_layout.addWidget(sidebar)

        self.content_area = QWidget()
        self.content_area.setStyleSheet(f"background-color: {C_CONTENT_BG};")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(32, 28, 32, 28)
        self.content_area.setLayout(self.content_layout)
        main_layout.addWidget(self.content_area, 1)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _crear_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(255)
        sidebar.setStyleSheet(f"background-color: {C_SIDEBAR_BG};")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(4, 0)
        shadow.setColor(QColor(0, 0, 0, 80))
        sidebar.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 28, 14, 28)
        layout.setSpacing(4)

        # Logo
        logo_frame = QFrame()
        logo_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {C_AMARILLO};
                border-radius: 12px;
            }}
        """)
        logo_lay = QHBoxLayout(logo_frame)
        logo_lay.setContentsMargins(14, 8, 14, 8)
        logo_lay.setSpacing(8)

        tec_lbl = QLabel("TEC")
        tec_lbl.setFont(QFont("Arial Black", 15, QFont.Black))
        tec_lbl.setStyleSheet("color: #111111; background: transparent;")
        shop_lbl = QLabel("SHOP")
        shop_lbl.setFont(QFont("Arial", 15, QFont.Bold))
        shop_lbl.setStyleSheet("color: #333333; background: transparent;")
        dot_lbl = QLabel("🛒")
        dot_lbl.setFont(QFont("Segoe UI Emoji", 16))
        dot_lbl.setStyleSheet("background: transparent;")

        logo_lay.addWidget(dot_lbl)
        logo_lay.addWidget(tec_lbl)
        logo_lay.addWidget(shop_lbl)
        logo_lay.addStretch()
        layout.addWidget(logo_frame)

        layout.addSpacing(6)

        # Separador sutil
        sep_lbl = QLabel("MENÚ PRINCIPAL")
        sep_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        sep_lbl.setStyleSheet(f"color: #4B5563; letter-spacing: 1.5px; padding: 10px 6px 4px 6px;")
        layout.addWidget(sep_lbl)

        # Botones de navegación
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

        # Botón de Usuarios (solo para administradores)
        if self.usuario_data['rol'].lower() in ['admin', 'administrador']:
            nav_items.append(("🔐", "Usuarios", self.show_usuarios))

        for icon, texto, callback in nav_items:
            btn = SidebarButton(icon, texto)

            def _make_cb(cb, name):
                def _cb():
                    cb()
                    self._set_active_btn(name)
                return _cb

            btn.clicked.connect(_make_cb(callback, texto))
            self._sidebar_buttons[texto] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # ── Separador ──
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #1F2937;")
        layout.addWidget(line)
        layout.addSpacing(8)

        # ── Panel de usuario ──
        user_frame = QFrame()
        user_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #1F2937;
                border-radius: 14px;
            }}
        """)
        u_lay = QVBoxLayout(user_frame)
        u_lay.setContentsMargins(14, 14, 14, 14)
        u_lay.setSpacing(4)

        avatar = QLabel("👤  " + self.usuario_data['nombre'])
        avatar.setFont(QFont("Segoe UI", 12, QFont.Bold))
        avatar.setStyleSheet(f"color: {C_WHITE}; background: transparent;")
        u_lay.addWidget(avatar)

        rol_lbl = QLabel(f"🔑  {self.usuario_data['rol'].capitalize()}")
        rol_lbl.setFont(QFont("Segoe UI", 10))
        rol_lbl.setStyleSheet(f"color: {C_GRAY_400}; background: transparent;")
        u_lay.addWidget(rol_lbl)

        u_lay.addSpacing(6)

        logout_btn = QPushButton("⏻   Cerrar Sesión")
        logout_btn.setFixedHeight(36)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
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
        logout_btn.clicked.connect(self.cerrar_sesion)
        u_lay.addWidget(logout_btn)

        layout.addWidget(user_frame)
        sidebar.setLayout(layout)
        return sidebar

    def _set_active_btn(self, nombre: str):
        for name, btn in self._sidebar_buttons.items():
            btn.set_active(name == nombre)

    # ── Helpers ───────────────────────────────────────────────────────────────
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
        """Encabezado estándar para cada sección."""
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

    # ── Vistas ────────────────────────────────────────────────────────────────
    def show_dashboard(self):
        self.limpiar_contenido()

        hdr = self._page_header("🏠", f"Bienvenido, {self.usuario_data['nombre']}",
                                f"Rol: {self.usuario_data['rol'].capitalize()}")
        self.content_layout.addWidget(hdr)
        self.content_layout.addSpacing(20)

        # Tarjetas informativas
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
        from UI.apartados_ui import VentanaApartados
        widget = VentanaApartados(
            id_usuario_actual=self.usuario_data['id_usuario'],
            id_caja_actual=self.id_caja_actual
        )
        self.content_layout.addWidget(widget)

    def show_reportes(self):
        self.limpiar_contenido()
        hdr = self._page_header("📊", "Reportes", "Informes y análisis de ventas")
        self.content_layout.addWidget(hdr)
        self.content_layout.addSpacing(12)
        widget = VentanaReportes(self.usuario_data)
        self.content_layout.addWidget(widget)

    # ── Nueva vista para Usuarios (solo administrador) ─────────────────────────
    def show_usuarios(self):
        self.limpiar_contenido()
        hdr = self._page_header("🔐", "Usuarios", "Administrar cuentas del personal")
        self.content_layout.addWidget(hdr)
        self.content_layout.addSpacing(12)
        widget = VentanaGestionUsuarios(self.usuario_data)
        self.content_layout.addWidget(widget)

    # ── Señales y cierre ──────────────────────────────────────────────────────
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