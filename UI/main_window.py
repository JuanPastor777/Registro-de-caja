# UI/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                              QPushButton, QMessageBox, QHBoxLayout, QFrame,
                              QGraphicsDropShadowEffect, QSizePolicy, QToolButton)
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
        self.original_icon = icon
        self.original_text = text
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
                    font-size: 14px;
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
                    font-size: 14px;
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
        self.sidebar_width_expanded = 255
        self.sidebar_width_collapsed = 70
        self.sidebar_animation = None
        self.sidebar_collapsed = False
        self.leave_timer = QTimer()
        self.leave_timer.setSingleShot(True)
        self.leave_timer.timeout.connect(self.collapse_sidebar)

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

    # ── Sidebar colapsable ───────────────────────────────────────────────────
    def _crear_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(self.sidebar_width_expanded)
        sidebar.setStyleSheet(f"background-color: {C_SIDEBAR_BG}; border: none;")
        self.sidebar = sidebar

        # Botón de hamburguesa (colapsar/expandir)
        btn_menu = QToolButton()
        btn_menu.setText("☰")
        btn_menu.setFont(QFont("Segoe UI", 14, QFont.Bold))
        btn_menu.setStyleSheet(f"""
            QToolButton {{
                background-color: {C_AMARILLO};
                color: #111;
                border-radius: 8px;
                padding: 6px;
            }}
            QToolButton:hover {{
                background-color: {C_AMARILLO_DARK};
            }}
        """)
        btn_menu.setCursor(Qt.PointingHandCursor)
        btn_menu.clicked.connect(self.toggle_sidebar)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 18, 12, 18)
        layout.setSpacing(8)

        # Logo (sin fondo amarillo)
        self.logo_frame = QFrame()
        self.logo_frame.setStyleSheet("background-color: transparent; border: none;")
        logo_lay = QHBoxLayout(self.logo_frame)
        logo_lay.setContentsMargins(0, 0, 0, 0)

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

        layout.addWidget(btn_menu, alignment=Qt.AlignLeft)
        layout.addSpacing(4)
        layout.addWidget(self.logo_frame)
        layout.addSpacing(20)

        # Separador "MENÚ PRINCIPAL"
        self.sep_lbl = QLabel("MENÚ PRINCIPAL")
        self.sep_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.sep_lbl.setStyleSheet(f"color: #4B5563; letter-spacing: 1.5px; padding: 8px 4px 2px 4px;")
        layout.addWidget(self.sep_lbl)

        # Botones de navegación
        nav_items = [
            ("🏠", "Dashboard", self.show_dashboard),
            ("🛍️", "Ventas", self.show_ventas),
            ("👥", "Clientes", self.show_clientes),
            ("📦", "Productos", self.show_productos),
            ("🏦", "Caja", self.show_caja),
            ("📋", "Apartados", self.show_apartados),
        ]
        if self.usuario_data['rol'].lower() in ['gerente', 'supervisor', 'admin', 'administrador']:
            nav_items.append(("📊", "Reportes", self.show_reportes))
        if self.usuario_data['rol'].lower() in ['admin', 'administrador']:
            nav_items.append(("🔐", "Usuarios", self.show_usuarios))

        for icon, texto, callback in nav_items:
            btn = SidebarButton(icon, texto)
            btn.clicked.connect(lambda checked, cb=callback, name=texto: (cb(), self._set_active_btn(name)))
            self._sidebar_buttons[texto] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Panel de usuario (ARREGLADO)
        self.user_frame = QFrame()
        self.user_frame.setStyleSheet("background-color: #1F2937; border-radius: 14px;")
        self.user_frame.setFixedHeight(110)  # Altura fija para que se vea bien
        u_lay = QVBoxLayout(self.user_frame)
        u_lay.setContentsMargins(12, 12, 12, 12)
        u_lay.setSpacing(6)

        # Nombre de usuario
        nombre_completo = self.usuario_data.get('nombre', 'Usuario')
        # Truncar si es muy largo
        if len(nombre_completo) > 20:
            nombre_completo = nombre_completo[:18] + "..."
        
        self.avatar_lbl = QLabel(f"👤  {nombre_completo}")
        self.avatar_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.avatar_lbl.setStyleSheet(f"color: {C_WHITE}; background: transparent;")
        self.avatar_lbl.setWordWrap(True)
        
        # Rol de usuario
        rol_texto = self.usuario_data.get('rol', 'Usuario').capitalize()
        self.rol_lbl = QLabel(f"🔑  {rol_texto}")
        self.rol_lbl.setFont(QFont("Segoe UI", 9))
        self.rol_lbl.setStyleSheet(f"color: {C_GRAY_400}; background: transparent;")

        u_lay.addWidget(self.avatar_lbl)
        u_lay.addWidget(self.rol_lbl)
        u_lay.addStretch()

        # Botón de cerrar sesión
        logout_btn = QPushButton("⏻  Cerrar Sesión")
        logout_btn.setFixedHeight(32)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {C_ACCENT_RED};
                border: 1px solid #3B1414;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #3B1414;
            }}
        """)
        logout_btn.clicked.connect(self.cerrar_sesion)
        u_lay.addWidget(logout_btn)

        layout.addWidget(self.user_frame)
        layout.addSpacing(8)

        sidebar.setLayout(layout)

        # Eventos para expandir al pasar el mouse
        sidebar.setMouseTracking(True)
        sidebar.enterEvent = self.sidebar_enter_event
        sidebar.leaveEvent = self.sidebar_leave_event

        return sidebar

    def toggle_sidebar(self):
        target_width = self.sidebar_width_collapsed if not self.sidebar_collapsed else self.sidebar_width_expanded
        self.animate_sidebar(target_width)
        self.sidebar_collapsed = not self.sidebar_collapsed
        self.update_sidebar_ui(self.sidebar_collapsed)

    def animate_sidebar(self, target_width):
        if self.sidebar_animation and self.sidebar_animation.state() == QPropertyAnimation.Running:
            self.sidebar_animation.stop()
        self.sidebar_animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.sidebar_animation.setDuration(200)
        self.sidebar_animation.setStartValue(self.sidebar.width())
        self.sidebar_animation.setEndValue(target_width)
        self.sidebar_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.sidebar_animation.start()

    def update_sidebar_ui(self, collapsed):
        # Mostrar/ocultar textos de los botones
        for btn in self._sidebar_buttons.values():
            if collapsed:
                btn.setText(f"  {btn.original_icon}   ")
                btn.setToolTip(btn.original_text)
            else:
                btn.setText(f"  {btn.original_icon}   {btn.original_text}")
                btn.setToolTip("")
        
        # Ajustar logo
        if collapsed:
            if not self.logo_pixmap.isNull():
                self.logo_label.setPixmap(self.logo_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.logo_label.setFont(QFont("Segoe UI Emoji", 22))
            # Ajustar panel de usuario para colapsado
            self.user_frame.setFixedHeight(70)
            self.avatar_lbl.setText("👤")
            self.rol_lbl.hide()
            # Cambiar texto del botón logout
            for i in range(self.user_frame.layout().count()):
                widget = self.user_frame.layout().itemAt(i).widget()
                if isinstance(widget, QPushButton):
                    widget.setText("⏻")
                    widget.setFixedWidth(32)
                    widget.setFixedHeight(32)
                    break
        else:
            if not self.logo_pixmap.isNull():
                self.logo_label.setPixmap(self.logo_pixmap.scaled(160, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.logo_label.setFont(QFont("Segoe UI Emoji", 28))
            # Restaurar panel de usuario para expandido
            self.user_frame.setFixedHeight(110)
            nombre_completo = self.usuario_data.get('nombre', 'Usuario')
            if len(nombre_completo) > 20:
                nombre_completo = nombre_completo[:18] + "..."
            self.avatar_lbl.setText(f"👤  {nombre_completo}")
            self.rol_lbl.show()
            # Restaurar texto del botón logout
            for i in range(self.user_frame.layout().count()):
                widget = self.user_frame.layout().itemAt(i).widget()
                if isinstance(widget, QPushButton):
                    widget.setText("⏻  Cerrar Sesión")
                    widget.setFixedWidth(9999)  # Reset to auto
                    widget.setFixedHeight(32)
                    break
        
        self.sep_lbl.setVisible(not collapsed)

    def sidebar_enter_event(self, event):
        if self.sidebar_collapsed:
            self.leave_timer.stop()
            self.animate_sidebar(self.sidebar_width_expanded)
            self.update_sidebar_ui(False)

    def sidebar_leave_event(self, event):
        if self.sidebar_collapsed:
            self.leave_timer.start(500)

    def collapse_sidebar(self):
        if self.sidebar_collapsed:
            self.animate_sidebar(self.sidebar_width_collapsed)
            self.update_sidebar_ui(True)

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