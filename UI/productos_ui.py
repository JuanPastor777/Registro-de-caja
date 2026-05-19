# UI/productos_ui.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDialog, QFormLayout, QLineEdit, QMessageBox,
                             QHeaderView, QTextEdit, QGroupBox, QComboBox)
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
        self.setFixedSize(550, 650)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)

        title = QLabel("Datos del Producto")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(20)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Nombre
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del producto")
        self.nombre_input.setStyleSheet("""
            QLineEdit {
                padding: 10px; 
                border-radius: 6px; 
                border: 1px solid #E5E7EB;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #F5C800;
            }
        """)
        form_layout.addRow("Nombre (*):", self.nombre_input)

        # Marca
        self.marca_input = QLineEdit()
        self.marca_input.setPlaceholderText("Marca")
        self.marca_input.setStyleSheet("""
            QLineEdit {
                padding: 10px; 
                border-radius: 6px; 
                border: 1px solid #E5E7EB;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #F5C800;
            }
        """)
        form_layout.addRow("Marca:", self.marca_input)

        # Modelo
        self.modelo_input = QLineEdit()
        self.modelo_input.setPlaceholderText("Modelo")
        self.modelo_input.setStyleSheet("""
            QLineEdit {
                padding: 10px; 
                border-radius: 6px; 
                border: 1px solid #E5E7EB;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #F5C800;
            }
        """)
        form_layout.addRow("Modelo:", self.modelo_input)

        # Precio Costo
        self.precio_input = QLineEdit()
        self.precio_input.setPlaceholderText("0.00")
        self.precio_input.setStyleSheet("""
            QLineEdit {
                padding: 10px; 
                border-radius: 6px; 
                border: 1px solid #E5E7EB;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #F5C800;
            }
        """)
        self.precio_input.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        form_layout.addRow("Precio Costo (Q):", self.precio_input)

        # Descripción
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Descripción del producto")
        self.descripcion_input.setMaximumHeight(120)
        self.descripcion_input.setStyleSheet("""
            QTextEdit {
                padding: 10px; 
                border-radius: 6px; 
                border: 1px solid #E5E7EB;
                font-size: 12px;
            }
            QTextEdit:focus {
                border: 2px solid #F5C800;
            }
        """)
        form_layout.addRow("Descripción:", self.descripcion_input)

        layout.addLayout(form_layout)
        layout.addSpacing(30)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px; 
                background-color: #F3F4F6; 
                border-radius: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E5E7EB;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Guardar")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px; 
                background-color: #F5C800; 
                border-radius: 8px; 
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E5B800;
            }
        """)
        save_btn.clicked.connect(self.guardar)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        if self.producto:
            self.cargar_datos()

    def cargar_datos(self):
        self.nombre_input.setText(self.producto.nombre)
        self.marca_input.setText(self.producto.marca if self.producto.marca else '')
        self.modelo_input.setText(self.producto.modelo if self.producto.modelo else '')
        self.precio_input.setText(f"{self.producto.precio_costo:.2f}")
        self.descripcion_input.setText(self.producto.descripcion if self.producto.descripcion else '')

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
                    self.producto.id_producto, 
                    nombre, 
                    marca, 
                    modelo, 
                    descripcion, 
                    precio_costo
                )
                QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")
            else:
                self.service.crear(nombre, marca, modelo, descripcion, precio_costo)
                QMessageBox.information(self, "Éxito", "Producto creado correctamente")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el producto: {str(e)}")


class VentanaProductos(QWidget):
    def __init__(self):
        super().__init__()
        self.service = ProductoService()
        self.init_ui()
        self.cargar_productos()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        title = QLabel("Gestión de Productos")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("+ Nuevo Producto")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5C800;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E5B800;
            }
        """)
        add_btn.clicked.connect(self.agregar_producto)
        header.addWidget(add_btn)

        layout.addLayout(header)

        # Filtros
        filtros_group = QGroupBox("Filtros de Búsqueda")
        filtros_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E5E7EB;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        filtros_layout = QVBoxLayout()
        fila_filtros = QHBoxLayout()
        fila_filtros.setSpacing(15)
        
        # Filtro nombre
        nombre_layout = QVBoxLayout()
        nombre_label = QLabel("Nombre:")
        nombre_label.setStyleSheet("font-size: 11px; color: #6B7280;")
        self.filtro_nombre = QLineEdit()
        self.filtro_nombre.setPlaceholderText("Buscar por nombre...")
        self.filtro_nombre.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #E5E7EB;")
        nombre_layout.addWidget(nombre_label)
        nombre_layout.addWidget(self.filtro_nombre)
        fila_filtros.addLayout(nombre_layout)
        
        # Filtro marca
        marca_layout = QVBoxLayout()
        marca_label = QLabel("Marca:")
        marca_label.setStyleSheet("font-size: 11px; color: #6B7280;")
        self.filtro_marca = QLineEdit()
        self.filtro_marca.setPlaceholderText("Buscar por marca...")
        self.filtro_marca.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #E5E7EB;")
        marca_layout.addWidget(marca_label)
        marca_layout.addWidget(self.filtro_marca)
        fila_filtros.addLayout(marca_layout)
        
        # Filtro modelo
        modelo_layout = QVBoxLayout()
        modelo_label = QLabel("Modelo:")
        modelo_label.setStyleSheet("font-size: 11px; color: #6B7280;")
        self.filtro_modelo = QLineEdit()
        self.filtro_modelo.setPlaceholderText("Buscar por modelo...")
        self.filtro_modelo.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #E5E7EB;")
        modelo_layout.addWidget(modelo_label)
        modelo_layout.addWidget(self.filtro_modelo)
        fila_filtros.addLayout(modelo_layout)
        
        filtros_layout.addLayout(fila_filtros)
        
        # Botones
        botones_filtros = QHBoxLayout()
        botones_filtros.setSpacing(10)
        
        buscar_btn = QPushButton("🔍 Buscar")
        buscar_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #3B82F6;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        buscar_btn.clicked.connect(self.buscar_productos)
        botones_filtros.addWidget(buscar_btn)
        
        limpiar_btn = QPushButton("Limpiar Filtros")
        limpiar_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #9CA3AF;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #6B7280;
            }
        """)
        limpiar_btn.clicked.connect(self.limpiar_filtros)
        botones_filtros.addWidget(limpiar_btn)
        
        botones_filtros.addStretch()
        filtros_layout.addLayout(botones_filtros)
        
        filtros_group.setLayout(filtros_layout)
        layout.addWidget(filtros_group)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Marca", "Modelo", "Precio Costo", "Descripción", "Acciones"])
        
        # Configurar el ancho de las columnas
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # Establecer anchos específicos
        self.table.setColumnWidth(0, 60)   # ID
        self.table.setColumnWidth(1, 200)  # Nombre
        self.table.setColumnWidth(2, 150)  # Marca
        self.table.setColumnWidth(3, 150)  # Modelo
        self.table.setColumnWidth(4, 120)  # Precio Costo
        self.table.setColumnWidth(6, 180)  # Acciones
        
        # Columna Descripción se estira
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)
        self.table.setTextElideMode(Qt.ElideNone)
        
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E7EB;
                border-radius: 12px;
                background-color: white;
                gridline-color: #F3F4F6;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                padding: 12px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #E5E7EB;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:alternate {
                background-color: #F9FAFB;
            }
        """)
        
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        self.setLayout(layout)

    def buscar_productos(self):
        nombre = self.filtro_nombre.text().strip()
        marca = self.filtro_marca.text().strip()
        modelo = self.filtro_modelo.text().strip()
        
        productos = self.service.listar(
            nombre=nombre if nombre else None, 
            marca=marca if marca else None,
            modelo=modelo if modelo else None
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
        
        for row_idx, producto in enumerate(productos):
            # ID (centrado)
            id_item = QTableWidgetItem(str(producto.id_producto))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, id_item)
            
            # Nombre (centrado)
            nombre_item = QTableWidgetItem(producto.nombre)
            nombre_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, nombre_item)
            
            # Marca (centrado)
            marca_item = QTableWidgetItem(producto.marca or '')
            marca_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 2, marca_item)
            
            # Modelo (centrado)
            modelo_item = QTableWidgetItem(producto.modelo or '')
            modelo_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 3, modelo_item)
            
            # Precio (centrado)
            precio_item = QTableWidgetItem(f"Q{producto.precio_costo:.2f}")
            precio_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 4, precio_item)
            
            # Descripción (centrado)
            desc_item = QTableWidgetItem(producto.descripcion or '')
            desc_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 5, desc_item)

            # Acciones (widget con botones centrados)
            acciones_widget = QWidget()
            acciones_layout = QHBoxLayout()
            acciones_layout.setContentsMargins(8, 4, 8, 4)
            acciones_layout.setSpacing(8)

            edit_btn = QPushButton("✏️ Editar")
            edit_btn.setFixedSize(80, 30)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border-radius: 4px;
                    border: none;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2563EB;
                }
            """)
            edit_btn.clicked.connect(lambda checked, p=producto: self.editar_producto(p.id_producto))
            acciones_layout.addWidget(edit_btn)

            delete_btn = QPushButton("🗑️ Eliminar")
            delete_btn.setFixedSize(80, 30)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444;
                    color: white;
                    border-radius: 4px;
                    border: none;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                }
            """)
            delete_btn.clicked.connect(lambda checked, p=producto: self.eliminar_producto(p))
            acciones_layout.addWidget(delete_btn)
            
            # Centrar horizontalmente los botones
            acciones_layout.addStretch()
            acciones_layout.insertStretch(0, 1)  # Stretch al inicio también para centrar
            acciones_widget.setLayout(acciones_layout)
            self.table.setCellWidget(row_idx, 6, acciones_widget)
            
            self.table.resizeRowToContents(row_idx)

        self.table.setUpdatesEnabled(True)
        
        if len(productos) == 0:
            self.table.setRowCount(1)
            mensaje = QTableWidgetItem("No se encontraron productos")
            mensaje.setTextAlignment(Qt.AlignCenter)
            font = QFont()
            font.setPointSize(12)
            mensaje.setFont(font)
            self.table.setSpan(0, 0, 1, 7)
            self.table.setItem(0, 0, mensaje)
            self.table.resizeRowToContents(0)

    def agregar_producto(self):
        dialog = DialogoProducto(parent=self)
        if dialog.exec_():
            self.cargar_productos()

    def editar_producto(self, id_producto):
        dialog = DialogoProducto(id_producto, self)
        if dialog.exec_():
            self.cargar_productos()

    def eliminar_producto(self, producto):
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar el producto '{producto.nombre}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.service.eliminar(producto.id_producto)
                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
                self.cargar_productos()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el producto: {str(e)}")