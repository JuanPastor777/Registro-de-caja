class Producto:
    def __init__(self, id_producto=None, nombre=None, marca=None,
                 modelo=None, descripcion=None, precio_costo=0):
        self.id_producto = id_producto
        self.nombre = nombre
        self.marca = marca
        self.modelo = modelo
        self.descripcion = descripcion
        self.precio_costo = precio_costo

    def to_dict(self):
        return {
            'id_producto': self.id_producto,
            'nombre': self.nombre,
            'marca': self.marca,
            'modelo': self.modelo,
            'descripcion': self.descripcion,
            'precio_costo': self.precio_costo
        }

    @staticmethod
    def from_dict(data):
        return Producto(
            id_producto=data.get('id_producto'),
            nombre=data.get('nombre'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            descripcion=data.get('descripcion'),
            precio_costo=data.get('precio_costo', 0)
        )

    def __str__(self):
        return f"{self.nombre} - {self.marca} {self.modelo}"


