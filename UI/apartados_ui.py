# UI/apartados_ui.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QComboBox, QDoubleSpinBox, QDateEdit, QMessageBox,
    QHeaderView, QInputDialog, QCheckBox, QGroupBox,
    QScrollArea, QLineEdit, QSpinBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.conexion import DatabaseConnection
from services.apartado_service import ApartadoService


class DialogoApartado(QDialog):
    """Diálogo para crear un nuevo apartado con descuento, incremento y envío"""

    def __init__(self, service: ApartadoService, parent=None):
        super().__init__(parent)
        self.service = service
        self.db = service.db
        self.init_ui()
        self.cargar_clientes()
        self.cargar_productos()
        self.cargar_empresas()

    def init_ui(self):
        self.setWindowTitle("Nuevo Apartado")
        self.setFixedSize(600, 800)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QTableWidget {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Título
        title = QLabel("📦 Registro de Apartado")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1E293B;")
        layout.addWidget(title)

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # ========== CLIENTE ==========
        self.cliente_combo = QComboBox()
        self.cliente_combo.setMinimumHeight(35)
        form_layout.addRow("👤 Cliente:", self.cliente_combo)

        # ========== PRODUCTO ==========
        producto_widget = QWidget()
        producto_row = QHBoxLayout()
        producto_row.setContentsMargins(0, 0, 0, 0)
        producto_row.setSpacing(6)
        self.producto_combo = QComboBox()
        self.producto_combo.setMinimumHeight(35)
        producto_row.addWidget(self.producto_combo)
        btn_nuevo_prod = QPushButton("+ Nuevo")
        btn_nuevo_prod.setFixedHeight(35)
        btn_nuevo_prod.setFixedWidth(70)
        btn_nuevo_prod.setStyleSheet("background:#6366F1;color:white;border-radius:6px;font-weight:600;")
        btn_nuevo_prod.clicked.connect(self.abrir_nuevo_producto)
        producto_row.addWidget(btn_nuevo_prod)
        producto_widget.setLayout(producto_row)
        form_layout.addRow("📦 Producto:", producto_widget)

        # Precio del producto
        self.lbl_precio = QLabel("Q 0.00")
        self.lbl_precio.setStyleSheet("color: #10B981; font-weight: bold; font-size: 14px;")
        form_layout.addRow("💰 Precio producto:", self.lbl_precio)
        
        self.producto_combo.currentIndexChanged.connect(self.actualizar_precio)

        # ========== MONTOS ==========
        self.monto_original = QDoubleSpinBox()
        self.monto_original.setMinimum(0)
        self.monto_original.setMaximum(999999)
        self.monto_original.setPrefix("Q ")
        self.monto_original.setMinimumHeight(35)
        self.monto_original.valueChanged.connect(self.calcular_total)
        form_layout.addRow("💵 Monto original:", self.monto_original)

        self.descuento_input = QDoubleSpinBox()
        self.descuento_input.setMinimum(0)
        self.descuento_input.setMaximum(999999)
        self.descuento_input.setPrefix("Q ")
        self.descuento_input.setMinimumHeight(35)
        self.descuento_input.setToolTip("Descuento en quetzales")
        self.descuento_input.valueChanged.connect(self.calcular_total)
        form_layout.addRow("🔻 Descuento (Q):", self.descuento_input)

        self.incremento_input = QDoubleSpinBox()
        self.incremento_input.setMinimum(0)
        self.incremento_input.setMaximum(999999)
        self.incremento_input.setPrefix("Q ")
        self.incremento_input.setMinimumHeight(35)
        self.incremento_input.setToolTip("Modificar precio: incremento por interés o recargo")
        self.incremento_input.valueChanged.connect(self.calcular_total)
        form_layout.addRow("✏️ Modificar precio (Q):", self.incremento_input)

        # Total a pagar
        self.total_producto = QDoubleSpinBox()
        self.total_producto.setMinimum(0)
        self.total_producto.setMaximum(999999)
        self.total_producto.setPrefix("Q ")
        self.total_producto.setReadOnly(True)
        self.total_producto.setMinimumHeight(35)
        self.total_producto.setStyleSheet("background-color: #F3F4F6; font-weight: bold; color: #059669;")
        form_layout.addRow("✅ Total a pagar:", self.total_producto)

        # ========== FECHA ==========
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate())
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setMinimumHeight(35)
        form_layout.addRow("📅 Fecha Inicio:", self.fecha_inicio)

        # ========== FORMA DE PAGO ==========
        self.forma_pago_combo = QComboBox()
        self.forma_pago_combo.setMinimumHeight(35)
        self.forma_pago_combo.addItem("💵 Efectivo", "EF")
        self.forma_pago_combo.addItem("💳 Tarjeta", "TC/TD")
        self.forma_pago_combo.addItem("🏦 Transferencia", "TF")
        self.forma_pago_combo.addItem("📥 Depósito", "DP")
        form_layout.addRow("💳 Forma de pago:", self.forma_pago_combo)

        # ========== ENVÍO ==========
        self.check_envio = QCheckBox("🚚 Este apartado es por envío")
        self.check_envio.setStyleSheet("font-weight: bold; margin-top: 5px;")
        self.check_envio.toggled.connect(self.toggle_envio)
        form_layout.addRow("", self.check_envio)

        self.empresa_combo = QComboBox()
        self.empresa_combo.setEnabled(False)
        self.empresa_combo.setMinimumHeight(35)
        form_layout.addRow("🏢 Empresa envío:", self.empresa_combo)

        self.numero_guia_input = QLineEdit()
        self.numero_guia_input.setEnabled(False)
        self.numero_guia_input.setPlaceholderText("Ej: GUI-123456")
        self.numero_guia_input.setMinimumHeight(35)
        form_layout.addRow("🔢 N° Guía:", self.numero_guia_input)

        scroll_layout.addLayout(form_layout)
        scroll_area.setWidget(scroll_widget)
        
        layout.addWidget(scroll_area)

        # ========== BOTONES ==========
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                color: #4B5563;
                border: 1px solid #E5E7EB;
            }
            QPushButton:hover {
                background-color: #E5E7EB;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("✅ Guardar Apartado")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5C800;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E5B800;
            }
        """)
        save_btn.clicked.connect(self.guardar)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def abrir_nuevo_producto(self):
        """Crea un producto rápidamente desde el diálogo de apartado"""
        from UI.ventas_ui import DialogoNuevoProducto
        dialog = DialogoNuevoProducto(self)
        if dialog.exec_():
            prod = dialog.producto_creado
            if prod:
                texto = prod['nombre']
                if prod.get('marca'):
                    texto += f" - {prod['marca']}"
                if prod.get('modelo'):
                    texto += f" ({prod['modelo']})"
                self.producto_combo.addItem(texto, prod)
                self.producto_combo.setCurrentIndex(self.producto_combo.count() - 1)

    def actualizar_precio(self):
        """Actualiza el precio del producto seleccionado"""
        producto_data = self.producto_combo.currentData()
        if producto_data and isinstance(producto_data, dict):
            precio = float(producto_data.get('precio_costo', 0))
            if precio:
                self.lbl_precio.setText(f"Q {precio:.2f}")
                self.monto_original.setValue(precio)
                self.calcular_total()

    def calcular_total(self):
        """Calcula: original - descuento + incremento"""
        original = self.monto_original.value()
        descuento = self.descuento_input.value()
        incremento = self.incremento_input.value()
        total = original - descuento + incremento
        self.total_producto.setValue(max(total, 0))

    def toggle_envio(self, checked):
        """Habilita/deshabilita campos de envío"""
        self.empresa_combo.setEnabled(checked)
        self.numero_guia_input.setEnabled(checked)

    def cargar_clientes(self):
        query = "SELECT id_cliente, nombre, apellido FROM cliente ORDER BY nombre"
        clientes = self.db.fetch_all(query) or []
        self.cliente_combo.clear()
        for cliente in clientes:
            nombre = f"{cliente['nombre']} {cliente['apellido']}" if cliente.get('apellido') else cliente['nombre']
            self.cliente_combo.addItem(nombre, cliente['id_cliente'])

    def cargar_productos(self):
        query = "SELECT id_producto, nombre, marca, modelo, precio_costo FROM producto ORDER BY nombre"
        productos = self.db.fetch_all(query) or []
        self.producto_combo.clear()
        for producto in productos:
            texto = producto['nombre']
            if producto.get('marca'):
                texto += f" - {producto['marca']}"
            if producto.get('modelo'):
                texto += f" ({producto['modelo']})"
            self.producto_combo.addItem(texto, producto)

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
            QMessageBox.warning(self, "Error", "❌ Seleccione un cliente")
            return
            
        if not producto_data or not isinstance(producto_data, dict):
            QMessageBox.warning(self, "Error", "❌ Seleccione un producto válido")
            return
            
        producto_id = producto_data['id_producto']
        
        monto_original = self.monto_original.value()
        descuento = self.descuento_input.value()
        incremento = self.incremento_input.value()
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
            msg = f"✅ Apartado #{resultado['id_apartado']} registrado correctamente!\n\n"
            msg += f"💰 Monto original: Q {resultado['monto_original']:.2f}\n"
            if resultado['descuento'] > 0:
                msg += f"🔻 Descuento: -Q {resultado['descuento']:.2f}\n"
            if resultado['incremento'] > 0:
                msg += f"✏️ Modificar precio: +Q {resultado['incremento']:.2f}\n"
            msg += f"✅ Total a pagar: Q {resultado['monto_final']:.2f}"
            if numero_guia:
                msg += f"\n📦 N° Guía: {numero_guia}"
            QMessageBox.information(self, "Éxito", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", f"❌ {resultado.get('message', 'No se pudo registrar el apartado')}")


class DialogoPagoApartado(QDialog):
    """Diálogo para registrar un pago de apartado"""

    def __init__(self, apartado: dict, service: ApartadoService, parent=None):
        super().__init__(parent)
        self.apartado = apartado
        self.service = service
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Registrar Pago - Apartado #{self.apartado['id_apartado']}")
        self.setFixedSize(500, 450)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Título
        title = QLabel("💰 Registrar Pago")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Información del apartado
        info_group = QGroupBox("Información del Apartado")
        info_layout = QFormLayout()
        
        cliente = f"{self.apartado['cliente_nombre']} {self.apartado.get('cliente_apellido', '')}"
        info_layout.addRow("Cliente:", QLabel(cliente))
        info_layout.addRow("Producto:", QLabel(self.apartado['producto_nombre']))
        info_layout.addRow("Total:", QLabel(f"Q {self.apartado['monto_final']:.2f}"))
        info_layout.addRow("Pagado:", QLabel(f"Q {self.apartado['total_pagado']:.2f}"))
        
        saldo = self.apartado['saldo_pendiente']
        saldo_label = QLabel(f"Q {saldo:.2f}")
        saldo_label.setStyleSheet("color: #DC2626; font-weight: bold;")
        info_layout.addRow("Saldo pendiente:", saldo_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Formulario de pago
        pago_group = QGroupBox("Datos del Pago")
        pago_layout = QFormLayout()
        pago_layout.setSpacing(12)

        # Monto a pagar
        self.monto_pago = QDoubleSpinBox()
        self.monto_pago.setMinimum(0.01)
        self.monto_pago.setMaximum(saldo)
        self.monto_pago.setPrefix("Q ")
        self.monto_pago.setMinimumHeight(35)
        pago_layout.addRow("💰 Monto a pagar:", self.monto_pago)

        # Forma de pago
        self.forma_pago = QComboBox()
        self.forma_pago.setMinimumHeight(35)
        self.forma_pago.addItem("💵 Efectivo", "EF")
        self.forma_pago.addItem("💳 Tarjeta", "TC/TD")
        self.forma_pago.addItem("🏦 Transferencia", "TF")
        self.forma_pago.addItem("📥 Depósito", "DP")
        self.forma_pago.addItem("🔀 Pago Mixto", "MIXTO")
        pago_layout.addRow("💳 Forma de pago:", self.forma_pago)

        # Tipo de documento
        self.tipo_doc = QComboBox()
        self.tipo_doc.setMinimumHeight(35)
        self.tipo_doc.addItem("📄 Factura", "FAC")
        self.tipo_doc.addItem("🧾 Recibo", "REC")
        pago_layout.addRow("📋 Tipo documento:", self.tipo_doc)

        # Número de documento
        self.numero_doc = QLineEdit()
        self.numero_doc.setPlaceholderText("Ej: 001-2025-00123")
        self.numero_doc.setMinimumHeight(35)
        pago_layout.addRow("🔢 N° documento:", self.numero_doc)

        pago_group.setLayout(pago_layout)
        layout.addWidget(pago_group)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("padding: 10px; background-color: #F3F4F6; border-radius: 8px;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self.pagar_btn = QPushButton("✅ Registrar Pago")
        self.pagar_btn.setStyleSheet("padding: 10px; background-color: #F5C800; border-radius: 8px; font-weight: bold;")
        self.pagar_btn.clicked.connect(self.registrar_pago)
        btn_layout.addWidget(self.pagar_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Conectar señal para habilitar/deshabilitar botón
        self.monto_pago.valueChanged.connect(self.validar_monto)
        self.numero_doc.textChanged.connect(self.validar_monto)

    def validar_monto(self):
        monto = self.monto_pago.value()
        tiene_numero = bool(self.numero_doc.text().strip())
        self.pagar_btn.setEnabled(monto > 0 and tiene_numero)

    def registrar_pago(self):
        monto = self.monto_pago.value()
        forma_pago = self.forma_pago.currentData()
        tipo_doc = self.tipo_doc.currentData()
        numero_doc = self.numero_doc.text().strip()

        if monto <= 0:
            QMessageBox.warning(self, "Error", "Ingrese un monto válido")
            return

        if not numero_doc:
            QMessageBox.warning(self, "Error", "Ingrese el número de documento")
            return

        # Si es pago mixto, abrir diálogo de distribución
        if forma_pago == "MIXTO":
            from UI.ventas_ui import DialogoPagoMixto
            dlg = DialogoPagoMixto(monto, self)
            if not dlg.exec_():
                return
            pagos_mixtos = dlg.resultado_pagos
            # Usar forma de pago principal (mayor monto)
            forma_principal = max(pagos_mixtos, key=lambda k: pagos_mixtos[k])
            forma_pago = forma_principal

            resultado = self.service.registrar_pago(
                self.apartado['id_apartado'],
                monto,
                'MIXTO',
                tipo_doc,
                numero_doc,
                pagos_mixtos=pagos_mixtos
            )
        else:
            resultado = self.service.registrar_pago(
                self.apartado['id_apartado'],
                monto,
                forma_pago,
                tipo_doc,
                numero_doc
            )

        if resultado.get('success'):
            QMessageBox.information(self, "Éxito", resultado['message'])
            self.accept()
        else:
            QMessageBox.critical(self, "Error", resultado.get('message', 'Error al registrar pago'))


class VentanaApartados(QWidget):
    """Ventana principal de gestión de apartados"""

    def __init__(self, id_usuario_actual: int, id_caja_actual: int = None):
        super().__init__()
        self.db = DatabaseConnection()
        self.apartado_service = ApartadoService(id_usuario_actual)
        self.id_usuario_actual = id_usuario_actual
        self.id_caja_actual = id_caja_actual
        self.init_ui()
        self.cargar_apartados()

    def init_ui(self):
        self.setWindowTitle("📦 Gestión de Apartados")
        self.setStyleSheet("""
            QWidget {
                background-color: #F8FAFC;
                font-family: 'Segoe UI', sans-serif;
            }
            QTableWidget {
                border: 1px solid #E5E7EB;
                border-radius: 12px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                padding: 12px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QPushButton {
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        
        title = QLabel("📦 Apartados Pendientes")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1E293B;")
        header.addWidget(title)
        
        header.addStretch()

        # Indicador de estado de caja
        self.caja_status_label = QLabel()
        self.actualizar_estado_caja()
        header.addWidget(self.caja_status_label)

        # Botón nuevo apartado
        add_btn = QPushButton("➕ Nuevo Apartado")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5C800;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #E5B800;
            }
        """)
        add_btn.clicked.connect(self.agregar_apartado)
        header.addWidget(add_btn)

        # Botón recargar
        reload_btn = QPushButton("🔄 Recargar")
        reload_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        reload_btn.clicked.connect(self.cargar_apartados)
        header.addWidget(reload_btn)

        layout.addLayout(header)

        # Tabla de apartados
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Producto", "Total", 
            "Pagado", "Saldo", "% Pagado", "Acciones"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def actualizar_estado_caja(self):
        """Actualiza el indicador visual del estado de la caja"""
        estado = self.apartado_service.obtener_estado_caja()
        if estado['abierta']:
            self.caja_status_label.setText("✅ Caja Abierta")
            self.caja_status_label.setStyleSheet("""
                QLabel {
                    color: #065F46;
                    font-weight: bold;
                    padding: 5px 15px;
                    background-color: #D1FAE5;
                    border-radius: 20px;
                }
            """)
            if not self.id_caja_actual:
                self.id_caja_actual = estado['id_caja']
        else:
            self.caja_status_label.setText("❌ Caja Cerrada")
            self.caja_status_label.setStyleSheet("""
                QLabel {
                    color: #991B1B;
                    font-weight: bold;
                    padding: 5px 15px;
                    background-color: #FEE2E2;
                    border-radius: 20px;
                }
            """)

    def cargar_apartados(self):
        """Carga los apartados pendientes"""
        apartados = self.apartado_service.obtener_apartados_pendientes()

        self.table.setRowCount(len(apartados))

        for row, apartado in enumerate(apartados):
            self.table.setRowHeight(row, 55)
            
            # ID
            id_item = QTableWidgetItem(str(apartado['id_apartado']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, id_item)

            # Cliente
            cliente = f"{apartado['cliente_nombre']} {apartado.get('cliente_apellido', '')}".strip()
            self.table.setItem(row, 1, QTableWidgetItem(cliente))

            # Producto
            producto = apartado['producto_nombre']
            if apartado.get('marca'):
                producto += f" - {apartado['marca']}"
            self.table.setItem(row, 2, QTableWidgetItem(producto))

            # Total
            total = float(apartado['monto_final'])
            total_item = QTableWidgetItem(f"Q {total:.2f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 3, total_item)

            # Pagado
            pagado = float(apartado['total_pagado'])
            pagado_item = QTableWidgetItem(f"Q {pagado:.2f}")
            pagado_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            pagado_item.setForeground(QColor("#059669"))
            self.table.setItem(row, 4, pagado_item)

            # Saldo
            saldo = float(apartado['saldo_pendiente'])
            saldo_item = QTableWidgetItem(f"Q {saldo:.2f}")
            saldo_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if saldo > 0:
                saldo_item.setForeground(QColor("#DC2626"))
                saldo_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(row, 5, saldo_item)

            # Porcentaje
            porcentaje = float(apartado['porcentaje_pagado'])
            porcentaje_item = QTableWidgetItem(f"{porcentaje:.1f}%")
            porcentaje_item.setTextAlignment(Qt.AlignCenter)
            if porcentaje >= 75:
                porcentaje_item.setForeground(QColor("#059669"))
            elif porcentaje >= 50:
                porcentaje_item.setForeground(QColor("#F59E0B"))
            else:
                porcentaje_item.setForeground(QColor("#DC2626"))
            self.table.setItem(row, 6, porcentaje_item)

            # Acciones
            acciones_widget = QWidget()
            acciones_layout = QHBoxLayout()
            acciones_layout.setContentsMargins(5, 5, 5, 5)
            acciones_layout.setSpacing(5)

            if saldo > 0 and self.id_caja_actual:
                pago_btn = QPushButton("💰 Pagar")
                pago_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #F5C800;
                        padding: 5px 10px;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #E5B800;
                    }
                """)
                pago_btn.clicked.connect(lambda checked, a=apartado: self.registrar_pago(a))
                acciones_layout.addWidget(pago_btn)

            detalle_btn = QPushButton("📋 Ver")
            detalle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #2563EB;
                }
            """)
            detalle_btn.clicked.connect(lambda checked, a=apartado: self.ver_detalle(a))
            acciones_layout.addWidget(detalle_btn)

            if saldo > 0:
                cancel_btn = QPushButton("❌ Cancelar")
                cancel_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FEE2E2;
                        color: #DC2626;
                        padding: 5px 10px;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #FECACA;
                    }
                """)
                cancel_btn.clicked.connect(lambda checked, a=apartado: self.cancelar_apartado(a))
                acciones_layout.addWidget(cancel_btn)

            acciones_widget.setLayout(acciones_layout)
            self.table.setCellWidget(row, 7, acciones_widget)

        self.table.resizeRowsToContents()

    def agregar_apartado(self):
        """Abre el diálogo para crear un nuevo apartado"""
        dialog = DialogoApartado(self.apartado_service, self)
        if dialog.exec_():
            self.cargar_apartados()

    def registrar_pago(self, apartado: dict):
        """Registra un pago para un apartado"""
        if not self.id_caja_actual:
            QMessageBox.warning(self, "Caja Cerrada", 
                "❌ No hay una caja abierta. Debe abrir caja primero.")
            return

        # Obtener datos actualizados
        detalle = self.apartado_service.obtener_detalle_apartado(apartado['id_apartado'])
        if not detalle:
            QMessageBox.warning(self, "Error", "No se pudo obtener el detalle del apartado")
            return

        dialog = DialogoPagoApartado(detalle, self.apartado_service, self)
        if dialog.exec_():
            self.cargar_apartados()

    def ver_detalle(self, apartado: dict):
        """Muestra el detalle completo del apartado"""
        detalle = self.apartado_service.obtener_detalle_apartado(apartado['id_apartado'])
        historial = self.apartado_service.obtener_historial_pagos(apartado['id_apartado'])
        
        if not detalle:
            QMessageBox.warning(self, "Error", "No se pudo obtener el detalle del apartado")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"📋 Detalle Apartado #{apartado['id_apartado']}")
        dialog.setMinimumSize(700, 600)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel(f"Detalle del Apartado #{detalle['id_apartado']}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Información del apartado
        info_group = QGroupBox("Información del Apartado")
        info_layout = QFormLayout()
        info_layout.setSpacing(10)
        
        total = float(detalle['monto_final'])
        pagado = float(detalle['total_pagado'])
        saldo = total - pagado
        
        info_layout.addRow("Cliente:", QLabel(f"{detalle['cliente_nombre']} {detalle.get('cliente_apellido', '')}"))
        info_layout.addRow("Teléfono:", QLabel(detalle.get('cliente_telefono') or 'N/A'))
        info_layout.addRow("Producto:", QLabel(f"{detalle['producto_nombre']} {detalle.get('marca', '')} {detalle.get('modelo', '')}"))
        info_layout.addRow("Monto original:", QLabel(f"Q {float(detalle['monto_original']):.2f}"))
        
        if float(detalle.get('descuento_pactado', 0)) > 0:
            info_layout.addRow("Descuento:", QLabel(f"- Q {float(detalle['descuento_pactado']):.2f}"))
        if float(detalle.get('incremento_pactado', 0)) > 0:
            info_layout.addRow("Modificar precio:", QLabel(f"+ Q {float(detalle['incremento_pactado']):.2f}"))
        
        info_layout.addRow("Total a pagar:", QLabel(f"Q {total:.2f}"))
        info_layout.addRow("Pagado:", QLabel(f"Q {pagado:.2f}"))
        
        saldo_label = QLabel(f"Q {saldo:.2f}")
        saldo_label.setStyleSheet("color: #DC2626; font-weight: bold;")
        info_layout.addRow("Saldo pendiente:", saldo_label)
        
        info_layout.addRow("Fecha Inicio:", QLabel(str(detalle['fecha_inicio'])))
        info_layout.addRow("Estado:", QLabel(detalle['estado']))
        
        if detalle.get('es_envio'):
            info_layout.addRow("Es Envío:", QLabel("✅ Sí"))
            if detalle.get('empresa_envio_nombre'):
                info_layout.addRow("Empresa:", QLabel(detalle['empresa_envio_nombre']))
            if detalle.get('numero_guia'):
                info_layout.addRow("N° Guía:", QLabel(detalle['numero_guia']))
        
        if detalle.get('forma_pago_acordada'):
            formas = {'EF': 'Efectivo', 'TC/TD': 'Tarjeta', 'TF': 'Transferencia', 'DP': 'Depósito'}
            info_layout.addRow("Forma de pago:", QLabel(formas.get(detalle['forma_pago_acordada'], detalle['forma_pago_acordada'])))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Historial de pagos
        if historial:
            history_group = QGroupBox(f"📜 Historial de Pagos ({len(historial)} pagos)")
            history_layout = QVBoxLayout()
            
            history_table = QTableWidget()
            history_table.setColumnCount(4)
            history_table.setHorizontalHeaderLabels(["Fecha", "Monto", "Usuario", "Descripción"])
            history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            history_table.setEditTriggers(QTableWidget.NoEditTriggers)
            history_table.setRowCount(len(historial))
            
            for i, pago in enumerate(historial):
                history_table.setItem(i, 0, QTableWidgetItem(str(pago['fecha_pago'])))
                monto_pago = float(pago['monto'])
                monto_item = QTableWidgetItem(f"Q {monto_pago:.2f}")
                monto_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                history_table.setItem(i, 1, monto_item)
                history_table.setItem(i, 2, QTableWidgetItem(pago.get('usuario_nombre', 'N/A')))
                desc = pago.get('descripcion', 'Abono a apartado')[:50]
                history_table.setItem(i, 3, QTableWidgetItem(desc))
            
            history_layout.addWidget(history_table)
            history_group.setLayout(history_layout)
            layout.addWidget(history_group)
        else:
            no_pagos = QLabel("📭 No hay pagos registrados aún")
            no_pagos.setStyleSheet("color: #6B7280; padding: 20px; text-align: center;")
            no_pagos.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_pagos)
        
        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #F5C800;
                border-radius: 8px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #E5B800;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def cancelar_apartado(self, apartado: dict):
        """Cancela un apartado"""
        if not self.id_caja_actual:
            QMessageBox.warning(self, "Caja Cerrada", 
                "❌ Debe abrir la caja para procesar una cancelación.")
            return

        total_pagado = float(apartado['total_pagado'])
        mensaje = f"⚠️ ¿Está seguro de CANCELAR el apartado #{apartado['id_apartado']}?\n\n"
        
        if total_pagado > 0:
            mensaje += f"💰 El cliente ha pagado Q {total_pagado:.2f}.\n"
            mensaje += f"📌 Este monto NO se devuelve — queda como ingreso en caja.\n\n"
            mensaje += f"¿Desea continuar con la cancelación?"
        else:
            mensaje += "❌ El cliente no ha realizado ningún pago.\n"
            mensaje += f"📝 Solo se cancelará el apartado.\n\n"
            mensaje += f"¿Desea continuar?"

        reply = QMessageBox.question(
            self,
            "Confirmar Cancelación",
            mensaje,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            resultado = self.apartado_service.cancelar_apartado(apartado['id_apartado'])

            if resultado.get('success'):
                msg = f"✅ Apartado #{apartado['id_apartado']} cancelado."
                if resultado.get('monto_retenido', 0) > 0:
                    msg += f"\n💰 Q {resultado['monto_retenido']:.2f} quedan registrados como ingreso en caja."
                QMessageBox.information(self, "Apartado Cancelado", msg)
                self.cargar_apartados()
            else:
                QMessageBox.critical(self, "Error", f"❌ {resultado.get('message', 'No se pudo cancelar el apartado')}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    ventana = VentanaApartados(id_usuario_actual=1, id_caja_actual=1)
    ventana.resize(1300, 700)
    ventana.show()
    sys.exit(app.exec_())