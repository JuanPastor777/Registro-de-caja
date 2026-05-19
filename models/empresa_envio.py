class EmpresaEnvio:
    def __init__(self, id_empresa=None, nombre=None, telefono=None):
        self.id_empresa = id_empresa
        self.nombre = nombre
        self.telefono = telefono

    def to_dict(self):
        return {
            'id_empresa': self.id_empresa,
            'nombre': self.nombre,
            'telefono': self.telefono
        }

    @staticmethod
    def from_dict(data):
        return EmpresaEnvio(
            id_empresa=data.get('id_empresa'),
            nombre=data.get('nombre'),
            telefono=data.get('telefono')
        )

    def __str__(self):
        return self.nombre