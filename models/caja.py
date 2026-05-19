class Caja:
    def __init__(self, id_caja=None, fecha=None):
        self.id_caja = id_caja
        self.fecha = fecha

    def to_dict(self):
        return {
            'id_caja': self.id_caja,
            'fecha': self.fecha
        }

    @staticmethod
    def from_dict(data):
        return Caja(
            id_caja=data.get('id_caja'),
            fecha=data.get('fecha')
        )

    def __str__(self):
        return f"Caja {self.id_caja} - {self.fecha}"
