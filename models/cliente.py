class Cliente:
    def __init__(self, id_cliente=None, nombre=None, apellido=None, telefono=None):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono

    def to_dict(self):
        return {
            'id_cliente': self.id_cliente,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'telefono': self.telefono
        }

    @staticmethod
    def from_dict(data):
        return Cliente(
            id_cliente=data.get('id_cliente'),
            nombre=data.get('nombre'),
            apellido=data.get('apellido'),
            telefono=data.get('telefono')
        )

    def nombre_completo(self):
        if self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.nombre

    def __str__(self):
        return self.nombre_completo()
