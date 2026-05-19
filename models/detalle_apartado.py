from datetime import date


class DetalleApartado:
    def __init__(self, id_detalle=None, id_apartado_fk=None, id_movimiento_fk=None,
                 fecha_pago=None, monto=0):
        self.id_detalle = id_detalle
        self.id_apartado_fk = id_apartado_fk
        self.id_movimiento_fk = id_movimiento_fk
        self.fecha_pago = fecha_pago or date.today()
        self.monto = monto

    def to_dict(self):
        return {
            'id_detalle': self.id_detalle,
            'id_apartado_fk': self.id_apartado_fk,
            'id_movimiento_fk': self.id_movimiento_fk,
            'fecha_pago': self.fecha_pago,
            'monto': self.monto
        }

    @staticmethod
    def from_dict(data):
        return DetalleApartado(
            id_detalle=data.get('id_detalle'),
            id_apartado_fk=data.get('id_apartado_fk'),
            id_movimiento_fk=data.get('id_movimiento_fk'),
            fecha_pago=data.get('fecha_pago'),
            monto=data.get('monto', 0)
        )

    def __str__(self):
        return f"Pago apartado {self.id_apartado_fk}: Q{self.monto} - {self.fecha_pago}"