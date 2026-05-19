# UI/ventas_ui.py

import sys
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QGroupBox,
    QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox,
    QMessageBox, QHeaderView, QDialog, QDialogButtonBox,
    QCheckBox, QFrame, QSizePolicy, QScrollArea, QButtonGroup,
    QRadioButton, QGridLayout, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.conexion import DatabaseConnection
from services.venta_service import ServiceVenta


# =========================================================
# ESTILOS GLOBALES
# =========================================================

ESTILO_GLOBAL = """
    QWidget {
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
        background-color: #F8FAFC;
        color: #1E293B;
    }
    QGroupBox {
        font-weight: bold;
        font-size: 13px;
        border: 1.5px solid #E2E8F0;
        border-radius: 10px;
        margin-top: 10px;
        padding: 10px;
        background: white;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        top: -1px;
        padding: 0 6px;
        color: #475569;
        background: white;
    }
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
        border: 1.5px solid #CBD5E1;
        border-radius: 7px;
        padding: 7px 10px;
        background: white;
        min-height: 20px;
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
        border-color: #6366F1;
    }
    QPushButton {
        border-radius: 7px;
        padding: 8px 16px;
        font-weight: 600;
        border: none;
        background: #E2E8F0;
        color: #475569;
    }
    QPushButton:hover {
        background: #CBD5E1;
    }
    QTableWidget {
        border: 1.5px solid #E2E8F0;
        border-radius: 8px;
        background: white;
        gridline-color: #F1F5F9;
    }
    QTableWidget::item {
        padding: 6px;
    }
    QTableWidget::item:selected {
        background: #EEF2FF;
        color: #3730A3;
    }
    QHeaderView::section {
        background: #F1F5F9;
        color: #475569;
        font-weight: 700;
        border: none;
        padding: 8px;
        font-size: 12px;
    }
    QCheckBox {
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1.5px solid #CBD5E1;
    }
    QCheckBox::indicator:checked {
        background: #f1c40f;
        border-color: #f1c40f
    }
    QScrollBar:vertical {
        background: #F1F5F9;
        width: 8px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: #CBD5E1;
        border-radius: 4px;
    }
"""

BTN_PRIMARY = """
    QPushButton {
        background: #F5C800;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 700;
        font-size: 14px;
    }
    QPushButton:hover { background: #4F46E5; }
    QPushButton:pressed { background: #4338CA; }
"""

BTN_SUCCESS = """
    QPushButton {
        background: #10B981;
        color: white;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 700;
        font-size: 15px;
    }
    QPushButton:hover { background: #059669; }
    QPushButton:pressed { background: #047857; }
"""

BTN_DANGER = """
    QPushButton {
        background: #FEE2E2;
        color: #DC2626;
        border-radius: 6px;
        padding: 4px 10px;
        font-weight: 700;
        font-size: 13px;
    }
    QPushButton:hover { background: #FECACA; }
"""

BTN_SECONDARY = """
    QPushButton {
        background: #F1F5F9;
        color: #475569;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        border: 1.5px solid #E2E8F0;
    }
    QPushButton:hover { background: #E2E8F0; }
"""

BTN_OUTLINE = """
    QPushButton {
        background: white;
        color: #6366F1;
        border-radius: 7px;
        padding: 7px 14px;
        font-weight: 600;
        border: 1.5px solid #6366F1;
    }
    QPushButton:hover { background: #EEF2FF; }
"""


# =========================================================
# DIÁLOGO: NUEVO CLIENTE RÁPIDO
# =========================================================

class DialogoNuevoCliente(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.cliente_creado = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Nuevo Cliente")
        self.setFixedWidth(420)
        self.setStyleSheet(ESTILO_GLOBAL)

        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        titulo = QLabel("Agregar Nuevo Cliente")
        titulo.setFont(QFont("Segoe UI", 15, QFont.Bold))
        titulo.setStyleSheet("color: #1E293B;")
        layout.addWidget(titulo)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(12)

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre del cliente")
        form.addRow("Nombre *", self.input_nombre)

        self.input_apellido = QLineEdit()
        self.input_apellido.setPlaceholderText("Apellido")
        form.addRow("Apellido", self.input_apellido)

        self.input_telefono = QLineEdit()
        self.input_telefono.setPlaceholderText("Teléfono")
        form.addRow("Teléfono", self.input_telefono)

        layout.addLayout(form)

        botones = QHBoxLayout()
        botones.setSpacing(10)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(BTN_SECONDARY)
        btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(btn_cancelar)

        btn_guardar = QPushButton("Guardar Cliente")
        btn_guardar.setStyleSheet(BTN_PRIMARY)
        btn_guardar.clicked.connect(self.guardar)
        botones.addWidget(btn_guardar)

        layout.addLayout(botones)
        self.setLayout(layout)

    def guardar(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
            return

        apellido = self.input_apellido.text().strip()
        telefono = self.input_telefono.text().strip()

        try:
            query = """
                INSERT INTO public.cliente (nombre, apellido, telefono)
                VALUES (%s, %s, %s)
                RETURNING id_cliente
            """
            resultado = self.db.fetch_one(query, (nombre, apellido or None, telefono or None))
            if resultado:
                self.cliente_creado = {
                    'id_cliente': resultado['id_cliente'],
                    'nombre': nombre,
                    'apellido': apellido,
                    'telefono': telefono
                }
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "No se pudo guardar el cliente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# =========================================================
# DIÁLOGO: NUEVO PRODUCTO RÁPIDO
# =========================================================

class DialogoNuevoProducto(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.producto_creado = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Nuevo Producto")
        self.setFixedWidth(460)
        self.setStyleSheet(ESTILO_GLOBAL)

        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        titulo = QLabel("Agregar Nuevo Producto")
        titulo.setFont(QFont("Segoe UI", 15, QFont.Bold))
        titulo.setStyleSheet("color: #1E293B;")
        layout.addWidget(titulo)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(12)

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre del producto")
        form.addRow("Nombre *", self.input_nombre)

        self.input_marca = QLineEdit()
        self.input_marca.setPlaceholderText("Marca")
        form.addRow("Marca", self.input_marca)

        self.input_modelo = QLineEdit()
        self.input_modelo.setPlaceholderText("Modelo")
        form.addRow("Modelo", self.input_modelo)

        self.input_descripcion = QLineEdit()
        self.input_descripcion.setPlaceholderText("Descripción breve")
        form.addRow("Descripción", self.input_descripcion)

        self.input_precio = QDoubleSpinBox()
        self.input_precio.setMinimum(0.0)
        self.input_precio.setMaximum(9999999.99)
        self.input_precio.setDecimals(2)
        self.input_precio.setPrefix("Q ")
        self.input_precio.setValue(0.0)
        form.addRow("Precio *", self.input_precio)

        layout.addLayout(form)

        botones = QHBoxLayout()
        botones.setSpacing(10)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(BTN_SECONDARY)
        btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(btn_cancelar)

        btn_guardar = QPushButton("Guardar Producto")
        btn_guardar.setStyleSheet(BTN_PRIMARY)
        btn_guardar.clicked.connect(self.guardar)
        botones.addWidget(btn_guardar)

        layout.addLayout(botones)
        self.setLayout(layout)

    def guardar(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre del producto es obligatorio.")
            return

        precio = self.input_precio.value()
        if precio <= 0:
            QMessageBox.warning(self, "Error", "El precio debe ser mayor a cero.")
            return

        marca = self.input_marca.text().strip()
        modelo = self.input_modelo.text().strip()
        descripcion = self.input_descripcion.text().strip()

        try:
            query = """
                INSERT INTO public.producto (nombre, marca, modelo, descripcion, precio_costo)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_producto
            """
            resultado = self.db.fetch_one(query, (
                nombre, marca or None, modelo or None,
                descripcion or None, precio
            ))
            if resultado:
                self.producto_creado = {
                    'id_producto': resultado['id_producto'],
                    'nombre': nombre,
                    'marca': marca,
                    'modelo': modelo,
                    'descripcion': descripcion,
                    'precio_costo': precio
                }
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "No se pudo guardar el producto.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# =========================================================
# DIÁLOGO: PAGOS MIXTOS
# =========================================================

class DialogoPagoMixto(QDialog):
    """Permite registrar un pago distribuido en múltiples formas de pago"""

    def __init__(self, total, parent=None):
        super().__init__(parent)
        self.total = float(total)
        self.resultado_pagos = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Pago Mixto")
        self.setFixedWidth(440)
        self.setStyleSheet(ESTILO_GLOBAL)

        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        titulo = QLabel("Distribución de Pago Mixto")
        titulo.setFont(QFont("Segoe UI", 14, QFont.Bold))
        titulo.setStyleSheet("color: #1E293B;")
        layout.addWidget(titulo)

        info = QLabel(f"Total a pagar: Q {self.total:.2f}")
        info.setStyleSheet("color: #6366F1; font-weight: 700; font-size: 15px;")
        layout.addWidget(info)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(10)

        self.spin_efectivo = QDoubleSpinBox()
        self.spin_efectivo.setMaximum(9999999)
        self.spin_efectivo.setPrefix("Q ")
        self.spin_efectivo.setDecimals(2)
        self.spin_efectivo.valueChanged.connect(self._actualizar_restante)
        form.addRow("💵 Efectivo:", self.spin_efectivo)

        self.spin_tarjeta = QDoubleSpinBox()
        self.spin_tarjeta.setMaximum(9999999)
        self.spin_tarjeta.setPrefix("Q ")
        self.spin_tarjeta.setDecimals(2)
        self.spin_tarjeta.valueChanged.connect(self._actualizar_restante)
        form.addRow("💳 Tarjeta:", self.spin_tarjeta)

        self.spin_transferencia = QDoubleSpinBox()
        self.spin_transferencia.setMaximum(9999999)
        self.spin_transferencia.setPrefix("Q ")
        self.spin_transferencia.setDecimals(2)
        self.spin_transferencia.valueChanged.connect(self._actualizar_restante)
        form.addRow("🏦 Transferencia:", self.spin_transferencia)

        self.spin_deposito = QDoubleSpinBox()
        self.spin_deposito.setMaximum(9999999)
        self.spin_deposito.setPrefix("Q ")
        self.spin_deposito.setDecimals(2)
        self.spin_deposito.valueChanged.connect(self._actualizar_restante)
        form.addRow("📥 Depósito:", self.spin_deposito)

        layout.addLayout(form)

        self.lbl_restante = QLabel(f"Restante: Q {self.total:.2f}")
        self.lbl_restante.setStyleSheet("font-weight: 700; font-size: 13px; color: #DC2626;")
        layout.addWidget(self.lbl_restante)

        botones = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(BTN_SECONDARY)
        btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(btn_cancelar)

        btn_ok = QPushButton("Confirmar Pago")
        btn_ok.setStyleSheet(BTN_SUCCESS)
        btn_ok.clicked.connect(self._confirmar)
        botones.addWidget(btn_ok)

        layout.addLayout(botones)
        self.setLayout(layout)

    def _actualizar_restante(self):
        suma = (self.spin_efectivo.value() + self.spin_tarjeta.value() +
                self.spin_transferencia.value() + self.spin_deposito.value())
        restante = self.total - suma
        self.lbl_restante.setText(f"Restante: Q {max(restante, 0):.2f}")
        color = "#10B981" if abs(restante) < 0.01 else "#DC2626"
        self.lbl_restante.setStyleSheet(f"font-weight: 700; font-size: 13px; color: {color};")

    def _confirmar(self):
        suma = (self.spin_efectivo.value() + self.spin_tarjeta.value() +
                self.spin_transferencia.value() + self.spin_deposito.value())
        if abs(suma - self.total) > 0.01:
            QMessageBox.warning(self, "Error",
                f"La suma de los pagos (Q {suma:.2f}) no coincide con el total (Q {self.total:.2f}).")
            return
        self.resultado_pagos = {
            'EF': self.spin_efectivo.value(),
            'TC/TD': self.spin_tarjeta.value(),
            'TF': self.spin_transferencia.value(),
            'DP': self.spin_deposito.value(),
        }
        self.accept()


# =========================================================
# DIÁLOGO: SELECCIONAR CLIENTE
# =========================================================

class DialogoSeleccionCliente(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.cliente_seleccionado = None
        self.clientes_data = []
        self.init_ui()
        self.cargar_clientes()

    def init_ui(self):
        self.setWindowTitle("Seleccionar Cliente")
        self.resize(680, 520)
        self.setStyleSheet(ESTILO_GLOBAL)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título + botón nuevo cliente
        top = QHBoxLayout()
        titulo = QLabel("Seleccionar Cliente")
        titulo.setFont(QFont("Segoe UI", 15, QFont.Bold))
        top.addWidget(titulo)
        top.addStretch()

        btn_nuevo = QPushButton("+ Nuevo Cliente")
        btn_nuevo.setStyleSheet(BTN_OUTLINE)
        btn_nuevo.clicked.connect(self.abrir_nuevo_cliente)
        top.addWidget(btn_nuevo)
        layout.addLayout(top)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Buscar por nombre o teléfono...")
        self.search_input.textChanged.connect(self.buscar_clientes)
        layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Teléfono"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.seleccionar_cliente)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        lbl_hint = QLabel("💡 Doble clic para seleccionar rápidamente")
        lbl_hint.setStyleSheet("color: #94A3B8; font-size: 11px;")
        layout.addWidget(lbl_hint)

        botones = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(BTN_SECONDARY)
        btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(btn_cancelar)

        btn_ok = QPushButton("Seleccionar")
        btn_ok.setStyleSheet(BTN_PRIMARY)
        btn_ok.clicked.connect(self.seleccionar_cliente)
        botones.addWidget(btn_ok)

        layout.addLayout(botones)
        self.setLayout(layout)

    def abrir_nuevo_cliente(self):
        dialog = DialogoNuevoCliente(self)
        if dialog.exec_():
            self.cliente_seleccionado = dialog.cliente_creado
            self.accept()

    def cargar_clientes(self):
        query = """
            SELECT id_cliente, nombre, apellido, telefono
            FROM public.cliente ORDER BY nombre
        """
        self.clientes_data = self.db.fetch_all(query) or []
        self.actualizar_tabla(self.clientes_data)

    def actualizar_tabla(self, clientes):
        self.table.setRowCount(len(clientes))
        for i, c in enumerate(clientes):
            self.table.setItem(i, 0, QTableWidgetItem(str(c['id_cliente'])))
            self.table.setItem(i, 1, QTableWidgetItem(c.get('nombre', '')))
            self.table.setItem(i, 2, QTableWidgetItem(c.get('apellido', '') or ''))
            self.table.setItem(i, 3, QTableWidgetItem(c.get('telefono', '') or ''))

    def buscar_clientes(self):
        texto = self.search_input.text().lower()
        if not texto:
            self.actualizar_tabla(self.clientes_data)
            return
        filtrados = [
            c for c in self.clientes_data
            if texto in f"{c.get('nombre','')} {c.get('apellido','')}".lower()
            or texto in (c.get('telefono') or '').lower()
        ]
        self.actualizar_tabla(filtrados)

    def seleccionar_cliente(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un cliente de la lista.")
            return
        cliente_id = int(self.table.item(row, 0).text())
        for c in self.clientes_data:
            if c['id_cliente'] == cliente_id:
                self.cliente_seleccionado = c
                break
        self.accept()


# =========================================================
# VENTANA PRINCIPAL VENTAS
# =========================================================

FORMAS_PAGO = {
    "EF":    "💵  Efectivo",
    "TC/TD": "💳  Tarjeta (Crédito/Débito)",
    "TF":    "🏦  Transferencia",
    "DP":    "📥  Depósito",
    "COD":   "📦  Contra Entrega (COD)",
}


class VentanasVentas(QWidget):

    def __init__(self, usuario_data=None, id_caja_actual=None):
        super().__init__()
        self.setStyleSheet(ESTILO_GLOBAL)
        self.db = DatabaseConnection()
        self.usuario_data = usuario_data or {}
        self.id_usuario = self.usuario_data.get('id_usuario', 1)
        self.service = ServiceVenta(id_usuario_actual=self.id_usuario)
        self.id_caja_actual = id_caja_actual
        self.cliente_actual = None
        self.carrito = []
        self.productos_data = []
        self.empresas_data = []
        self.init_ui()
        self.cargar_productos()
        self.cargar_empresas()

    # =====================================================
    # UI PRINCIPAL
    # =====================================================

    def init_ui(self):
        self.setWindowTitle("Ventas — Tech Shop")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        # HEADER
        header = QHBoxLayout()
        titulo = QLabel(" Nueva Venta")
        titulo.setFont(QFont("Segoe UI", 20, QFont.Bold))
        titulo.setStyleSheet("color: #1E293B;")
        header.addWidget(titulo)
        header.addStretch()

        # Badge estado caja
        self.lbl_caja = QLabel("⚡ Verificando caja...")
        self.lbl_caja.setStyleSheet("""
            background: #FEF3C7; color: #92400E;
            border-radius: 12px; padding: 4px 14px;
            font-weight: 600; font-size: 12px;
        """)
        header.addWidget(self.lbl_caja)
        layout.addLayout(header)

        QTimer.singleShot(200, self.verificar_estado_caja)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(sep)

        # CLIENTE
        layout.addWidget(self.crear_panel_cliente())

        # CONTENIDO PRINCIPAL
        contenido = QHBoxLayout()
        contenido.setSpacing(16)
        contenido.addWidget(self.crear_panel_izquierdo(), 1)
        contenido.addWidget(self.crear_panel_carrito(), 2)
        layout.addLayout(contenido)

        self.setLayout(layout)

    def verificar_estado_caja(self):
        resultado = self.service.verificar_caja_abierta()
        if resultado['success']:
            self.lbl_caja.setText("Caja abierta")
            self.lbl_caja.setStyleSheet("""
                background: #D1FAE5; color: #065F46;
                border-radius: 12px; padding: 4px 14px;
                font-weight: 600; font-size: 12px;
            """)
        else:
            self.lbl_caja.setText("Sin caja abierta")
            self.lbl_caja.setStyleSheet("""
                background: #FEE2E2; color: #991B1B;
                border-radius: 12px; padding: 4px 14px;
                font-weight: 600; font-size: 12px;
            """)

    # =====================================================
    # PANEL CLIENTE
    # =====================================================

    def crear_panel_cliente(self):
        box = QGroupBox("Cliente")
        layout = QHBoxLayout()
        layout.setSpacing(12)

        self.lbl_cliente = QLabel("Ningún cliente seleccionado")
        self.lbl_cliente.setStyleSheet("""
            padding: 10px 16px;
            background: #F8FAFC;
            border: 1.5px dashed #CBD5E1;
            border-radius: 8px;
            color: #94A3B8;
            font-size: 13px;
        """)
        self.lbl_cliente.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.lbl_cliente)

        btn_sel = QPushButton(" Seleccionar Cliente")
        btn_sel.setStyleSheet(BTN_PRIMARY)
        btn_sel.setFixedHeight(40)
        btn_sel.clicked.connect(self.seleccionar_cliente)
        layout.addWidget(btn_sel)

        btn_limpiar_cliente = QPushButton("✕")
        btn_limpiar_cliente.setFixedSize(40, 40)
        btn_limpiar_cliente.setStyleSheet(BTN_DANGER)
        btn_limpiar_cliente.setToolTip("Quitar cliente")
        btn_limpiar_cliente.clicked.connect(self.quitar_cliente)
        layout.addWidget(btn_limpiar_cliente)

        box.setLayout(layout)
        return box

    # =====================================================
    # PANEL IZQUIERDO (Producto + Documento + Envío)
    # =====================================================

    def crear_panel_izquierdo(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.crear_panel_producto())
        layout.addWidget(self.crear_panel_documento())
        layout.addWidget(self.crear_panel_envio())
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    # =====================================================
    # PANEL PRODUCTO
    # =====================================================

    def crear_panel_producto(self):
        box = QGroupBox("Producto")
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Búsqueda + botón nuevo producto
        busqueda_row = QHBoxLayout()
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("🔍  Buscar producto...")
        self.input_busqueda.textChanged.connect(self.buscar_productos)
        busqueda_row.addWidget(self.input_busqueda)

        btn_nuevo_prod = QPushButton("+ Nuevo")
        btn_nuevo_prod.setStyleSheet(BTN_OUTLINE)
        btn_nuevo_prod.setFixedHeight(36)
        btn_nuevo_prod.setToolTip("Crear nuevo producto rápidamente")
        btn_nuevo_prod.clicked.connect(self.abrir_nuevo_producto)
        busqueda_row.addWidget(btn_nuevo_prod)
        layout.addLayout(busqueda_row)

        self.combo_productos = QComboBox()
        self.combo_productos.setMaxVisibleItems(12)
        self.combo_productos.currentIndexChanged.connect(self.producto_seleccionado)
        layout.addWidget(self.combo_productos)

        # Precio (solo lectura, se rellena automático)
        precio_row = QHBoxLayout()
        lbl = QLabel("Precio unitario:")
        lbl.setStyleSheet("color: #64748B; font-size: 12px;")
        precio_row.addWidget(lbl)

        self.lbl_precio_producto = QLabel("Q 0.00")
        self.lbl_precio_producto.setStyleSheet("""
            font-weight: 700; font-size: 14px; color: #6366F1;
            background: #EEF2FF; border-radius: 6px;
            padding: 4px 12px;
        """)
        precio_row.addWidget(self.lbl_precio_producto)
        precio_row.addStretch()
        layout.addLayout(precio_row)

        # Cantidad y descuento
        fila = QHBoxLayout()
        fila.setSpacing(10)

        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Cantidad"))
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(1)
        self.spin_cantidad.setMaximum(9999)
        self.spin_cantidad.valueChanged.connect(self.actualizar_preview_subtotal)
        col1.addWidget(self.spin_cantidad)
        fila.addLayout(col1)

        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Modificar precio (Q)"))
        self.spin_descuento = QDoubleSpinBox()
        self.spin_descuento.setMaximum(999999)
        self.spin_descuento.setPrefix("Q ")
        self.spin_descuento.valueChanged.connect(self.actualizar_preview_subtotal)
        col2.addWidget(self.spin_descuento)
        fila.addLayout(col2)

        layout.addLayout(fila)

        # Preview subtotal
        self.lbl_preview = QLabel("Subtotal: Q 0.00")
        self.lbl_preview.setStyleSheet("""
            color: #6366F1; font-weight: 600;
            font-size: 12px; padding: 2px 0;
        """)
        layout.addWidget(self.lbl_preview)

        # Botón agregar
        btn_add = QPushButton("＋  Agregar al Carrito")
        btn_add.setStyleSheet(BTN_PRIMARY)
        btn_add.setMinimumHeight(42)
        btn_add.clicked.connect(self.agregar_producto)
        layout.addWidget(btn_add)

        box.setLayout(layout)
        return box

    # =====================================================
    # PANEL DOCUMENTO
    # =====================================================

    def crear_panel_documento(self):
        box = QGroupBox("Documento")
        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Tipo: FAC / REC
        tipo_layout = QVBoxLayout()
        tipo_layout.addWidget(QLabel("Tipo:"))
        tipo_btns = QHBoxLayout()
        tipo_btns.setSpacing(8)

        self.btn_fac = QPushButton("📄  Factura")
        self.btn_fac.setCheckable(True)
        self.btn_fac.setChecked(True)
        self.btn_fac.clicked.connect(lambda: self.set_tipo_doc("FAC"))

        self.btn_rec = QPushButton("🧾  Recibo")
        self.btn_rec.setCheckable(True)
        self.btn_rec.clicked.connect(lambda: self.set_tipo_doc("REC"))

        self._tipo_doc = "FAC"
        self.actualizar_estilo_tipo_doc()

        tipo_btns.addWidget(self.btn_fac)
        tipo_btns.addWidget(self.btn_rec)
        tipo_layout.addLayout(tipo_btns)
        layout.addLayout(tipo_layout)

        # Número de documento
        num_layout = QVBoxLayout()
        num_layout.addWidget(QLabel("Número de documento:"))
        self.input_num_doc = QLineEdit()
        self.input_num_doc.setPlaceholderText("Ej. 001-2025-00123")
        num_layout.addWidget(self.input_num_doc)
        layout.addLayout(num_layout)

        box.setLayout(layout)
        return box

    def set_tipo_doc(self, tipo):
        self._tipo_doc = tipo
        self.btn_fac.setChecked(tipo == "FAC")
        self.btn_rec.setChecked(tipo == "REC")
        self.actualizar_estilo_tipo_doc()

    def actualizar_estilo_tipo_doc(self):
        activo = """
            QPushButton {
                background: #F5C800; color: white;
                border-radius: 7px; padding: 7px 14px;
                font-weight: 700; border: none;
            }
        """
        inactivo = """
            QPushButton {
                background: #F1F5F9; color: #64748B;
                border-radius: 7px; padding: 7px 14px;
                font-weight: 600; border: 1.5px solid #E2E8F0;
            }
            QPushButton:hover { background: #E2E8F0; }
        """
        self.btn_fac.setStyleSheet(activo if self._tipo_doc == "FAC" else inactivo)
        self.btn_rec.setStyleSheet(activo if self._tipo_doc == "REC" else inactivo)

    # =====================================================
    # PANEL ENVÍO
    # =====================================================

    def crear_panel_envio(self):
        self.box_envio = QGroupBox("Envío")
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Toggle envío
        toggle = QHBoxLayout()
        self.check_envio = QCheckBox("Esta venta es un envío")
        self.check_envio.setStyleSheet("font-weight: 600;")
        self.check_envio.toggled.connect(self.toggle_envio)
        toggle.addWidget(self.check_envio)
        toggle.addStretch()
        layout.addLayout(toggle)

        # Contenido envío (se muestra/oculta)
        self.frame_envio = QFrame()
        envio_layout = QFormLayout()
        envio_layout.setSpacing(10)

        self.combo_empresa = QComboBox()
        self.combo_empresa.setMinimumWidth(180)
        envio_layout.addRow("Empresa:", self.combo_empresa)

        self.input_guia = QLineEdit()
        self.input_guia.setPlaceholderText("Número de guía (opcional)")
        envio_layout.addRow("N° Guía:", self.input_guia)

        self.spin_envio = QDoubleSpinBox()
        self.spin_envio.setMaximum(99999)
        self.spin_envio.setPrefix("Q ")
        self.spin_envio.valueChanged.connect(self.actualizar_total)
        envio_layout.addRow("Costo envío:", self.spin_envio)

        self.frame_envio.setLayout(envio_layout)
        self.frame_envio.setVisible(False)
        layout.addWidget(self.frame_envio)

        self.box_envio.setLayout(layout)
        return self.box_envio

    def toggle_envio(self, checked):
        self.frame_envio.setVisible(checked)

    def cargar_empresas(self):
        empresas = self.service.listar_empresas_envio()
        self.empresas_data = empresas
        self.combo_empresa.clear()
        for e in empresas:
            self.combo_empresa.addItem(e['nombre'], e['id_empresa'])

    # =====================================================
    # PANEL CARRITO
    # =====================================================

    def crear_panel_carrito(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # Título
        top = QHBoxLayout()
        lbl = QLabel("Carrito de Venta")
        lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        top.addWidget(lbl)
        top.addStretch()
        self.lbl_items = QLabel("0 productos")
        self.lbl_items.setStyleSheet("""
            background: #EEF2FF; color: #4F46E5;
            border-radius: 10px; padding: 2px 10px;
            font-weight: 600; font-size: 12px;
        """)
        top.addWidget(self.lbl_items)
        layout.addLayout(top)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Producto", "Cant.", "Precio Unit.", "Descuento", "Subtotal", ""
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 50)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(200)
        layout.addWidget(self.table)

        # Forma de pago + ¿Pagado?
        pago_box = QGroupBox("Pago")
        pago_layout = QHBoxLayout()
        pago_layout.setSpacing(20)

        # Forma pago
        fp_col = QVBoxLayout()
        fp_col.addWidget(QLabel("Forma de pago:"))
        self.combo_pago = QComboBox()
        for codigo, label in FORMAS_PAGO.items():
            self.combo_pago.addItem(label, codigo)
        self.combo_pago.addItem("🔀  Pago Mixto", "MIXTO")
        self.combo_pago.setMinimumWidth(220)
        self.combo_pago.currentIndexChanged.connect(self.pago_cambiado)
        fp_col.addWidget(self.combo_pago)
        pago_layout.addLayout(fp_col)

        # Pagado
        pagado_col = QVBoxLayout()
        pagado_col.addWidget(QLabel("Estado:"))
        self.check_pagado = QCheckBox("Producto ya pagado")
        self.check_pagado.setChecked(True)
        self.check_pagado.setStyleSheet("font-weight: 600;")
        pagado_col.addWidget(self.check_pagado)
        pago_layout.addLayout(pagado_col)

        pago_layout.addStretch()
        pago_box.setLayout(pago_layout)
        layout.addWidget(pago_box)

        # Totales
        totales_frame = QFrame()
        totales_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1.5px solid #E2E8F0;
                border-radius: 10px;
                padding: 6px;
            }
        """)
        totales_layout = QVBoxLayout()
        totales_layout.setSpacing(4)

        subtotal_row = QHBoxLayout()
        subtotal_row.addWidget(QLabel("Subtotal productos:"))
        subtotal_row.addStretch()
        self.lbl_subtotal = QLabel("Q 0.00")
        self.lbl_subtotal.setStyleSheet("color: #64748B;")
        subtotal_row.addWidget(self.lbl_subtotal)
        totales_layout.addLayout(subtotal_row)

        envio_row = QHBoxLayout()
        envio_row.addWidget(QLabel("Costo envío:"))
        envio_row.addStretch()
        self.lbl_envio_total = QLabel("Q 0.00")
        self.lbl_envio_total.setStyleSheet("color: #64748B;")
        envio_row.addWidget(self.lbl_envio_total)
        totales_layout.addLayout(envio_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #E2E8F0;")
        totales_layout.addWidget(sep)

        total_row = QHBoxLayout()
        lbl_t = QLabel("TOTAL:")
        lbl_t.setFont(QFont("Segoe UI", 14, QFont.Bold))
        total_row.addWidget(lbl_t)
        total_row.addStretch()
        self.lbl_total = QLabel("Q 0.00")
        self.lbl_total.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.lbl_total.setStyleSheet("color: #10B981;")
        total_row.addWidget(self.lbl_total)
        totales_layout.addLayout(total_row)

        totales_frame.setLayout(totales_layout)
        layout.addWidget(totales_frame)

        # Botones finales
        botones = QHBoxLayout()
        botones.setSpacing(10)

        btn_limpiar = QPushButton(" Limpiar Todo")
        btn_limpiar.setStyleSheet(BTN_SECONDARY)
        btn_limpiar.setMinimumHeight(44)
        btn_limpiar.clicked.connect(self.confirmar_limpiar)
        botones.addWidget(btn_limpiar)

        btn_finalizar = QPushButton("✔  Finalizar Venta")
        btn_finalizar.setStyleSheet(BTN_SUCCESS)
        btn_finalizar.setMinimumHeight(44)
        btn_finalizar.clicked.connect(self.finalizar_venta)
        botones.addWidget(btn_finalizar)

        layout.addLayout(botones)
        widget.setLayout(layout)
        return widget

    def pago_cambiado(self):
        forma = self.combo_pago.currentData()
        if forma == 'COD':
            self.check_pagado.setChecked(False)
        else:
            self.check_pagado.setChecked(True)

    # =====================================================
    # LÓGICA CLIENTE
    # =====================================================

    def abrir_nuevo_producto(self):
        """Abre diálogo para crear un producto nuevo rápidamente"""
        dialog = DialogoNuevoProducto(self)
        if dialog.exec_():
            prod = dialog.producto_creado
            if prod:
                self.productos_data.append(prod)
                self._llenar_combo(self.productos_data)
                # Seleccionar el recién creado
                for i in range(self.combo_productos.count()):
                    d = self.combo_productos.itemData(i)
                    if d and d.get('id_producto') == prod['id_producto']:
                        self.combo_productos.setCurrentIndex(i)
                        break

    def seleccionar_cliente(self):
        dialog = DialogoSeleccionCliente(self)
        if dialog.exec_():
            self.cliente_actual = dialog.cliente_seleccionado
            nombre = (
                f"{self.cliente_actual.get('nombre', '')} "
                f"{self.cliente_actual.get('apellido', '')}"
            ).strip()
            self.lbl_cliente.setText(f"👤  {nombre}")
            self.lbl_cliente.setStyleSheet("""
                padding: 10px 16px;
                background: #EEF2FF;
                border: 1.5px solid #A5B4FC;
                border-radius: 8px;
                color: #3730A3;
                font-weight: 600;
                font-size: 13px;
            """)

    def quitar_cliente(self):
        self.cliente_actual = None
        self.lbl_cliente.setText("Ningún cliente seleccionado")
        self.lbl_cliente.setStyleSheet("""
            padding: 10px 16px;
            background: #F8FAFC;
            border: 1.5px dashed #CBD5E1;
            border-radius: 8px;
            color: #94A3B8;
            font-size: 13px;
        """)

    # =====================================================
    # LÓGICA PRODUCTOS
    # =====================================================

    def cargar_productos(self):
        query = """
            SELECT id_producto, nombre, marca, modelo, precio_costo
            FROM public.producto ORDER BY nombre
        """
        self.productos_data = self.db.fetch_all(query) or []
        self._llenar_combo(self.productos_data)

    def _llenar_combo(self, productos):
        self.combo_productos.blockSignals(True)
        self.combo_productos.clear()
        for p in productos:
            partes = [p['nombre']]
            if p.get('marca'):
                partes.append(p['marca'])
            if p.get('modelo'):
                partes.append(p['modelo'])
            self.combo_productos.addItem(" — ".join(partes), p)
        self.combo_productos.blockSignals(False)
        self.producto_seleccionado()

    def buscar_productos(self):
        texto = self.input_busqueda.text().lower()
        if not texto:
            self._llenar_combo(self.productos_data)
            return
        filtrados = [
            p for p in self.productos_data
            if texto in f"{p.get('nombre','')} {p.get('marca','')} {p.get('modelo','')}".lower()
        ]
        self._llenar_combo(filtrados)

    def producto_seleccionado(self):
        producto = self.combo_productos.currentData()
        if producto:
            precio = float(producto.get('precio_costo') or 0)
            self.lbl_precio_producto.setText(f"Q {precio:.2f}")
            self.actualizar_preview_subtotal()

    def actualizar_preview_subtotal(self):
        producto = self.combo_productos.currentData()
        if not producto:
            return
        precio = float(producto.get('precio_costo') or 0)
        cantidad = self.spin_cantidad.value()
        descuento = self.spin_descuento.value()
        subtotal = (cantidad * precio) - descuento
        self.lbl_preview.setText(f"Subtotal: Q {max(subtotal, 0):.2f}")

    def agregar_producto(self):
        producto = self.combo_productos.currentData()
        if not producto:
            QMessageBox.warning(self, "Error", "Seleccione un producto.")
            return

        precio = float(producto.get('precio_costo') or 0)
        if precio <= 0:
            QMessageBox.warning(
                self, "Sin precio",
                f"El producto '{producto['nombre']}' no tiene precio configurado."
            )
            return

        cantidad = self.spin_cantidad.value()
        descuento = self.spin_descuento.value()
        subtotal = max((cantidad * precio) - descuento, 0)

        self.carrito.append({
            'id_producto': producto['id_producto'],
            'nombre': producto['nombre'],
            'cantidad': cantidad,
            'precio_unitario': precio,
            'descuento': descuento,
            'subtotal': subtotal
        })

        self.actualizar_tabla_carrito()
        self.actualizar_total()

        # Resetear campos
        self.spin_cantidad.setValue(1)
        self.spin_descuento.setValue(0)
        self.input_busqueda.clear()

    def eliminar_producto(self, row):
        self.carrito.pop(row)
        self.actualizar_tabla_carrito()
        self.actualizar_total()

    def actualizar_tabla_carrito(self):
        self.table.setRowCount(len(self.carrito))
        for i, item in enumerate(self.carrito):
            self.table.setItem(i, 0, QTableWidgetItem(item['nombre']))
            self.table.setItem(i, 1, QTableWidgetItem(str(item['cantidad'])))
            self.table.setItem(i, 2, QTableWidgetItem(f"Q {item['precio_unitario']:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"Q {item['descuento']:.2f}"))

            item_sub = QTableWidgetItem(f"Q {item['subtotal']:.2f}")
            item_sub.setForeground(QColor("#059669"))
            item_sub.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(i, 4, item_sub)

            btn = QPushButton("✕")
            btn.setStyleSheet(BTN_DANGER)
            btn.setFixedSize(34, 28)
            btn.clicked.connect(lambda _, r=i: self.eliminar_producto(r))
            self.table.setCellWidget(i, 5, btn)

        self.lbl_items.setText(f"{len(self.carrito)} producto{'s' if len(self.carrito) != 1 else ''}")

    def actualizar_total(self):
        subtotal = sum(item['subtotal'] for item in self.carrito)
        envio = self.spin_envio.value() if self.check_envio.isChecked() else 0
        total = subtotal + envio

        self.lbl_subtotal.setText(f"Q {subtotal:.2f}")
        self.lbl_envio_total.setText(f"Q {envio:.2f}")
        self.lbl_total.setText(f"Q {total:.2f}")

    # =====================================================
    # LIMPIAR
    # =====================================================

    def confirmar_limpiar(self):
        if not self.carrito:
            self.limpiar_todo()
            return
        resp = QMessageBox.question(
            self, "Confirmar",
            "¿Desea limpiar el carrito y todos los campos?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            self.limpiar_todo()

    def limpiar_todo(self):
        self.carrito = []
        self.actualizar_tabla_carrito()
        self.actualizar_total()
        self.quitar_cliente()
        self.input_num_doc.clear()
        self.input_guia.clear()
        self.spin_envio.setValue(0)
        self.spin_cantidad.setValue(1)
        self.spin_descuento.setValue(0)
        self.check_envio.setChecked(False)
        self.check_pagado.setChecked(True)
        self.combo_pago.setCurrentIndex(0)
        self.set_tipo_doc("FAC")
        self.input_busqueda.clear()

    # =====================================================
    # FINALIZAR VENTA
    # =====================================================

    def finalizar_venta(self):

        # Validaciones
        if not self.cliente_actual:
            QMessageBox.warning(self, "Cliente requerido", "Debe seleccionar un cliente.")
            return

        if not self.carrito:
            QMessageBox.warning(self, "Carrito vacío", "Agregue al menos un producto.")
            return

        num_doc = self.input_num_doc.text().strip()
        if not num_doc:
            QMessageBox.warning(self, "Documento requerido", "Ingrese el número de documento.")
            self.input_num_doc.setFocus()
            return

        tipo_doc = self._tipo_doc

        es_envio = self.check_envio.isChecked()
        id_empresa = None
        numero_guia = None
        precio_envio = 0

        if es_envio:
            if self.combo_empresa.count() == 0:
                QMessageBox.warning(self, "Sin empresa", "No hay empresas de envío registradas.")
                return
            id_empresa = self.combo_empresa.currentData()
            numero_guia = self.input_guia.text().strip() or None
            precio_envio = self.spin_envio.value()

        forma_pago = self.combo_pago.currentData()
        producto_pagado = self.check_pagado.isChecked()

        # Si es pago mixto, abrir diálogo
        if forma_pago == 'MIXTO':
            total_carrito = sum(item['subtotal'] for item in self.carrito)
            total_carrito += float(precio_envio or 0)
            dlg = DialogoPagoMixto(total_carrito, self)
            if not dlg.exec_():
                return
            pagos_mixtos = dlg.resultado_pagos
            # Registrar movimientos individuales por cada forma de pago
            try:
                caja_info = self.service.verificar_caja_abierta()
                if not caja_info.get('success'):
                    QMessageBox.warning(self, "Caja cerrada", caja_info.get('message'))
                    return
                # Usar EF como forma_pago principal (primera con monto > 0)
                forma_principal = next(
                    (k for k, v in pagos_mixtos.items() if v > 0), 'EF'
                )
                resultado = self.service.registrar_venta(
                    id_cliente=self.cliente_actual['id_cliente'],
                    forma_pago='MIXTO',
                    tipo_documento=tipo_doc,
                    numero_documento_manual=num_doc,
                    es_envio=es_envio,
                    id_empresa_fk=id_empresa,
                    numero_guia=numero_guia,
                    precio_envio=precio_envio,
                    producto_pagado=True,
                    productos=self.carrito,
                    pagos_mixtos=pagos_mixtos
                )
                if resultado.get('success'):
                    detalle_pago = "  |  ".join(
                        f"{k}: Q{v:.2f}" for k, v in pagos_mixtos.items() if v > 0
                    )
                    QMessageBox.information(
                        self,
                        "✅ Venta Registrada",
                        f"Documento:  {resultado['numero_documento']}\n"
                        f"Total:          Q {resultado['total']:.2f}\n"
                        f"Pago Mixto: {detalle_pago}"
                    )
                    self.limpiar_todo()
                else:
                    QMessageBox.warning(self, "Error", resultado.get('message', 'Error desconocido'))
            except Exception as e:
                QMessageBox.critical(self, "Error inesperado", str(e))
            return

        try:
            resultado = self.service.registrar_venta(
                id_cliente=self.cliente_actual['id_cliente'],
                forma_pago=forma_pago,
                tipo_documento=tipo_doc,
                numero_documento_manual=num_doc,
                es_envio=es_envio,
                id_empresa_fk=id_empresa,
                numero_guia=numero_guia,
                precio_envio=precio_envio,
                producto_pagado=producto_pagado,
                productos=self.carrito
            )

            if resultado.get('success'):
                estado_pago = (
                    "✅ Pagado"
                    if producto_pagado
                    else "⏳ Pendiente (Cuenta por cobrar)"
                )
                QMessageBox.information(
                    self,
                    "✅ Venta Registrada",
                    f"Documento:  {resultado['numero_documento']}\n"
                    f"Total:          Q {resultado['total']:.2f}\n"
                    f"Pago:           {estado_pago}"
                )
                self.limpiar_todo()
            else:
                QMessageBox.warning(self, "Error", resultado.get('message', 'Error desconocido'))

        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", str(e))


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanasVentas()
    ventana.resize(1400, 860)
    ventana.show()
    sys.exit(app.exec_())