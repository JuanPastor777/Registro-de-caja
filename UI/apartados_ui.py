# UI/apartados_ui.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QComboBox, QDoubleSpinBox, QDateEdit, QMessageBox,
    QHeaderView, QCheckBox, QGroupBox,
    QScrollArea, QLineEdit, QApplication
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.conexion import DatabaseConnection
from services.apartado_service import ApartadoService


# =========================================================
# HOJA DE ESTILOS CORREGIDA (TEXTOS VISIBLES Y COMBOS LIMPIOS)
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
        color: #0F172A;
        background-color: #FFFFFF;
    }
    QGroupBox QLabel {
        color: #1E293B;
        font-weight: 500;
    }
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        padding: 8px;
        background-color: white;
        color: #1E293B;
        min-height: 35px;
        font-size: 13px;
    }
    QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
        border-color: #3B82F6;
    }
    
    /* ARREGLO PARA DESPLEGABLES CON FONDO OSCURO */
    QComboBox QAbstractItemView {
        background-color: white;
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        selection-background-color: #EEF2FF;
        selection-color: #312E81;
        color: #1E293B;
    }
    
    QPushButton {
        border-radius: 8px;
        padding: 10px 15px;
        font-weight: bold;
        font-size: 12px;
        min-height: 35px;
    }
    QTableWidget { 
        border: 1px solid #E5E7EB; 
        border-radius: 12px; 
        background-color: white; 
    }
    QHeaderView::section { 
        background-color: #F9FAFB; 
        color: #475569;
        padding: 12px; 
        font-weight: bold; 
        border: none; 
    }
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
        self.setFixedSize(400, 350)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        title = QLabel("➕ Nuevo Cliente")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
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
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("background-color: #F3F4F6; color: #1E293B;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Guardar Cliente")
        save_btn.setStyleSheet("background-color: #10B981; color: white;")
        save_btn.clicked.connect(self.guardar)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def guardar(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
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
            QMessageBox.warning(self, "Error", "No se pudo guardar el cliente")


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
        self.setFixedSize(450, 480)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        title = QLabel("➕ Nuevo Producto")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
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
        
        self.input_precio = QDoubleSpinBox()
        self.input_precio.setMinimum(0)
        self.input_precio.setMaximum(999999)
        self.input_precio.setPrefix("Q ")
        self.input_precio.setMinimumHeight(35)
        form.addRow("Precio costo", self.input_precio)
        
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("background-color: #F3F4F6; color: #1E293B;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Guardar Producto")
        save_btn.setStyleSheet("background-color: #6366F1; color: white;")
        save_btn.clicked.connect(self.guardar)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def guardar(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        
        precio = self.input_precio.value()
        if precio <= 0:
            QMessageBox.warning(self, "Error", "El precio debe ser mayor a 0")
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
            QMessageBox.warning(self, "Error", "No se pudo guardar el producto")


# =========================================================
# DIÁLOGO APARTADO
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
        self.setFixedSize(650, 850)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel("📦 Registro de Apartado")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1E293B;")
        layout.addWidget(title)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # CLIENTE
        cliente_widget = QWidget()
        cliente_layout = QHBoxLayout()
        cliente_layout.setContentsMargins(0, 0, 0, 0)
        cliente_layout.setSpacing(8)

        self.cliente_combo = QComboBox()
        self.cliente_combo.setMinimumHeight(40)
        self.cliente_combo.setEditable(True)
        self.cliente_combo.setInsertPolicy(QComboBox.NoInsert)
        self.cliente_combo.lineEdit().setPlaceholderText("Escriba nombre para buscar...")
        self.cliente_combo.lineEdit().textEdited.connect(self.buscar_cliente)
        cliente_layout.addWidget(self.cliente_combo)

        btn_nuevo_cliente = QPushButton("➕")
        btn_nuevo_cliente.setFixedSize(42, 40)
        btn_nuevo_cliente.setStyleSheet("background:#10B981;color:white;border-radius:6px;font-size:16px;")
        btn_nuevo_cliente.clicked.connect(self.abrir_nuevo_cliente)
        cliente_layout.addWidget(btn_nuevo_cliente)

        cliente_widget.setLayout(cliente_layout)
        form_layout.addRow("👤 Cliente:", cliente_widget)

        # PRODUCTO
        producto_widget = QWidget()
        producto_layout = QHBoxLayout()
        producto_layout.setContentsMargins(0, 0, 0, 0)
        producto_layout.setSpacing(8)

        self.producto_combo = QComboBox()
        self.producto_combo.setMinimumHeight(40)
        self.producto_combo.setEditable(True)
        self.producto_combo.setInsertPolicy(QComboBox.NoInsert)
        self.producto_combo.lineEdit().setPlaceholderText("Escriba producto para buscar...")
        self.producto_combo.lineEdit().textEdited.connect(self.buscar_producto)
        
        # Conexión doble para asegurar la actualización en modo editable
        self.producto_combo.currentIndexChanged.connect(self.actualizar_precio)
        self.producto_combo.activated.connect(self.actualizar_precio)
        
        producto_layout.addWidget(self.producto_combo)

        btn_nuevo_prod = QPushButton("➕")
        btn_nuevo_prod.setFixedSize(42, 40)
        btn_nuevo_prod.setStyleSheet("background:#6366F1;color:white;border-radius:6px;font-size:16px;")
        btn_nuevo_prod.clicked.connect(self.abrir_nuevo_producto)
        producto_layout.addWidget(btn_nuevo_prod)

        producto_widget.setLayout(producto_layout)
        form_layout.addRow("📦 Producto:", producto_widget)

        # PRECIO DEL PRODUCTO SELECCIONADO
        self.lbl_precio = QLabel("Q 0.00")
        self.lbl_precio.setStyleSheet("color: #10B981; font-weight: bold; font-size: 15px;")
        form_layout.addRow("💰 Precio producto:", self.lbl_precio)

        # MONTOS
        self.monto_original = QDoubleSpinBox()
        self.monto_original.setMinimum(0)
        self.monto_original.setMaximum(999999)
        self.monto_original.setPrefix("Q ")
        self.monto_original.setMinimumHeight(40)
        self.monto_original.valueChanged.connect(self.calcular_total)
        form_layout.addRow("💵 Monto original:", self.monto_original)

        # DESCUENTO
        descuento_widget = QWidget()
        descuento_layout = QHBoxLayout()
        descuento_layout.setContentsMargins(0, 0, 0, 0)
        descuento_layout.setSpacing(6)

        self.descuento_input = QDoubleSpinBox()
        self.descuento_input.setMinimum(0)
        self.descuento_input.setMaximum(999999)
        self.descuento_input.setDecimals(2)
        self.descuento_input.setMinimumHeight(40)
        self.descuento_input.valueChanged.connect(self.calcular_total)
        descuento_layout.addWidget(self.descuento_input)

        self.descuento_tipo = QComboBox()
        self.descuento_tipo.setMinimumHeight(40)
        self.descuento_tipo.setFixedWidth(70)
        self.descuento_tipo.addItem("Q", "Q")
        self.descuento_tipo.addItem("%", "%")
        self.descuento_tipo.currentIndexChanged.connect(self._on_descuento_tipo_changed)
        descuento_layout.addWidget(self.descuento_tipo)

        self.lbl_descuento_equiv = QLabel("= Q 0.00")
        self.lbl_descuento_equiv.setStyleSheet("color: #DC2626; font-size: 12px; min-width: 80px;")
        self.lbl_descuento_equiv.setVisible(False)
        descuento_layout.addWidget(self.lbl_descuento_equiv)

        descuento_widget.setLayout(descuento_layout)
        form_layout.addRow("🔻 Descuento:", descuento_widget)

        # INCREMENTO
        incremento_widget = QWidget()
        incremento_layout = QHBoxLayout()
        incremento_layout.setContentsMargins(0, 0, 0, 0)
        incremento_layout.setSpacing(6)

        self.incremento_input = QDoubleSpinBox()
        self.incremento_input.setMinimum(0)
        self.incremento_input.setMaximum(999999)
        self.incremento_input.setDecimals(2)
        self.incremento_input.setMinimumHeight(40)
        self.incremento_input.valueChanged.connect(self.calcular_total)
        incremento_layout.addWidget(self.incremento_input)

        self.incremento_tipo = QComboBox()
        self.incremento_tipo.setMinimumHeight(40)
        self.incremento_tipo.setFixedWidth(70)
        self.incremento_tipo.addItem("Q", "Q")
        self.incremento_tipo.addItem("%", "%")
        self.incremento_tipo.currentIndexChanged.connect(self._on_incremento_tipo_changed)
        incremento_layout.addWidget(self.incremento_tipo)

        self.lbl_incremento_equiv = QLabel("= Q 0.00")
        self.lbl_incremento_equiv.setStyleSheet("color: #059669; font-size: 12px; min-width: 80px;")
        self.lbl_incremento_equiv.setVisible(False)
        incremento_layout.addWidget(self.lbl_incremento_equiv)

        incremento_widget.setLayout(incremento_layout)
        form_layout.addRow("✏️ Aumento:", incremento_widget)

        self.total_producto = QDoubleSpinBox()
        self.total_producto.setMinimum(0)
        self.total_producto.setMaximum(999999)
        self.total_producto.setPrefix("Q ")
        self.total_producto.setReadOnly(True)
        self.total_producto.setMinimumHeight(40)
        self.total_producto.setStyleSheet("background-color: #F3F4F6; font-weight: bold; color: #059669;")
        form_layout.addRow("✅ Total a pagar:", self.total_producto)

        # FECHA
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate())
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setMinimumHeight(40)
        form_layout.addRow("📅 Fecha Inicio:", self.fecha_inicio)

        # FORMA DE PAGO SIN MIXTO
        self.forma_pago_combo = QComboBox()
        self.forma_pago_combo.setMinimumHeight(40)
        self.forma_pago_combo.addItem("💵 Efectivo", "EF")
        self.forma_pago_combo.addItem("💳 Tarjeta", "TC/TD")
        self.forma_pago_combo.addItem("🏦 Transferencia", "TF")
        self.forma_pago_combo.addItem("📥 Depósito", "DP")
        form_layout.addRow("💳 Forma de pago:", self.forma_pago_combo)

        # ENVÍO
        self.check_envio = QCheckBox("🚚 Este apartado es por envío")
        self.check_envio.setStyleSheet("font-weight: bold; margin-top: 8px; color: #1E293B;")
        self.check_envio.toggled.connect(self.toggle_envio)
        form_layout.addRow("", self.check_envio)

        self.empresa_combo = QComboBox()
        self.empresa_combo.setEnabled(False)
        self.empresa_combo.setMinimumHeight(40)
        form_layout.addRow("🏢 Empresa envío:", self.empresa_combo)

        self.numero_guia_input = QLineEdit()
        self.numero_guia_input.setEnabled(False)
        self.numero_guia_input.setPlaceholderText("Ej: GUI-123456")
        self.numero_guia_input.setMinimumHeight(40)
        form_layout.addRow("🔢 N° Guía:", self.numero_guia_input)

        scroll_layout.addLayout(form_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # BOTONES
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setStyleSheet("background-color: #F3F4F6; color: #4B5563; border: 1px solid #E5E7EB;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("✅ Guardar Apartado")
        save_btn.setMinimumHeight(45)
        save_btn.setStyleSheet("background-color: #F5C800; color: white; font-weight: bold;")
        save_btn.clicked.connect(self.guardar)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def cargar_todos_clientes(self):
        query = "SELECT id_cliente, nombre, apellido FROM cliente ORDER BY nombre"
        self.todos_clientes = self.db.fetch_all(query) or []
        self.actualizar_combo_clientes(self.todos_clientes)

    def actualizar_combo_clientes(self, clientes):
        self.cliente_combo.blockSignals(True)
        self.cliente_combo.clear()
        for cliente in clientes:
            nombre = f"{cliente['nombre']} {cliente['apellido']}" if cliente.get('apellido') else cliente['nombre']
            self.cliente_combo.addItem(nombre, cliente['id_cliente'])
        self.cliente_combo.blockSignals(False)

    def buscar_cliente(self, texto):
        if not texto:
            self.actualizar_combo_clientes(self.todos_clientes)
            return
        texto_lower = texto.lower()
        filtrados = [c for c in self.todos_clientes if texto_lower in f"{c['nombre']} {c.get('apellido', '')}".lower()]
        self.actualizar_combo_clientes(filtrados)
        self.cliente_combo.lineEdit().setText(texto)

    def abrir_nuevo_cliente(self):
        dialog = DialogoNuevoCliente(self)
        if dialog.exec_() and dialog.cliente_creado:
            nuevo = dialog.cliente_creado
            self.todos_clientes.append(nuevo)
            self.actualizar_combo_clientes(self.todos_clientes)
            for i in range(self.cliente_combo.count()):
                if self.cliente_combo.itemData(i) == nuevo['id_cliente']:
                    self.cliente_combo.setCurrentIndex(i)
                    break

    def cargar_todos_productos(self):
        query = "SELECT id_producto, nombre, marca, modelo, precio_costo FROM producto ORDER BY nombre"
        self.todos_productos = self.db.fetch_all(query) or []
        self.actualizar_combo_productos(self.todos_productos)

    def actualizar_combo_productos(self, productos):
        self.producto_combo.blockSignals(True)
        self.producto_combo.clear()
        for producto in productos:
            texto = producto['nombre']
            if producto.get('marca'):
                texto += f" - {producto['marca']}"
            if producto.get('modelo'):
                texto += f" ({producto['modelo']})"
            self.producto_combo.addItem(texto, producto)
        self.producto_combo.blockSignals(False)

    def buscar_producto(self, texto):
        if not texto:
            self.actualizar_combo_productos(self.todos_productos)
            return
        texto_lower = texto.lower()
        filtrados = [p for p in self.todos_productos
                    if texto_lower in p['nombre'].lower()
                    or (p.get('marca') and texto_lower in p['marca'].lower())
                    or (p.get('modelo') and texto_lower in p['modelo'].lower())]
        self.actualizar_combo_productos(filtrados)
        self.producto_combo.lineEdit().setText(texto)

    def abrir_nuevo_producto(self):
        dialog = DialogoNuevoProducto(self)
        if dialog.exec_() and dialog.producto_creado:
            nuevo = dialog.producto_creado
            self.todos_productos.append(nuevo)
            self.actualizar_combo_productos(self.todos_productos)
            for i in range(self.producto_combo.count()):
                data = self.producto_combo.itemData(i)
                if data and isinstance(data, dict) and data.get('id_producto') == nuevo['id_producto']:
                    self.producto_combo.setCurrentIndex(i)
                    self.actualizar_precio()
                    break

    def actualizar_precio(self):
        # CORRECCIÓN: Captura el producto seleccionado de forma segura y actualiza al instante
        producto_data = self.producto_combo.currentData()
        if producto_data and isinstance(producto_data, dict):
            precio = float(producto_data.get('precio_costo', 0))
            self.lbl_precio.setText(f"Q {precio:.2f}")
            self.monto_original.setValue(precio)
            self.calcular_total()

    def _on_descuento_tipo_changed(self):
        es_pct = self.descuento_tipo.currentText() == "%"
        self.descuento_input.setMaximum(100 if es_pct else 999999)
        self.lbl_descuento_equiv.setVisible(es_pct)
        self.calcular_total()

    def _on_incremento_tipo_changed(self):
        es_pct = self.incremento_tipo.currentText() == "%"
        self.incremento_input.setMaximum(100 if es_pct else 999999)
        self.lbl_incremento_equiv.setVisible(es_pct)
        self.calcular_total()

    def _quetzales_descuento(self):
        original = self.monto_original.value()
        val = self.descuento_input.value()
        if self.descuento_tipo.currentText() == "%":
            return round(original * val / 100, 2)
        return val

    def _quetzales_incremento(self):
        original = self.monto_original.value()
        val = self.incremento_input.value()
        if self.incremento_tipo.currentText() == "%":
            return round(original * val / 100, 2)
        return val

    def calcular_total(self):
        original = self.monto_original.value()
        descuento_q = self._quetzales_descuento()
        incremento_q = self._quetzales_incremento()

        if self.descuento_tipo.currentText() == "%":
            self.lbl_descuento_equiv.setText(f"= Q {descuento_q:.2f}")
        if self.incremento_tipo.currentText() == "%":
            self.lbl_incremento_equiv.setText(f"= Q {incremento_q:.2f}")

        total = original - descuento_q + incremento_q
        self.total_producto.setValue(max(total, 0))

    def toggle_envio(self, checked):
        self.empresa_combo.setEnabled(checked)
        self.numero_guia_input.setEnabled(checked)

    def cargar_empresas(self):
        query = "SELECT id_empresa, nombre FROM empresa_envio ORDER BY nombre"
        empresas = self.db.fetch_all(query) or []
        self.empresa_combo.clear()
        self.empresa_combo.addItem("Seleccionar empresa", None)
        for empresa in empresas:
            self.empresa_combo.addItem(empresa['nombre'], empresa['id_empresa'])

    def guardar(self):
        cliente_id = self.cliente_combo.currentData()
        producto_data = self.producto_combo.currentData()
        
        if not cliente_id:
            QMessageBox.warning(self, "Error", "❌ Seleccione un cliente válido")
            return
        if not producto_data:
            QMessageBox.warning(self, "Error", "❌ Seleccione un producto válido")
            return
            
        producto_id = producto_data['id_producto']
        monto_original = self.monto_original.value()
        descuento = self._quetzales_descuento()
        incremento = self._quetzales_incremento()
        monto_final = self.total_producto.value()
        fecha = self.fecha_inicio.date().toPyDate()
        es_envio = self.check_envio.isChecked()
        id_empresa = self.empresa_combo.currentData() if es_envio else None
        numero_guia = self.numero_guia_input.text().strip() if es_envio else None
        forma_pago = self.forma_pago_combo.currentData()

        if monto_final <= 0:
            QMessageBox.warning(self, "Error", "❌ El total debe ser mayor a 0")
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
            'numero_guia': numero_guia,
            'forma_pago_acordada': forma_pago
        }

        resultado = self.service.crear_apartado(data)
        
        if resultado.get('success'):
            msg = f"✅ Apartado #{resultado['id_apartado']} registrado!\n\n"
            msg += f"💰 Monto original: Q {resultado['monto_original']:.2f}\n"
            if resultado['descuento'] > 0:
                msg += f"🔻 Descuento: -Q {resultado['descuento']:.2f}\n"
            if resultado['incremento'] > 0:
                msg += f"✏️ Modificar: +Q {resultado['incremento']:.2f}\n"
            msg += f"✅ Total a pagar: Q {resultado['monto_final']:.2f}"
            QMessageBox.information(self, "Éxito", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", f"❌ {resultado.get('message')}")


# =========================================================
# DIÁLOGO PAGO APARTADO
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
        self.setFixedSize(500, 650)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel("💰 Registrar Pago")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info_group = QGroupBox("Información")
        info_layout = QFormLayout()
        
        cliente = f"{self.apartado['cliente_nombre']} {self.apartado.get('cliente_apellido', '')}"
        info_layout.addRow("Cliente:", QLabel(cliente))
        info_layout.addRow("Producto:", QLabel(self.apartado['producto_nombre']))
        info_layout.addRow("Total:", QLabel(f"Q {self.apartado['monto_final']:.2f}"))
        info_layout.addRow("Pagado:", QLabel(f"Q {self.apartado['total_pagado']:.2f}"))
        
        saldo = self.apartado['saldo_pendiente']
        saldo_label = QLabel(f"Q {saldo:.2f}")
        saldo_label.setStyleSheet("color: #DC2626; font-weight: bold;")
        info_layout.addRow("Saldo:", saldo_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        pago_group = QGroupBox("Datos del Pago")
        pago_layout = QFormLayout()
        pago_layout.setSpacing(12)

        self.monto_pago = QDoubleSpinBox()
        self.monto_pago.setMinimum(0.01)
        self.monto_pago.setMaximum(saldo)
        self.monto_pago.setPrefix("Q ")
        self.monto_pago.setMinimumHeight(40)
        pago_layout.addRow("💰 Monto:", self.monto_pago)

        # SIN MIXTO
        self.forma_pago = QComboBox()
        self.forma_pago.setMinimumHeight(40)
        self.forma_pago.addItem("💵 Efectivo", "EF")
        self.forma_pago.addItem("💳 Tarjeta", "TC/TD")
        self.forma_pago.addItem("🏦 Transferencia", "TF")
        self.forma_pago.addItem("📥 Depósito", "DP")
        pago_layout.addRow("💳 Forma pago:", self.forma_pago)

        self.tipo_doc = QComboBox()
        self.tipo_doc.setMinimumHeight(40)
        self.tipo_doc.addItem("📄 Factura", "FAC")
        self.tipo_doc.addItem("🧾 Recibo", "REC")
        pago_layout.addRow("📋 Tipo doc:", self.tipo_doc)

        self.numero_doc = QLineEdit()
        self.numero_doc.setPlaceholderText("Ej: 001-2025")
        self.numero_doc.setMinimumHeight(40)
        pago_layout.addRow("🔢 N° documento:", self.numero_doc)

        pago_group.setLayout(pago_layout)
        layout.addWidget(pago_group)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setStyleSheet("background-color: #F3F4F6; color: #1E293B;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self.pagar_btn = QPushButton("✅ Pagar")
        self.pagar_btn.setMinimumHeight(40)
        self.pagar_btn.setStyleSheet("background-color: #F5C800; color: white; font-weight: bold;")
        self.pagar_btn.clicked.connect(self.registrar_pago)
        btn_layout.addWidget(self.pagar_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.monto_pago.valueChanged.connect(self.validar)
        self.numero_doc.textChanged.connect(self.validar)

    def validar(self):
        self.pagar_btn.setEnabled(self.monto_pago.value() > 0 and bool(self.numero_doc.text().strip()))

    def registrar_pago(self):
        forma_pago = self.forma_pago.currentData()
        monto = self.monto_pago.value()
        tipo_doc = self.tipo_doc.currentData()
        numero_doc = self.numero_doc.text().strip()

        # Solo efectivo va a caja; transferencia/depósito/tarjeta NO
        id_caja_para_pago = self.id_caja if forma_pago == "EF" else None

        resultado = self.service.registrar_pago(
            self.apartado['id_apartado'],
            monto,
            forma_pago,
            tipo_doc,
            numero_doc,
            id_caja=id_caja_para_pago
        )
        if resultado.get('success'):
            QMessageBox.information(self, "Éxito", resultado['message'])
            self.accept()
        else:
            QMessageBox.critical(self, "Error", resultado.get('message'))


# =========================================================
# VENTANA PRINCIPAL APARTADOS
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

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        title = QLabel("📦 Apartados Pendientes")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        self.caja_status_label = QLabel()
        self.actualizar_estado_caja()
        header.addWidget(self.caja_status_label)

        add_btn = QPushButton("➕ Nuevo Apartado")
        add_btn.setMinimumHeight(40)
        add_btn.setStyleSheet("background-color: #F5C800; color: white; padding: 10px 20px; font-weight: bold;")
        add_btn.clicked.connect(self.agregar_apartado)
        header.addWidget(add_btn)

        reload_btn = QPushButton("🔄 Recargar")
        reload_btn.setMinimumHeight(40)
        reload_btn.setStyleSheet("background-color: #3B82F6; color: white; padding: 10px 20px; font-weight: bold;")
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

        self.setLayout(layout)

    def actualizar_estado_caja(self):
        estado = self.apartado_service.obtener_estado_caja()
        if estado['abierta']:
            self.caja_status_label.setText("✅ Caja Abierta")
            self.caja_status_label.setStyleSheet("color: #065F46; font-weight: bold; padding: 8px 18px; background-color: #D1FAE5; border-radius: 20px;")
            if not self.id_caja_actual:
                self.id_caja_actual = estado['id_caja']
        else:
            self.caja_status_label.setText("❌ Caja Cerrada")
            self.caja_status_label.setStyleSheet("color: #991B1B; font-weight: bold; padding: 8px 18px; background-color: #FEE2E2; border-radius: 20px;")

    def cargar_apartados(self):
        apartados = self.apartado_service.obtener_apartados_pendientes()
        self.table.setRowCount(len(apartados))

        for row, a in enumerate(apartados):
            self.table.setRowHeight(row, 50)
            self.table.setItem(row, 0, QTableWidgetItem(f"{a['cliente_nombre']} {a.get('cliente_apellido', '')}".strip()))
            
            producto = a['producto_nombre']
            if a.get('marca'):
                producto += f" - {a['marca']}"
            self.table.setItem(row, 1, QTableWidgetItem(producto))
            
            total = float(a['monto_final'])
            total_item = QTableWidgetItem(f"Q {total:.2f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 2, total_item)
            
            pagado = float(a['total_pagado'])
            pagado_item = QTableWidgetItem(f"Q {pagado:.2f}")
            pagado_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            pagado_item.setForeground(QColor("#059669"))
            self.table.setItem(row, 3, pagado_item)
            
            saldo = float(a['saldo_pendiente'])
            saldo_item = QTableWidgetItem(f"Q {saldo:.2f}")
            saldo_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if saldo > 0:
                saldo_item.setForeground(QColor("#DC2626"))
                saldo_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(row, 4, saldo_item)
            
            porcentaje = float(a['porcentaje_pagado'])
            pct_item = QTableWidgetItem(f"{porcentaje:.1f}%")
            pct_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, pct_item)

            acciones_widget = QWidget()
            acciones_layout = QHBoxLayout()
            acciones_layout.setContentsMargins(5, 5, 5, 5)
            acciones_layout.setSpacing(8)

            if saldo > 0 and self.id_caja_actual:
                pago_btn = QPushButton("💰")
                pago_btn.setFixedSize(42, 38)
                pago_btn.setStyleSheet("background-color: #F5C800; border-radius: 6px; font-size: 18px;")
                pago_btn.clicked.connect(lambda checked, ap=a: self.registrar_pago(ap))
                acciones_layout.addWidget(pago_btn)

            detalle_btn = QPushButton("📋")
            detalle_btn.setFixedSize(42, 38)
            detalle_btn.setStyleSheet("background-color: #3B82F6; color: white; border-radius: 6px; font-size: 18px;")
            detalle_btn.clicked.connect(lambda checked, ap=a: self.ver_detalle(ap))
            acciones_layout.addWidget(detalle_btn)

            if saldo > 0:
                cancel_btn = QPushButton("❌")
                cancel_btn.setFixedSize(42, 38)
                cancel_btn.setStyleSheet("background-color: #FEE2E2; color: #DC2626; border-radius: 6px; font-size: 18px;")
                cancel_btn.clicked.connect(lambda checked, ap=a: self.cancelar_apartado(ap))
                acciones_layout.addWidget(cancel_btn)

            acciones_widget.setLayout(acciones_layout)
            self.table.setCellWidget(row, 6, acciones_widget)

    def agregar_apartado(self):
        dialog = DialogoApartado(self.apartado_service, self)
        if dialog.exec_():
            self.cargar_apartados()

    def registrar_pago(self, apartado):
        if not self.id_caja_actual:
            QMessageBox.warning(self, "Error", "No hay caja abierta")
            return
        detalle = self.apartado_service.obtener_detalle_apartado(apartado['id_apartado'])
        if detalle:
            dialog = DialogoPagoApartado(detalle, self.apartado_service, self.id_caja_actual, self)
            if dialog.exec_():
                self.cargar_apartados()

    def ver_detalle(self, apartado):
        detalle = self.apartado_service.obtener_detalle_apartado(apartado['id_apartado'])
        historial = self.apartado_service.obtener_historial_pagos(apartado['id_apartado'])
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Detalle Apartado")
        dialog.setMinimumSize(700, 550)
        dialog.setStyleSheet(ESTILO_INTERFAZ)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("📋 Detalle del Apartado")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        info_group = QGroupBox("Información")
        info_layout = QFormLayout()
        
        total = float(detalle['monto_final'])
        pagado = float(detalle['total_pagado'])
        
        info_layout.addRow("Cliente:", QLabel(f"{detalle['cliente_nombre']} {detalle.get('cliente_apellido', '')}"))
        info_layout.addRow("Producto:", QLabel(detalle['producto_nombre']))
        info_layout.addRow("Monto original:", QLabel(f"Q {float(detalle['monto_original']):.2f}"))
        if float(detalle.get('descuento_pactado', 0)) > 0:
            info_layout.addRow("Descuento:", QLabel(f"- Q {float(detalle['descuento_pactado']):.2f}"))
        if float(detalle.get('incremento_pactado', 0)) > 0:
            info_layout.addRow("Incremento:", QLabel(f"+ Q {float(detalle['incremento_pactado']):.2f}"))
        info_layout.addRow("Total:", QLabel(f"Q {total:.2f}"))
        info_layout.addRow("Pagado:", QLabel(f"Q {pagado:.2f}"))
        info_layout.addRow("Saldo:", QLabel(f"Q {total - pagado:.2f}"))
        info_layout.addRow("Estado:", QLabel(detalle['estado']))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        if historial:
            hist_group = QGroupBox(f"Historial ({len(historial)} pagos)")
            hist_layout = QVBoxLayout()
            hist_table = QTableWidget()
            hist_table.setColumnCount(3)
            hist_table.setHorizontalHeaderLabels(["Fecha", "Monto", "Usuario"])
            hist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            hist_table.setRowCount(len(historial))
            for i, p in enumerate(historial):
                hist_table.setItem(i, 0, QTableWidgetItem(str(p['fecha_pago'])))
                hist_table.setItem(i, 1, QTableWidgetItem(f"Q {float(p['monto']):.2f}"))
                hist_table.setItem(i, 2, QTableWidgetItem(p.get('usuario_nombre', 'N/A')))
            hist_layout.addWidget(hist_table)
            hist_group.setLayout(hist_layout)
            layout.addWidget(hist_group)
        
        close_btn = QPushButton("Cerrar")
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet("background-color: #F5C800; color: white; border-radius: 8px; font-weight: bold; margin-top: 10px;")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def cancelar_apartado(self, apartado):
        if not self.id_caja_actual:
            QMessageBox.warning(self, "Error", "No hay caja abierta")
            return

        total_pagado = float(apartado['total_pagado'])
        msg = f"⚠️ ¿Cancelar apartado #{apartado['id_apartado']}?\n\n"
        if total_pagado > 0:
            msg += f"💰 Pagado: Q {total_pagado:.2f}\nEste monto NO se devuelve."
        
        if QMessageBox.question(self, "Confirmar", msg, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            resultado = self.apartado_service.cancelar_apartado(apartado['id_apartado'])
            if resultado.get('success'):
                QMessageBox.information(self, "Éxito", "Apartado cancelado")
                self.cargar_apartados()
            else:
                QMessageBox.critical(self, "Error", resultado.get('message'))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaApartados(id_usuario_actual=1, id_caja_actual=1)
    ventana.resize(1200, 650)
    ventana.show()
    sys.exit(app.exec_())