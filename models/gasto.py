class Gasto:
    TIPO_PROVEEDOR = 'PAGO PROVEEDORES'
    TIPO_SUELDOS = 'PAGO SUELDOS'
    TIPO_SERVICIOS = 'PAGO SERVICIOS'
    TIPO_INSUMOS = 'COMPRA INSUMOS'
    TIPO_DEVOLUCION = 'DEVOLUCION APARTADO'

    def __init__(self, id_gasto=None, id_movimiento_fk=None, tipo_gasto=None,
                 descripcion=None, monto=0):
        self.id_gasto = id_gasto
        self.id_movimiento_fk = id_movimiento_fk
        self.tipo_gasto = tipo_gasto
        self.descripcion = descripcion
        self.monto = monto

    def to_dict(self):
        return {
            'id_gasto': self.id_gasto,
            'id_movimiento_fk': self.id_movimiento_fk,
            'tipo_gasto': self.tipo_gasto,
            'descripcion': self.descripcion,
            'monto': self.monto
        }

    @staticmethod
    def from_dict(data):
        return Gasto(
            id_gasto=data.get('id_gasto'),
            id_movimiento_fk=data.get('id_movimiento_fk'),
            tipo_gasto=data.get('tipo_gasto'),
            descripcion=data.get('descripcion'),
            monto=data.get('monto', 0)
        )

    def __str__(self):
        return f"Gasto: {self.tipo_gasto} - Q{self.monto}"