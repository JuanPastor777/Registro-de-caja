# UI/apartados_ui.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QComboBox, QDoubleSpinBox, QDateEdit, QMessageBox,
    QHeaderView, QCheckBox, QGroupBox,
    QScrollArea, QLineEdit, QApplication, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.conexion import DatabaseConnection
from services.apartado_service import ApartadoService


# =========================================================
# ESTILOS OPTIMIZADOS PARA PANTALLAS PEQUEÑAS
# =========================================================
ESTILO_INTERFAZ = """
    QWidget { 
        background-color: #F8FAFC; 
        font-family: 'Segoe UI', sans-serif; 
        color: #1E293B;
    }
    QDialog, QScrollArea, QScrollArea QWidget {
        background-color: white;
    }
    QGroupBox {
        font-weight: bold;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 15px;
        background-color: #FFFFFF;
    }
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        padding: 5px;
        background-color: white;
        min-height: 30px;
        font-size: 12px;
    }
    QPushButton {
        border-radius: 6px;
        padding: 5px 12px;
        font-weight: bold;
        font-size: 11px;
        min-height: 30px;
    }
    QTableWidget { border: 1px solid #E5E7EB; border-radius: 12px; }
    QHeaderView::section { background-color: #F9FAFB; padding: 8px; font-weight: bold; }
"""


# =========================================================
# DIÁLOGO NUEVO CLIENTE
# =========================================================
class DialogoNuevoCliente(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.cliente_creado = None
        self.setStyleSheet(ESTILO_INTERFAZ)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Nuevo Cliente")
        self.setMinimumSize(350, 320)
        self.resize(400, 350)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("➕ Nuevo Cliente")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
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

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("background-color: #F3F4F6;")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Guardar Cliente")
        save_btn.setStyleSheet("background-color: #10B981; color: white;")
        save_btn.clicked.connect(self.guardar)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def guardar(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "Nombre obligatorio")
            return
        apellido = self.input_apellido.text().strip() or None
        telefono = self.input_telefono.text().strip() or None
        query = "INSERT INTO cliente (nombre, apellido, telefono) VALUES (%s, %s, %s) RETURNING id_cliente"
        resultado = self.db.fetch_one(query, (nombre, apellido, telefono))
        if resultado:
            self.cliente_creado = {
                'id_cliente': resultado['id_cliente'],
                'nombre': nombre,
                'apellido': apellido,
                'telefono': telefono
            }
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "No se pudo guardar")


# =========================================================
# DIÁLOGO NUEVO PRODUCTO
# =========================================================
class DialogoNuevoProducto(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.producto_creado = None
        self.setStyleSheet(ESTILO_INTERFAZ)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Nuevo Producto")
        self.setMinimumSize(380, 420)
        self.resize(450, 480)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("➕ Nuevo Producto")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre del producto")
        form.addRow("Nombre *", self.input_nombre)

        self.input_marca = QLineEdit()
        self.input_marca.setPlaceholderText("Marca")
        form.addRow("Marca", self.input_marca)

        self.input_modelo = QLineEdit()
        self.input_modelo.setPlaceholderText("Modelo")
        form.addRow("Modelo", self.input_modelo)

        self.input_precio = QDoubleSpinBox()
        self.input_precio.setMinimum(0)
        self.input_precio.setMaximum(999999)
        self.input_precio.setPrefix("Q ")
        form.addRow("Precio costo", self.input_precio)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("background-color: #F3F4F6;")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Guardar Producto")
        save_btn.setStyleSheet("background-color: #6366F1; color: white;")
        save_btn.clicked.connect(self.guardar)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def guardar(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "Nombre obligatorio")
            return
        precio = self.input_precio.value()
        if precio <= 0:
            QMessageBox.warning(self, "Error", "Precio mayor a 0")
            return
        query = """
            INSERT INTO producto (nombre, marca, modelo, precio_costo)
            VALUES (%s, %s, %s, %s) RETURNING id_producto
        """
        resultado = self.db.fetch_one(query, (
            nombre,
            self.input_marca.text().strip() or None,
            self.input_modelo.text().strip() or None,
            precio
        ))
        if resultado:
            self.producto_creado = {
                'id_producto': resultado['id_producto'],
                'nombre': nombre,
                'marca': self.input_marca.text().strip(),
                'modelo': self.input_modelo.text().strip(),
                'precio_costo': precio
            }
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "No se pudo guardar")


# =========================================================
# DIÁLOGO APARTADO (CON SCROLL VERTICAL)
# =========================================================
class DialogoApartado(QDialog):
    def __init__(self, service: ApartadoService, parent=None):
        super().__init__(parent)
        self.service = service
        self.db = service.db
        self.todos_clientes = []
        self.todos_productos = []
        self.setStyleSheet(ESTILO_INTERFAZ)
        self.init_ui()
        self.cargar_todos_clientes()
        self.cargar_todos_productos()
        self.cargar_empresas()

    def init_ui(self):
        self.setWindowTitle("Nuevo Apartado")
        self.setMinimumSize(500, 550)
        self.resize(620, 700)

        # Layout principal vertical
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area que envuelve todo el contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)

        title = QLabel("📦 Registro de Apartado")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # Cliente
        cliente_widget = QWidget()
        cliente_layout = QHBoxLayout()
        cliente_layout.setContentsMargins(0, 0, 0, 0)
        cliente_layout.setSpacing(6)
        self.cliente_combo = QComboBox()
        self.cliente_combo.setEditable(True)
        self.cliente_combo.setInsertPolicy(QComboBox.NoInsert)
        self.cliente_combo.lineEdit().setPlaceholderText("Escriba nombre...")
        self.cliente_combo.lineEdit().textEdited.connect(self.buscar_cliente)
        cliente_layout.addWidget(self.cliente_combo)
        btn_nuevo_cliente = QPushButton("➕")
        btn_nuevo_cliente.setFixedSize(32, 30)
        btn_nuevo_cliente.setStyleSheet("background:#10B981;color:white;")
        btn_nuevo_cliente.clicked.connect(self.abrir_nuevo_cliente)
        cliente_layout.addWidget(btn_nuevo_cliente)
        cliente_widget.setLayout(cliente_layout)
        form_layout.addRow("👤 Cliente:", cliente_widget)

        # Producto
        producto_widget = QWidget()
        producto_layout = QHBoxLayout()
        producto_layout.setContentsMargins(0, 0, 0, 0)
        producto_layout.setSpacing(6)
        self.producto_combo = QComboBox()
        self.producto_combo.setEditable(True)
        self.producto_combo.setInsertPolicy(QComboBox.NoInsert)
        self.producto_combo.lineEdit().setPlaceholderText("Escriba producto...")
        self.producto_combo.lineEdit().textEdited.connect(self.buscar_producto)
        self.producto_combo.currentIndexChanged.connect(self.actualizar_precio)
        producto_layout.addWidget(self.producto_combo)
        btn_nuevo_prod = QPushButton("➕")
        btn_nuevo_prod.setFixedSize(32, 30)
        btn_nuevo_prod.setStyleSheet("background:#6366F1;color:white;")
        btn_nuevo_prod.clicked.connect(self.abrir_nuevo_producto)
        producto_layout.addWidget(btn_nuevo_prod)
        producto_widget.setLayout(producto_layout)
        form_layout.addRow("📦 Producto:", producto_widget)

        self.lbl_precio = QLabel("Q 0.00")
        self.lbl_precio.setStyleSheet("color:#10B981; font-weight:bold;")
        form_layout.addRow("💰 Precio:", self.lbl_precio)

        self.monto_original = QDoubleSpinBox()
        self.monto_original.setPrefix("Q ")
        self.monto_original.setMaximum(999999)
        self.monto_original.valueChanged.connect(self.calcular_total)
        form_layout.addRow("💵 Monto original:", self.monto_original)

        # Descuento
        desc_widget = QWidget()
        desc_layout = QHBoxLayout()
        desc_layout.setContentsMargins(0,0,0,0)
        self.descuento_input = QDoubleSpinBox()
        self.descuento_input.setMaximum(999999)
        self.descuento_input.valueChanged.connect(self.calcular_total)
        self.descuento_tipo = QComboBox()
        self.descuento_tipo.addItems(["Q", "%"])
        self.descuento_tipo.setFixedWidth(55)
        self.descuento_tipo.currentIndexChanged.connect(self._on_descuento_tipo_changed)
        self.lbl_desc_equiv = QLabel("= Q 0.00")
        self.lbl_desc_equiv.setVisible(False)
        self.lbl_desc_equiv.setStyleSheet("color:#DC2626; font-size:11px;")
        desc_layout.addWidget(self.descuento_input)
        desc_layout.addWidget(self.descuento_tipo)
        desc_layout.addWidget(self.lbl_desc_equiv)
        desc_widget.setLayout(desc_layout)
        form_layout.addRow("🔻 Descuento:", desc_widget)

        # Incremento
        inc_widget = QWidget()
        inc_layout = QHBoxLayout()
        inc_layout.setContentsMargins(0,0,0,0)
        self.incremento_input = QDoubleSpinBox()
        self.incremento_input.setMaximum(999999)
        self.incremento_input.valueChanged.connect(self.calcular_total)
        self.incremento_tipo = QComboBox()
        self.incremento_tipo.addItems(["Q", "%"])
        self.incremento_tipo.setFixedWidth(55)
        self.incremento_tipo.currentIndexChanged.connect(self._on_incremento_tipo_changed)
        self.lbl_inc_equiv = QLabel("= Q 0.00")
        self.lbl_inc_equiv.setVisible(False)
        self.lbl_inc_equiv.setStyleSheet("color:#059669; font-size:11px;")
        inc_layout.addWidget(self.incremento_input)
        inc_layout.addWidget(self.incremento_tipo)
        inc_layout.addWidget(self.lbl_inc_equiv)
        inc_widget.setLayout(inc_layout)
        form_layout.addRow("✏️ Aumento:", inc_widget)

        self.total_producto = QDoubleSpinBox()
        self.total_producto.setPrefix("Q ")
        self.total_producto.setReadOnly(True)
        self.total_producto.setStyleSheet("background:#F3F4F6; font-weight:bold; color:#059669;")
        form_layout.addRow("✅ Total:", self.total_producto)

        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate())
        self.fecha_inicio.setCalendarPopup(True)
        form_layout.addRow("📅 Fecha inicio:", self.fecha_inicio)

        self.check_envio = QCheckBox("🚚 Es envío")
        self.check_envio.toggled.connect(self.toggle_envio)
        form_layout.addRow("", self.check_envio)

        self.empresa_combo = QComboBox()
        self.empresa_combo.setEnabled(False)
        form_layout.addRow("🏢 Empresa envío:", self.empresa_combo)

        self.numero_guia_input = QLineEdit()
        self.numero_guia_input.setEnabled(False)
        self.numero_guia_input.setPlaceholderText("Número de guía")
        form_layout.addRow("🔢 Guía:", self.numero_guia_input)

        container_layout.addLayout(form_layout)

        # Botones
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Guardar Apartado")
        save_btn.setStyleSheet("background-color:#F5C800; color:white; font-weight:bold;")
        save_btn.clicked.connect(self.guardar)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        container_layout.addLayout(btn_layout)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    # ========== MÉTODOS AUXILIARES (iguales que el original) ==========
    def cargar_todos_clientes(self):
        query = "SELECT id_cliente, nombre, apellido FROM cliente ORDER BY nombre"
        self.todos_clientes = self.db.fetch_all(query) or []
        self.actualizar_combo_clientes(self.todos_clientes)

    def actualizar_combo_clientes(self, clientes):
        line = self.cliente_combo.lineEdit()
        self.cliente_combo.blockSignals(True)
        line.blockSignals(True)
        txt = line.text()
        self.cliente_combo.clear()
        for c in clientes:
            nombre = f"{c['nombre']} {c['apellido']}" if c.get('apellido') else c['nombre']
            self.cliente_combo.addItem(nombre, c['id_cliente'])
        line.setText(txt)
        self.cliente_combo.blockSignals(False)
        line.blockSignals(False)

    def buscar_cliente(self, texto):
        if not texto:
            self.actualizar_combo_clientes(self.todos_clientes)
            return
        tl = texto.lower()
        filt = [c for c in self.todos_clientes if tl in f"{c['nombre']} {c.get('apellido','')}".lower()]
        self.actualizar_combo_clientes(filt)

    def abrir_nuevo_cliente(self):
        dlg = DialogoNuevoCliente(self)
        if dlg.exec_() and dlg.cliente_creado:
            self.todos_clientes.append(dlg.cliente_creado)
            self.actualizar_combo_clientes(self.todos_clientes)
            for i in range(self.cliente_combo.count()):
                if self.cliente_combo.itemData(i) == dlg.cliente_creado['id_cliente']:
                    self.cliente_combo.setCurrentIndex(i)
                    break

    def cargar_todos_productos(self):
        query = "SELECT id_producto, nombre, marca, modelo, precio_costo FROM producto ORDER BY nombre"
        self.todos_productos = self.db.fetch_all(query) or []
        self.actualizar_combo_productos(self.todos_productos)

    def actualizar_combo_productos(self, productos):
        line = self.producto_combo.lineEdit()
        self.producto_combo.blockSignals(True)
        line.blockSignals(True)
        txt = line.text()
        self.producto_combo.clear()
        for p in productos:
            texto = p['nombre']
            if p.get('marca'): texto += f" - {p['marca']}"
            if p.get('modelo'): texto += f" ({p['modelo']})"
            self.producto_combo.addItem(texto, p)
        line.setText(txt)
        self.producto_combo.blockSignals(False)
        line.blockSignals(False)

    def buscar_producto(self, texto):
        if not texto:
            self.actualizar_combo_productos(self.todos_productos)
            return
        tl = texto.lower()
        filt = [p for p in self.todos_productos if tl in p['nombre'].lower()
                or (p.get('marca') and tl in p['marca'].lower())
                or (p.get('modelo') and tl in p['modelo'].lower())]
        self.actualizar_combo_productos(filt)

    def abrir_nuevo_producto(self):
        dlg = DialogoNuevoProducto(self)
        if dlg.exec_() and dlg.producto_creado:
            self.todos_productos.append(dlg.producto_creado)
            self.actualizar_combo_productos(self.todos_productos)
            for i in range(self.producto_combo.count()):
                data = self.producto_combo.itemData(i)
                if data and isinstance(data, dict) and data.get('id_producto') == dlg.producto_creado['id_producto']:
                    self.producto_combo.setCurrentIndex(i)
                    self.actualizar_precio()
                    break

    def actualizar_precio(self):
        data = self.producto_combo.currentData()
        if data and isinstance(data, dict):
            precio = float(data.get('precio_costo', 0))
            self.lbl_precio.setText(f"Q {precio:.2f}")
            self.monto_original.setValue(precio)
            self.calcular_total()

    def _on_descuento_tipo_changed(self):
        es_pct = self.descuento_tipo.currentText() == "%"
        self.descuento_input.setMaximum(100 if es_pct else 999999)
        self.lbl_desc_equiv.setVisible(es_pct)
        self.calcular_total()

    def _on_incremento_tipo_changed(self):
        es_pct = self.incremento_tipo.currentText() == "%"
        self.incremento_input.setMaximum(100 if es_pct else 999999)
        self.lbl_inc_equiv.setVisible(es_pct)
        self.calcular_total()

    def _quetzales_descuento(self):
        orig = self.monto_original.value()
        val = self.descuento_input.value()
        if self.descuento_tipo.currentText() == "%":
            return round(orig * val / 100, 2)
        return val

    def _quetzales_incremento(self):
        orig = self.monto_original.value()
        val = self.incremento_input.value()
        if self.incremento_tipo.currentText() == "%":
            return round(orig * val / 100, 2)
        return val

    def calcular_total(self):
        orig = self.monto_original.value()
        desc_q = self._quetzales_descuento()
        inc_q = self._quetzales_incremento()
        if self.descuento_tipo.currentText() == "%":
            self.lbl_desc_equiv.setText(f"= Q {desc_q:.2f}")
        if self.incremento_tipo.currentText() == "%":
            self.lbl_inc_equiv.setText(f"= Q {inc_q:.2f}")
        total = orig - desc_q + inc_q
        self.total_producto.setValue(max(total, 0))

    def toggle_envio(self, checked):
        self.empresa_combo.setEnabled(checked)
        self.numero_guia_input.setEnabled(checked)

    def cargar_empresas(self):
        query = "SELECT id_empresa, nombre FROM empresa_envio ORDER BY nombre"
        empresas = self.db.fetch_all(query) or []
        self.empresa_combo.clear()
        self.empresa_combo.addItem("Seleccionar empresa", None)
        for e in empresas:
            self.empresa_combo.addItem(e['nombre'], e['id_empresa'])

    def guardar(self):
        cliente_id = self.cliente_combo.currentData()
        prod_data = self.producto_combo.currentData()
        if not cliente_id:
            QMessageBox.warning(self, "Error", "Seleccione cliente")
            return
        if not prod_data:
            QMessageBox.warning(self, "Error", "Seleccione producto")
            return
        producto_id = prod_data['id_producto']
        monto_original = self.monto_original.value()
        descuento = self._quetzales_descuento()
        incremento = self._quetzales_incremento()
        monto_final = self.total_producto.value()
        fecha = self.fecha_inicio.date().toPyDate()
        es_envio = self.check_envio.isChecked()
        id_empresa = self.empresa_combo.currentData() if es_envio else None
        numero_guia = self.numero_guia_input.text().strip() if es_envio else None
        if monto_final <= 0:
            QMessageBox.warning(self, "Error", "Total debe ser > 0")
            return
        data = {
            'id_cliente_fk': cliente_id,
            'id_producto_fk': producto_id,
            'monto_original': monto_original,
            'descuento_pactado': descuento,
            'incremento_pactado': incremento,
            'fecha_inicio': fecha,
            'es_envio': es_envio,
            'id_empresa_fk': id_empresa,
            'numero_guia': numero_guia
        }
        resultado = self.service.crear_apartado(data)
        if resultado.get('success'):
            QMessageBox.information(self, "Éxito", f"Apartado #{resultado['id_apartado']} registrado")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", resultado.get('message'))


# =========================================================
# DIÁLOGO PAGO APARTADO (CON SCROLL)
# =========================================================
class DialogoPagoApartado(QDialog):
    def __init__(self, apartado: dict, service: ApartadoService, id_caja: int = None, parent=None):
        super().__init__(parent)
        self.apartado = apartado
        self.service = service
        self.id_caja = id_caja
        self.setStyleSheet(ESTILO_INTERFAZ)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Registrar Pago")
        self.setMinimumSize(400, 450)
        self.resize(480, 520)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("💰 Registrar Pago")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info_group = QGroupBox("Información")
        info_form = QFormLayout()
        cliente = f"{self.apartado['cliente_nombre']} {self.apartado.get('cliente_apellido', '')}"
        info_form.addRow("Cliente:", QLabel(cliente))
        info_form.addRow("Producto:", QLabel(self.apartado['producto_nombre']))
        info_form.addRow("Total:", QLabel(f"Q {self.apartado['monto_final']:.2f}"))
        info_form.addRow("Pagado:", QLabel(f"Q {self.apartado['total_pagado']:.2f}"))
        saldo = self.apartado['saldo_pendiente']
        saldo_lbl = QLabel(f"Q {saldo:.2f}")
        saldo_lbl.setStyleSheet("color:#DC2626; font-weight:bold;")
        info_form.addRow("Saldo:", saldo_lbl)
        info_group.setLayout(info_form)
        layout.addWidget(info_group)

        pago_group = QGroupBox("Datos del Pago")
        pago_form = QFormLayout()
        self.monto_pago = QDoubleSpinBox()
        self.monto_pago.setPrefix("Q ")
        self.monto_pago.setMaximum(round(saldo, 2))
        self.monto_pago.valueChanged.connect(self.validar)
        pago_form.addRow("💰 Monto:", self.monto_pago)

        self.forma_pago = QComboBox()
        self.forma_pago.addItems(["💵 Efectivo", "💳 Tarjeta", "🏦 Transferencia", "📥 Depósito"])
        self.forma_pago.setCurrentData("EF")
        pago_form.addRow("💳 Forma pago:", self.forma_pago)

        self.tipo_doc = QComboBox()
        self.tipo_doc.addItems(["📄 Factura", "🧾 Recibo"])
        pago_form.addRow("📋 Tipo doc:", self.tipo_doc)

        self.numero_doc = QLineEdit()
        self.numero_doc.setPlaceholderText("Ej: 001-2025")
        self.numero_doc.textChanged.connect(self.validar)
        pago_form.addRow("🔢 N° documento:", self.numero_doc)

        pago_group.setLayout(pago_form)
        layout.addWidget(pago_group)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        self.pagar_btn = QPushButton("✅ Pagar")
        self.pagar_btn.setStyleSheet("background-color:#F5C800; color:white; font-weight:bold;")
        self.pagar_btn.setEnabled(False)
        self.pagar_btn.clicked.connect(self.registrar_pago)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.pagar_btn)
        layout.addLayout(btn_layout)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def validar(self):
        self.pagar_btn.setEnabled(self.monto_pago.value() > 0 and bool(self.numero_doc.text().strip()))

    def registrar_pago(self):
        forma = self.forma_pago.currentText()
        cod_forma = {"💵 Efectivo":"EF","💳 Tarjeta":"TC/TD","🏦 Transferencia":"TF","📥 Depósito":"DP"}[forma]
        monto = self.monto_pago.value()
        tipo_doc = "FAC" if self.tipo_doc.currentText() == "📄 Factura" else "REC"
        numero_doc = self.numero_doc.text().strip()
        id_caja_pago = self.id_caja if cod_forma == "EF" else None
        resultado = self.service.registrar_pago(
            self.apartado['id_apartado'], monto, cod_forma, tipo_doc, numero_doc, id_caja=id_caja_pago
        )
        if resultado.get('success'):
            QMessageBox.information(self, "Éxito", resultado['message'])
            self.accept()
        else:
            QMessageBox.critical(self, "Error", resultado.get('message'))


# =========================================================
# VENTANA PRINCIPAL APARTADOS (CON SCROLL)
# =========================================================
class VentanaApartados(QWidget):
    def __init__(self, id_usuario_actual: int, id_caja_actual: int = None):
        super().__init__()
        self.db = DatabaseConnection()
        self.apartado_service = ApartadoService(id_usuario_actual)
        self.id_usuario_actual = id_usuario_actual
        self.id_caja_actual = id_caja_actual
        self.setStyleSheet(ESTILO_INTERFAZ)
        self.init_ui()
        self.cargar_apartados()

    def init_ui(self):
        self.setWindowTitle("📦 Gestión de Apartados")
        self.setMinimumSize(800, 500)

        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        header = QHBoxLayout()
        title = QLabel("📦 Apartados Pendientes")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        self.caja_status_label = QLabel()
        self.actualizar_estado_caja()
        header.addWidget(self.caja_status_label)

        add_btn = QPushButton("➕ Nuevo Apartado")
        add_btn.setStyleSheet("background-color:#F5C800; color:white; font-weight:bold;")
        add_btn.clicked.connect(self.agregar_apartado)
        header.addWidget(add_btn)

        reload_btn = QPushButton("🔄 Recargar")
        reload_btn.setStyleSheet("background-color:#3B82F6; color:white; font-weight:bold;")
        reload_btn.clicked.connect(self.cargar_apartados)
        header.addWidget(reload_btn)

        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Cliente", "Producto", "Total", "Pagado", "Saldo", "%", "Acciones"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        main_scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_scroll)

    def actualizar_estado_caja(self):
        estado = self.apartado_service.obtener_estado_caja()
        if estado['abierta']:
            self.caja_status_label.setText("✅ Caja Abierta")
            self.caja_status_label.setStyleSheet("color:#065F46; background:#D1FAE5; padding:4px 12px; border-radius:20px;")
            if not self.id_caja_actual:
                self.id_caja_actual = estado['id_caja']
        else:
            self.caja_status_label.setText("❌ Caja Cerrada")
            self.caja_status_label.setStyleSheet("color:#991B1B; background:#FEE2E2; padding:4px 12px; border-radius:20px;")

    def cargar_apartados(self):
        apartados = self.apartado_service.obtener_apartados_pendientes()
        self.table.setRowCount(len(apartados))
        for row, a in enumerate(apartados):
            self.table.setRowHeight(row, 45)
            self.table.setItem(row, 0, QTableWidgetItem(f"{a['cliente_nombre']} {a.get('cliente_apellido','')}".strip()))
            prod = a['producto_nombre']
            if a.get('marca'):
                prod += f" - {a['marca']}"
            self.table.setItem(row, 1, QTableWidgetItem(prod))
            total = float(a['monto_final'])
            self.table.setItem(row, 2, QTableWidgetItem(f"Q {total:.2f}"))
            pagado = float(a['total_pagado'])
            pag_item = QTableWidgetItem(f"Q {pagado:.2f}")
            pag_item.setForeground(QColor("#059669"))
            self.table.setItem(row, 3, pag_item)
            saldo = float(a['saldo_pendiente'])
            sal_item = QTableWidgetItem(f"Q {saldo:.2f}")
            if saldo > 0:
                sal_item.setForeground(QColor("#DC2626"))
                sal_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.table.setItem(row, 4, sal_item)
            pct = float(a['porcentaje_pagado'])
            self.table.setItem(row, 5, QTableWidgetItem(f"{pct:.1f}%"))

            acciones = QWidget()
            acc_layout = QHBoxLayout()
            acc_layout.setContentsMargins(4,2,4,2)
            if saldo > 0 and self.id_caja_actual:
                pago_btn = QPushButton("💰")
                pago_btn.setFixedSize(32, 30)
                pago_btn.setStyleSheet("background:#F5C800;")
                pago_btn.clicked.connect(lambda ch, ap=a: self.registrar_pago(ap))
                acc_layout.addWidget(pago_btn)
            detalle_btn = QPushButton("📋")
            detalle_btn.setFixedSize(32, 30)
            detalle_btn.setStyleSheet("background:#3B82F6; color:white;")
            detalle_btn.clicked.connect(lambda ch, ap=a: self.ver_detalle(ap))
            acc_layout.addWidget(detalle_btn)
            if saldo > 0:
                cancel_btn = QPushButton("❌")
                cancel_btn.setFixedSize(32, 30)
                cancel_btn.setStyleSheet("background:#FEE2E2; color:#DC2626;")
                cancel_btn.clicked.connect(lambda ch, ap=a: self.cancelar_apartado(ap))
                acc_layout.addWidget(cancel_btn)
            acciones.setLayout(acc_layout)
            self.table.setCellWidget(row, 6, acciones)

    def agregar_apartado(self):
        dlg = DialogoApartado(self.apartado_service, self)
        if dlg.exec_():
            self.cargar_apartados()

    def registrar_pago(self, apartado):
        if not self.id_caja_actual:
            QMessageBox.warning(self, "Error", "No hay caja abierta")
            return
        detalle = self.apartado_service.obtener_detalle_apartado(apartado['id_apartado'])
        if detalle:
            dlg = DialogoPagoApartado(detalle, self.apartado_service, self.id_caja_actual, self)
            if dlg.exec_():
                self.cargar_apartados()

    def ver_detalle(self, apartado):
        detalle = self.apartado_service.obtener_detalle_apartado(apartado['id_apartado'])
        historial = self.apartado_service.obtener_historial_pagos(apartado['id_apartado'])
        dlg = QDialog(self)
        dlg.setWindowTitle("Detalle Apartado")
        dlg.setMinimumSize(600, 450)
        dlg.setStyleSheet(ESTILO_INTERFAZ)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20,20,20,20)

        titulo = QLabel("📋 Detalle del Apartado")
        titulo.setFont(QFont("Segoe UI", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        info_group = QGroupBox("Información")
        info_form = QFormLayout()
        info_form.addRow("Cliente:", QLabel(f"{detalle['cliente_nombre']} {detalle.get('cliente_apellido','')}"))
        info_form.addRow("Producto:", QLabel(detalle['producto_nombre']))
        info_form.addRow("Monto original:", QLabel(f"Q {float(detalle['monto_original']):.2f}"))
        if float(detalle.get('descuento_pactado',0)) > 0:
            info_form.addRow("Descuento:", QLabel(f"- Q {float(detalle['descuento_pactado']):.2f}"))
        if float(detalle.get('incremento_pactado',0)) > 0:
            info_form.addRow("Incremento:", QLabel(f"+ Q {float(detalle['incremento_pactado']):.2f}"))
        info_form.addRow("Total:", QLabel(f"Q {float(detalle['monto_final']):.2f}"))
        info_form.addRow("Pagado:", QLabel(f"Q {float(detalle['total_pagado']):.2f}"))
        saldo = float(detalle['monto_final']) - float(detalle['total_pagado'])
        info_form.addRow("Saldo:", QLabel(f"Q {saldo:.2f}"))
        info_form.addRow("Estado:", QLabel(detalle['estado']))
        info_group.setLayout(info_form)
        layout.addWidget(info_group)

        if historial:
            hist_group = QGroupBox(f"Historial ({len(historial)} pagos)")
            hist_layout = QVBoxLayout()
            tabla_hist = QTableWidget()
            tabla_hist.setColumnCount(3)
            tabla_hist.setHorizontalHeaderLabels(["Fecha", "Monto", "Usuario"])
            tabla_hist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            tabla_hist.setRowCount(len(historial))
            for i, p in enumerate(historial):
                tabla_hist.setItem(i,0, QTableWidgetItem(str(p['fecha_pago'])))
                tabla_hist.setItem(i,1, QTableWidgetItem(f"Q {float(p['monto']):.2f}"))
                tabla_hist.setItem(i,2, QTableWidgetItem(p.get('usuario_nombre','N/A')))
            hist_layout.addWidget(tabla_hist)
            hist_group.setLayout(hist_layout)
            layout.addWidget(hist_group)

        close_btn = QPushButton("Cerrar")
        close_btn.setStyleSheet("background-color:#F5C800; color:white; font-weight:bold;")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        dlg.exec_()

    def cancelar_apartado(self, apartado):
        if not self.id_caja_actual:
            QMessageBox.warning(self, "Error", "No hay caja abierta")
            return
        total_pagado = float(apartado['total_pagado'])
        msg = f"⚠️ ¿Cancelar apartado #{apartado['id_apartado']}?\n\n"
        if total_pagado > 0:
            msg += f"💰 Pagado: Q {total_pagado:.2f}\nEste monto NO se devuelve."
        if QMessageBox.question(self, "Confirmar", msg, QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            resultado = self.apartado_service.cancelar_apartado(apartado['id_apartado'])
            if resultado.get('success'):
                QMessageBox.information(self, "Éxito", "Apartado cancelado")
                self.cargar_apartados()
            else:
                QMessageBox.critical(self, "Error", resultado.get('message'))