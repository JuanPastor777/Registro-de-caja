class DetalleVenta:
    def __init__(self, id_detalle=None, id_venta_fk=None, id_producto_fk=None,
                 cantidad=0, precio_unitario=0, subtotal=0, descuento=0):
        self.id_detalle = id_detalle
        self.id_venta_fk = id_venta_fk
        self.id_producto_fk = id_producto_fk
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = subtotal
        self.descuento = descuento

    def to_dict(self):
        return {
            'id_detalle': self.id_detalle,
            'id_venta_fk': self.id_venta_fk,
            'id_producto_fk': self.id_producto_fk,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'subtotal': self.subtotal,
            'descuento': self.descuento
        }

    @staticmethod
    def from_dict(data):
        return DetalleVenta(
            id_detalle=data.get('id_detalle'),
            id_venta_fk=data.get('id_venta_fk'),
            id_producto_fk=data.get('id_producto_fk'),
            cantidad=data.get('cantidad', 0),
            precio_unitario=data.get('precio_unitario', 0),
            subtotal=data.get('subtotal', 0),
            descuento=data.get('descuento', 0)
        )

    def calcular_subtotal(self):
        self.subtotal = self.cantidad * self.precio_unitario - self.descuento
        return self.subtotal

    def __str__(self):
        return f"{self.cantidad} x {self.precio_unitario} = {self.subtotal}"