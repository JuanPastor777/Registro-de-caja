# UI/ventas_ui.py

import sys
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QGroupBox,
    QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox,
    QMessageBox, QHeaderView, QDialog, QCheckBox, QFrame,
    QSizePolicy, QApplication, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.conexion import DatabaseConnection
from services.venta_service import ServiceVenta

# ========== ESTILOS ==========
ESTILO_GLOBAL = """
    QWidget { font-family: 'Segoe UI'; font-size: 14px; background-color: #F8FAFC; color: #1E293B; }
    QGroupBox { font-weight: bold; border: 1.5px solid #E2E8F0; border-radius: 12px; margin-top: 12px; padding-top: 12px; background: white; }
    QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; background: white; }
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { border: 1.5px solid #CBD5E1; border-radius: 8px; padding: 8px 12px; background: white; }
    QPushButton { border-radius: 8px; padding: 8px 16px; font-weight: 600; border: none; background: #E2E8F0; }
    QPushButton:hover { background: #CBD5E1; }
    QTableWidget { border: 1.5px solid #E2E8F0; border-radius: 12px; background: white; gridline-color: #F1F5F9; }
    QHeaderView::section { background: #F1F5F9; padding: 10px; font-weight: 700; }
"""
BTN_PRIMARY = "QPushButton { background: #F5C800; color: white; border-radius: 8px; padding: 10px 20px; font-weight: 700; } QPushButton:hover { background: #4F46E5; }"
BTN_SUCCESS = "QPushButton { background: #10B981; color: white; border-radius: 8px; padding: 12px 24px; font-weight: 700; } QPushButton:hover { background: #059669; }"
BTN_DANGER = "QPushButton { background: #FEE2E2; color: #DC2626; border-radius: 6px; padding: 4px 10px; font-weight: 700; }"
BTN_OUTLINE = "QPushButton { background: white; color: #6366F1; border: 1.5px solid #6366F1; border-radius: 8px; padding: 8px 16px; } QPushButton:hover { background: #EEF2FF; }"
BTN_SECONDARY = "QPushButton { background: #F1F5F9; color: #475569; border: 1px solid #CBD5E1; border-radius: 8px; padding: 8px 16px; } QPushButton:hover { background: #E2E8F0; }"

# ========== DIÁLOGOS ==========
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
        layout.addWidget(titulo)

        form = QFormLayout()
        self.input_nombre = QLineEdit()
        self.input_apellido = QLineEdit()
        self.input_telefono = QLineEdit()
        form.addRow("Nombre *", self.input_nombre)
        form.addRow("Apellido", self.input_apellido)
        form.addRow("Teléfono", self.input_telefono)
        layout.addLayout(form)

        botones = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_guardar = QPushButton("Guardar Cliente")
        btn_guardar.setStyleSheet(BTN_PRIMARY)
        btn_guardar.clicked.connect(self.guardar)
        botones.addWidget(btn_cancelar)
        botones.addWidget(btn_guardar)
        layout.addLayout(botones)
        self.setLayout(layout)

    def guardar(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "Nombre obligatorio")
            return
        apellido = self.input_apellido.text().strip() or None
        telefono = self.input_telefono.text().strip() or None
        query = "INSERT INTO public.cliente (nombre, apellido, telefono) VALUES (%s, %s, %s) RETURNING id_cliente"
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
        layout.addWidget(titulo)

        form = QFormLayout()
        self.input_nombre = QLineEdit()
        self.input_marca = QLineEdit()
        self.input_modelo = QLineEdit()
        self.input_descripcion = QLineEdit()
        self.input_precio = QDoubleSpinBox()
        self.input_precio.setMinimum(0)
        self.input_precio.setPrefix("Q ")
        self.input_precio.setValue(0)
        form.addRow("Nombre *", self.input_nombre)
        form.addRow("Marca", self.input_marca)
        form.addRow("Modelo", self.input_modelo)
        form.addRow("Descripción", self.input_descripcion)
        form.addRow("Precio *", self.input_precio)
        layout.addLayout(form)

        botones = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_guardar = QPushButton("Guardar Producto")
        btn_guardar.setStyleSheet(BTN_PRIMARY)
        btn_guardar.clicked.connect(self.guardar)
        botones.addWidget(btn_cancelar)
        botones.addWidget(btn_guardar)
        layout.addLayout(botones)
        self.setLayout(layout)

    def guardar(self):
        nombre = self.input_nombre.text().strip()
        precio = self.input_precio.value()
        if not nombre or precio <= 0:
            QMessageBox.warning(self, "Error", "Nombre y precio válido")
            return
        marca = self.input_marca.text().strip() or None
        modelo = self.input_modelo.text().strip() or None
        desc = self.input_descripcion.text().strip() or None
        query = "INSERT INTO public.producto (nombre, marca, modelo, descripcion, precio_costo) VALUES (%s,%s,%s,%s,%s) RETURNING id_producto"
        resultado = self.db.fetch_one(query, (nombre, marca, modelo, desc, precio))
        if resultado:
            self.producto_creado = {
                'id_producto': resultado['id_producto'],
                'nombre': nombre,
                'marca': marca,
                'modelo': modelo,
                'descripcion': desc,
                'precio_costo': precio
            }
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "No se pudo guardar")


class DialogoPagoMixto(QDialog):
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
        layout.addWidget(titulo)

        info = QLabel(f"Total a pagar: Q {self.total:.2f}")
        info.setStyleSheet("color:#6366F1;font-weight:700")
        layout.addWidget(info)

        form = QFormLayout()
        self.spin_efectivo = QDoubleSpinBox()
        self.spin_efectivo.setMaximum(9999999)
        self.spin_efectivo.setPrefix("Q ")
        self.spin_tarjeta = QDoubleSpinBox()
        self.spin_tarjeta.setMaximum(9999999)
        self.spin_tarjeta.setPrefix("Q ")
        self.spin_transferencia = QDoubleSpinBox()
        self.spin_transferencia.setMaximum(9999999)
        self.spin_transferencia.setPrefix("Q ")
        self.spin_deposito = QDoubleSpinBox()
        self.spin_deposito.setMaximum(9999999)
        self.spin_deposito.setPrefix("Q ")

        for s in (self.spin_efectivo, self.spin_tarjeta, self.spin_transferencia, self.spin_deposito):
            s.valueChanged.connect(self._actualizar_restante)

        form.addRow("💵 Efectivo:", self.spin_efectivo)
        form.addRow("💳 Tarjeta:", self.spin_tarjeta)
        form.addRow("🏦 Transferencia:", self.spin_transferencia)
        form.addRow("📥 Depósito:", self.spin_deposito)
        layout.addLayout(form)

        self.lbl_restante = QLabel(f"Restante: Q {self.total:.2f}")
        self.lbl_restante.setStyleSheet("font-weight:700;color:#DC2626")
        layout.addWidget(self.lbl_restante)

        botones = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_ok = QPushButton("Confirmar Pago")
        btn_ok.setStyleSheet(BTN_SUCCESS)
        btn_ok.clicked.connect(self._confirmar)
        botones.addWidget(btn_cancelar)
        botones.addWidget(btn_ok)
        layout.addLayout(botones)
        self.setLayout(layout)

    def _actualizar_restante(self):
        suma = (self.spin_efectivo.value() + self.spin_tarjeta.value() +
                self.spin_transferencia.value() + self.spin_deposito.value())
        restante = self.total - suma
        self.lbl_restante.setText(f"Restante: Q {max(restante, 0):.2f}")
        color = "#10B981" if abs(restante) < 0.01 else "#DC2626"
        self.lbl_restante.setStyleSheet(f"font-weight:700;color:{color}")

    def _confirmar(self):
        suma = (self.spin_efectivo.value() + self.spin_tarjeta.value() +
                self.spin_transferencia.value() + self.spin_deposito.value())
        if abs(suma - self.total) > 0.01:
            QMessageBox.warning(self, "Error",
                                f"La suma ({suma:.2f}) no coincide con el total ({self.total:.2f})")
            return
        self.resultado_pagos = {
            'EF': self.spin_efectivo.value(),
            'TC/TD': self.spin_tarjeta.value(),
            'TF': self.spin_transferencia.value(),
            'DP': self.spin_deposito.value(),
        }
        self.accept()


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

        top = QHBoxLayout()
        top.addWidget(QLabel("Seleccionar Cliente"))
        top.addStretch()
        btn_nuevo = QPushButton("+ Nuevo Cliente")
        btn_nuevo.setStyleSheet(BTN_OUTLINE)
        btn_nuevo.clicked.connect(self.abrir_nuevo_cliente)
        top.addWidget(btn_nuevo)
        layout.addLayout(top)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Buscar...")
        self.search.textChanged.connect(self.buscar)
        layout.addWidget(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Teléfono"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.doubleClicked.connect(self.seleccionar)
        layout.addWidget(self.table)

        botones = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_ok = QPushButton("Seleccionar")
        btn_ok.setStyleSheet(BTN_PRIMARY)
        btn_ok.clicked.connect(self.seleccionar)
        botones.addWidget(btn_cancelar)
        botones.addWidget(btn_ok)
        layout.addLayout(botones)
        self.setLayout(layout)

    def abrir_nuevo_cliente(self):
        dlg = DialogoNuevoCliente(self)
        if dlg.exec_():
            self.cliente_seleccionado = dlg.cliente_creado
            self.accept()

    def cargar_clientes(self):
        self.clientes_data = self.db.fetch_all(
            "SELECT id_cliente, nombre, apellido, telefono FROM cliente ORDER BY nombre"
        ) or []
        self.actualizar_tabla(self.clientes_data)

    def actualizar_tabla(self, datos):
        self.table.setRowCount(len(datos))
        for i, c in enumerate(datos):
            self.table.setItem(i, 0, QTableWidgetItem(str(c['id_cliente'])))
            self.table.setItem(i, 1, QTableWidgetItem(c.get('nombre', '')))
            self.table.setItem(i, 2, QTableWidgetItem(c.get('apellido', '') or ''))
            self.table.setItem(i, 3, QTableWidgetItem(c.get('telefono', '') or ''))

    def buscar(self):
        texto = self.search.text().lower()
        if not texto:
            self.actualizar_tabla(self.clientes_data)
            return
        filtrados = [c for c in self.clientes_data if texto in f"{c['nombre']} {c.get('apellido','')}".lower()
                     or texto in (c.get('telefono', '') or '').lower()]
        self.actualizar_tabla(filtrados)

    def seleccionar(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un cliente")
            return
        cid = int(self.table.item(row, 0).text())
        self.cliente_seleccionado = next((c for c in self.clientes_data if c['id_cliente'] == cid), None)
        self.accept()


# ========== VENTANA PRINCIPAL ==========
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
        self.precio_original = 0
        self.precio_final = 0
        self._tipo_doc = "FAC"
        self.init_ui()
        self.cargar_productos()
        self.cargar_empresas()

    def init_ui(self):
        self.setWindowTitle("Ventas — Tech Shop")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        titulo = QLabel(" Nueva Venta")
        titulo.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(titulo)
        header.addStretch()
        self.lbl_caja = QLabel("⚡ Verificando caja...")
        self.lbl_caja.setStyleSheet("background:#FEF3C7;color:#92400E;border-radius:16px;padding:6px 16px;font-weight:600")
        header.addWidget(self.lbl_caja)
        layout.addLayout(header)

        QTimer.singleShot(200, self.verificar_estado_caja)

        layout.addWidget(self.crear_panel_cliente())

        contenido = QHBoxLayout()
        contenido.setSpacing(20)
        contenido.addWidget(self.crear_panel_izquierdo(), 4)
        contenido.addWidget(self.crear_panel_carrito(), 6)
        layout.addLayout(contenido)

        self.setLayout(layout)

    # ========== MÉTODOS AUXILIARES ==========
    def verificar_estado_caja(self):
        res = self.service.verificar_caja_abierta()
        if res['success']:
            self.lbl_caja.setText("✅ Caja abierta")
            self.lbl_caja.setStyleSheet("background:#D1FAE5;color:#065F46;border-radius:16px;padding:6px 16px;font-weight:600")
        else:
            self.lbl_caja.setText("❌ Sin caja abierta")
            self.lbl_caja.setStyleSheet("background:#FEE2E2;color:#991B1B;border-radius:16px;padding:6px 16px;font-weight:600")

    def crear_panel_cliente(self):
        box = QGroupBox("Cliente")
        layout = QHBoxLayout()
        self.lbl_cliente = QLabel("Ningún cliente seleccionado")
        self.lbl_cliente.setStyleSheet("padding:10px 16px;background:#F8FAFC;border:1.5px dashed #CBD5E1;border-radius:8px;color:#94A3B8")
        self.lbl_cliente.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.lbl_cliente)

        btn_sel = QPushButton(" Seleccionar Cliente")
        btn_sel.setStyleSheet(BTN_PRIMARY)
        btn_sel.clicked.connect(self.seleccionar_cliente)
        layout.addWidget(btn_sel)

        btn_limpiar = QPushButton("✕")
        btn_limpiar.setFixedSize(40, 40)
        btn_limpiar.setStyleSheet(BTN_DANGER)
        btn_limpiar.clicked.connect(self.quitar_cliente)
        layout.addWidget(btn_limpiar)

        box.setLayout(layout)
        return box

    def crear_panel_izquierdo(self):
        w = QWidget()
        ly = QVBoxLayout()
        ly.setSpacing(15)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.addWidget(self.crear_panel_producto())
        ly.addWidget(self.crear_panel_documento())
        ly.addWidget(self.crear_panel_envio())
        ly.addStretch()
        w.setLayout(ly)
        return w

    def crear_panel_producto(self):
        box = QGroupBox("Producto")
        ly = QVBoxLayout()
        ly.setSpacing(10)

        # Búsqueda y botón nuevo
        top = QHBoxLayout()
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("🔍 Buscar producto...")
        self.input_busqueda.textChanged.connect(self.buscar_productos)
        btn_nuevo = QPushButton("+ Nuevo")
        btn_nuevo.setStyleSheet(BTN_OUTLINE)
        btn_nuevo.clicked.connect(self.abrir_nuevo_producto)
        top.addWidget(self.input_busqueda)
        top.addWidget(btn_nuevo)
        ly.addLayout(top)

        # Combo productos
        self.combo_productos = QComboBox()
        self.combo_productos.currentIndexChanged.connect(self.producto_seleccionado)
        ly.addWidget(self.combo_productos)

        # Precio original
        self.lbl_precio_original = QLabel("Precio original: Q 0.00")
        self.lbl_precio_original.setStyleSheet("color:#64748B;font-size:12px; margin-top: 5px;")
        ly.addWidget(self.lbl_precio_original)

        # Panel de modificación de precio (compacto)
        self.mod_frame = QFrame()
        self.mod_frame.setStyleSheet("border:1px solid #E2E8F0; border-radius:8px; padding:6px; background:#F9FAFB; margin-top: 5px;")
        mod_ly = QVBoxLayout(self.mod_frame)
        mod_ly.setSpacing(6)

        self.chk_modificar = QCheckBox("Modificar precio para esta venta")
        self.chk_modificar.setStyleSheet("font-weight:600")
        self.chk_modificar.toggled.connect(self.toggle_modificacion)
        mod_ly.addWidget(self.chk_modificar)

        self.mod_widgets = QWidget()
        mw_ly = QVBoxLayout(self.mod_widgets)
        mw_ly.setSpacing(6)
        self.mod_widgets.setVisible(False)

        # Tipo de modificación (aumento/descuento)
        tipo_row = QHBoxLayout()
        self.radio_aumento = QRadioButton("Aumento")
        self.radio_descuento = QRadioButton("Descuento")
        self.radio_aumento.setChecked(True)
        self.btn_group_mod = QButtonGroup()
        self.btn_group_mod.addButton(self.radio_aumento)
        self.btn_group_mod.addButton(self.radio_descuento)
        tipo_row.addWidget(self.radio_aumento)
        tipo_row.addWidget(self.radio_descuento)
        tipo_row.addStretch()
        mw_ly.addLayout(tipo_row)

        # Valor y tipo (monto/porcentaje)
        valor_row = QHBoxLayout()
        self.combo_tipo_valor = QComboBox()
        self.combo_tipo_valor.addItems(["Monto fijo (Q)", "Porcentaje (%)"])
        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setMinimum(0)
        self.spin_valor.setMaximum(9999999)
        self.spin_valor.setPrefix("Q ")
        self.combo_tipo_valor.currentTextChanged.connect(
            lambda t: self.spin_valor.setPrefix("Q " if "Monto" in t else "%")
        )
        self.spin_valor.valueChanged.connect(self.calcular_precio_modificado)
        valor_row.addWidget(self.combo_tipo_valor)
        valor_row.addWidget(self.spin_valor)
        mw_ly.addLayout(valor_row)

        # Precio final
        self.lbl_precio_final = QLabel("Precio final: Q 0.00")
        self.lbl_precio_final.setStyleSheet("font-weight:700;color:#10B981;font-size:13px")
        mw_ly.addWidget(self.lbl_precio_final)

        mod_ly.addWidget(self.mod_widgets)
        ly.addWidget(self.mod_frame)

        # Cantidad (sin descuento adicional)
        cant_layout = QHBoxLayout()
        cant_layout.addWidget(QLabel("Cantidad:"))
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(1)
        self.spin_cantidad.valueChanged.connect(self.actualizar_preview)
        cant_layout.addWidget(self.spin_cantidad)
        cant_layout.addStretch()
        ly.addLayout(cant_layout)

        # Preview subtotal
        self.lbl_preview = QLabel("Subtotal: Q 0.00")
        self.lbl_preview.setStyleSheet("color:#6366F1;font-weight:600; margin-top: 5px;")
        ly.addWidget(self.lbl_preview)

        # Botón agregar
        btn_add = QPushButton("＋ Agregar al Carrito")
        btn_add.setStyleSheet(BTN_PRIMARY)
        btn_add.clicked.connect(self.agregar_producto)
        ly.addWidget(btn_add)

        box.setLayout(ly)
        return box

    def toggle_modificacion(self, checked):
        self.mod_widgets.setVisible(checked)
        if not checked:
            self.calcular_precio_modificado()

    def producto_seleccionado(self):
        p = self.combo_productos.currentData()
        if p:
            self.precio_original = float(p.get('precio_costo', 0))
            self.lbl_precio_original.setText(f"Precio original: Q {self.precio_original:.2f}")
            self.calcular_precio_modificado()
        else:
            self.precio_original = 0

    def calcular_precio_modificado(self):
        if not self.chk_modificar.isChecked() or self.precio_original == 0:
            self.precio_final = self.precio_original
            self.lbl_precio_final.setText(f"Precio final: Q {self.precio_original:.2f}")
            self.actualizar_preview()
            return

        valor = self.spin_valor.value()
        es_porcentaje = "Porcentaje" in self.combo_tipo_valor.currentText()
        modificacion = valor if self.radio_aumento.isChecked() else -valor
        if es_porcentaje:
            ajuste = self.precio_original * (modificacion / 100)
        else:
            ajuste = modificacion
        self.precio_final = max(self.precio_original + ajuste, 0)
        self.lbl_precio_final.setText(f"Precio final: Q {self.precio_final:.2f}")
        self.actualizar_preview()

    def actualizar_preview(self):
        subtotal = self.spin_cantidad.value() * self.precio_final
        self.lbl_preview.setText(f"Subtotal: Q {max(subtotal, 0):.2f}")

    def agregar_producto(self):
        p = self.combo_productos.currentData()
        if not p:
            QMessageBox.warning(self, "Error", "Seleccione producto")
            return
        final_price = self.precio_final if hasattr(self, 'precio_final') else float(p.get('precio_costo', 0))
        if final_price <= 0:
            QMessageBox.warning(self, "Sin precio", "El precio final debe ser mayor a 0")
            return
        cantidad = self.spin_cantidad.value()
        subtotal = cantidad * final_price

        aumento_porcentaje = 0
        aumento_monto = 0
        if self.chk_modificar.isChecked():
            valor = self.spin_valor.value()
            es_porcentaje = "Porcentaje" in self.combo_tipo_valor.currentText()
            if self.radio_aumento.isChecked():
                if es_porcentaje:
                    aumento_porcentaje = valor
                else:
                    aumento_monto = valor
            else:
                if es_porcentaje:
                    aumento_porcentaje = -valor
                else:
                    aumento_monto = -valor

        self.carrito.append({
            'id_producto': p['id_producto'],
            'nombre': p['nombre'],
            'cantidad': cantidad,
            'precio_unitario': final_price,
            'descuento': 0,  # ya no se usa descuento separado
            'subtotal': subtotal,
            'aumento_porcentaje': aumento_porcentaje,
            'aumento_monto': aumento_monto
        })
        self.actualizar_tabla_carrito()
        self.actualizar_total()

        self.spin_cantidad.setValue(1)
        self.input_busqueda.clear()

    def actualizar_tabla_carrito(self):
        self.table.setRowCount(len(self.carrito))
        for i, item in enumerate(self.carrito):
            self.table.setItem(i, 0, QTableWidgetItem(item['nombre']))
            self.table.setItem(i, 1, QTableWidgetItem(str(item['cantidad'])))
            self.table.setItem(i, 2, QTableWidgetItem(f"Q {item['precio_unitario']:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem("-"))  # columna descuento vacía
            sub = QTableWidgetItem(f"Q {item['subtotal']:.2f}")
            sub.setForeground(QColor("#059669"))
            sub.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(i, 4, sub)
            btn = QPushButton("✕")
            btn.setStyleSheet(BTN_DANGER)
            btn.clicked.connect(lambda _, r=i: self.eliminar_producto(r))
            self.table.setCellWidget(i, 5, btn)
        self.lbl_items.setText(f"{len(self.carrito)} producto{'s' if len(self.carrito) != 1 else ''}")

    def eliminar_producto(self, row):
        self.carrito.pop(row)
        self.actualizar_tabla_carrito()
        self.actualizar_total()

    def actualizar_total(self):
        subtotal = sum(item['subtotal'] for item in self.carrito)
        envio = self.spin_envio.value() if self.check_envio.isChecked() else 0
        total = subtotal + envio
        self.lbl_subtotal.setText(f"Q {subtotal:.2f}")
        self.lbl_envio_total.setText(f"Q {envio:.2f}")
        self.lbl_total.setText(f"Q {total:.2f}")

    def crear_panel_documento(self):
        box = QGroupBox("Documento")
        ly = QHBoxLayout()
        ly.setSpacing(15)

        tipo_ly = QVBoxLayout()
        tipo_ly.addWidget(QLabel("Tipo:"))
        btns = QHBoxLayout()
        btns.setSpacing(8)
        self.btn_fac = QPushButton("📄 Factura")
        self.btn_fac.setCheckable(True)
        self.btn_fac.setChecked(True)
        self.btn_fac.clicked.connect(lambda: self.set_tipo_doc("FAC"))
        self.btn_rec = QPushButton("🧾 Recibo")
        self.btn_rec.setCheckable(True)
        self.btn_rec.clicked.connect(lambda: self.set_tipo_doc("REC"))
        btns.addWidget(self.btn_fac)
        btns.addWidget(self.btn_rec)
        tipo_ly.addLayout(btns)
        ly.addLayout(tipo_ly)

        num_ly = QVBoxLayout()
        num_ly.addWidget(QLabel("Número de documento:"))
        self.input_num_doc = QLineEdit()
        self.input_num_doc.setPlaceholderText("Ej. 001-2025-00123")
        num_ly.addWidget(self.input_num_doc)
        ly.addLayout(num_ly)

        box.setLayout(ly)
        return box

    def set_tipo_doc(self, t):
        self._tipo_doc = t
        self.btn_fac.setChecked(t == "FAC")
        self.btn_rec.setChecked(t == "REC")
        estilo_activo = "background:#F5C800;color:white;border-radius:7px;padding:7px 14px;font-weight:700;border:none"
        estilo_inactivo = "background:#F1F5F9;color:#64748B;border-radius:7px;padding:7px 14px;font-weight:600;border:1.5px solid #E2E8F0"
        self.btn_fac.setStyleSheet(estilo_activo if t == "FAC" else estilo_inactivo)
        self.btn_rec.setStyleSheet(estilo_activo if t == "REC" else estilo_inactivo)

    def crear_panel_envio(self):
        self.box_envio = QGroupBox("Envío")
        ly = QVBoxLayout()
        ly.setSpacing(8)

        toggle = QHBoxLayout()
        self.check_envio = QCheckBox("Esta venta es un envío")
        self.check_envio.toggled.connect(self.toggle_envio)
        toggle.addWidget(self.check_envio)
        toggle.addStretch()
        ly.addLayout(toggle)

        self.frame_envio = QFrame()
        envio_ly = QFormLayout()
        envio_ly.setSpacing(8)
        self.combo_empresa = QComboBox()
        envio_ly.addRow("Empresa:", self.combo_empresa)
        self.input_guia = QLineEdit()
        self.input_guia.setPlaceholderText("Número de guía (opcional)")
        envio_ly.addRow("N° Guía:", self.input_guia)
        self.spin_envio = QDoubleSpinBox()
        self.spin_envio.setMaximum(99999)
        self.spin_envio.setPrefix("Q ")
        self.spin_envio.valueChanged.connect(self.actualizar_total)
        envio_ly.addRow("Costo envío:", self.spin_envio)

        self.frame_envio.setLayout(envio_ly)
        self.frame_envio.setVisible(False)
        ly.addWidget(self.frame_envio)

        self.box_envio.setLayout(ly)
        return self.box_envio

    def toggle_envio(self, ch):
        self.frame_envio.setVisible(ch)

    def cargar_empresas(self):
        query = "SELECT id_empresa, nombre, telefono FROM public.empresa_envio ORDER BY nombre"
        emp = self.db.fetch_all(query) or []
        self.empresas_data = emp
        self.combo_empresa.clear()
        for e in emp:
            self.combo_empresa.addItem(e['nombre'], e['id_empresa'])

    def crear_panel_carrito(self):
        w = QWidget()
        ly = QVBoxLayout()
        ly.setSpacing(12)

        top = QHBoxLayout()
        lbl = QLabel("Carrito de Venta")
        lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        top.addWidget(lbl)
        top.addStretch()
        self.lbl_items = QLabel("0 productos")
        self.lbl_items.setStyleSheet("background:#EEF2FF;color:#4F46E5;border-radius:12px;padding:4px 12px;font-weight:600")
        top.addWidget(self.lbl_items)
        ly.addLayout(top)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Producto", "Cant.", "Precio Unit.", "Descuento", "Subtotal", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setColumnWidth(5, 50)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        ly.addWidget(self.table)

        pago_box = QGroupBox("Pago")
        pago_ly = QHBoxLayout()
        pago_ly.setSpacing(20)

        fp_col = QVBoxLayout()
        fp_col.addWidget(QLabel("Forma de pago:"))
        self.combo_pago = QComboBox()
        for cod, lab in [("EF", "💵 Efectivo"), ("TC/TD", "💳 Tarjeta"), ("TF", "🏦 Transferencia"), ("DP", "📥 Depósito"), ("COD", "📦 Contra Entrega")]:
            self.combo_pago.addItem(lab, cod)
        self.combo_pago.addItem("🔀 Pago Mixto", "MIXTO")
        self.combo_pago.currentIndexChanged.connect(self.pago_cambiado)
        fp_col.addWidget(self.combo_pago)
        pago_ly.addLayout(fp_col)

        pagado_col = QVBoxLayout()
        pagado_col.addWidget(QLabel("Estado:"))
        self.check_pagado = QCheckBox("Producto ya pagado")
        self.check_pagado.setChecked(True)
        pagado_col.addWidget(self.check_pagado)
        pago_ly.addLayout(pagado_col)
        pago_ly.addStretch()
        pago_box.setLayout(pago_ly)
        ly.addWidget(pago_box)

        totales_frame = QFrame()
        totales_frame.setStyleSheet("background:white;border:1.5px solid #E2E8F0;border-radius:12px;padding:10px")
        totales_ly = QVBoxLayout()
        totales_ly.setSpacing(6)

        sub_row = QHBoxLayout()
        sub_row.addWidget(QLabel("Subtotal productos:"))
        sub_row.addStretch()
        self.lbl_subtotal = QLabel("Q 0.00")
        sub_row.addWidget(self.lbl_subtotal)
        totales_ly.addLayout(sub_row)

        envio_row = QHBoxLayout()
        envio_row.addWidget(QLabel("Costo envío:"))
        envio_row.addStretch()
        self.lbl_envio_total = QLabel("Q 0.00")
        envio_row.addWidget(self.lbl_envio_total)
        totales_ly.addLayout(envio_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        totales_ly.addWidget(sep)

        total_row = QHBoxLayout()
        total_row.addWidget(QLabel("TOTAL:"))
        total_row.addStretch()
        self.lbl_total = QLabel("Q 0.00")
        self.lbl_total.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.lbl_total.setStyleSheet("color:#10B981")
        total_row.addWidget(self.lbl_total)
        totales_ly.addLayout(total_row)

        totales_frame.setLayout(totales_ly)
        ly.addWidget(totales_frame)

        botones = QHBoxLayout()
        botones.setSpacing(10)
        btn_limpiar = QPushButton(" Limpiar Todo")
        btn_limpiar.clicked.connect(self.confirmar_limpiar)
        btn_limpiar.setStyleSheet(BTN_SECONDARY)
        btn_finalizar = QPushButton("✔ Finalizar Venta")
        btn_finalizar.setStyleSheet(BTN_SUCCESS)
        btn_finalizar.clicked.connect(self.finalizar_venta)
        botones.addWidget(btn_limpiar)
        botones.addWidget(btn_finalizar)
        ly.addLayout(botones)

        w.setLayout(ly)
        return w

    def pago_cambiado(self):
        if self.combo_pago.currentData() == 'COD':
            self.check_pagado.setChecked(False)
        else:
            self.check_pagado.setChecked(True)

    def abrir_nuevo_producto(self):
        dlg = DialogoNuevoProducto(self)
        if dlg.exec_():
            self.productos_data.append(dlg.producto_creado)
            self._llenar_combo(self.productos_data)

    def seleccionar_cliente(self):
        dlg = DialogoSeleccionCliente(self)
        if dlg.exec_():
            self.cliente_actual = dlg.cliente_seleccionado
            nombre = f"{self.cliente_actual['nombre']} {self.cliente_actual.get('apellido', '')}".strip()
            self.lbl_cliente.setText(f"👤 {nombre}")
            self.lbl_cliente.setStyleSheet("padding:10px 16px;background:#EEF2FF;border:1.5px solid #A5B4FC;border-radius:8px;color:#3730A3;font-weight:600")

    def quitar_cliente(self):
        self.cliente_actual = None
        self.lbl_cliente.setText("Ningún cliente seleccionado")
        self.lbl_cliente.setStyleSheet("padding:10px 16px;background:#F8FAFC;border:1.5px dashed #CBD5E1;border-radius:8px;color:#94A3B8")

    def cargar_productos(self):
        query = "SELECT id_producto, nombre, marca, modelo, precio_costo FROM producto ORDER BY nombre"
        self.productos_data = self.db.fetch_all(query) or []
        self._llenar_combo(self.productos_data)

    def _llenar_combo(self, prods):
        self.combo_productos.blockSignals(True)
        self.combo_productos.clear()
        for p in prods:
            texto = p['nombre']
            if p.get('marca'):
                texto += f" - {p['marca']}"
            if p.get('modelo'):
                texto += f" ({p['modelo']})"
            self.combo_productos.addItem(texto, p)
        self.combo_productos.blockSignals(False)
        self.producto_seleccionado()

    def buscar_productos(self):
        t = self.input_busqueda.text().lower()
        if not t:
            self._llenar_combo(self.productos_data)
            return
        filtrados = [p for p in self.productos_data if t in f"{p['nombre']} {p.get('marca', '')} {p.get('modelo', '')}".lower()]
        self._llenar_combo(filtrados)

    def confirmar_limpiar(self):
        if self.carrito:
            resp = QMessageBox.question(self, "Confirmar", "¿Limpiar carrito?", QMessageBox.Yes | QMessageBox.No)
            if resp == QMessageBox.Yes:
                self.limpiar_todo()
        else:
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
        self.check_envio.setChecked(False)
        self.check_pagado.setChecked(True)
        self.combo_pago.setCurrentIndex(0)
        self.set_tipo_doc("FAC")
        self.input_busqueda.clear()
        self.chk_modificar.setChecked(False)
        self.spin_valor.setValue(0)

    def finalizar_venta(self):
        if not self.cliente_actual:
            QMessageBox.warning(self, "Cliente", "Seleccione un cliente")
            return
        if not self.carrito:
            QMessageBox.warning(self, "Carrito", "Agregue productos")
            return
        num = self.input_num_doc.text().strip()
        if not num:
            QMessageBox.warning(self, "Documento", "Ingrese número de documento")
            return
        tipo = self._tipo_doc
        es_envio = self.check_envio.isChecked()
        id_empresa = self.combo_empresa.currentData() if es_envio and self.combo_empresa.count() > 0 else None
        guia = self.input_guia.text().strip() or None
        costo_envio = self.spin_envio.value() if es_envio else 0
        forma = self.combo_pago.currentData()
        pagado = self.check_pagado.isChecked()

        if forma == 'MIXTO':
            total_carrito = sum(i['subtotal'] for i in self.carrito) + costo_envio
            dlg = DialogoPagoMixto(total_carrito, self)
            if not dlg.exec_():
                return
            mix = dlg.resultado_pagos
            resp = self.service.registrar_venta(
                self.cliente_actual['id_cliente'], 'MIXTO', tipo, num,
                es_envio, id_empresa, guia, costo_envio, True, self.carrito, mix
            )
        else:
            resp = self.service.registrar_venta(
                self.cliente_actual['id_cliente'], forma, tipo, num,
                es_envio, id_empresa, guia, costo_envio, pagado, self.carrito
            )

        if resp.get('success'):
            QMessageBox.information(self, "Éxito", f"Venta {resp['numero_documento']} registrada\nTotal: Q {resp['total']:.2f}")
            self.limpiar_todo()
        else:
            QMessageBox.warning(self, "Error", resp.get('message', 'Error desconocido'))


# ========== MAIN ==========
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = VentanasVentas()
    win.resize(1400, 860)
    win.show()
    sys.exit(app.exec_())