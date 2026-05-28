# UI/productos_ui.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDialog, QFormLayout, QLineEdit, QMessageBox,
                             QHeaderView, QTextEdit, QGroupBox, QComboBox,
                             QScrollArea, QSizePolicy, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.producto_service import ProductoService


class DialogoProducto(QDialog):
    def __init__(self, producto_id=None, parent=None):
        super().__init__(parent)
        self.producto_id = producto_id
        self.service = ProductoService()
        self.producto = None
        if producto_id:
            self.producto = self.service.buscar_por_id(producto_id)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Nuevo Producto" if not self.producto else "Editar Producto")
        self.setMinimumSize(400, 500)
        self.resize(550, 650)
        self.setStyleSheet("background-color: white;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel("Datos del Producto")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del producto")
        self.nombre_input.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #E5E7EB;")
        form_layout.addRow("Nombre (*):", self.nombre_input)

        self.marca_input = QLineEdit()
        self.marca_input.setPlaceholderText("Marca")
        self.marca_input.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #E5E7EB;")
        form_layout.addRow("Marca:", self.marca_input)

        self.modelo_input = QLineEdit()
        self.modelo_input.setPlaceholderText("Modelo")
        self.modelo_input.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #E5E7EB;")
        form_layout.addRow("Modelo:", self.modelo_input)

        self.precio_input = QLineEdit()
        self.precio_input.setPlaceholderText("0.00")
        self.precio_input.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #E5E7EB;")
        self.precio_input.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        form_layout.addRow("Precio Costo (Q):", self.precio_input)

        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Descripción del producto")
        self.descripcion_input.setMaximumHeight(100)
        self.descripcion_input.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #E5E7EB;")
        form_layout.addRow("Descripción:", self.descripcion_input)

        layout.addLayout(form_layout)
        layout.addSpacing(20)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("padding: 8px 16px; background-color: #F3F4F6; border-radius: 8px;")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Guardar")
        save_btn.setStyleSheet("padding: 8px 16px; background-color: #F5C800; border-radius: 8px; font-weight: bold;")
        save_btn.clicked.connect(self.guardar)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        if self.producto:
            self.cargar_datos()

    def cargar_datos(self):
        self.nombre_input.setText(self.producto.nombre)
        self.marca_input.setText(self.producto.marca or '')
        self.modelo_input.setText(self.producto.modelo or '')
        self.precio_input.setText(f"{self.producto.precio_costo:.2f}")
        self.descripcion_input.setText(self.producto.descripcion or '')

    def guardar(self):
        nombre = self.nombre_input.text().strip()
        marca = self.marca_input.text().strip()
        modelo = self.modelo_input.text().strip()
        precio_text = self.precio_input.text().strip()
        descripcion = self.descripcion_input.toPlainText().strip()

        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre del producto es requerido")
            return
        try:
            precio_costo = float(precio_text) if precio_text else 0.0
        except ValueError:
            QMessageBox.warning(self, "Error", "El precio debe ser un número válido")
            return

        try:
            if self.producto:
                self.service.actualizar(
                    self.producto.id_producto, nombre, marca, modelo, descripcion, precio_costo
                )
                QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")
            else:
                self.service.crear(nombre, marca, modelo, descripcion, precio_costo)
                QMessageBox.information(self, "Éxito", "Producto creado correctamente")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {str(e)}")


class VentanaProductos(QWidget):
    def __init__(self):
        super().__init__()
        self.service = ProductoService()
        self.init_ui()
        self.cargar_productos()

    def init_ui(self):
        self.setMinimumSize(800, 500)
        self.setStyleSheet("background-color: #F9FAFB;")

        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        title = QLabel("Gestión de Productos")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()
        add_btn = QPushButton("+ Nuevo Producto")
        add_btn.setStyleSheet("background-color: #F5C800; border-radius: 8px; padding: 8px 16px; font-weight: bold;")
        add_btn.clicked.connect(self.agregar_producto)
        header.addWidget(add_btn)
        layout.addLayout(header)

        # Filtros
        filtros_group = QGroupBox("Filtros de Búsqueda")
        filtros_group.setStyleSheet("""
            QGroupBox { border: 2px solid #E5E7EB; border-radius: 10px; margin-top: 10px; padding-top: 10px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        filtros_layout = QVBoxLayout()
        fila_filtros = QHBoxLayout()
        fila_filtros.setSpacing(12)

        for label, attr in [("Nombre:", "filtro_nombre"), ("Marca:", "filtro_marca"), ("Modelo:", "filtro_modelo")]:
            sub = QVBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 11px; color: #6B7280;")
            entry = QLineEdit()
            entry.setPlaceholderText(f"Buscar por {label.lower().replace(':', '')}...")
            entry.setStyleSheet("padding: 6px; border-radius: 6px; border: 1px solid #E5E7EB;")
            setattr(self, attr, entry)
            sub.addWidget(lbl)
            sub.addWidget(entry)
            fila_filtros.addLayout(sub)
        filtros_layout.addLayout(fila_filtros)

        botones_filtros = QHBoxLayout()
        buscar_btn = QPushButton("Buscar")
        buscar_btn.setStyleSheet("padding: 6px 16px; background-color: #3B82F6; color: white; border-radius: 6px; font-weight: bold;")
        buscar_btn.clicked.connect(self.buscar_productos)
        limpiar_btn = QPushButton("Limpiar Filtros")
        limpiar_btn.setStyleSheet("padding: 6px 16px; background-color: #9CA3AF; color: white; border-radius: 6px;")
        limpiar_btn.clicked.connect(self.limpiar_filtros)
        botones_filtros.addWidget(buscar_btn)
        botones_filtros.addWidget(limpiar_btn)
        botones_filtros.addStretch()
        filtros_layout.addLayout(botones_filtros)
        filtros_group.setLayout(filtros_layout)
        layout.addWidget(filtros_group)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Marca", "Modelo", "Precio Costo", "Descripción", "Acciones"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.setColumnWidth(0, 60)   # ID
        self.table.setColumnWidth(1, 180)  # Nombre
        self.table.setColumnWidth(2, 120)  # Marca
        self.table.setColumnWidth(3, 120)  # Modelo
        self.table.setColumnWidth(4, 100)  # Precio
        self.table.setColumnWidth(6, 200)  # Acciones (más ancho para botones)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)  # Descripción

        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)
        self.table.setStyleSheet("""
            QTableWidget { border: 1px solid #E5E7EB; border-radius: 12px; background-color: white; }
            QHeaderView::section { background-color: #F9FAFB; padding: 8px; font-weight: bold; border-bottom: 1px solid #E5E7EB; }
            QTableWidget::item { padding: 6px; }
        """)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        main_scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_scroll)

    def buscar_productos(self):
        productos = self.service.listar(
            nombre=self.filtro_nombre.text().strip() or None,
            marca=self.filtro_marca.text().strip() or None,
            modelo=self.filtro_modelo.text().strip() or None
        )
        self.mostrar_productos_en_tabla(productos)

    def limpiar_filtros(self):
        self.filtro_nombre.clear()
        self.filtro_marca.clear()
        self.filtro_modelo.clear()
        self.cargar_productos()

    def cargar_productos(self):
        productos = self.service.listar()
        self.mostrar_productos_en_tabla(productos)

    def mostrar_productos_en_tabla(self, productos):
        self.table.setRowCount(len(productos))
        self.table.setUpdatesEnabled(False)

        for row_idx, prod in enumerate(productos):
            # Datos
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(prod.id_producto)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(prod.nombre))
            self.table.setItem(row_idx, 2, QTableWidgetItem(prod.marca or ''))
            self.table.setItem(row_idx, 3, QTableWidgetItem(prod.modelo or ''))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"Q{prod.precio_costo:.2f}"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(prod.descripcion or ''))
            # Centrar todas las celdas
            for col in range(6):
                self.table.item(row_idx, col).setTextAlignment(Qt.AlignCenter)

            # Botones de acciones (simplificados)
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(8)

            edit_btn = QPushButton("Editar")
            edit_btn.setFixedSize(80, 30)
            edit_btn.setStyleSheet("background-color: #3b82f6; color: white; border: none; border-radius: 4px; font-weight: bold;")
            edit_btn.clicked.connect(lambda ch, pid=prod.id_producto: self.editar_producto(pid))

            del_btn = QPushButton("Eliminar")
            del_btn.setFixedSize(80, 30)
            del_btn.setStyleSheet("background-color: #ef4444; color: white; border: none; border-radius: 4px; font-weight: bold;")
            del_btn.clicked.connect(lambda ch, p=prod: self.eliminar_producto(p))

            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(del_btn)
            btn_layout.addStretch()
            self.table.setCellWidget(row_idx, 6, btn_widget)
            self.table.setRowHeight(row_idx, 45)  # Altura fija para que los botones quepan

        self.table.setUpdatesEnabled(True)

        if not productos:
            self.table.setRowCount(1)
            msg = QTableWidgetItem("No se encontraron productos")
            msg.setTextAlignment(Qt.AlignCenter)
            self.table.setSpan(0, 0, 1, 7)
            self.table.setItem(0, 0, msg)

    def agregar_producto(self):
        dlg = DialogoProducto(parent=self)
        if dlg.exec_():
            self.cargar_productos()

    def editar_producto(self, id_producto):
        dlg = DialogoProducto(id_producto, self)
        if dlg.exec_():
            self.cargar_productos()

    def eliminar_producto(self, producto):
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar '{producto.nombre}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.service.eliminar(producto.id_producto)
                QMessageBox.information(self, "Éxito", "Producto eliminado")
                self.cargar_productos()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))